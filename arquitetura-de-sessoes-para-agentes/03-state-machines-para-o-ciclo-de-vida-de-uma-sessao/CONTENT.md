# State Machines para o Ciclo de Vida de uma Sessão

![capa](cover.png)

## Sobre este capítulo

Uma sessão agêntica não é um objeto estático — ela transita por estados bem definidos ao longo da sua vida: começa ociosa, entra em execução quando o usuário envia uma mensagem, aguarda resultados de tool calls, pode ser suspensa, compactada ou expirada. Modelar esse ciclo de vida explicitamente com uma state machine não é overkill — é o que separa um sistema que responde de forma previsível de um que corrompeu silenciosamente o estado porque duas invocações concorrentes do Lambda tentaram gravar ao mesmo tempo. Este capítulo ensina a desenhar e implementar a state machine de uma sessão, incluindo transições, guards e o mapeamento para o ambiente serverless do leitor.

A posição aqui — após o modelo mental (cap. 2) e antes da persistência (cap. 4) — é deliberada: a state machine define *quais* estados precisam ser persistidos e quando, o que diretamente informa o schema de armazenamento do próximo capítulo.

## Estrutura

Os grandes blocos são: (1) estados do ciclo de vida — definição e semântica de cada estado (IDLE, RUNNING, AWAITING_TOOL, COMPACTING, SUSPENDED, EXPIRED, FAILED) com as transições válidas entre eles e os gatilhos que as disparam; (2) guards e invariantes — condições que devem ser satisfeitas antes de uma transição (ex: não iniciar RUNNING se já há uma execução ativa; não EXPIRE uma sessão RUNNING), e como implementar esses guards de forma atômica com MongoDB; (3) concorrência e idempotência no Lambda stateless — como múltiplas invocações concorrentes podem corromper o estado da sessão e as estratégias para prevenir isso (optimistic locking, conditional writes, TTL locks no MongoDB); (4) implementação prática — uma state machine minimal em Python usando a biblioteca `transitions` ou implementação manual com dicionário de handlers, integrada ao fluxo existente do leitor.

## Objetivo

Ao terminar este capítulo, o leitor será capaz de desenhar o diagrama de estados completo de uma sessão agêntica, implementar a state machine em Python com guards de concorrência, e identificar onde o projeto atual viola invariantes de estado (ex: duas mensagens sendo processadas simultaneamente para o mesmo `input_id`). O modelo de estados produzido aqui será referenciado diretamente nos capítulos 6, 7 e 9.

## Fontes utilizadas

- [GitHub - statelyai/agent: Create state-machine-powered LLM agents using XState](https://github.com/statelyai/agent)
- [7 State Persistence Strategies for Long-Running AI Agents in 2026 — Indium Tech](https://www.indium.tech/blog/7-state-persistence-strategies-ai-agents-2026/)
- [AI Agent Architecture: Build Systems That Work in 2026 — Redis](https://redis.io/blog/ai-agent-architecture/)
- [Stateful Continuation for AI Agents: Why Transport Layers Now Matter — InfoQ](https://www.infoq.com/articles/ai-agent-transport-layer/)
- [Stateful vs Stateless AI Agents: A Practical Comparison — Tacnode](https://tacnode.io/post/stateful-vs-stateless-ai-agents-practical-architecture-guide-for-developers)
