# Modo RPC — Protocolo JSONL Sobre stdin/stdout

![capa](cover.png)

## Sobre este subcapítulo

O modo RPC transforma o pi.dev em um servidor headless que se comunica exclusivamente via stdin/stdout usando JSONL estrito. O processo fica vivo entre turnos — diferente do Print/JSON, que nasce e morre em cada invocação — e aceita comandos do caller enquanto emite eventos de volta à medida que o agente processa cada prompt. Essa arquitetura é o que torna o modo RPC uma opção viável para hosting de longa vida (Fargate com container permanente, por exemplo) e a alternativa direta ao SDK embedado que o capítulo 5 vai comparar em detalhe.

Este subcapítulo é o mais denso tecnicamente do capítulo: o protocolo RPC tem semântica própria, e entendê-lo em profundidade — framing, tipos de evento, correlação de request/response, ciclo de vida do processo — é pré-requisito direto para a decisão de arquitetura dos capítulos 4 e 5. O leitor que sair daqui conseguirá escrever um cliente RPC do zero se precisar.

## Estrutura

O subcapítulo cobre: (1) **framing JSONL** — delimitação obrigatória por LF (`\n`), por que `\r\n` deve ser normalizado, por que usar `readline` do Node.js é um erro (Unicode separators U+2028/U+2029 quebrando o framing), alternativas corretas de parsing; (2) **tipos de eventos emitidos** — `text_chunk` (fragmento incremental da resposta), `tool_call` (chamada a uma tool com argumentos), `tool_result` (resultado retornado pela tool), `status` (estado do ciclo de vida do agente: idle, processing, waiting_approval), formato JSON de cada um; (3) **request/response correlation** — campo `id` opcional em cada comando, como o response espelha o mesmo `id`, por que correlação é necessária quando múltiplos comandos podem estar em flight; (4) **ciclo de vida do processo entre turnos** — como o processo persiste, como o caller envia o próximo turno sem reiniciar o processo, o que acontece se o processo morrer e como detectar isso; (5) **aprovação de tool calls** — o protocolo de aprovação/rejeição de chamadas antes que a tool execute, relevância para ambientes controlados.

## Objetivo

Ao terminar este subcapítulo, o leitor conseguirá implementar um cliente RPC básico em Node.js — enviando prompts via stdin e processando eventos do stdout — e saberá diagnosticar os erros de framing mais comuns. Entenderá o ciclo de vida do processo RPC o suficiente para avaliar, no capítulo 5, quando wrapping de processo RPC é preferível ao SDK embedado, e quando não é.

## Fontes utilizadas

- [RPC Mode — docs/rpc.md (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/rpc.md)
- [RPC Mode — pi-mono docs (hochej mirror)](https://hochej.github.io/pi-mono/coding-agent/rpc/)
- [pi-mono-ai-agent-toolkit — docs/rpc.md (skyiron fork)](https://github.com/skyiron/pi-mono-ai-agent-toolkit/blob/main/packages/coding-agent/docs/rpc.md)
- [@mariozechner/pi-coding-agent — npm package](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)
- [pi.dev.details.md — community gist com detalhes do protocolo RPC](https://gist.github.com/rajeshpv/eccc1dc8d70e8cdcf948de3312ca111f)
- [Pi Coding Agent — Sandbox Analysis Report (Agent Safehouse)](https://agent-safehouse.dev/docs/agent-investigations/pi)
