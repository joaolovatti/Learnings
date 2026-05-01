# Fork e Branch na Prática — Criar e Navegar

![capa](cover.png)

## Sobre este subcapítulo

Com o modelo de árvore claro e os tipos de entrada especiais mapeados, este subcapítulo trata do aspecto operacional: como o usuário ou o código cria um fork ou um branch, o que acontece exatamente no arquivo JSONL quando isso ocorre, e como o harness navega para retomar um branch específico. A distinção entre fork e branch — que conceitualmente pode parecer sutil — tem consequências concretas no arquivo e, portanto, no que precisa ser persistido: fork cria um novo arquivo `.jsonl` com `parentSession` apontando para o original; branch adiciona novos nós no mesmo arquivo.

Para o engenheiro que vai implementar persistência externa, saber quando haverá um arquivo novo (fork) vs. quando o arquivo existente crescerá de forma não-linear (branch) é essencial para desenhar a estratégia de sincronização correta.

## Estrutura

O subcapítulo cobre: (1) **branch via TUI** — o comando `/tree` no terminal interativo, como o leitor navega a árvore com as setas, seleciona um nó anterior e inicia edição a partir dele, e o que o harness escreve no arquivo nesse momento (novos nós com `parentId` apontando para o nó selecionado); (2) **branch via SDK** — o método `branch(entryId)` da interface `SessionManager`, o que `branchWithSummary()` faz diferente (injeta um `BranchSummaryEntry` antes de continuar), e como receber o `leafId` correto para navegar programaticamente; (3) **fork via TUI** — o comando `/fork` na sessão ativa, o que ele cria no disco (novo arquivo `.jsonl` no diretório de sessões), e o campo `parentSession` no `SessionHeader` do arquivo filho; (4) **fork via SDK** — `SessionManager.forkFrom(entryId)` vs. fork completo, o que o método retorna, e por que o fork é "independente" (edições no filho não alteram o pai).

## Objetivo

Ao terminar este subcapítulo, o leitor entenderá a diferença operacional entre fork e branch ao nível do arquivo JSONL, saberá o que acontece no disco em cada operação, conseguirá invocar `branch()` e `forkFrom()` via SDK com os parâmetros corretos, e estará preparado para avaliar como cada operação afeta a estratégia de persistência externa — em especial o que precisa ser versionado ou replicado quando o usuário faz fork numa sessão persistida em S3 ou EFS.

## Conceitos

A explicação completa destes conceitos vive em [`CONCEPTS.md`](CONCEPTS.md), construída sequencialmente pela skill `estudo-explicar-conceito`.

1. Branch via TUI — o comando `/tree`, como navegar a árvore com setas e selecionar um nó anterior, e o que o harness escreve no arquivo JSONL ao confirmar (novos nós com `parentId` apontando para o nó selecionado, sem criar arquivo novo)
2. Branch via SDK — o método `branch(entryId)` da interface `SessionManager`, o que ele retorna (o `leafId` do novo nó criado), e como usar esse `leafId` para continuar a conversa programaticamente a partir do ponto escolhido
3. `branchWithSummary()` vs `branch()` — o que `branchWithSummary(id, summary)` faz diferente: injeta um `BranchSummaryEntry` antes de continuar, quando usar cada forma, e a implicação para quem serializa o arquivo para persistência externa
4. Fork via TUI — o comando `/fork` na sessão ativa, o que ele cria no disco (novo arquivo `.jsonl` no diretório de sessões), e o campo `parentSession` no `SessionHeader` do arquivo filho que aponta para o caminho absoluto do arquivo original
5. Fork via SDK — `SessionManager.forkFrom(sourcePath, targetCwd)` e sua variante de fork parcial por `entryId`, o que o método retorna, e por que edições no arquivo filho não alteram o arquivo pai (independência completa entre arquivos)
6. Implicação operacional para persistência externa — quando haverá um arquivo novo que precisa ser replicado/sincronizado (fork) vs. quando o arquivo existente cresce de forma não-linear (branch), e o que isso significa concretamente para estratégias de sincronização com EFS ou S3

## Fontes utilizadas

- [Pi sessions — pi.dev/docs/latest](https://pi.dev/docs/latest/sessions)
- [Pi session-format — pi.dev/docs/latest](https://pi.dev/docs/latest/session-format)
- [Session Management and Persistence — DeepWiki (agentic-dev-io/pi-agent)](https://deepwiki.com/agentic-dev-io/pi-agent/2.4-session-management-and-persistence)
- [Managing Context Windows with pi /tree — StackToHeap](https://stacktoheap.com/blog/2026/02/26/pi-tree-context-window-management/)
- [@mariozechner/pi-coding-agent — npm](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)
