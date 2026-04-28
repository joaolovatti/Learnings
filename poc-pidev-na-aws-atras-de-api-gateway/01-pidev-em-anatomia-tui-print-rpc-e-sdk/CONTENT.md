# Pi.dev em Anatomia — TUI, Print, RPC e SDK

![capa](cover.png)

## Sobre este capítulo

Pi.dev expõe quatro modos de execução com superfícies radicalmente diferentes: TUI (interface interativa no terminal), Print/JSON (saída determinística para pipe), RPC (protocolo JSONL sobre stdin/stdout para integração de processo), e SDK (biblioteca embedável em código próprio). Para quem está chegando sem ter aberto o harness uma vez, a primeira tarefa é entender o que cada modo oferece, o que cada um exige do ambiente, e por que uma POC headless na AWS elimina dois deles de imediato e deixa RPC e SDK como as duas apostas reais.

Este capítulo é a leitura do mapa antes de começar a caminhar. Sem dominar o modelo de execução do pi.dev, qualquer decisão de hosting na AWS — Lambda vs Fargate, SDK vs processo wrappado — fica no ar. A anatomia aqui não é turismo: é o alicerce que torna os capítulos 4 e 5 possíveis.

## Estrutura

O capítulo cobre: (1) **modo TUI** — o que é, como invocar, por que não cabe em ambiente headless e quando ele ainda é útil para desenvolvimento local; (2) **modo Print/JSON** — saída de uma só resposta em batch, uso em scripts, limitações de sessão; (3) **modo RPC** — protocolo JSONL sobre stdin/stdout, framing LF-delimitado, estrutura de eventos emitidos (text chunks, tool calls, status), por que o processo precisa ficar vivo entre turnos; (4) **modo SDK** — classes `createAgentSession`, `SessionManager`, `ModelRegistry`, `AuthStorage`, como embedar em Node.js/TypeScript; (5) **subset relevante para POC headless** — quais flags, quais eventos e quais classes do SDK entram de verdade no handler da POC e o que pode ser ignorado neste momento.

## Objetivo

Ao terminar este capítulo, o leitor saberá invocar pi.dev em cada um dos quatro modos, entenderá o contrato de I/O de RPC (JSONL framing, eventos, ciclo de vida do processo) e o contrato de API do SDK (criação de sessão, envio de turno, leitura de eventos), e conseguirá decidir com base em raciocínio técnico próprio por que a POC headless vai usar SDK embedado ou RPC — não por intuição. Esse entendimento alimenta diretamente o capítulo 4 (Lambda vs Fargate) e o capítulo 5 (SDK vs RPC no handler).

## Subcapítulos

1. [Modo TUI — o Terminal Interativo e Por Que Ele Não Cabe em Headless](01-modo-tui-o-terminal-interativo-e-por-que-nao-cabe-em-headless/CONTENT.md) — flags de invocação, rendering diferencial, dependências de TTY, e por que ambiente headless descarta esse modo
2. [Modo Print/JSON — Saída Determinística Para Scripts](02-modo-print-json-saida-deterministica-para-scripts/CONTENT.md) — invocação com -p e --mode json, event stream de saída única, limitação de sessão única e o que isso exclui para POC multi-turno
3. [Modo RPC — Protocolo JSONL Sobre stdin/stdout](03-modo-rpc-protocolo-jsonl-sobre-stdin-stdout/CONTENT.md) — framing LF-delimitado, tipos de eventos emitidos (text chunk, tool call, status), request/response correlation, e ciclo de vida do processo entre turnos
4. [Modo SDK — Embedando Pi.dev em Node.js/TypeScript](04-modo-sdk-embedando-pidev-em-nodejs-typescript/CONTENT.md) — createAgentSession, SessionManager, ModelRegistry, AuthStorage, e o loop de leitura de eventos
5. [O Subset que Importa Para a POC Headless](05-o-subset-que-importa-para-a-poc-headless/CONTENT.md) — eliminação técnica de TUI e Print, flags e classes concretas de RPC e SDK que entram no handler, e o gancho para os capítulos 4 e 5

## Fontes utilizadas

- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [Pi Documentation — pi.dev/docs/latest](https://pi.dev/docs/latest)
- [@mariozechner/pi-coding-agent — npm package](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)
- [Getting Started — DeepWiki pi-agent](https://deepwiki.com/agentic-dev-io/pi-agent/1.1-getting-started)
- [pi.dev.details.md — community gist com detalhes do protocolo RPC](https://gist.github.com/rajeshpv/eccc1dc8d70e8cdcf948de3312ca111f)
- [Pi Coding Agent — Sandbox Analysis Report](https://agent-safehouse.dev/docs/agent-investigations/pi)
