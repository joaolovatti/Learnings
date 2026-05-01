# O Sistema de Extensions — Protocolo e Ciclo de Vida

![capa](cover.png)

## Sobre este subcapítulo

O sistema de extensions é o mecanismo pelo qual o pi.dev aceita comportamentos programáticos adicionais sem alterar o core do harness. Uma extension é um módulo TypeScript que recebe um objeto `ExtensionAPI` e usa-o para se inscrever em eventos do ciclo de vida, registrar tools adicionais, adicionar comandos e interceptar ou modificar resultados de ferramentas antes que o LLM os veja.

Entender esse protocolo em detalhe é necessário antes de decidir se a POC vai usar extensions em disco (carregamento automático) ou `customTools` passados via SDK (abordagem programática coberta no próximo subcapítulo). O ciclo de vida de uma tool call — a sequência exata de eventos desde a decisão do LLM até o resultado devolvido — também determina onde um extension pode intervir e por quê.

## Estrutura

O subcapítulo cobre: (1) **descoberta e carregamento de extensions** — as três formas de carregar uma extension (`~/.pi/agent/extensions/*.ts` para escopo global, `.pi/extensions/*.ts` para escopo de projeto, e a flag `-e ./path.ts` para testes), o papel do `jiti` para execução de TypeScript sem compilação explícita, e as implicações desse mecanismo em ambiente Lambda onde não há home directory; (2) **o contrato de `ExtensionAPI`** — a interface que o factory default export recebe, os métodos de registro disponíveis (`registerTool`, `addCommand`, `on`/`off` para eventos), e o que é e o que não é acessível via essa API; (3) **o ciclo de vida completo de uma tool call** — a sequência `tool_execution_start → tool_call (pode bloquear) → execute → tool_execution_update (streaming) → tool_result (pode modificar) → tool_execution_end`, o que cada evento carrega no contexto, e como múltiplos handlers se encadeiam em middleware para `tool_result`; (4) **interceptação e bloqueio** — como o handler de `tool_call` pode impedir a execução de uma tool (ex: operações destrutivas), e como isso se comporta quando `ctx.hasUI === false`.

## Objetivo

Ao terminar este subcapítulo, o leitor saberá descrever o protocolo completo pelo qual uma extension é carregada e opera dentro de uma sessão pi.dev, identificar os pontos exatos no ciclo de vida onde um handler pode intervir, e antecipar por que o mecanismo de descoberta por disco (`~/.pi/extensions/`) é problemático em ambiente Lambda — abrindo caminho para a solução programática do subcapítulo 03.

## Conceitos

A explicação completa destes conceitos vive em [`CONCEPTS.md`](CONCEPTS.md), construída sequencialmente pela skill `estudo-explicar-conceito`.

1. O que é uma extension no pi.dev — módulo TypeScript com factory default export que recebe ExtensionAPI
2. Descoberta automática de extensions — os dois caminhos em disco (~/.pi/agent/extensions/ e .pi/extensions/) e a flag -e para teste direto
3. O papel do jiti — execução de TypeScript sem compilação, o ambiente virtualizado e o que está disponível no escopo
4. O contrato de ExtensionAPI — o que o factory recebe: registerTool, registerCommand, registerShortcut, e on/off para eventos
5. A sequência completa de eventos de uma tool call — tool_execution_start → tool_call → execute → tool_execution_update → tool_result → tool_execution_end
6. Interceptar e bloquear em tool_call — como o handler pode cancelar a execução de uma tool e o que acontece com o turno do LLM quando isso ocorre
7. Modificar o resultado em tool_result — encadeamento middleware de handlers, como cada um recebe e pode transformar o resultado antes do LLM ver
8. Por que a descoberta em disco falha em Lambda — ausência de home directory, filesystem efêmero, e o que ctx.hasUI === false significa para handlers que tentam abrir UI dialogs

## Fontes utilizadas

- [pi-mono extensions.md — documentação completa do sistema de extensions](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)
- [Pi Documentation — docs/latest/extensions](https://pi.dev/docs/latest/extensions)
- [Pi Coding Agent README — seção de extensibility](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [Extending Pi Coding Agent with Custom Tools and Widgets — JoelClaw](https://joelclaw.com/extending-pi-with-custom-tools)
- [How to Build a Custom Agent Framework with PI — Nader Dabit](https://nader.substack.com/p/how-to-build-a-custom-agent-framework)
