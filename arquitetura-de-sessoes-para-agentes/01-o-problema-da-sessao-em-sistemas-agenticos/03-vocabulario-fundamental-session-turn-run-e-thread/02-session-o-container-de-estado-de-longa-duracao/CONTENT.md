# Session: o container de estado de longa duração

![capa](cover.png)

O conceito anterior estabeleceu por que precisamos de nomes precisos antes de escrever qualquer linha de implementação — e terminou com uma distinção central: quando o bug é diagnosticado como "o agente está perdendo contexto", a pergunta que transforma o diagnóstico vago num plano de ação é "qual contexto, em qual camada?". A session é exatamente a resposta para a primeira metade dessa pergunta. Ela nomeia a camada de estado que persiste entre invocações, independente de qualquer chamada ao modelo — e compreender o que ela contém (e o que ela deliberadamente não contém) é o passo que separa arquiteturas que apenas parecem stateful daquelas que realmente são.

A confusão mais comum é tratar session e histórico de chat como sinônimos. Esse equívoco é compreensível porque, em sistemas simples, os dois são quase equivalentes: você tem uma lista de mensagens no MongoDB e a passa de volta a cada chamada. Mas a equivalência é superficial e quebra assim que o sistema precisa de mais do que mensagens. Considere o caso: o agente está no meio de uma tarefa de múltiplos passos — ele criou um ticket no ClickUp, está esperando aprovação e precisa retomar de onde parou quando o usuário responder no dia seguinte. Histórico de chat guarda as mensagens trocadas; mas onde fica o status atual da tarefa? Onde fica o `ticket_id` que precisa ser rastreado? Onde fica a intenção ativa — o fato de que o agente ainda está "no meio de algo"? Nenhum desses dados é uma mensagem. Uma session é o container que os carrega.

A definição operacional de session, no vocabulário deste livro: **uma session é o objeto persistente que representa o estado completo de uma conversa ou workflow agêntico em curso, desde o seu início até o encerramento explícito ou por timeout**. "Completo" aqui é preciso — não inclui a janela de contexto que o modelo vai receber em cada inferência (essa é efêmera, montada na hora, e descartada depois), mas inclui tudo que precisa sobreviver entre invocações.

Na prática, os campos de uma session bem projetada agrupam-se em três categorias:

| Categoria | Exemplos de campos | Durabilidade |
|---|---|---|
| **Metadados de identidade** | `session_id`, `user_id`, `app_name`, `created_at`, `updated_at`, `status` | Toda a vida da session |
| **Histórico de eventos** | Lista de mensagens, resultados de tool calls, erros, observações | Toda a vida da session, com possível compactação |
| **Estado do agente** | Intenções ativas, variáveis de scratchpad, status de tarefas em andamento, último ponto de checkpoint | Toda a vida da session, atualizado a cada turn |

O estado do agente — a terceira categoria — é o que mais distingue uma session de simples histórico de chat. O Google ADK usa o termo `session.state` para esse scratchpad: um dicionário de variáveis relevantes apenas para a conversa atual, que o agente lê e atualiza conforme avança. Não é um campo de texto livre; é estado estruturado que tem campos com semântica conhecida — `current_task_id`, `pending_approval`, `collected_fields`, o que for relevante para o domínio. O OpenAI Agents SDK chama esse campo de forma diferente mas a mecânica é idêntica: o runner salva os itens novos ao final de cada turno e os recupera no início do próximo, montando um estado contínuo que o agente percebe como uma única sessão de trabalho.

A separação entre o que a session guarda e o que a janela de contexto contém não é cosmética — é a distinção arquitetural mais importante do livro inteiro. A **janela de contexto** é efêmera por design: ela é construída antes de cada chamada ao modelo, inclui um subconjunto dos eventos da session (nem sempre todos — dependendo do token budget disponível), e é descartada após a inferência terminar. Ela é uma projeção da session para aquele momento específico, não a session em si. Isso significa que a session pode crescer indefinidamente (com política de compactação se necessário) sem que o modelo precise consumir tudo de uma vez; a projeção seleciona o que é relevante para a chamada em questão. O capítulo 2 deste livro aprofunda exatamente esse padrão de substrato persistente e janela de contexto como projeção — mas para usar o vocabulário corretamente daqui em diante, o que importa fixar agora é que session ≠ contexto que vai para o modelo.

```
INVOCAÇÃO DO AGENTE (Lambda / container)
│
├── Carrega SESSION do banco (MongoDB, DynamoDB, etc.)
│   ├── session_id, user_id, status
│   ├── events: [msg1, tc1, res1, msg2, ...]   ← tudo que aconteceu
│   └── state: { current_task: "...", ... }    ← scratchpad do agente
│
├── MONTA JANELA DE CONTEXTO  ←─── operação efêmera
│   ├── system prompt
│   ├── seleção de events (pode ser subconjunto)
│   └── mensagem nova do usuário
│
├── CHAMA O MODELO com a janela montada
│
├── Processa resposta / tool calls
│
└── Persiste SESSION atualizada no banco
    ├── Appenda novos events
    └── Atualiza state se necessário
```

Esse fluxo explica por que a session precisa ser explicitamente carregada e salva — não é algo que o Lambda ou qualquer runtime stateless mantém automaticamente. Cada invocação começa com estado zerado na memória do processo; a continuidade vem do carregamento da session do banco no início e da sua atualização no fim. Isso também responde uma dúvida prática que o leitor provavelmente já se fez: se o processo morre no meio da execução, o que acontece? A resposta depende de quando a session foi salva pela última vez. Sessions bem projetadas persistem eventos incrementalmente, não apenas ao final — isso transforma o histórico em um log de eventos auditável e reduz a janela de perda em caso de falha.

O `session_id` merece atenção especial. Ele é o ponto de acoplamento entre o contrato externo da API (o que o chamador fornece para identificar uma conversa) e o estado interno (o que o sistema carrega e atualiza). A ausência de um `session_id` explícito — ou sua fusão com o `user_id` — é um dos bugs de arquitetura mais comuns em sistemas que cresceram organicamente. Um mesmo usuário pode ter múltiplas sessões ativas ao mesmo tempo (em diferentes devices, em contextos diferentes), e tratar `user_id` como `session_id` impede isso. Pior: alguns sistemas geram um `session_id` por invocação HTTP, o que significa que cada request é uma sessão nova — um anti-padrão que destrói qualquer continuidade agêntica, pois o sistema perde toda a memória a cada turno.

O ciclo de vida de uma session começa com a sua criação — geralmente quando o primeiro turno de uma nova conversa chega e não há `session_id` no payload. A session persiste ativa enquanto houver turnos chegando dentro de um intervalo de tempo razoável. Ela pode ser suspensa (pausada explicitamente), retomada (reativada com o mesmo `session_id`), ou expirada (encerrada por TTL após inatividade). O capítulo 3 deste livro vai modelar esses estados como uma state machine completa com guards e transições; o que importa fixar aqui é que session tem um ciclo de vida, não é apenas um registro no banco que fica lá para sempre.

Uma observação sobre a terminologia em frameworks existentes: o LangGraph usa "thread" onde este livro usa "session"; o que a OpenAI Assistants API chama de "thread" é mais próximo da definição de session aqui — um container persistente de mensagens com um ID que sobrevive entre runs. Essa polissemia é exatamente o problema que o conceito anterior descreveu. No vocabulário deste livro, session e thread têm significados distintos — a diferença vai ser estabelecida com precisão nos conceitos 5 e 6 deste subcapítulo. Por ora, o que importa é internalizar que, independente de como cada framework chama, o padrão estrutural é o mesmo: um objeto com ID, com histórico de eventos, com estado do agente, que sobrevive entre invocações e que é carregado no início de cada turno.

## Fontes utilizadas

- [Sessions — OpenAI Agents SDK](https://openai.github.io/openai-agents-python/sessions/)
- [Introduction to Conversational Context: Session, State, and Memory — Google ADK](https://adk.dev/sessions/)
- [Building an Agent Architecture: How Sessions, State, Events, Context, and Runner Work Together — Medium](https://medium.com/@aktooall/building-an-agent-architecture-how-sessions-state-events-context-and-runner-work-together-d8dbdb64d52b)
- [Agent Session State — Agno](https://docs.agno.com/basics/state/agent/overview)
- [What Is AI Agent Memory? — IBM](https://www.ibm.com/think/topics/ai-agent-memory)
- [Stateful vs. stateless agents: Why stateful architecture is essential for agentic AI — ZBrain](https://zbrain.ai/stateful-architecture-for-agentic-ai-systems/)

---

**Próximo conceito** → [Turn: o ciclo usuário→agente](../03-turn-o-ciclo-usuario-agente/CONTENT.md)
