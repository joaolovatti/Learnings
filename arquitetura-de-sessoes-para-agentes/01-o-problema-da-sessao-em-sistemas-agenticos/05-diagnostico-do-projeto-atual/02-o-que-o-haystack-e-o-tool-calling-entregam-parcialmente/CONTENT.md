# O que o Haystack e o tool calling entregam parcialmente

![capa](cover.png)

O MongoDB resolve a amnésia entre invocações — mas a conversa que o agente tem com as ferramentas durante uma invocação, o ciclo interno de raciocínio-ação-observação que acontece enquanto o Lambda está rodando, esse tem uma estrutura própria que o Haystack organiza, mesmo que de forma incompleta. Entender o que essa estrutura entrega — e onde ela para — é o segundo ponto do diagnóstico.

O ponto de partida é o componente `Agent` do Haystack. Quando o agente recebe uma mensagem do usuário e começa a processar, o Haystack instancia um loop interno. Esse loop funciona assim: o LLM recebe a lista de mensagens até então e a lista de ferramentas disponíveis (seus schemas JSON); o LLM responde com uma decisão — ou uma resposta final, ou um ou mais `ToolCall`; se a resposta for um `ToolCall`, o `ToolInvoker` executa a ferramenta correspondente e empacota o resultado como uma `ChatMessage` com role `tool`; essa mensagem de resultado é adicionada à lista de mensagens em memória e o loop volta para o LLM; quando o LLM decide que tem informação suficiente para responder ao usuário, emite a resposta final e o loop encerra.

```
Loop interno do Agent (Haystack) durante um run:

  [messages: user + history]
         ↓
    ChatGenerator (LLM)
         ↓
  ┌─ resposta final? → retorna messages completo
  │
  └─ ToolCall? →
         ↓
     ToolInvoker
         ↓
   ChatMessage(role=tool, content=resultado)
         ↓
   adiciona à lista messages em memória
         ↓
    ChatGenerator (LLM)  ← loop até exit_condition
```

O que o Haystack estrutura aqui é exatamente o que o vocabulário do subcapítulo 3 chamou de **run**: a execução completa do loop agêntico dentro de um único turn, incluindo múltiplos ciclos de raciocínio-ação-observação. Isso não é trivial. Um sistema ingênuo teria que implementar esse loop manualmente — controlar quando o LLM está pedindo uma ferramenta, despachar a chamada, coletar o resultado, reinjetar no contexto, repetir. O Haystack faz tudo isso com `max_agent_steps`, `exit_conditions` configuráveis e um `state_schema` opcional para dados adicionais que as ferramentas podem ler e escrever durante a execução.

Os tipos de dados que o Haystack define para o ciclo de tool calling também merecem atenção. A `ChatMessage` não é apenas uma string com um role — ela carrega um campo `tool_calls` (lista de objetos `ToolCall`) quando o LLM decide invocar ferramentas, e um campo `tool_call_results` (lista de objetos `ToolCallResult`) quando o resultado volta do `ToolInvoker`. Cada `ToolCall` contém o nome da ferramenta, os argumentos serializados como JSON, e um `tool_call_id` único que conecta a chamada ao resultado. Essa estrutura tipada é significativamente mais rica do que um texto plano — ela representa um **evento** com identidade, intenção e resultado.

```python
# O que uma ChatMessage de tool call parece internamente
ChatMessage(
    role=<ChatRole.ASSISTANT>,
    content=None,
    tool_calls=[
        ToolCall(
            tool_name="create_clickup_task",
            arguments={"title": "Revisar PR #42", "project_id": "abc123"},
            id="call_xyz789"
        )
    ]
)

# E o resultado correspondente
ChatMessage(
    role=<ChatRole.TOOL>,
    content=None,
    tool_call_results=[
        ToolCallResult(
            result='{"task_id": "task_999", "url": "https://..."}',
            origin=ToolCall(tool_name="create_clickup_task", id="call_xyz789"),
            error=False
        )
    ]
)
```

O `tool_call_id` que conecta `ToolCall` a `ToolCallResult` é particularmente importante: sem ele, num sistema com múltiplos tool calls em paralelo, seria impossível saber qual resultado pertence a qual chamada. O Haystack gerencia isso automaticamente dentro do loop. Esse é o valor concreto que o framework entrega: organização estruturada de um run, com tipagem explícita dos eventos de tool calling.

A limitação começa exatamente onde o run termina. Ao final do `agent.run()`, o Haystack retorna o atributo `messages` — a lista completa de mensagens que foram trocadas durante aquele run, incluindo os `ToolCall` e `ToolCallResult`. Mas essa lista existe **na memória do processo Lambda** durante a execução e é retornada como output do componente. O que acontece com ela depois depende inteiramente de quem chama o agente. O Haystack não persiste nada automaticamente; não sabe o que é uma sessão; não tem o conceito de session_id. Quando o Lambda retorna a resposta para a API Gateway e o processo encerra, todo o estado interno do loop desaparece.

O que o sistema atual faz com essa lista retornada é exatamente o que o conceito anterior descreveu: serializa as mensagens e as grava no MongoDB como histórico de chat. Mas observe o que se perde nessa transição: as mensagens gravadas são as `ChatMessage` serializadas — e dependendo de como a serialização está implementada, os campos `tool_calls` e `tool_call_results` podem ser preservados como JSON ou podem ser achatados para texto plano. Se forem achatados, a riqueza estrutural que o Haystack construiu durante o run — o `tool_call_id`, a tipagem do resultado, o flag de erro — se perde na persistência. Na próxima invocação, quando o histórico é carregado do MongoDB e injetado no contexto, o modelo recebe uma versão empobrecida do que aconteceu.

| O que o Haystack estrutura durante o run | O que sobrevive à persistência no MongoDB |
|------------------------------------------|-------------------------------------------|
| `ToolCall` com nome, args e `tool_call_id` | Depende da serialização — pode ser texto plano |
| `ToolCallResult` com resultado tipado e flag de erro | Idem |
| Sequência ordenada de raciocínio→ação→observação | Preservada como lista de mensagens |
| `state_schema` com dados adicionais das ferramentas | Geralmente **não** persiste — in-memory only |
| `max_agent_steps` e controle do loop | Não persiste — existe apenas durante o run |

O `state_schema` merece atenção específica. O Haystack permite que as ferramentas leiam e escrevam em um objeto `State` compartilhado durante a execução do agente — útil para passar documentos recuperados, contexto acumulado, ou qualquer dado que não cabe numa mensagem de chat. Mas esse `State` é instanciado no início do `agent.run()` e descartado ao final. Não há mecanismo no Haystack para serializar o `State` e armazená-lo entre invocações. Se uma ferramenta escreveu documentos relevantes no `State` durante o run, esses documentos existem durante aquele Lambda — e somem quando o Lambda termina.

O segundo ponto de incompletude é a ausência de `session_id` como conceito nativo no Haystack. O framework não tem noção de sessão: cada chamada a `agent.run()` é independente. É o código da aplicação que decide o que passar como `chat_history` no início do run — e é o código da aplicação que decide como identificar qual histórico buscar no MongoDB. Na arquitetura atual, esse identificador pode ser o `user_id` do Slack, o `channel_id`, ou alguma outra chave de negócio. O Haystack não sabe qual é, não a rastreia, e não garante consistência. A identidade da sessão é implícita no dado passado para o agente, não explícita como objeto gerenciado.

```
O que existe no sistema atual (implícito):

  Slack channel ID ─→ MongoDB query ─→ messages[] ─→ agent.run(chat_history=messages)
                                                                    ↓
                                                           run acontece, loop interno OK
                                                                    ↓
                                                     agent retorna messages completo
                                                                    ↓
                                            código grava messages de volta no MongoDB
                                            (com a mesma Slack channel ID como chave)

  Não existe: session object, session_id gerenciado, ciclo de vida da sessão
```

Há um terceiro ponto de entrega parcial que é sutil: o Haystack registra as invocações do `ChatGenerator` e do `ToolInvoker` internamente para fins de tracing (visível via OpenTelemetry se configurado). Isso cria um rastro auditável dos eventos que aconteceram dentro de um run — mas o rastro existe no nível da observabilidade, não no nível da sessão. Ele permite depurar o que aconteceu num run específico, mas não responde à pergunta "o que o agente estava tentando fazer ao longo dos últimos 5 turns desta sessão". São níveis de abstração diferentes.

O resultado do diagnóstico neste ponto é preciso: o Haystack e o tool calling entregam a estrutura do run — o loop interno, a tipagem dos eventos, o encadeamento de tool calls dentro de uma única invocação — mas não entregam nada além da fronteira do run. Não há session_id nativo, não há persistência do State entre runs, não há gestão do ciclo de vida da sessão, e a riqueza estrutural dos ToolCall/ToolCallResult pode ou não sobreviver à serialização para o MongoDB. O framework faz bem o que faz; a lacuna está no que ele deliberadamente não faz — e que precisa ser construído na camada acima.

## Fontes utilizadas

- [Agent — Haystack Documentation](https://docs.haystack.deepset.ai/docs/agent)
- [Build a Tool-Calling Agent — Haystack Tutorial](https://haystack.deepset.ai/tutorials/43_building_a_tool_calling_agent)
- [Tool — Haystack Documentation](https://docs.haystack.deepset.ai/docs/tool)
- [ToolInvoker — Haystack Documentation](https://docs.haystack.deepset.ai/docs/toolinvoker)
- [Define & Run Tools — Haystack Cookbook](https://haystack.deepset.ai/cookbook/tools_support)
- [Building a Chat Agent with Function Calling — Haystack Tutorial](https://haystack.deepset.ai/tutorials/40_building_chat_application_with_function_calling)
- [Runs — OpenAI API Reference](https://platform.openai.com/docs/api-reference/runs)

---

**Próximo conceito** → [O que a API Gateway contribui implicitamente](../03-o-que-a-api-gateway-contribui-implicitamente/CONTENT.md)
