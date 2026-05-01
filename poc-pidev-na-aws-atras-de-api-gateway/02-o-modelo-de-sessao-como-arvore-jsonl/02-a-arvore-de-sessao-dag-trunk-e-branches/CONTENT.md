# A Árvore de Sessão — DAG, Trunk e Branches

![capa](cover.png)

## Sobre este subcapítulo

Uma vez compreendido o esquema de cada linha, o próximo passo é entender o que o conjunto de linhas forma: não uma lista cronológica linear, mas um grafo dirigido acíclico (DAG). O campo `parentId` transforma o arquivo JSONL num grafo onde cada nó aponta para seu predecessor — e onde múltiplos nós podem apontar para o mesmo `parentId`, criando bifurcações. Este subcapítulo constrói a intuição geométrica da estrutura: o que é o trunk (o caminho principal desde o início até a posição ativa), o que é um branch (um caminho alternativo que divergiu a partir de um nó compartilhado), e como múltiplos branches coexistem no mesmo arquivo físico sem se interferirem.

Entender essa geometria é o que diferencia o engenheiro que trata a sessão pi.dev como um simples log de chat daquele que compreende por que persistir, versionar ou replicar esse arquivo exige cuidado adicional.

## Estrutura

O subcapítulo cobre: (1) **parentId como ponteiro de grafo** — como a cadeia de referências de cada linha até `parentId: null` forma um caminho único da folha até a raiz, e o que acontece quando dois nós compartilham o mesmo `parentId`; (2) **o conceito de leaf (folha ativa)** — o nó sem filhos no caminho atual é a posição presente da sessão; mover-se na árvore significa trocar de leaf; (3) **trunk vs branch** — trunk é o caminho canônico da sessão; um branch é qualquer caminho alternativo que divergiu de um nó do trunk; os dois coexistem no mesmo arquivo; (4) **coexistência no arquivo físico** — por que o arquivo JSONL não segmenta branches em blocos separados (as linhas de diferentes branches estão intercaladas no arquivo em ordem de timestamp de escrita), e como o `SessionManager` usa o índice in-memory de id → entrada para reconstruir qualquer caminho.

## Objetivo

Ao terminar este subcapítulo, o leitor conseguirá descrever a estrutura de árvore de uma sessão pi.dev em termos de nós, arestas e folha ativa, distinguir trunk de branch com precisão, e explicar por que o arquivo JSONL físico não está organizado em blocos separados por branch. Esse modelo mental é o pré-requisito direto para entender o que acontece no arquivo durante um fork ou uma operação de branch — tema do subcapítulo 04.

## Conceitos

Roteiro completo em [CONCEPTS.md](CONCEPTS.md).

1. O DAG formado por `parentId` — como a cadeia de referências `id → parentId` de cada linha até `parentId: null` forma um grafo dirigido acíclico, e por que essa estrutura é um DAG e não uma árvore binária convencional nem um log linear
2. O nó raiz e o `SessionHeader` como âncora do grafo — por que a primeira entrada com `parentId: null` é o único nó sem predecessores, como ela ancora toda a estrutura e o que acontece se ela for perdida ou corrompida
3. A leaf (folha ativa) como posição presente da sessão — o que define uma leaf (nó sem filhos no caminho atual), como o `SessionManager` a rastreia, e por que "mover-se na árvore" significa exatamente trocar a leaf ativa
4. Trunk — o caminho canônico da raiz à leaf ativa — definição precisa de trunk como o conjunto ordenado de entradas no caminho da raiz até a posição atual, e como `buildSessionContext()` percorre esse caminho de volta (leaf → root) para montar o contexto enviado ao LLM
5. Branch — divergência a partir de um nó compartilhado — o que torna um caminho um branch (dois ou mais filhos do mesmo `parentId`), a distinção entre trunk e branch como relativa à leaf ativa (não absoluta ao arquivo), e o que acontece com o branch abandonado quando a leaf muda
6. Coexistência de branches no arquivo físico e o índice in-memory do `SessionManager` — por que as linhas de diferentes branches estão intercaladas no arquivo em ordem de timestamp de escrita (não segregadas por bloco), como o `SessionManager` constrói o mapa `id → entrada` ao ler o arquivo, e como `getBranch(leafId)` isola um caminho lógico completo dentro do arquivo compartilhado

## Fontes utilizadas

- [Pi sessions — pi.dev/docs/latest](https://pi.dev/docs/latest/sessions)
- [Pi session-format — pi.dev/docs/latest](https://pi.dev/docs/latest/session-format)
- [Session Management and Persistence — DeepWiki (agentic-dev-io/pi-agent)](https://deepwiki.com/agentic-dev-io/pi-agent/2.4-session-management-and-persistence)
- [Managing Context Windows with pi /tree — StackToHeap](https://stacktoheap.com/blog/2026/02/26/pi-tree-context-window-management/)
- [Pi Coding Agent overview — hochej.github.io](https://hochej.github.io/pi-mono/coding-agent/overview/)
