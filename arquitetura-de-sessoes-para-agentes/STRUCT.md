# Estrutura do Livro

> Mapa rapido da organizacao do livro: capitulos, subcapitulos e conceitos. Mantido automaticamente pela skill `estudo-atualizar-struct` — nao edite a mao.

```
arquitetura-de-sessoes-para-agentes/ — Arquitetura de Sessões para Agentes
├── 01-o-problema-da-sessao-em-sistemas-agenticos/ — Por que agentes stateless falham; vocabulário fundamental de session, turn, run e thread
│   ├── 01-o-agente-sem-sessao-nao-e-um-agente/ — por que o problema da sessão é central em sistemas agênticos e o que distingue um chatbot glorificado de um agente real
│   │   ├── 01-o-llm-e-o-modelo-stateless-por-design/ — por que cada chamada de inferência parte do zero e o que "stateless" significa no nível da API do modelo
│   │   ├── 02-a-definicao-operacional-de-agente/ — o que diferencia tecnicamente um agente de um chatbot: persistência de intenções, observação contínua e coerência multi-turno
│   │   ├── 03-o-colapso-stateless-de-agente-a-chatbot-glorificado/ — o mecanismo pelo qual a ausência de estado persistido faz o sistema perder intenções ativas e tomar decisões contraditórias
│   │   ├── 04-por-que-a-falha-nao-e-obvia-em-desenvolvimento/ — como o ambiente de teste mascara o problema (o dev fornece contexto manualmente) e por que produção expõe a falha imediatamente
│   │   └── 05-a-sessao-como-substrato-de-continuidade/ — o que a sessão realmente é: não histórico de chat, mas o substrato que mantém intenções ativas, ações rastreadas e coerência entre turnos
│   ├── 02-anatomia-de-uma-falha-stateless/ — exemplos concretos de perda de contexto entre tool calls, perguntas repetidas e decisões contraditórias em turnos consecutivos
│   │   ├── 01-perda-de-contexto-entre-tool-calls/ — o que acontece quando o resultado de um tool call não persiste e a próxima invocação começa sem acesso a esse resultado
│   │   ├── 02-o-mecanismo-da-pergunta-repetida/ — por que o agente repergunta informações já fornecidas pelo usuário em turnos anteriores e como isso destrói a experiência em workflows multi-step
│   │   ├── 03-decisoes-contraditorias-em-turnos-consecutivos/ — como a ausência de memória entre turns faz o agente criar, em N+1, algo que já criou em N
│   │   ├── 04-a-falha-silenciosa-do-lambda-stateless/ — como a natureza stateless do Lambda amplifica os três padrões anteriores, já que cada invocação começa com estado zerado mesmo quando o desenvolvedor acredita estar passando histórico suficiente
│   │   └── 05-reconhecimento-de-padrao-vs-diagnostico-vago/ — a distinção entre "o agente está se comportando de forma estranha" e ter vocabulário técnico preciso para nomear cada tipo de falha
│   ├── 03-vocabulario-fundamental-session-turn-run-e-thread/ — definições precisas dos quatro conceitos e mapeamento direto para o código Lambda/Haystack existente do leitor
│   │   ├── 01-por-que-nomear-antes-de-implementar/ — a distinção entre ter um sintoma e ter um vocabulário técnico preciso; por que a imprecisão de linguagem perpetua bugs de arquitetura
│   │   ├── 02-session-o-container-de-estado-de-longa-duracao/ — o que a session contém (histórico, metadados, estado do agente), o que ela não contém (janela de contexto efêmera) e o que a torna diferente de "histórico de chat"
│   │   ├── 03-turn-o-ciclo-usuario-agente/ — a unidade de interação vista do lado externo; como um turn se delimita do ponto de vista de quem chama a API e como mapeia para uma invocação HTTP no sistema do leitor
│   │   ├── 04-run-a-execucao-interna-do-loop-agentico/ — o que acontece dentro de um turn quando há tool calls encadeados; por que um único turn pode conter múltiplos ciclos de raciocínio-ação-observação
│   │   ├── 05-thread-sequencia-linear-de-turns-numa-sessao/ — o que distingue thread de session; por que a distinção importa em sistemas que suportam ramificações ou contextos paralelos dentro de uma mesma sessão
│   │   ├── 06-session-vs-thread-a-distincao-que-mais-confunde/ — os dois termos que frameworks distintos usam de forma intercambiável; como fixar a diferença com precisão e quando a confusão leva a bugs reais
│   │   └── 07-mapeamento-para-o-codigo-existente/ — como session, turn, run e thread se projetam sobre a stack Lambda + MongoDB + Haystack do leitor: onde cada conceito existe, onde está implícito e onde está ausente
│   ├── 04-o-espectro-stateless-stateful/ — posicionamento de diferentes arquiteturas nesse espectro, do Lambda stateless puro até agentes com memória episódica completa
│   │   ├── 01-o-polo-stateless-puro/ — Lambda sem armazenamento externo: cada invocação é independente, o que isso garante e o que impossibilita, com os casos de uso legítimos onde essa posição é suficiente
│   │   ├── 02-por-que-passar-historico-nao-e-ter-sessao/ — a diferença semântica entre injetar histórico de chat a cada chamada e manter um estado estruturado persistente; por que o padrão Lambda + MongoDB é stateless com histórico externo, não stateful
│   │   ├── 03-stateful-com-session-explicita/ — o que muda quando existe um session object persistido e carregado a cada turn: quais campos ele carrega e por que isso é qualitativamente diferente da posição anterior
│   │   ├── 04-agentes-com-memoria-episodica-completa/ — arquiteturas como Letta/MemGPT que gerenciam múltiplos tipos de memória (episódica, semântica, procedural); quando esse nível de complexidade é justificado e quando é overengineering
│   │   └── 05-o-criterio-de-posicionamento-no-espectro/ — como identificar objetivamente em qual posição do espectro um sistema está, e qual a próxima posição racional a atingir sem pular níveis
│   └── 05-diagnostico-do-projeto-atual/ — como identificar os pontos de perda de estado no sistema Lambda + MongoDB existente e o que já funciona versus o que ainda falta
│       ├── 01-o-que-o-mongodb-como-historico-de-chat-ja-resolve/ — o que a camada de persistência atual entrega e onde ela para: persistência de mensagens entre invocações, mas sem session object estruturado
│       ├── 02-o-que-o-haystack-e-o-tool-calling-entregam-parcialmente/ — como o framework cria estrutura implícita de runs sem session_id explícito rastreado entre turns
│       ├── 03-o-que-a-api-gateway-contribui-implicitamente/ — como o contorno HTTP da API Gateway cria fronteiras de sessão implícitas, e por que isso não é suficiente
│       ├── 04-as-lacunas-estruturais-do-sistema-atual/ — o que está completamente ausente: session_id explícito persistido, estado do agente entre runs, compactação de contexto, suporte a sessões além do timeout do Lambda
│       ├── 05-o-checklist-operacional-de-diagnostico/ — o conjunto de perguntas que o leitor pode aplicar a qualquer sistema agêntico para posicioná-lo no espectro e identificar cada categoria de lacuna com precisão
│       └── 06-o-diagnostico-como-documento-de-decisao/ — como transformar o inventário (o que funciona / incompleto / ausente) num mapa de decisões que alimenta o design do capítulo 2, sem transformá-lo numa lista de tarefas
├── 02-substrato-persistente-e-janela-de-contexto/ — A separação central entre estado persistido e projeção efêmera para cada inferência; o padrão de context assembly
├── 03-state-machines-para-o-ciclo-de-vida-de-uma-sessao/ — Modelagem de estados (idle, running, waiting_tool, compacting, suspended, expired), transições e guards
├── 04-esquemas-de-persistencia-de-estado/ — Comparativo MongoDB vs DynamoDB vs S3; design do documento de sessão; serialização de ChatMessage e ToolCall
├── 05-gerenciamento-de-contexto-e-compactacao/ — Token budget; políticas de compactação (summarização, sliding window, relevance scoring)
├── 06-os-limites-do-lambda-stateless/ — Hard limits de timeout e memória; o que falha primeiro num agente real; padrões de workaround
├── 07-lambda-durable-functions-e-step-functions/ — Checkpoint-and-replay; orquestração multi-step; quando Lambda Durable Functions resolve e quando não
├── 08-sessoes-de-longa-duracao-com-fargate-ecs/ — Agent loop como processo contínuo; containerização; comunicação entre API Gateway e Fargate
├── 09-websocket-api-gateway-e-steering-em-tempo-real/ — Arquitetura WebSocket na AWS; streaming de tokens; o padrão de steering (interromper/redirecionar mid-execution)
├── 10-sessao-como-substrato-do-loop-agentico/ — Como a sessão alimenta o ReAct loop; gravação de tool call events; coerência multi-turn sem explodir o token budget
├── 11-multi-tenancy-e-isolamento-de-sessoes/ — Isolamento por usuário/organização; TTL e expiração; branch e retomada; o modelo Pi.dev como referência de UX
└── 12-observabilidade-e-debug-de-sessoes-agenticas/ — Tracing com OpenTelemetry; métricas de saúde; replay de runs; circuit breakers para loops infinitos
```
