# Anatomia de uma Entrada JSONL

![capa](cover.png)

## Sobre este subcapítulo

O pi.dev persiste sessões como arquivos JSONL — um formato onde cada linha é um objeto JSON completo e autossuficiente. Antes de qualquer discussão sobre árvores, forks ou persistência externa, o leitor precisa saber exatamente o que está em cada linha: quais campos são obrigatórios, quais são opcionais, o que cada campo carrega, e como o harness escreve e lê esse arquivo. Este subcapítulo desmonta uma entrada de sessão campo a campo, cobrindo o `SessionHeader` (a linha especial que abre o arquivo) e as `SessionMessageEntry`s (as linhas regulares que registram a conversa), além do comportamento de escrita append-only que torna o formato seguro e previsível.

Este é o ponto de partida obrigatório: sem entender o esquema de uma entrada individual, é impossível raciocinar sobre a estrutura de árvore que o conjunto de entradas forma, ou sobre o que precisa ser salvo quando a persistência sai do disco local.

## Estrutura

O subcapítulo cobre: (1) **SessionHeader** — campos `type`, `version`, `id` (UUID), `cwd` e o campo opcional `parentSession` que aparece em sessões derivadas de fork; (2) **SessionMessageEntry** — campos `type: "message"`, `id` (hex de 8 caracteres), `parentId` (null na primeira entrada, referência a outra entrada nas demais), `timestamp` (ISO 8601), e o objeto `message` com os roles possíveis (`user`, `assistant`, `toolResult`, `bashExecution`, `custom`, `branchSummary`, `compactionSummary`); (3) **entradas de metadados** — `model_change`, `thinking_level_change` e `custom` como tipos de linha que registram mudanças de estado sem alterar o contexto do LLM; (4) **append-only como contrato de escrita** — como o harness abre o arquivo em modo append, escreve uma linha e fecha, garantindo que cada escrita seja atômica ao nível de linha.

## Objetivo

Ao terminar este subcapítulo, o leitor será capaz de abrir um arquivo `.jsonl` de sessão do pi.dev e identificar cada campo por nome e semântica, distinguir o `SessionHeader` das demais entradas, reconhecer os diferentes roles dentro do campo `message`, e entender por que o append-only torna cada linha-write atômica. Esse conhecimento prepara diretamente o subcapítulo seguinte, onde as referências `id`/`parentId` passam a fazer sentido como estrutura de árvore.

## Conceitos

Veja o roteiro completo em [CONCEPTS.md](CONCEPTS.md).

1. O que é JSONL e por que o pi.dev o usa para sessões — o formato linha-por-objeto, por que ele é adequado para logs append-only, e como o pi.dev organiza um arquivo de sessão como sequência de linhas independentes
2. `SessionHeader` — a linha de abertura obrigatória do arquivo, com campos `type: "session"`, `version`, `id` (UUID), `timestamp`, `cwd`, e o campo opcional `parentSession` que aparece em sessões derivadas de fork
3. `SessionMessageEntry` base — os quatro campos estruturais que toda entrada regular carrega: `type: "message"`, `id` (hex de 8 caracteres), `parentId` (null na primeira entrada do trunk, referência hex nas demais), e `timestamp` ISO 8601
4. O objeto `message` e seus roles — a anatomia interna de uma `SessionMessageEntry`: o que cada role representa (`user`, `assistant`, `toolResult`, `bashExecution`, `custom`, `branchSummary`, `compactionSummary`) e os campos específicos por role
5. Entradas de metadados — `model_change` e `thinking_level_change` como tipos de linha que participam da árvore via `id`/`parentId` mas registram mudanças de estado sem carregar conteúdo de mensagem para o LLM
6. Append-only como contrato de escrita — como o harness abre o arquivo em modo append, escreve uma linha completa e fecha, por que isso torna cada write atômica ao nível de linha, e o que esse contrato proíbe (editar, truncar, reordenar)

## Fontes utilizadas

- [Pi session-format — pi.dev/docs/latest](https://pi.dev/docs/latest/session-format)
- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [Session Management and Persistence — DeepWiki (agentic-dev-io/pi-agent)](https://deepwiki.com/agentic-dev-io/pi-agent/2.4-session-management-and-persistence)
- [@mariozechner/pi-coding-agent — npmx](https://npmx.dev/package/@mariozechner/pi-coding-agent)
- [JSONL for Log Processing — JSONL.help](https://jsonl.help/use-cases/log-processing/)
