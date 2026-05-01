# Conceitos: Entradas Especiais — Compaction, BranchSummary e Labels

> Além das `SessionMessageEntry`s regulares, o arquivo JSONL de sessão do pi.dev contém quatro tipos especiais de entradas — `CompactionEntry`, `BranchSummaryEntry`, `LabelEntry`, `custom` e `custom_message` — que o harness usa para gerenciar janela de contexto, preservar raciocínio ao trocar de branch, marcar posições de interesse e injetar estado de extensions. Para quem vai implementar persistência externa, esses tipos são críticos: ignorá-los ao serializar ou filtrar o arquivo quebra a capacidade do harness de reconstruir o contexto corretamente. Este subcapítulo é o terceiro de seis no capítulo "O Modelo de Sessão Como Árvore JSONL", após a anatomia das entradas regulares e o modelo DAG, e antes de fork/branch na prática.

## Roteiro

1. CompactionEntry — estrutura do tipo (`summary`, `firstKeptEntryId`, `tokensBefore`, `fromHook`), quando o harness dispara compactação automática, e como `firstKeptEntryId` funciona como ponteiro de corte para reconstruir o contexto pós-compactação sem incluir mensagens já resumidas
2. BranchSummaryEntry — estrutura do tipo (`fromId`, `summary`, `fromHook`), quando é gerada (troca de branch via `/tree`), lógica do ancestral comum, e por que essa entrada não pode ser descartada ao serializar o arquivo para persistência externa
3. LabelEntry — estrutura do tipo (`targetId`, `label`), como criar e apagar bookmarks (Shift+L no TUI; `label: undefined` remove), e uso programático como marcador de ponto de retomada sem criar novos nós de conversa
4. `custom` vs `custom_message` — distinção entre estado interno de extension que não entra no contexto LLM (`custom`) e conteúdo injetado por extension que entra (`custom_message`), campos `customType`, `data`, `content` e `display`, e a implicação prática ao filtrar o arquivo para reconstruir o contexto

## 1. CompactionEntry — estrutura do tipo (`summary`, `firstKeptEntryId`, `tokensBefore`, `fromHook`), quando o harness dispara compactação automática, e como `firstKeptEntryId` funciona como ponteiro de corte para reconstruir o contexto pós-compactação sem incluir mensagens já resumidas

A janela de contexto de um LLM tem limite finito. Em sessões longas — múltiplos turnos, muitas chamadas de tool, leituras de arquivo — o acúmulo de mensagens na árvore JSONL eventualmente ultrapassa esse limite. O pi.dev resolve o problema sem descartar o histórico: gera um resumo em linguagem natural das mensagens mais antigas, registra esse resumo como uma entrada especial no arquivo, e usa o resumo no lugar das mensagens originais na próxima chamada ao modelo. Esse é o papel da `CompactionEntry`.

A entrada tem `"type": "compaction"` e carrega quatro campos centrais além de `id`, `parentId` e `timestamp`:

| Campo | Tipo | Significado |
|---|---|---|
| `summary` | `string` | Resumo gerado pelo LLM cobrindo as mensagens que foram descartadas da janela |
| `firstKeptEntryId` | `string` | ID da primeira entrada que **não** foi resumida — o ponto de corte |
| `tokensBefore` | `number` | Contagem de tokens do contexto imediatamente antes da compactação ocorrer |
| `fromHook` | `boolean` | `true` se a entrada foi gerada por uma extension; `false`/ausente se gerada pelo harness |

O campo `details` é opcional e armazena metadados de implementação. Na compactação padrão, carrega `{ readFiles: string[], modifiedFiles: string[] }` — os arquivos que o agente tinha lido ou modificado antes do ponto de corte, preservados para que o LLM saiba o estado do workspace mesmo sem ver as mensagens que os produziram. Extensions que implementam compactação customizada podem armazenar dados arbitrários aqui.

A compactação automática dispara quando `contextTokens > contextWindow - reserveTokens`. O valor padrão de `reserveTokens` é 16.384 tokens — uma reserva para a resposta do modelo. O usuário também pode disparar manualmente via `/compact [instruções]` no TUI, passando instruções opcionais que guiam o resumo.

O mecanismo de reconstrução de contexto usa `firstKeptEntryId` como ponteiro de corte. Quando o harness reconstrói o contexto para uma chamada ao LLM e encontra uma `CompactionEntry` na path ativa da árvore, ele emite: (1) o `summary` como mensagem do assistente ou de sistema, seguido de (2) todas as entradas a partir de `firstKeptEntryId` até a leaf ativa. Mensagens antes do `firstKeptEntryId` não entram — elas foram substituídas pelo resumo.

Em compactações repetidas (uma sessão longa o suficiente para compactar mais de uma vez), o intervalo de mensagens a ser resumido começa no `firstKeptEntryId` da compactação anterior, não na `CompactionEntry` em si. O harness recalcula `tokensBefore` a partir do contexto efetivo que será substituído, portanto o valor no arquivo reflete com precisão os tokens removidos naquela rodada. Esse encadeamento garante que mensagens que sobreviveram a uma compactação anterior são incluídas no resumo da próxima — sem buracos de contexto entre compactações.

Para quem vai implementar persistência externa (capítulos 8 e 9 deste livro), a `CompactionEntry` não pode ser ignorada ou filtrada ao serializar o arquivo. Ela é um nó da árvore com `parentId` próprio, e o `firstKeptEntryId` pode apontar para qualquer entrada na path — se o storage externo omitir a entrada ou perder o `firstKeptEntryId`, o harness reconstruirá o contexto errado ou não encontrará o ponteiro de corte. O efeito prático é que a sessão se comporta como se mensagens intermediárias tivessem sumido, o que produz respostas incoerentes ou falha silenciosa na reconstrução. A `BranchSummaryEntry` tem motivação análoga — veremos no próximo conceito como o mesmo problema aparece na troca de branch.

**Fontes utilizadas:**

- [Compaction & Branch Summarization — pi.dev/docs/latest/compaction](https://pi.dev/docs/latest/compaction)
- [Session Format — pi.dev/docs/latest/session-format](https://pi.dev/docs/latest/session-format)
- [Compaction and Context Management — DeepWiki agentic-dev-io/pi-agent](https://deepwiki.com/agentic-dev-io/pi-agent/2.5-compaction-and-context-management)
- [pi-mono/packages/coding-agent/docs/compaction.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/compaction.md)

## 2. BranchSummaryEntry — estrutura do tipo (`fromId`, `summary`, `fromHook`), quando é gerada (troca de branch via `/tree`), lógica do ancestral comum, e por que essa entrada não pode ser descartada ao serializar o arquivo para persistência externa

A motivação da `BranchSummaryEntry` espelha a da `CompactionEntry`, mas para um problema diferente. Quando o usuário navega pelo `/tree` e muda de um branch para outro, os dois paths da árvore divergem a partir de um ancestral comum. O novo path não inclui as mensagens do branch abandonado — elas existem no arquivo JSONL mas não fazem parte da `pathFromRoot` do ponto de destino. Se o LLM simplesmente continuasse a partir do novo leaf sem nenhuma injeção, ele perderia o raciocínio e as decisões que foram desenvolvidas no branch que ficou para trás. A `BranchSummaryEntry` é a resposta: um resumo LLM-gerado das mensagens do branch abandonado, inserido no ponto de chegada para que o modelo carregue o contexto daquele trabalho sem ter que re-ler cada mensagem.

A entrada tem `"type": "branch_summary"` e os seguintes campos centrais:

| Campo | Tipo | Significado |
|---|---|---|
| `fromId` | `string` | ID do leaf abandonado — a posição de onde o usuário navegou |
| `summary` | `string` | Resumo LLM-gerado do branch abandonado, do ancestral comum até o leaf |
| `fromHook` | `boolean` | `true` se gerada por extension; `false`/ausente se gerada pelo próprio harness |
| `details` | `object` (opcional) | `{ readFiles: string[], modifiedFiles: string[] }` — arquivos que o agente tocou no branch resumido |

O `parentId` da `BranchSummaryEntry` é o nó de destino da navegação — ela é filha do novo leaf, não do ancestral comum. O `fromId` é o ponteiro explícito para o leaf que foi abandonado. Essa distinção é importante: `parentId` posiciona a entrada na árvore (onde ela vive), e `fromId` documenta a proveniência do resumo (de onde o contexto veio).

O algoritmo que gera o resumo funciona em três passos. Primeiro, encontra o ancestral comum mais profundo entre o leaf de origem e o leaf de destino: percorre o path do leaf de destino da folha para a raiz, construindo um conjunto de IDs; depois percorre o path do leaf de origem da folha para a raiz e retorna o primeiro ID que aparece no conjunto — esse é o nó mais fundo compartilhado por ambos os paths. Segundo, coleta todas as entradas entre o leaf de origem e o ancestral comum (exclusive), em ordem cronológica, truncando tool results a 2.000 caracteres para manter o pedido de resumo dentro de um budget de tokens. Notavelmente, esse processo **não para em `CompactionEntry`s** — elas são incluídas na coleção, o que significa que o resumo do branch tem acesso a todo o trabalho feito ali, incluindo resumos internos de compactação. Terceiro, envia a coleção ao LLM com um prompt de sumarização e registra o resultado como o `summary`.

Quando o harness reconstrói o contexto para uma chamada ao LLM a partir do novo leaf, ele inclui a `BranchSummaryEntry` como uma mensagem de contexto antes das mensagens regulares do path atual. O efeito é que o modelo "sabe" o que aconteceu no branch abandonado sem que aquelas mensagens consumam tokens do contexto ativo. Isso é análogo ao papel do `summary` na `CompactionEntry` — ambos substituem mensagens históricas por um resumo condensado — mas a `BranchSummaryEntry` cruza paths da árvore (contexto lateral), enquanto a `CompactionEntry` opera linearmente dentro do mesmo path (contexto profundo).

A geração da `BranchSummaryEntry` é opcional: ao navegar com `/tree`, o usuário pode escolher (1) não gerar resumo, (2) resumir com o prompt padrão, ou (3) resumir com instruções customizadas que guiam o foco do resumo. A opção 3 é útil quando o branch abandonado tinha muito ruído e apenas uma parte específica do trabalho é relevante para o path de destino.

Para persistência externa, a implicação é direta. A `BranchSummaryEntry` é um nó da árvore com `parentId` próprio — removê-la do arquivo quebra a cadeia de `parentId` no path que a inclui, e o harness não conseguirá reconstruir a árvore corretamente. Mais sutil: mesmo que a cadeia de IDs não quebre (se o storage simplesmente omite a linha sem apagar referências), o harness perderá o resumo de contexto. A próxima chamada ao LLM a partir daquele leaf não encontrará a `BranchSummaryEntry` na path e o modelo operará sem o contexto do branch abandonado — o que pode parecer comportamento correto até o LLM tomar uma decisão que contradiz trabalho feito em outro branch. Esse tipo de falha é silencioso e difícil de diagnosticar sem inspecionar o arquivo JSONL diretamente. O `LabelEntry` — próximo conceito — tem uma mecânica de inserção mais simples mas compartilha o mesmo princípio: qualquer entrada que altera a semântica da árvore não pode ser filtrada ingenuamente ao serializar.

**Fontes utilizadas:**

- [Session Format — pi.dev/docs/latest/session-format](https://pi.dev/docs/latest/session-format)
- [Session Tree Navigation — pi.dev/docs/latest/tree](https://pi.dev/docs/latest/tree)
- [Compaction and Context Management — DeepWiki agentic-dev-io/pi-agent](https://deepwiki.com/agentic-dev-io/pi-agent/2.5-compaction-and-context-management)
- [pi-mono/packages/coding-agent/src/core/compaction/branch-summarization.ts — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/src/core/compaction/branch-summarization.ts)
- [Managing Context Windows with pi /tree — StackToHeap](https://stacktoheap.com/blog/2026/02/26/pi-tree-context-window-management/)

## 3. LabelEntry — estrutura do tipo (`targetId`, `label`), como criar e apagar bookmarks (Shift+L no TUI; `label: undefined` remove), e uso programático como marcador de ponto de retomada sem criar novos nós de conversa

Enquanto a `CompactionEntry` e a `BranchSummaryEntry` têm papel direto na reconstrução do contexto LLM, a `LabelEntry` serve a um propósito diferente: ela é um bookmark — uma anotação nomeada sobre um nó existente da árvore, sem alterar a estrutura de conversa, sem criar nós filho de mensagem, e sem participar do fluxo de tokens enviados ao modelo.

A entrada tem `"type": "label"` e os seguintes campos além de `id`, `parentId` e `timestamp`:

| Campo | Tipo | Significado |
|---|---|---|
| `targetId` | `string` | ID do nó que está sendo bookmarkado — o ponto de interesse na árvore |
| `label` | `string \| undefined` | Nome do bookmark; quando `undefined`, o bookmark do `targetId` é removido |

O `parentId` da `LabelEntry` posiciona a entrada na árvore como qualquer outra — ela é filha do nó corrente no momento em que o bookmark é criado. O `targetId`, por sua vez, é uma referência cruzada: aponta para o nó que o usuário quer marcar, que pode ser qualquer entrada existente no arquivo, incluindo nós em outros paths da árvore. Isso significa que label e alvo não precisam ser pai/filho — um bookmark pode "apontar para trás" para um nó de dois branches distintos do trunk.

No TUI, o fluxo é: o usuário abre `/tree`, navega até o nó de interesse, e pressiona Shift+L. O harness exibe um prompt para digitar o nome do bookmark e escreve a `LabelEntry` no arquivo. Labels aparecem como marcadores visuais na tela do `/tree` ao lado do nó alvo, o que torna a navegação em sessões longas muito mais rápida — em vez de percorrer dezenas de nós para achar "aquele ponto onde a análise começou", o usuário vê o bookmark nomeado diretamente. Shift+T alterna a exibição de timestamps nos labels.

Para remover um bookmark, o usuário executa o mesmo Shift+L sobre um nó já labelado — o harness detecta a existência de um label e escreve uma nova `LabelEntry` com `"label": undefined` (ou omite o campo). A lógica de leitura trata isso como um "apagamento": ao encontrar uma `LabelEntry` com `label` ausente ou `undefined` para um `targetId`, descarta o bookmark anterior. O arquivo preserva o histórico das operações (append-only), mas o estado efetivo de labels para um `targetId` é determinado pela entrada mais recente que o referencia.

Via SDK, a `SessionManager` expõe dois métodos:

```typescript
sm.appendLabelChange(targetId: string, label: string | undefined): void
sm.getLabel(targetId: string): string | undefined
```

`appendLabelChange` grava uma nova `LabelEntry` no arquivo — tanto para criar quanto para remover (passando `undefined`). `getLabel` varre o arquivo e retorna o estado atual do label para aquele `targetId`. O padrão é consistente com o restante da API da `SessionManager`: toda escrita é append, toda leitura é derivada do estado mais recente das entradas existentes.

O uso programático mais relevante para a POC é marcar automaticamente nós de interesse durante a execução do agente — por exemplo, o harness de persistência pode escrever uma `LabelEntry` logo após salvar um snapshot externo, com um label como `"snapshotted"`, para saber exatamente a partir de qual nó a próxima janela de contexto deve ser reconstituída. Isso evita a necessidade de um índice externo separado — o próprio arquivo JSONL carrega o marcador.

Para persistência externa (capítulos 8 e 9), a `LabelEntry` tem uma implicação menos crítica que a `CompactionEntry` ou a `BranchSummaryEntry`: ela não afeta a reconstrução do contexto LLM diretamente, porque o harness não injeta o texto do label nas mensagens enviadas ao modelo. Mas ela afeta a integridade da árvore: uma `LabelEntry` tem `parentId` como qualquer outra entrada, e o `targetId` é uma referência cruzada que precisa apontar para um nó presente no arquivo. Se o storage externo filtrar `LabelEntry`s ao serializar, nenhum nó é perdido da árvore de conversa — mas o usuário perde todos os bookmarks ao recarregar a sessão. Para sessões de desenvolvimento interativo em que o usuário marcou checkpoints relevantes, isso pode ser suficientemente inconveniente para justificar preservar as entradas. Para uma POC headless automatizada, onde labels são gerados programaticamente como metadados de controle (ex: `"snapshotted"`, `"checkpoint-before-deploy"`), filtrar a entrada quebra a lógica do próprio harness de persistência. A decisão de preservar ou descartar `LabelEntry`s ao serializar depende portanto do papel que labels exercem no sistema — o próximo conceito, `custom` vs `custom_message`, completa o mapa dos tipos especiais com a distinção entre estado interno de extension e conteúdo injetado no contexto LLM.

**Fontes utilizadas:**

- [Session Format — pi.dev/docs/latest/session-format](https://pi.dev/docs/latest/session-format)
- [pi-mono README — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [pi-mono SDK docs — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [Keybindings — pi-mono/packages/coding-agent/docs/keybindings.md](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/keybindings.md)

## 4. `custom` vs `custom_message` — distinção entre estado interno de extension que não entra no contexto LLM (`custom`) e conteúdo injetado por extension que entra (`custom_message`), campos `customType`, `data`, `content` e `display`, e a implicação prática ao filtrar o arquivo para reconstruir o contexto

Os três tipos especiais anteriores — `CompactionEntry`, `BranchSummaryEntry` e `LabelEntry` — têm em comum o fato de serem gerados pelo próprio harness ou pelo usuário via TUI. Os dois últimos tipos especiais, `custom` e `custom_message`, têm origem diferente: são emitidos exclusivamente por extensions, e a distinção entre eles mapeia diretamente para a pergunta "este dado precisa chegar ao LLM?" — o que torna a escolha entre os dois uma decisão de design, não de conveniência.

Uma extension usa `pi.appendEntry(customType, data)` para gravar um `custom` entry. A entrada tem `"type": "custom"` e carrega estado arbitrário no campo `data` (um objeto JSON), identificado pelo campo `customType` (uma string que a própria extension define — ex: `"todo-list"`, `"connection-state"`). O harness **não inclui** esse dado no array de mensagens enviado ao LLM em nenhuma circunstância. Ele existe exclusivamente para que a extension reconstrua seu estado ao recarregar a sessão: no evento `session_start`, a extension itera as entradas do arquivo filtrando por `type === "custom" && customType === "minha-extension"` e restaura as estruturas internas a partir de `entry.data`. Em sessões longas com fork/branch, pode haver múltiplas entradas `custom` do mesmo `customType` em paths diferentes da árvore; a extension precisa resolver qual estado está ativo lendo o path correto — o mesmo princípio de `pathFromRoot` que governa `CompactionEntry` e `BranchSummaryEntry` se aplica aqui.

Uma extension usa `pi.sendMessage({ customType, content, display, details }, options)` para gravar um `custom_message` entry. A diferença estrutural é direta:

| Campo | `custom` | `custom_message` |
|---|---|---|
| `type` | `"custom"` | `"custom_message"` |
| `customType` | string — identifica a extension | string — identifica a extension |
| `data` | objeto JSON — estado interno | — (não existe) |
| `content` | — (não existe) | string ou array de `TextContent`/`ImageContent` — **enviado ao LLM** |
| `display` | — (não existe) | boolean — controla exibição no TUI |
| `details` | — (não existe) | objeto opcional — metadados de renderização, **não enviado ao LLM** |

O campo `content` de um `custom_message` entra no contexto LLM exatamente como entraria uma mensagem de usuário ou assistente — com a diferença que o `role` é `"custom"` em vez de `"user"` ou `"assistant"`, e o harness o identifica pelo `customType` para fins de renderização. O campo `details`, por contraste, é metadado para o TUI ou para a própria extension — nunca aparece no array de mensagens enviado ao modelo. O campo `display: true` faz a entrada aparecer no TUI com estilo distinto (marcada como mensagem de extension); `display: false` a torna invisível na interface mas não afeta a participação no contexto LLM.

O mecanismo de `sendMessage` tem modos de entrega que controlam o timing: `"steer"` (padrão) enfileira a mensagem após o batch de tool calls corrente e antes da próxima chamada ao LLM; `"followUp"` aguarda a conclusão de todos os tools do turno; `"nextTurn"` agenda para o próximo prompt do usuário. Esses modos afetam quando a entrada `custom_message` aparece na sequência de `parentId` no arquivo — a posição na árvore é a do momento em que a entrada é efetivamente gravada, não quando foi enfileirada.

Para a reconstrução de contexto em persistência externa (capítulos 8 e 9), a distinção tem implicações práticas diretas. Ao serializar o arquivo para enviar ao modelo em uma chamada reconstituída:

- Entradas `custom` podem ser **ignoradas com segurança** no array de mensagens — elas nunca participam do contexto LLM. Mas elas **não podem ser omitidas do arquivo serializado**: são nós da árvore com `parentId` próprios; removê-las quebra a cadeia de IDs e impede a extension de reconstruir seu estado no próximo `session_start`.
- Entradas `custom_message` precisam ser **incluídas no array de mensagens** enviado ao LLM, com `content` mapeado para o role adequado. Omiti-las significa que o modelo perderá contexto que a extension havia injetado — o que pode fazer o agente tomar decisões que ignoram informação que ele "deveria ter visto". O campo `details` pode ser descartado ao construir o array de mensagens (nunca vai ao LLM), mas deve ser preservado no arquivo serializado para que a extension consiga acessá-lo no evento `session_start`.

A assimetria de tratamento — `custom` preservado no arquivo mas invisível ao LLM, `custom_message` preservado no arquivo **e** visível ao LLM — é o contrato fundamental. Qualquer lógica de filtragem que trate os dois tipos da mesma forma (ou que ignore ambos) está errada: ou desperdiça contexto (omitindo `custom_message`) ou polui o contexto com estado interno (incluindo `data` de `custom`).

Na POC, a probabilidade de encontrar `custom` e `custom_message` no arquivo de sessão depende de quais extensions estão habilitadas. A maioria das POCs headless simples não habilita extensions além das embutidas — e as extensions embutidas do pi.dev (como a de compactação automática) usam `CompactionEntry`, não `custom`. Se a POC não usa extensions customizadas, `custom` e `custom_message` podem não aparecer no arquivo. Mas o harness de persistência precisa estar preparado para os dois — a lógica de reconstrução de contexto que os ignora completamente quebrará silenciosamente no momento em que uma extension for adicionada. Os subcapítulos `05-append-only-como-contrato-de-persistencia-efs-vs-s3` e `06-operacoes-proibidas-e-restricoes-de-integridade` aprofundam as implicações de integridade que todos os tipos especiais — incluindo estes dois — impõem sobre o storage externo.

**Fontes utilizadas:**

- [Session Format — pi.dev/docs/latest/session-format](https://pi.dev/docs/latest/session-format)
- [Extensions — pi.dev/docs/latest/extensions](https://pi.dev/docs/latest/extensions)
- [pi-mono/packages/coding-agent/docs/extensions.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)

> _Pendente: 4 / 4 conceitos preenchidos._

---

**Próximo subcapítulo** → [Fork e Branch na Prática — Criar e Navegar](../04-fork-e-branch-na-pratica-criar-e-navegar/CONTENT.md)
