# Custom Tools via SDK — registerTool e customTools

![capa](cover.png)

## Sobre este subcapítulo

O pi.dev oferece duas formas de adicionar tools além das sete nativas: via extensions em disco (o mecanismo coberto no subcapítulo anterior) e via `customTools` passados diretamente na criação da sessão pelo SDK. Para a POC, a segunda forma é a que importa: num handler Lambda não existe home directory, não existe `.pi/extensions/` acessível, e não há como garantir que o jiti encontre os módulos TypeScript corretamente. Passar `customTools` programaticamente ao chamar `createAgentSession` é a única via controlada e reproduzível nesse ambiente.

Este subcapítulo detalha o contrato de `registerTool` — como se define um `AgentTool` com nome, descrição, parâmetros (TypeBox schemas), e função `execute` assíncrona — e a diferença prática entre tools registradas via `ExtensionAPI.registerTool` dentro de uma extension e tools passadas no array `customTools` da sessão. Esse entendimento é essencial para o subcapítulo 05 (filtro) e para o capítulo 05 do livro (SDK embedado no handler).

## Estrutura

O subcapítulo cobre: (1) **o objeto `AgentTool` e seu contrato** — os campos obrigatórios (`name`, `description`, `parameters` com schema TypeBox, função `execute`), os campos opcionais (`promptSnippet` para descrição compacta no prompt do LLM, `promptGuidelines` para bullets de uso), e como o LLM recebe o catálogo de tools disponíveis; (2) **`customTools` na criação de sessão** — a assinatura de `createAgentSession`, onde o array `customTools` é passado, como ele coexiste com as sete tools nativas (ou as substitui quando `--no-builtin-tools` está ativo), e o escopo de vida das custom tools (por sessão); (3) **`registerTool` via `ExtensionAPI` vs. `customTools` no SDK** — as diferenças de timing (extension roda no boot da sessão; customTools são resolvidas antes do primeiro turno), de escopo (extension pode ser global; customTools são por instância de sessão), e de portabilidade (extension depende de disco; customTools são código JavaScript puro injetado); (4) **implicações para agente embedded em Lambda** — por que `customTools` é o padrão correto para o handler, como passar tools que fazem chamadas a serviços AWS dentro do handler, e o cuidado com cold start quando a definição das tools envolve I/O.

## Objetivo

Ao terminar este subcapítulo, o leitor conseguirá implementar um `AgentTool` completo usando TypeBox, passá-lo via `customTools` ao criar uma sessão no SDK, e explicar por que essa abordagem é preferível a extensions em disco num ambiente Lambda. O leitor também entenderá o trade-off de escopo e ciclo de vida entre as duas formas de registrar tools.

## Conceitos

A explicação completa destes conceitos vive em [`CONCEPTS.md`](CONCEPTS.md), construída sequencialmente pela skill `estudo-explicar-conceito`.

1. `defineTool` vs `registerTool` — as duas formas de criar uma tool no SDK e quando cada uma é a interface correta
2. O tipo `AgentTool<T>` e o padrão TypeBox — `Type.Object`, a inferência `typeof schema`, e o contrato do `execute(toolCallId, params)`
3. O parâmetro `customTools` em `createAgentSession` — como o array se combina com tools de extensions carregadas, e o escopo por sessão
4. O parâmetro `tools` vs `customTools` em `createAgentSession` — distinção entre instâncias de tool pré-construídas e definições dinâmicas via `defineTool`
5. `promptSnippet` e `promptGuidelines` — como o LLM recebe a descrição compacta da tool e bullets de uso, e o impacto no token budget por turno
6. Por que `customTools` é o padrão certo para Lambda — ausência de `agentDir` acessível, inexistência de extensions carregadas em disco, e a inicialização de tools como código JavaScript puro no handler
7. Cold start e o custo de I/O na definição de tools — o que não fazer no corpo do `execute` durante inicialização, e como inicializar conexões com serviços AWS fora do factory de tools

## Fontes utilizadas

- [Pi Documentation — docs/latest/extensions, seção registerTool](https://pi.dev/docs/latest/extensions)
- [pi-mono extensions.md — ExtensionAPI e registerTool](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)
- [@mariozechner/pi-coding-agent — npm, seção createAgentSession e customTools](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)
- [How to Build a Custom Agent Framework with PI — Nader Dabit](https://nader.substack.com/p/how-to-build-a-custom-agent-framework)
- [pi-agent-extensions — exemplos de custom tools (sessions, ask_user, handoff)](https://github.com/jayshah5696/pi-agent-extensions)
