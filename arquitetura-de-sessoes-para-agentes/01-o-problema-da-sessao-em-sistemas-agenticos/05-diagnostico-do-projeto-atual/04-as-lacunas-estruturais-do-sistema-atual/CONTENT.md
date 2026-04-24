# As lacunas estruturais do sistema atual

![capa](cover.png)

Os três conceitos anteriores fizeram um inventário do que existe: o MongoDB persiste mensagens entre invocações, o Haystack estrutura o loop interno de tool calling dentro de cada run, e a API Gateway entrega identidade validada e granularidade de turn pelo protocolo HTTP. O diagnóstico até aqui foi generoso com o sistema — reconheceu o valor real de cada camada. O que este conceito faz é completar o inventário pelo outro lado: o que está completamente ausente, não parcialmente entregue, não implicitamente presente — ausente.

A distinção importa porque "incompleto" e "ausente" pedem respostas diferentes. Um componente incompleto pode ser estendido. Um componente ausente precisa ser desenhado do zero, com todas as decisões que isso implica: o que guardar, onde guardar, em qual formato, com qual ciclo de vida. As lacunas que seguem pertencem à segunda categoria.

**A primeira lacuna é o `session_id` explícito como objeto gerenciado.** O que o sistema atual tem é uma chave de negócio — o `user_id` vindo do JWT, ou o `channel_id` do Slack — usada como índice no MongoDB. Essa chave não é um `session_id`. Ela não foi gerada para representar uma sessão; foi reutilizada para esse papel por conveniência. A consequência prática foi identificada no conceito anterior: dois usuários com o mesmo `channel_id` compartilham o mesmo histórico, e o mesmo usuário em dois canais diferentes tem dois históricos separados sem que isso corresponda necessariamente a duas sessões distintas do ponto de vista do agente.

Mas o problema vai além da confusão de cardinalidade. Um `session_id` genuíno carrega semântica: ele é gerado na criação da sessão, persistido com a sessão, passado em todos os turnos subsequentes, e permite que o sistema responda à pergunta "o que está acontecendo nesta sessão agora?" com um objeto concreto em vez de uma lista de mensagens. Sem ele, a sessão é inferida retroativamente pela chave usada para buscar o histórico — o que é equivalente a identificar uma pessoa pelo último lugar onde ela esteve, em vez de pelo seu nome.

```python
# O que o sistema atual tem: chave de negócio reutilizada como "session_id"
session_key = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
messages = db.conversations.find_one({"user_id": session_key})["messages"]

# O que deveria existir: session_id explícito com ciclo de vida gerenciado
session_id = event["body"]["session_id"]  # gerado pelo cliente ou pelo sistema na primeira chamada
session = db.sessions.find_one({"session_id": session_id})
# session contém: messages, agent_state, created_at, last_turn_at, status, user_id, metadata
```

A linha de código é trivialmente diferente. A estrutura que ela pressupõe é radicalmente diferente. Um documento de sessão real carrega não apenas as mensagens, mas o `status` (idle, running, suspended, expired), o `user_id` como metadado de dono — não como chave primária —, timestamps do ciclo de vida, e campos para o estado do agente que os conceitos seguintes vão detalhar. O `session_id` é a âncora que conecta todos esses dados num objeto coerente.

**A segunda lacuna é a ausência de estado do agente entre runs.** O estado que o Haystack mantém durante o `agent.run()` — a lista de mensagens em memória, o `State` acessível pelas ferramentas, o número de steps executados, as decisões intermediárias do LLM antes de chegar à resposta final — existe exclusivamente na memória do processo Lambda durante aquela invocação. Quando o Lambda retorna, esse estado some. O que sobrevive é apenas o que o código da aplicação explicitamente serializa e grava no MongoDB: as mensagens finais do turn.

O que isso impede concretamente: se o agente começa a executar um workflow de cinco passos no turn 3 — digamos, criar uma tarefa no ClickUp, buscar membros do projeto, atribuir a tarefa, adicionar uma descrição e criar um comentário de acompanhamento — e o usuário envia uma mensagem no turn 4 antes que o workflow do turn 3 tenha concluído, o sistema não tem como saber que um workflow estava em andamento. O MongoDB contém as mensagens do turn 3 até o ponto em que foram gravadas; não contém o estado interno da execução do agente. O turn 4 começa como se o turn 3 fosse apenas mais uma troca de mensagens.

```
Turn 3 — workflow em andamento no momento da invocação Lambda:

  agent.run():
    step 1: create_clickup_task ✓ → task_id = "task_999"
    step 2: fetch_project_members ✓ → ["alice", "bob"]
    step 3: assign_task ✓ → assigned to "alice"
    step 4: add_description ... [timeout ou erro de rede]

  Estado que o Lambda tem em memória ao encerrar:
    - task_id criado: "task_999"
    - passos 1-3 concluídos
    - passo 4 não concluído
    - passo 5 não iniciado

  Estado que o MongoDB recebe após o turn:
    - mensagens do turno até onde chegaram
    - sem task_id estruturado
    - sem registro de passos concluídos/pendentes
    - sem intenção ativa

Turn 4 — o que o agente sabe:
    - o texto das mensagens do turn 3
    - não sabe que a descrição não foi adicionada
    - não sabe que o passo 5 está pendente
    → resultado: o agente pode reiniciar o workflow do zero, duplicar ações, ou simplesmente não saber que havia algo inacabado
```

A solução para essa lacuna exige um campo estruturado no documento de sessão para o estado do agente — não as mensagens, mas o estado da execução: quais intenções estão ativas, quais ações foram concluídas, qual é o passo atual de um workflow multi-step. Isso é o que frameworks como Letta e o SDK de agentes da OpenAI armazenam como `state` separado das mensagens. O Haystack não fornece esse mecanismo; ele precisa ser construído na camada de orquestração que envolve o `agent.run()`.

**A terceira lacuna é a ausência de qualquer política de compactação de contexto.** O MongoDB armazena o histórico de mensagens fielmente, mas não toma nenhuma decisão sobre quais mensagens projetar na janela de contexto do LLM. O padrão atual — injetar o histórico completo em cada invocação — funciona até que não funciona mais. O Gemini 1.5 Pro tem uma janela de contexto de até 1 milhão de tokens, o que cria uma falsa sensação de segurança: "a conversa nunca vai ser longa o suficiente para estourar". Mas o problema não é só estourar — é o custo e a qualidade da inferência.

Uma conversa com 200 turns de um assistente de ClickUp/Slack contém inevitavelmente muitas mensagens que não são relevantes para o turn atual: confirmações de ações já concluídas, erros que foram corrigidos, contexto de projetos que não fazem parte da conversa presente. Injetar tudo isso no contexto aumenta o custo de tokens linearmente com o número de turns e, em modelos com janelas longas, pode degradar a qualidade da atenção — o fenômeno da "lost in the middle" onde o modelo atende menos às informações no meio da janela de contexto. Sem uma política de compactação, o sistema não tem escolha: injeta tudo ou trunca arbitrariamente.

As políticas que resolvem isso — sliding window (manter os N últimos turns completos), summarização (condensar turns antigos em resumo estruturado), relevance scoring (selecionar as K mensagens mais relevantes para o turn atual) — todas requerem que o sistema saiba o que é uma sessão, o que é um turn, e como recuperar o histórico estruturadamente. Elas não podem ser implementadas sobre uma lista plana de mensagens sem session_id e sem metadados de turn. A compactação é, portanto, dependente da solução das lacunas anteriores.

| Política de compactação | O que requer | Status no sistema atual |
|------------------------|--------------|------------------------|
| Sliding window (últimos N turns) | Turns numerados na sessão | Ausente — não há numeração de turns |
| Summarização de turns antigos | Session_id + campo para o resumo | Ausente — não há session object |
| Relevance scoring por embeddings | Turns como unidades indexáveis | Ausente — não há estrutura de turn |
| Token budget por turn | Contagem de tokens por mensagem | Ausente — não há metadados de tokens |

**A quarta lacuna é o suporte a sessões que excedem o timeout do Lambda.** A AWS impõe um limite absoluto de 15 minutos por invocação — qualquer execução que ultrapasse esse limite é encerrada forçosamente. Para o caso de uso atual do assistente Slack/ClickUp com tool calls típicos de segundos a poucos minutos, esse limite raramente é atingido. Mas o timeout do Lambda não é a única fronteira relevante.

O problema mais comum não é uma única invocação que dura mais de 15 minutos — é uma sessão que precisa ser retomada após um intervalo longo. Um usuário que inicia um workflow complexo às 14h, é interrompido, e volta às 17h para continuar está usando uma sessão que durou 3 horas — mas cada turn individual durou segundos. O Lambda não tem problema algum com isso. O que o Lambda não consegue fazer é manter qualquer estado entre esses turnos por conta própria. E se o estado da sessão não for persistido de forma estruturada, o agente que retoma às 17h não sabe que havia um workflow em andamento às 14h.

O cenário mais crítico é diferente: quando um único turn precisa executar operações longas — uma análise de dados, uma busca em múltiplos sistemas, uma operação que depende de um callback assíncrono. Nesses casos, o timeout de 15 minutos é um limite real, não teórico. E quando o Lambda é encerrado por timeout, o estado da execução é perdido sem que haja nenhum checkpoint gravado. O sistema atual não tem o conceito de checkpoint: não sabe como pausar a execução, gravar onde parou, e retomar de lá.

```
Cenário de timeout sem checkpoint:

  Turn N: usuário pede análise longa
    → Lambda começa execução
    → passo 1: busca dados (30s) ✓
    → passo 2: processa dataset (8min) ✓
    → passo 3: chama API externa... aguardando...
    → [15 min: Lambda é encerrado pela AWS]
    → Estado gravado no MongoDB: mensagens até o início do turn N
    → Estado perdido: passos 1 e 2 concluídos, passo 3 em andamento
    → Turn N+1: usuário pergunta "terminou?" — o agente não sabe nem que começou
```

Resolver essa lacuna é, tecnicamente, a mais complexa das quatro. Ela exige ou checkpoint-and-replay (gravar o estado após cada passo significativo para que uma nova invocação possa retomar), ou migrar para uma infraestrutura com estado nativo como Lambda Durable Functions ou Fargate — exatamente o que os capítulos 6, 7 e 8 do livro abordam.

O que as quatro lacunas têm em comum é que todas derivam de um único problema raiz: o sistema foi construído sobre o padrão de Lambda stateless com histórico externo, que os conceitos anteriores deste subcapítulo identificaram como uma posição válida no espectro — mas insuficiente para o que um agente real precisa. O MongoDB resolveu a amnésia de mensagens sem resolver a ausência de session object. O Haystack resolveu o loop interno de run sem resolver a persistência do estado entre runs. A API Gateway resolveu a identidade do usuário sem resolver a identidade da sessão. As quatro lacunas não são falhas independentes — são sintomas da mesma decisão arquitetural de nunca ter construído um session object com ciclo de vida gerenciado como componente de primeira classe do sistema.

A implicação para os próximos capítulos é direta: o capítulo 2 (Substrato Persistente e Janela de Contexto) vai projetar o session object que está ausente hoje — com `session_id`, estado do agente, e a separação entre o que é persistido e o que é projetado para a janela de contexto a cada inferência. Os capítulos subsequentes vão construir as políticas de compactação, as state machines de ciclo de vida, e os padrões de infraestrutura para sessões longas. O diagnóstico deste subcapítulo não é uma lista de tarefas — é o mapa que dá coordenadas concretas para cada uma dessas decisões de design.

## Fontes utilizadas

- [Building an Agent Architecture: How Sessions, State, Events, Context, and Runner Work Together — Medium](https://medium.com/@aktooall/building-an-agent-architecture-how-sessions-state-events-context-and-runner-work-together-d8dbdb64d52b)
- [Overview — OpenAI Agents SDK: Sessions](https://openai.github.io/openai-agents-python/sessions/)
- [Use isolated sessions for agents — Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-sessions.html)
- [Session Management in AWS Lambda: Guide — AWS for Engineers](https://awsforengineers.com/blog/session-management-in-aws-lambda-guide/)
- [Context compression — Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/context/compaction/)
- [Compaction (summarization) — Letta Docs](https://docs.letta.com/guides/core-concepts/messages/compaction/)
- [Compaction vs Summarization: Agent Context Management Compared — Morph](https://www.morphllm.com/compaction-vs-summarization)
- [7 State Persistence Strategies for Long-Running AI Agents in 2026 — Indium Tech](https://www.indium.tech/blog/7-state-persistence-strategies-ai-agents-2026/)
- [Configure Lambda function timeout — AWS Lambda Docs](https://docs.aws.amazon.com/lambda/latest/dg/configuration-timeout.html)
- [When 15 Minutes Isn't Enough: Overcoming Lambda Timeout Limits — DEV Community](https://dev.to/heppoko/when-15-minutes-isnt-enough-overcoming-lambda-timeout-limits-2fn3)
- [Agent Lifecycle in Agentic AI: Architecture & Implementation — Azilen](https://www.azilen.com/learning/agent-lifecycle/)

---

**Próximo conceito** → [O checklist operacional de diagnóstico](../05-o-checklist-operacional-de-diagnostico/CONTENT.md)
