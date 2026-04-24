# Perda de contexto entre tool calls

![capa](cover.png)

Há uma assimetria invisível no coração de qualquer sistema agêntico construído sobre uma API de LLM: o modelo que raciocina e decide é fundamentalmente diferente do processo que persiste e carrega estado. A inferência do modelo é uma função pura — recebe tokens, produz tokens, não retém absolutamente nada. Quando o seu agente Haystack chama `tool_call("get_slack_messages", channel="engineering")` e recebe a lista de mensagens, esse resultado existe em apenas um lugar: dentro da janela de contexto da chamada HTTP que está viva naquele instante. Uma vez que a requisição termina, o modelo esquece. O harness do agente — o código Python rodando dentro do Lambda — é responsável por capturar esse resultado e injetá-lo de volta no contexto da próxima chamada de inferência. Se ele não fizer isso de forma completa e estruturada, a janela seguinte começa vazia daquele resultado.

O mecanismo exato é o seguinte. O agente executa um `run` — um ciclo de raciocínio que pode conter múltiplos tool calls encadeados. Em cada iteração do loop ReAct, o modelo recebe a mensagem do usuário mais o histórico de trocas anteriores como entrada, produz uma resposta que pode conter um ou mais `tool_use` blocks, e o harness executa esses tools, coleta os resultados como `tool_result` blocks, e os concatena ao contexto antes de invocar o modelo novamente. Esse fluxo pode ser representado como:

```
[system_prompt]
[user_message]                       ← turno inicial
[assistant: tool_use(A)]             ← modelo decide chamar tool A
[tool_result(A): "resultado de A"]   ← harness executa, injeta resultado
[assistant: tool_use(B)]             ← modelo vê resultado de A, decide chamar B
[tool_result(B): "resultado de B"]   ← harness executa, injeta resultado
[assistant: resposta final]          ← modelo vê tudo, produz resposta
```

Enquanto esse loop está ativo — dentro da mesma invocação do Lambda — tudo funciona. O problema não é o loop interno; é o que acontece quando esse run termina e uma segunda mensagem do usuário chega em uma invocação subsequente do Lambda.

Nesse segundo turno, o harness precisa reconstruir o contexto do zero. Ele vai ao MongoDB, busca o histórico de chat, e injeta as mensagens como contexto. Mas qual é o formato desse histórico? Se ele armazena apenas pares `(user_message, assistant_message)` — o padrão mais natural e comum — os `tool_use` e `tool_result` blocks do run anterior não estão lá. O que o modelo vê no segundo turno é uma resposta do assistente que menciona resultados de ferramentas, mas sem os blocos estruturados que provam que aquelas ferramentas foram chamadas e que retornaram aqueles valores. O modelo não tem como saber se está diante de um fato verificado ou de algo que ele mesmo inventou no turno anterior.

A perda de contexto aqui não é dramática nem imediata — é gradual e silenciosa. O modelo vai funcionar bem se a resposta do turno anterior for auto-suficiente. Mas em workflows multi-step, onde o agente coletou um `task_id` do ClickUp no turno 1 para usá-lo no turno 3, esse `task_id` pode estar presente como texto na resposta do assistente mas ausente como dado estruturado verificável. Numa invocação subsequente, o modelo pode não conseguir rastrear de onde aquele ID veio, se ele ainda é válido, se a ação associada a ele foi concluída — e começa a fazer suposições.

O efeito se torna ainda mais pronunciado quando o run contém tool calls com resultados longos. Se o agente buscou 40 mensagens do Slack e a resposta da ferramenta tinha 6 mil tokens, o harness precisa decidir o que fazer com esses 6 mil tokens ao persistir o turno. Estratégias comuns incluem truncar o resultado, armazenar apenas o resumo, ou não armazenar o `tool_result` de forma alguma — apenas a conclusão do assistente. Cada uma dessas escolhas cria uma classe diferente de perda: truncamento cria resultados incompletos, resumo cria imprecisão factual, ausência total cria a situação em que o modelo afirma ter feito algo mas não tem prova estrutural disso.

```
Turno 1 — persiste como:
  user: "crie uma tarefa no ClickUp para o bug X"
  assistant: "criei a tarefa #18472"      ← tool_use/tool_result foram descartados

Turno 2 — harness injeta:
  [user: "crie uma tarefa..."]
  [assistant: "criei a tarefa #18472"]
  [user: "qual o status dessa tarefa?"]

O modelo vê "#18472" como texto na resposta anterior.
Não vê o tool_result com o objeto JSON da tarefa criada.
Não sabe se #18472 foi confirmado pela API ou foi alucinado.
```

Existe também uma categoria de perda que ocorre *dentro* de um único run, em arquiteturas onde o harness não mantém o acúmulo de `tool_result` blocks corretamente entre as iterações do loop. O issue #1738 do `google/adk-python` documenta exatamente esse padrão: o agente chama um tool corretamente, recebe a resposta, e na iteração seguinte do loop age como se nunca tivesse chamado — repetindo a mesma chamada indefinidamente. O motivo é que o estado interno do loop não estava sendo propagado entre iterações; o contexto do `tool_result` era descartado ao invés de ser concatenado ao histórico da janela atual. Esse bug é didaticamente útil porque isola o problema: não é uma falha de persistência entre turns, é uma falha de acumulação dentro de um único run.

A distinção entre esses dois tipos de perda — perda entre runs (cross-turn) e perda dentro do run (intra-run) — é importante porque têm raízes diferentes e correções diferentes. A perda intra-run é um bug de implementação do harness: o loop não está construindo o contexto corretamente. A perda cross-turn é um problema de design da camada de sessão: o esquema de persistência não captura o estado estrutural necessário para reconstruir o contexto de forma fiel. O primeiro pode ser corrigido num pull request; o segundo exige um modelo de dados de sessão.

| Tipo de perda | Onde ocorre | Causa raiz | Sintoma observável |
|---|---|---|---|
| Intra-run | Dentro de um único run, entre iterações | Harness não acumula `tool_result` blocks | Tool call repetido em loop, resultado ignorado |
| Cross-turn (resultado) | Entre runs de turnos diferentes | Histórico não persiste `tool_use`/`tool_result` | Modelo perde rastreabilidade de ações passadas |
| Cross-turn (dados) | Entre runs de turnos diferentes | Resultado longo truncado/resumido ao persistir | Decisões baseadas em dados incompletos ou imprecisos |

O que todos esses cenários têm em comum é a natureza do LLM como função pura. O modelo não tem acesso privilegiado a nada além dos tokens na janela de contexto. Se o `task_id` criado no turno anterior não está nos tokens, o modelo simplesmente não sabe que ele existe. Não há cache interno, não há variável global, não há memória implícita entre chamadas de inferência. Toda continuidade tem que ser construída e injetada explicitamente pelo harness — e essa responsabilidade total pelo estado é exatamente a razão pela qual a camada de sessão precisa ser um objeto de primeira classe no sistema, não um afterthought de persistência de chat.

## Fontes utilizadas

- [LLMAgent loses context/state after tool execution — google/adk-python #1738](https://github.com/google/adk-python/issues/1738)
- [Why AI Agents Forget: The Stateless LLM Problem Explained — Atlan](https://atlan.com/know/why-ai-agents-forget/)
- [Memory and State in LLM Applications — Arize AI](https://arize.com/blog/memory-and-state-in-llm-applications/)
- [Context Engineering for Agents — LangChain Blog](https://blog.langchain.com/context-engineering-for-agents/)
- [Effective Context Engineering for AI Agents — Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [What Is an Agent Harness? — Firecrawl](https://www.firecrawl.dev/blog/what-is-an-agent-harness)
- [Stateful vs Stateless AI Agents: Architecture Guide — Tacnode](https://tacnode.io/post/stateful-vs-stateless-ai-agents-practical-architecture-guide-for-developers)
- [Why AI Agents Fail: 3 Failure Modes — DEV Community / AWS](https://dev.to/aws/why-ai-agents-fail-3-failure-modes-that-cost-you-tokens-and-time-1flb)

---

**Próximo conceito** → [O mecanismo da pergunta repetida](../02-o-mecanismo-da-pergunta-repetida/CONTENT.md)
