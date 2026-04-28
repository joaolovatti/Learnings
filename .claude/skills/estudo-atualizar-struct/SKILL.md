---
name: estudo-atualizar-struct
description: Reconstroi o `STRUCT.md` na raiz de um livro de estudo varrendo seus capitulos, subcapitulos e conceitos no disco e renderizando uma arvore de diretorios com descricao de 1 linha em cada nivel. Use sempre que qualquer skill do metodo de estudo materializar ou modificar a estrutura de um livro — depois de criar o livro em `estudo-listar-dominios`, depois de materializar capitulos em `estudo-listar-capitulos`, subcapitulos em `estudo-listar-subcapitulos`, esqueletos de conceitos em `estudo-listar-conceitos` ou explicacoes preenchidas em `estudo-explicar-conceito`. Tambem dispare quando o usuario disser explicitamente "atualiza o STRUCT", "reconstroi o indice do livro", "regenera a estrutura", ou pedir um panorama rapido da organizacao do livro. E uma skill utilitaria reutilizavel composta pelas demais skills do metodo de estudo.
---

# estudo-atualizar-struct

Skill utilitaria que reconstroi `STRUCT.md` na raiz de um livro de estudo. **Idempotente** — pode rodar quantas vezes quiser, sempre produz o mesmo resultado para o mesmo estado em disco. Pensada para ser **reutilizada** pelas demais skills do metodo (`estudo-listar-dominios`, `estudo-listar-capitulos`, `estudo-listar-subcapitulos`, `estudo-listar-conceitos`, `estudo-explicar-conceito`), e tambem invocavel diretamente pelo usuario.

## Quando usar

- Outra skill do metodo de estudo acabou de materializar ou alterar artefatos no livro — invoque esta no fim do fluxo para refrescar o indice.
- O usuario pediu explicitamente para atualizar/reconstruir o `STRUCT.md`.
- O usuario quer um panorama rapido da organizacao do livro — rode a skill e depois leia o `STRUCT.md`.

## O que `STRUCT.md` e

Um unico arquivo na raiz do livro (`<book-dir>/STRUCT.md`) com uma arvore visual em bloco de codigo. Exemplo:

```
godot-para-um-rpg-2d-online-estilo-pokemon/ — Godot para um RPG 2D Online Estilo Pokémon
├── 01-introducao/ — briefing estrategico da escolha de engine
│   ├── 01-o-recorte-do-jogo-alvo/ — MVP Pokemon Fire Red-like
│   └── 05-o-mapa-do-livro/ — como os 4 blocos se encadeiam
│       ├── 01-os-4-blocos/ — bloco 1 fundamentos, bloco 2 sistemas...
│       └── 02-a-logica-das-dependencias/ — por que cada bloco precisa do anterior
└── 02-nodes-scenes-e-a-arvore-de-cena/ — paradigma de cena
```

Cada linha = um diretorio do livro + descricao de 1 linha. Capitulos, subcapitulos e conceitos formam tres niveis hierarquicos.

As descricoes saem das listagens curadas que cada skill do metodo ja escreve nos pais:

- **Capitulos** → secao `## Capítulos` em `<book-dir>/INTRODUCTION.md`
- **Subcapitulos** → secao `## Subcapítulos` em `<book-dir>/<NN-cap>/CONTENT.md`
- **Conceitos** → secao `## Conceitos` em `<book-dir>/<NN-cap>/<MM-sub>/CONTENT.md`

Quando uma listagem ainda nao existe (ex: livro recem-materializado, sem capitulos), o item aparece com fallback no H1 do proprio CONTENT.md/INTRODUCTION.md. Isso permite rodar a skill **a qualquer momento**, mesmo com o livro semi-materializado.

## Entrada

Caminho do diretorio do livro. Aceita relativo (resolve a partir do cwd) ou absoluto. Aceita `/` ou `\` como separador. Exemplos:

- `godot-para-um-rpg-2d-online-estilo-pokemon`
- `sql-para-analise-de-dados`
- `C:/Users/.../godot-para-um-rpg-2d-online-estilo-pokemon`

Se faltar, peca uma vez: _"Qual e o diretorio do livro?"_ Valide que o diretorio existe e contem `INTRODUCTION.md` (o script aborta se nao tiver).

## Como executar

Rode o script `scripts/build_struct.py` via Bash:

```bash
python "<REPO_ROOT>/.claude/skills/estudo-atualizar-struct/scripts/build_struct.py" "<book-dir>"
```

**Use path absoluto para o script** — esta skill e composta por outras skills do metodo, que podem rodar em background com cwd diferente do esperado. Path absoluto elimina essa dependencia implicita (mesma logica que ja se aplica a `gerar-imagem`). O argumento `<book-dir>` pode ser relativo (resolve a partir do cwd) ou absoluto.

Exemplo concreto no ambiente do usuario:

```bash
python "C:/Users/joaop/Desktop/development/teste/aprendizado/.claude/skills/estudo-atualizar-struct/scripts/build_struct.py" \
  "C:/Users/joaop/Desktop/development/teste/aprendizado/godot-para-um-rpg-2d-online-estilo-pokemon"
```

O script:

- Le `<book-dir>/INTRODUCTION.md` para obter o titulo do livro (H1) e a listagem `## Capítulos`.
- Varre os subdiretorios `NN-slug/` (capitulos), depois `NN-slug/MM-slug/` (subcapitulos), depois `NN-slug/MM-slug/KK-slug/` (conceitos), em qualquer profundidade que siga o padrao `dois-digitos-hifen-slug`.
- Para cada nivel, resolve a descricao na listagem do pai; se ausente, cai para o H1 do `CONTENT.md` proprio.
- Reescreve `<book-dir>/STRUCT.md` em UTF-8 (idempotente — substitui o anterior).
- Imprime o caminho absoluto do `STRUCT.md` no stdout.

## Saida ao usuario

Apos executar, informe em uma linha:

> _STRUCT.md atualizado em `<caminho>`._

Quando esta skill foi invocada por outra skill como passo final do fluxo, basta um menciao breve no encerramento da skill consumidora — nao precisa duplicar a linha acima.

## Composicao com as skills do metodo

As skills do metodo chamam esta no fim de seus fluxos:

| Skill consumidora           | Quando chama                                                |
|-----------------------------|-------------------------------------------------------------|
| `estudo-listar-dominios`    | Apos criar `INTRODUCTION.md` do livro novo                  |
| `estudo-listar-capitulos`   | Apos materializar capitulos e atualizar `INTRODUCTION.md`   |
| `estudo-listar-subcapitulos`| Apos materializar subcapitulos e atualizar CONTENT do cap.  |
| `estudo-listar-conceitos`   | Apos materializar diretorios de conceitos                   |
| `estudo-explicar-conceito`  | Apos preencher o CONTENT.md do conceito                     |

E todas as skills do metodo **leem** o `STRUCT.md` no comeco de seus fluxos como contexto rapido — ele evita ter que abrir 15 CONTENT.md so para entender onde algo se encaixa no livro.

## O que evitar

- **Nao** edite o `STRUCT.md` a mao — ele e regenerado a partir do disco. Edicoes manuais somem na proxima execucao.
- **Nao** invente descricoes — o script so le o que ja existe no `INTRODUCTION.md`/`CONTENT.md` do pai (ou no H1 do filho como fallback).
- **Nao** rode com `<book-dir>` que nao tem `INTRODUCTION.md` — o script aborta com erro claro.
- **Nao** tente embutir a logica Python no SKILL.md — o codigo vive em `scripts/build_struct.py`, conforme a convencao de organizacao de scripts.
- **Nao** chame esta skill em loop dentro de outra skill — basta uma chamada no final do fluxo, depois que toda a materializacao terminou.
