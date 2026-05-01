# As Sete Tools Nativas

![capa](cover.png)

## Sobre este subcapítulo

Pi.dev chega ao agente com um conjunto fixo de sete ferramentas embutidas — `read`, `write`, `edit`, `bash`, `grep`, `find` e `ls` — que cobrem as operações fundamentais sobre o sistema de arquivos e o shell. Entender cada uma dessas tools antes de qualquer decisão de extensão ou filtro é obrigatório: elas são o vocabulário base que o LLM usa para agir, e a forma como o runtime as expõe determina quais são candidatas viáveis num ambiente headless e quais exigem atenção especial.

Este subcapítulo estabelece o inventário preciso do ponto de partida: o que cada tool promete, como o LLM decide invocar uma delas, e quais flags (`--tools`, `--no-builtin-tools`) permitem controlar o conjunto ativo em tempo de invocação. Essa base é o pré-requisito direto para o subcapítulo de filtro (05) e para o mapa de IAM (06).

## Estrutura

O subcapítulo cobre: (1) **o contrato de cada tool nativa** — `read` (leitura de arquivo por path), `write` (criação ou sobrescrita de arquivo), `edit` (substituição textual dentro de arquivo existente), `bash` (execução de comando shell), `grep` (busca por padrão em arquivos), `find` (descoberta de arquivos por padrão), `ls` (listagem de diretório) — o que cada uma recebe, o que retorna, e como o LLM a invoca via tool call; (2) **controle do conjunto ativo** — a flag `--tools` para allowlist explícita de tools habilitadas, `--no-builtin-tools` para desabilitar tudo embutido, e como isso se aplica na criação de sessão via SDK; (3) **comportamento quando o ambiente não tem TTY** — tools que dependem de shell interativo vs. tools que rodam em modo não-interativo, e o que `ctx.hasUI === false` significa para o runtime das ferramentas.

## Objetivo

Ao terminar este subcapítulo, o leitor conseguirá descrever com precisão o que cada uma das sete tools nativas faz, qual é o contrato de input/output de cada uma, e como restringir programaticamente o conjunto de tools que o agente pode usar. Esse inventário é a base sobre a qual os subcapítulos 05 e 06 aplicam o filtro de viabilidade headless e o mapeamento de permissões IAM.

## Conceitos

A explicação completa destes conceitos vive em [`CONCEPTS.md`](CONCEPTS.md), construída sequencialmente pela skill `estudo-explicar-conceito`.

1. Por que pi.dev parte de apenas 4 tools por padrão — a filosofia de tool budget mínimo e por que grep/find/ls são opcionais
2. `read` — parâmetros, paginação com offset/limit, e o caso especial de imagens (JPG, PNG) como ImageContent
3. `write` — criação automática de diretórios pai e o que acontece em ambiente sem filesystem persistente entre invocações
4. `edit` — o contrato oldText/newText, o fuzzy fallback, e por que a precisão do match importa num agente headless
5. `bash` — execução de shell, streaming de stdout/stderr, e o killProcessTree como garantia de cleanup entre turnos
6. `grep`, `find`, `ls` — as três read-only tools opcionais, o que cada uma retorna, e respeito a .gitignore
7. A flag `--tools` como allowlist explícita — como passar nomes de tools como string[] para controlar exatamente o conjunto ativo
8. `--no-builtin-tools` e `--no-tools` — desabilitar o conjunto padrão para registrar as próprias tools sem conflito de nomes

## Fontes utilizadas

- [Pi Coding Agent README — seção de built-in tools](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [Pi Documentation — docs/latest/extensions](https://pi.dev/docs/latest/extensions)
- [pi-mono extensions.md — tool lifecycle events](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)
- [Pi Coding Agent: A Self-Documenting, Extensible AI Partner — DEV Community](https://dev.to/theoklitosbam7/pi-coding-agent-a-self-documenting-extensible-ai-partner-dn)
- [@mariozechner/pi-coding-agent — npm package docs](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)
