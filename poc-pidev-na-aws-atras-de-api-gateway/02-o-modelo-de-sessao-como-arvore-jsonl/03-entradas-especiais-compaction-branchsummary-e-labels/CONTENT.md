# Entradas Especiais — Compaction, BranchSummary e Labels

![capa](cover.png)

## Sobre este subcapítulo

Além das `SessionMessageEntry`s regulares que compõem a conversa, o arquivo JSONL de sessão do pi.dev contém um conjunto de entradas especiais com semânticas próprias: `CompactionEntry`, `BranchSummaryEntry` e `label`. Essas entradas não são mensagens da conversa — são metadados que o harness usa para gerenciar janela de contexto, preservar raciocínio ao trocar de branch, e marcar posições de interesse. Para quem vai implementar persistência externa, esses tipos são críticos: ignorá-los ao serializar ou filtrar o arquivo quebra a capacidade de o harness reconstruir o contexto corretamente.

Este subcapítulo cobre exatamente esses tipos especiais — o que cada um carrega, quando é emitido, e o que significa para a leitura do arquivo.

## Estrutura

O subcapítulo cobre: (1) **CompactionEntry** — quando o harness decide compactar (contexto próximo do limite de tokens), o que o campo `summary` carrega (resumo LLM-gerado das mensagens anteriores), o que `firstKeptEntryId` significa (o nó a partir do qual as mensagens originais ainda são incluídas no contexto), e por que o leitor precisa respeitar esse ponteiro ao reconstruir o contexto; (2) **BranchSummaryEntry** — gerada automaticamente quando o usuário troca de branch, captura em linguagem natural o estado do branch abandonado para que o LLM não perca o fio ao voltar; como identificá-la no arquivo (role `branchSummary`) e quando ela aparece no contexto; (3) **label entries** — bookmarks nomeados que o usuário cria com Shift+L no `/tree`; o campo `targetId` aponta para uma entrada existente, e `label: undefined` apaga o bookmark; uso programático para marcar pontos de retomada sem criar novos nós; (4) **`custom` vs `custom_message`** — `custom` é estado interno de extensions que não entra no contexto do LLM; `custom_message` é conteúdo injetado por extensions que entra; distinção crítica ao filtrar o arquivo para reconstruir o contexto.

## Objetivo

Ao terminar este subcapítulo, o leitor saberá identificar cada tipo de entrada especial no arquivo JSONL, entenderá o que `firstKeptEntryId` significa para a reconstrução de contexto pós-compaction, saberá quando `BranchSummaryEntry` é emitida e por que não pode ser descartada ao trocar de branch, e distinguirá `custom` de `custom_message` ao filtrar o arquivo. Esse conhecimento é necessário para implementar corretamente qualquer lógica que leia ou replique o arquivo de sessão.

## Conceitos

Roteiro completo em [CONCEPTS.md](CONCEPTS.md).

1. CompactionEntry — estrutura do tipo (`summary`, `firstKeptEntryId`, `tokensBefore`, `fromHook`), quando o harness dispara compactação automática, e como `firstKeptEntryId` funciona como ponteiro de corte para reconstruir o contexto pós-compactação sem incluir mensagens já resumidas
2. BranchSummaryEntry — estrutura do tipo (`fromId`, `summary`, `fromHook`), quando é gerada (troca de branch via `/tree`), lógica do ancestral comum, e por que essa entrada não pode ser descartada ao serializar o arquivo para persistência externa
3. LabelEntry — estrutura do tipo (`targetId`, `label`), como criar e apagar bookmarks (Shift+L no TUI; `label: undefined` remove), e uso programático como marcador de ponto de retomada sem criar novos nós de conversa
4. `custom` vs `custom_message` — distinção entre estado interno de extension que não entra no contexto LLM (`custom`) e conteúdo injetado por extension que entra (`custom_message`), campos `customType`, `data`, `content` e `display`, e a implicação prática ao filtrar o arquivo para reconstruir o contexto

## Fontes utilizadas

- [Pi session-format — pi.dev/docs/latest](https://pi.dev/docs/latest/session-format)
- [Session Management and Persistence — DeepWiki (agentic-dev-io/pi-agent)](https://deepwiki.com/agentic-dev-io/pi-agent/2.4-session-management-and-persistence)
- [Pi sessions — pi.dev/docs/latest](https://pi.dev/docs/latest/sessions)
- [Managing Context Windows with pi /tree — StackToHeap](https://stacktoheap.com/blog/2026/02/26/pi-tree-context-window-management/)
- [@mariozechner/pi-coding-agent — npm](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)
