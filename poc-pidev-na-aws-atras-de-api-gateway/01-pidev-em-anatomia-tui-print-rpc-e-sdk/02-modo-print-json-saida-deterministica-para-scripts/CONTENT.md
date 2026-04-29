# Modo Print/JSON — Saída Determinística Para Scripts

![capa](cover.png)

## Sobre este subcapítulo

O modo Print/JSON é a porta de entrada do pi.dev para automação: uma única invocação recebe um prompt, processa, e escreve a resposta no stdout antes de sair. Sem estado persistido entre chamadas, sem UI, sem processo de longa vida — exatamente o contrato que scripts, pipelines de CI, e tarefas batch precisam. Dentro do capítulo, este subcapítulo ocupa a posição de segundo modo a ser descartado para a POC headless: embora funcione sem TTY, sua limitação de sessão única o torna inutilizável para conversas de múltiplos turnos.

A distinção entre `--mode print` (resposta final em texto puro) e `--mode json` (event stream JSONL com cada evento intermediário) é relevante porque o `--mode json` revela parcialmente a estrutura de eventos que o modo RPC vai explorar por completo — aprender Print/JSON é uma rampa de entrada natural para o subcapítulo seguinte.

## Estrutura

O subcapítulo cobre: (1) **invocação do modo Print** — a flag `-p "prompt"` e `--mode print`, o ciclo de vida do processo (inicia, processa, imprime, sai), o que é escrito no stdout e o que vai para stderr; (2) **invocação do modo JSON** — `--mode json` como event stream JSONL de saída única, os tipos de eventos emitidos durante o processamento (text chunk, tool call, tool result, status), formato de cada evento; (3) **limitação de sessão única** — por que cada invocação começa um contexto do zero, o que isso significa para conversas com memória, e como isso difere do contrato que a POC precisa honrar (múltiplos turnos preservando estado); (4) **uso legítimo em pipe e scripts** — integração com `jq`, processamento de saída, casos onde a limitação de sessão não é problema.

## Objetivo

Ao terminar este subcapítulo, o leitor conseguirá invocar pi.dev em modo Print e JSON, entenderá o formato dos eventos emitidos em `--mode json` (e reconhecerá esses tipos de evento quando eles reaparecerem no modo RPC), e saberá articular por que a limitação de sessão única descarta esse modo para qualquer endpoint de conversação multi-turno como o que a POC expõe.

## Conceitos

A explicação completa destes conceitos vive em [`CONCEPTS.md`](CONCEPTS.md), construída sequencialmente pela skill `estudo-explicar-conceito`.

1. Invocação do modo Print — a flag `-p` e `--mode print`, o ciclo de vida do processo (inicia, processa, imprime, sai), e o que é escrito no stdout versus no stderr
2. O modo JSON como event stream JSONL — `--mode json` como saída única no stdout, o cabeçalho de sessão como primeira linha, e a convenção de framing LF-delimitado
3. Tipos de eventos emitidos em `--mode json` — agent/turn/message lifecycle events, tool execution events, queue_update e compaction: estrutura de cada tipo e sequência de emissão
4. Limitação de sessão única — por que cada invocação começa um contexto do zero, o que isso impede para conversas com memória entre turnos, e o contraste com o contrato que a POC precisa honrar
5. Uso legítimo em pipe e scripts — integração com `jq`, piped stdin (`cat | pi -p`), e os casos concretos onde a limitação de sessão não é obstáculo
6. Print/JSON como rampa de entrada para RPC — como os tipos de evento visíveis em `--mode json` reaparecem no modo RPC e por que entender essa estrutura aqui reduz a curva do subcapítulo seguinte

## Fontes utilizadas

- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [@mariozechner/pi-coding-agent — npm package](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)
- [Pi Coding Agent CLI — DeepWiki badlogic/pi-mono](https://deepwiki.com/badlogic/pi-mono/4-pi-coding-agent:-coding-agent-cli)
- [RPC Mode — pi-mono docs (hochej mirror)](https://hochej.github.io/pi-mono/coding-agent/rpc/)
- [Pi Coding Agent — Sandbox Analysis Report (Agent Safehouse)](https://agent-safehouse.dev/docs/agent-investigations/pi)
