# Modo SDK — Embedando Pi.dev em Node.js/TypeScript

![capa](cover.png)

## Sobre este subcapítulo

O SDK do pi.dev expõe o harness como biblioteca Node.js/TypeScript — sem spawn de processo externo, sem protocolo de pipe, sem framing manual. O código importa diretamente as classes do pacote `@mariozechner/pi-coding-agent` e chama o agente como se fosse qualquer biblioteca local. Esse modelo de embedding é a alternativa mais direta ao modo RPC para quem já está em Node.js, e é o que projetos como o OpenClaw usam em produção para integrar pi.dev sem abrir uma camada de processo separada.

Este subcapítulo mapeia as quatro peças fundamentais da API do SDK (`createAgentSession`, `SessionManager`, `ModelRegistry`, `AuthStorage`) e o loop de leitura de eventos — suficiente para que o leitor entenda, no subcapítulo 5, o que concretamente está em jogo quando a POC precisa decidir entre SDK e wrapping de processo RPC.

## Estrutura

O subcapítulo cobre: (1) **`createAgentSession`** — a factory function central, seus parâmetros (sessionManager, modelRegistry, authStorage, resourceLoader), o que retorna, e como o AgentSession criado se comporta em relação ao ciclo de vida; (2) **`SessionManager`** — os modos de abertura de sessão (`inMemory()`, `open()`, `continueRecent()`, `forkFrom()`, `list()`), o que cada modo implica para persistência e continuidade de contexto, e como o SessionManager customizado backed por S3 se encaixa aqui (gancho para o capítulo 9); (3) **`ModelRegistry` e `AuthStorage`** — como o SDK resolve credenciais de modelo e storage de autenticação, o que precisa ser configurado para rodar em Lambda sem home directory do usuário; (4) **loop de leitura de eventos** — como o SDK emite eventos (text chunk, tool call, status) de forma análoga ao RPC, a diferença é que são callbacks/Promises em vez de linhas de stdout, padrões de consume com `async for` ou event listener; (5) **`ResourceLoader`** — como o SDK carrega extensions, skills, prompt templates e context files, e o que pode ser omitido na POC sem quebrar o comportamento básico do agente.

## Objetivo

Ao terminar este subcapítulo, o leitor conseguirá escrever um handler Node.js/TypeScript mínimo que embeda o pi.dev via SDK — instanciando sessão, enviando um turno, e consumindo os eventos de resposta — e saberá quais classes e parâmetros são obrigatórios versus opcionais para o cenário da POC. Esse domínio é o insumo direto para o capítulo 5, que compara lado a lado esse modelo de embedding com o wrapping de processo RPC.

## Fontes utilizadas

- [SDK Mode — docs/sdk.md (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [Session Management — docs/session.md (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/session.md)
- [@mariozechner/pi-coding-agent — npm package](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)
- [How to Build a Custom Agent Framework with PI — Nader Dabit (gist)](https://gist.github.com/dabit3/e97dbfe71298b1df4d36542aceb5f158)
- [Pi integration architecture — OpenClaw docs](https://docs.openclaw.ai/pi)
- [Pi Coding Agent CLI — DeepWiki badlogic/pi-mono](https://deepwiki.com/badlogic/pi-mono/4-pi-coding-agent:-coding-agent-cli)
