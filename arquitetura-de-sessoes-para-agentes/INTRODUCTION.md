# Arquitetura de Sessões para Agentes

![capa](cover.png)

## Sobre este livro

Um agente de IA que esquece o que fez três turnos atrás não é um agente — é um chatbot com ambição. O problema central de sistemas agênticos em produção não é o modelo de linguagem nem o tool calling: é a sessão. Como representar, persistir, projetar e evoluir o estado de uma conversa que pode durar minutos, horas ou retomar dias depois, enquanto o agente executa ações no ambiente?

Este livro parte de um cenário concreto — uma API Gateway + Lambda com Gemini que já faz tool calling — e traz ao leitor o vocabulário, os padrões e as decisões de implementação para transformá-la numa plataforma agêntica com sessões reais: estado persistido entre chamadas, contexto montado dinamicamente para cada inferência, rastreabilidade de ações executadas e suporte a sessões longas que excedem os limites do Lambda stateless.

## Estrutura

Os grandes blocos são: (1) fundamentos de sessão agêntica — o que é uma sessão, a distinção entre substrato persistente e janela de contexto como projeção, state machines para representar o ciclo de vida de uma sessão; (2) persistência e reconstrução de estado — padrões de armazenamento (MongoDB, DynamoDB, S3), serialização de contexto, compactação e política de esquecimento; (3) infraestrutura AWS para sessões longas — limites do Lambda stateless, Lambda Durable Functions, Fargate/ECS como runtime de agente, WebSocket API Gateway para streaming e steering em tempo real; (4) integração com o loop agêntico — como a sessão alimenta o ReAct loop, como eventos de tool call são gravados na sessão, como múltiplos turnos mantêm coerência sem explodir o token budget; (5) sessões como produto — multi-tenancy, isolamento por usuário, expiração, branch e retomada de sessões, o modelo de sessão do Pi.dev como referência de UX.

## Objetivo

Ao terminar, o leitor será capaz de projetar e implementar a camada de sessão de um sistema agêntico a partir do zero, tomar decisões fundamentadas sobre quando Lambda é suficiente e quando migrar para Fargate, implementar o padrão substrato/projeção para gerenciar contexto sem desperdiçar tokens, e conectar essa camada de sessão ao loop de tool calling que ele já tem — evoluindo o projeto existente passo a passo em vez de reescrevê-lo.

## Sobre o leitor

O leitor é um engenheiro de software com atuação profissional em sistemas de IA, que já construiu e opera uma API Gateway na AWS integrada a um Lambda com modelo Gemini via Vertex AI. Ele tem tool calling funcional com Slack, ClickUp e MCP usando o framework Haystack, histórico de conversas em MongoDB e observabilidade com OpenTelemetry. Tem experiência prévia com multi-agent usando LangGraph e a API da OpenAI — ou seja, não é um iniciante em agentes, mas sua experiência com multi-agent veio de frameworks que abstraem o gerenciamento de estado, e ele nunca implementou a camada de sessão por baixo.

O objetivo declarado é transformar seu sistema atual em algo próximo ao Pi.dev: um agente com acesso a skills que consegue interagir com o ambiente numa sessão persistente, via API Gateway, com o usuário podendo intervir em tempo real. Para isso, a lacuna principal não é o modelo nem as ferramentas — é entender como modelar a sessão, persistir o estado entre invocações stateless do Lambda, e decidir quando essa arquitetura atinge seu limite e precisa evoluir para algo com estado nativo.

O leitor traz como ativo relevante o MongoDB já em uso para histórico de chat, a familiaridade com Haystack e a experiência com a AWS — o livro foi calibrado para alavancar esses pontos de partida em vez de partir do zero.

## Capítulos

1. [O Problema da Sessão em Sistemas Agênticos](01-o-problema-da-sessao-em-sistemas-agenticos/CONTENT.md) — Por que agentes stateless falham; vocabulário fundamental de session, turn, run e thread
2. [Substrato Persistente e Janela de Contexto](02-substrato-persistente-e-janela-de-contexto/CONTENT.md) — A separação central entre estado persistido e projeção efêmera para cada inferência; o padrão de context assembly
3. [State Machines para o Ciclo de Vida de uma Sessão](03-state-machines-para-o-ciclo-de-vida-de-uma-sessao/CONTENT.md) — Modelagem de estados (idle, running, waiting_tool, compacting, suspended, expired), transições e guards
4. [Esquemas de Persistência de Estado](04-esquemas-de-persistencia-de-estado/CONTENT.md) — Comparativo MongoDB vs DynamoDB vs S3; design do documento de sessão; serialização de ChatMessage e ToolCall
5. [Gerenciamento de Contexto e Compactação](05-gerenciamento-de-contexto-e-compactacao/CONTENT.md) — Token budget; políticas de compactação (summarização, sliding window, relevance scoring)
6. [Os Limites do Lambda Stateless](06-os-limites-do-lambda-stateless/CONTENT.md) — Hard limits de timeout e memória; o que falha primeiro num agente real; padrões de workaround
7. [Lambda Durable Functions e Step Functions](07-lambda-durable-functions-e-step-functions/CONTENT.md) — Checkpoint-and-replay; orquestração multi-step; quando Lambda Durable Functions resolve e quando não
8. [Sessões de Longa Duração com Fargate/ECS](08-sessoes-de-longa-duracao-com-fargate-ecs/CONTENT.md) — Agent loop como processo contínuo; containerização; comunicação entre API Gateway e Fargate
9. [WebSocket API Gateway e Steering em Tempo Real](09-websocket-api-gateway-e-steering-em-tempo-real/CONTENT.md) — Arquitetura WebSocket na AWS; streaming de tokens; o padrão de steering (interromper/redirecionar mid-execution)
10. [Sessão como Substrato do Loop Agêntico](10-sessao-como-substrato-do-loop-agentico/CONTENT.md) — Como a sessão alimenta o ReAct loop; gravação de tool call events; coerência multi-turn sem explodir o token budget
11. [Multi-Tenancy e Isolamento de Sessões](11-multi-tenancy-e-isolamento-de-sessoes/CONTENT.md) — Isolamento por usuário/organização; TTL e expiração; branch e retomada; o modelo Pi.dev como referência de UX
12. [Observabilidade e Debug de Sessões Agênticas](12-observabilidade-e-debug-de-sessoes-agenticas/CONTENT.md) — Tracing com OpenTelemetry; métricas de saúde; replay de runs; circuit breakers para loops infinitos

## Fontes utilizadas

- [Building an Agent Architecture: How Sessions, State, Events, Context, and Runner Work Together](https://medium.com/@aktooall/building-an-agent-architecture-how-sessions-state-events-context-and-runner-work-together-d8dbdb64d52b)
- [CaveAgent: Transforming LLMs into Stateful Runtime Operators](https://arxiv.org/html/2601.01569v1)
- [Dynamic Context Assembly and Projection Patterns for LLM Agent Runtimes](https://zylos.ai/research/2026-03-17-dynamic-context-assembly-projection-llm-agent-runtimes)
- [Stateful Agents: The Missing Link in LLM Intelligence — Letta](https://www.letta.com/blog/stateful-agents)
- [Effectively building AI agents on AWS Serverless — AWS Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
- [AWS Introduces Durable Functions: Stateful Logic Directly in Lambda Code — InfoQ](https://www.infoq.com/news/2025/12/aws-lambda-durable-functions/)
- [Lambda, Fargate, Bedrock Agent — Which serverless option to choose for your Agentic pattern?](https://medium.com/@loic.labeye/lambda-fargate-agentcore-which-severless-option-to-choose-for-your-agentic-pattern-aaf68cb99700)
- [Architecting for agentic AI development on AWS — AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/architecting-for-agentic-ai-development-on-aws/)
