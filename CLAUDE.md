# CLAUDE.md

Instruções do repositório para o método de estudo estruturado. Priorize esta regra sobre comportamentos padrão.

## Regra de organização: README.md como índice de livros

### Contexto

A raiz do repositório contém **um diretório por livro** (ex: `godot-para-um-rpg-2d-online-estilo-pokemon/`). Cada livro tem, no seu nível raiz, uma `cover.png` (capa didática), um `INTRODUCTION.md` (apresentação completa do livro) e um `STRUCT.md` (índice hierárquico de capítulos/subcapítulos/conceitos). O `README.md` da raiz é o **ponto de entrada humano** do repositório — quem abre o repositório no GitHub ou no navegador de arquivos tem que conseguir, em segundos, ver quais livros existem e entrar no que quiser.

### Regra

O `README.md` da raiz **deve** ser um índice dos livros do repositório, nesta forma:

1. **Cabeçalho curto** com o nome do repositório (`# learnings`) e um parágrafo (2-3 linhas) explicando o método: estudo estruturado em livros, cada livro subdividido em capítulos → subcapítulos → conceitos, com cover, introdução e conceitos completos.
2. **Seção `## Livros`** listando cada livro como uma sub-seção `### [Título do livro](<slug>/INTRODUCTION.md)` — o título é um link direto para o `INTRODUCTION.md` do livro.
3. Logo abaixo do título, **a imagem da capa** via `![capa](<slug>/cover.png)`.
4. Logo abaixo da capa, **um parágrafo curto** (2-4 linhas) destilando o que é o livro — derivado das seções "Sobre este livro" + "Estrutura" + "Objetivo" do `INTRODUCTION.md`, mas reescrito em prosa compacta para funcionar como gancho de leitura. Não colar literalmente o `INTRODUCTION.md`.
5. Ordem: pela ordem cronológica/lógica do método (livros fundamentais primeiro). Quando não houver ordem óbvia, manter alfabética por slug.

### Quando atualizar

- **Ao criar um novo livro** (novo diretório na raiz com `INTRODUCTION.md` + `cover.png`): adicionar a sub-seção correspondente no `README.md`.
- **Ao renomear um livro ou trocar a capa**: refletir no `README.md`.
- **Ao reescrever o `INTRODUCTION.md`** de forma que mude o escopo/objetivo do livro: revisar o parágrafo-gancho no `README.md` para continuar fiel.

### Exemplo da forma esperada

```markdown
## Livros

### [Godot para um RPG 2D Online Estilo Pokémon](godot-para-um-rpg-2d-online-estilo-pokemon/INTRODUCTION.md)

![capa](godot-para-um-rpg-2d-online-estilo-pokemon/cover.png)

Travessia de um engenheiro de software sênior — sem vivência prévia com engines — até ter um RPG 2D top-down online no molde de Pokémon Fire Red rodando em Godot 4. Cobre fundamentos (nodes, scenes, tilemaps, signals), os sistemas clássicos de um Pokémon-like (movimento em grid, NPCs, combate por turnos, inventário), a camada online (cliente-servidor, autoridade, sincronização, persistência) e a integração com pipeline de assets gerados por AI.
```

### Por que essa forma

- **Capa + título clicável** é o contrato visual mínimo: dá reconhecimento imediato e leva ao `INTRODUCTION.md` em um clique.
- **Parágrafo curto (não o `INTRODUCTION.md` inteiro)** preserva o README como índice navegável — quem quer o detalhe vai para o `INTRODUCTION.md`; quem está escolhendo o que ler fica no README.
- **Sem duplicar capítulos/STRUCT**: o índice detalhado vive em `STRUCT.md` de cada livro; o README é só a porta de entrada.

### Exemplo prático

**Usuário:** "Complete todos os conceitos de `godot-para-um-rpg-2d-online-estilo-pokemon/01-introducao/01-o-recorte-do-jogo-alvo/`"

**Fluxo:**

1. Abrir `01-o-recorte-do-jogo-alvo/CONCEPTS.md`. Ler `## Roteiro` → N=7 conceitos. Contar seções `## 1.` … `## K.` já preenchidas. Suponha K=1 (só o conceito 1 já está escrito). Pendentes: 2 a 7.
2. Disparar agente `explicador-de-conceito` com prompt `Subcapítulo: <caminho absoluto>`. O agente lê `CONCEPTS.md`, vê K=1, processa conceito 2, anexa a seção `## 2. ...`, atualiza `## Fontes utilizadas` e `Pendente: 2 / 7`.
3. Aguardar conclusão. Disparar o próximo agente com o mesmo prompt. Ele lê o `CONCEPTS.md` agora com K=2, processa conceito 3.
4. Repetir até o conceito 7. Quando for o conceito 7 (último), o próprio agente roda `compute_next_link.py --apply` para anexar o link de navegação.
5. Invocar a skill `/estudo-atualizar-struct <book-dir>` uma única vez para o livro.
6. Encerrar:
   > _Conceitos anexados: 6 (2/7 → 7/7)._
   > _Arquivo: `./.../01-o-recorte-do-jogo-alvo/CONCEPTS.md`._
   > _`STRUCT.md` reconstruído. Boa leitura._
