---
name: estudo-listar-conceitos
description: Gera uma lista de conceitos atômicos a partir do **caminho de um subcapítulo já materializado** pela skill `estudo-listar-subcapitulos` (ex: `godot-para-um-rpg-2d-online-estilo-pokemon/01-introducao/05-o-mapa-do-livro`) e materializa um único arquivo `CONCEPTS.md` no diretório do subcapítulo, contendo o esqueleto numerado dos conceitos a serem explicados em sequência. Atualiza também o `CONTENT.md` do subcapítulo com a seção `## Conceitos` (lista numerada, sem subdiretórios). Use quando o usuário apresentar o **caminho de um subcapítulo** (livro/capítulo/subcapítulo) e pedir "liste os conceitos", "quebra esse subcapítulo em conceitos", "destrincha esse subcapítulo", "materializa os conceitos", "quais ideias eu preciso aprender aqui", "me mostra as unidades de conhecimento". Antes de gerar, a skill lê o `STRUCT.md`, o `INTRODUCTION.md` do livro, o `CONTENT.md` do capítulo e o `CONTENT.md` do subcapítulo como contexto obrigatório, e pesquisa fontes reais na internet para identificar as ideias atômicas consolidadas no campo. Esta é a **quarta etapa** do método de estudo estruturado.
---

# estudo-listar-conceitos

Quarta etapa do método de estudo estruturado. Recebe o **caminho de um subcapítulo já materializado** (pela skill `estudo-listar-subcapitulos`), desdobra-o em conceitos atômicos pedagogicamente ordenados e materializa **um único arquivo `CONCEPTS.md` no próprio diretório do subcapítulo**, contendo o esqueleto numerado dos conceitos. O texto explicativo de cada conceito é preenchido depois, sequencialmente, pela skill `estudo-explicar-conceito` — que **incrementa o mesmo `CONCEPTS.md`** a cada iteração, transformando-o numa aula contínua.

Por fim, atualiza o `CONTENT.md` do subcapítulo com a lista numerada de conceitos (`## Conceitos`).

## Quando usar

O usuário já tem um subcapítulo materializado (subdiretório do capítulo com `cover.png` + `CONTENT.md`) e quer a próxima camada: o subcapítulo destrinchado em **conceitos atômicos** que serão ensinados em sequência num único arquivo. A saída alimenta a skill `estudo-explicar-conceito`.

## Entrada

O **caminho do diretório do subcapítulo** (relativo ao diretório de trabalho atual), no formato `<book-dir>/<NN-cap>/<MM-sub>/`. Exemplos:

- `godot-para-um-rpg-2d-online-estilo-pokemon/01-introducao/05-o-mapa-do-livro`
- `godot-para-um-rpg-2d-online-estilo-pokemon/09-npcs-dialogos-e-eventos-de-mundo/02-sistema-de-dialogo`
- `sql-para-analise-de-dados/05-agregacoes-e-group-by/01-a-clausula-group-by`

Aceita `/` ou `\` como separador (Windows/Unix). Aceita ou não barra final.

Esse caminho carrega implicitamente os três níveis obrigatórios de contexto: o **livro-pai** (`<book-dir>/`), o **capítulo** (`<NN-cap>/`) e o **subcapítulo** (`<MM-sub>/`).

Se o usuário não trouxer o caminho, pergunte uma única vez: _"Qual é o caminho do subcapítulo (ex: `godot-para-um-rpg-2d-online-estilo-pokemon/01-introducao/05-o-mapa-do-livro`) que você quer destrinchar em conceitos?"_

Valide que o caminho existe e contém `CONTENT.md`, que o capítulo-pai contém `CONTENT.md`, e que o livro-pai contém `INTRODUCTION.md`. Se algo falhar, avise e interrompa — a skill depende dos artefatos das três etapas anteriores.

## Contexto obrigatório (quatro fontes)

Antes de qualquer pesquisa ou geração, leia **as quatro fontes na ordem abaixo**. Elas calibram juntas o recorte e a granularidade dos conceitos.

### 1. `<book-dir>/STRUCT.md` — o mapa estrutural do livro (referência primária para a criação)

Carrega o mapa visual completo do livro: todos os capítulos e subcapítulos já materializados, com descrição de 1 linha em cada um. Esta é a **árvore de arquivos canônica** do livro — o que existe em disco e o que está sendo construído sobre ela. Use-o em duas frentes:

1. **Como localizador rápido**: você se posiciona no livro inteiro sem abrir 15 CONTENT.md.
2. **Como referência estrutural para a sua criação** (uso central nesta skill): a árvore deixa visível **como o livro está organizando o conhecimento**. Antes de listar os conceitos, leia os ramos vizinhos do `STRUCT.md` e confira:
   - **Que tipo de ideia vira nó atômico neste livro?** Os nomes dos conceitos vizinhos (em `## Conceitos` dos `CONTENT.md` de subcapítulos vizinhos) revelam o nível de granularidade que o livro adota para o leitor descrito no `INTRODUCTION.md`. Espelhe esse nível (não desça a sintaxe pura se vizinhos ficam em "ideias mecanicamente ensináveis", nem suba a meta-conceitos vagos se vizinhos ficam em mecânica concreta). **Granularidade — sim**; **número de conceitos — não**: nunca ajuste o tamanho da sua lista para parecer com o vizinho. Se o subcapítulo legitimamente exige 12 e o vizinho tem 5, fique nos 12.
   - **O conceito proposto está coberto em outro subcapítulo?** A árvore expõe nomes de subcapítulos vizinhos. Se um conceito candidato é o tema central de outro subcapítulo já listado (ou previsto pelo `## Estrutura` do capítulo), descarte-o aqui — o livro não duplica território.
   - **A trilha de pré-requisitos lê coerente?** Subcapítulos vizinhos de índice menor (anteriores na sequência) já cobriram conceitos que o seu roteiro pode assumir como bagagem. Conceito que viraria "1 — definição de signal" pode ser cortado se um subcapítulo anterior já o materializou.

Se `STRUCT.md` ainda não existe (livro recém-criado, este é um dos primeiros subcapítulos a ganhar conceitos), siga em frente sem ele — a régua de granularidade volta a ser apenas o `INTRODUCTION.md` e o `CONTENT.md` do subcapítulo.

### 2. `<book-dir>/INTRODUCTION.md` — o contrato do livro

Carrega o quadro maior:

- **Título completo do livro** e seu recorte ("para Análise de Dados", "para um RPG 2D Online Estilo Pokémon").
- **Sobre este livro**, **Estrutura**, **Objetivo** — a promessa global que o subcapítulo está atendendo.
- **Sobre o leitor** — nível, experiências adjacentes, objetivo declarado. Calibra a profundidade e a linguagem dos conceitos.
- **Capítulos** — a lista completa.
- **Fontes utilizadas** — referências do recorte do livro inteiro.

### 3. `<book-dir>/<NN-cap>/CONTENT.md` — o contrato do capítulo

Carrega o nível intermediário:

- **Sobre este capítulo** — recorte exato do capítulo dentro do livro.
- **Estrutura** — os blocos do capítulo, que viraram os subcapítulos atuais.
- **Subcapítulos** — listagem dos subcapítulos irmãos. Use para entender **o que é território deste subcapítulo e o que pertence aos vizinhos**: se um conceito candidato é, na verdade, o tema central de outro subcapítulo do mesmo capítulo, ele não cabe aqui.
- **Objetivo** — a capacidade que o leitor terá ao fim do capítulo. O conjunto de conceitos do subcapítulo contribui para esse objetivo.
- **Fontes utilizadas** — base inicial de fontes.

### 4. `<book-dir>/<NN-cap>/<MM-sub>/CONTENT.md` — o contrato do subcapítulo

Carrega as restrições mais finas:

- **Título do subcapítulo** (H1).
- **Sobre este subcapítulo** — a proposta exata do recorte.
- **Estrutura** — esta seção é frequentemente uma **prévia explícita dos conceitos** (no formato `(1) ... ; (2) ... ; (3) ...`). Use-a como **âncora primária**: os blocos enumerados ali são candidatos naturais a virar conceitos atômicos. Se precisar refinar, pode subdividir um bloco em dois conceitos, fundir dois blocos pequenos, ou inserir um conceito de fechamento — mas **nunca contradiga** o que o subcapítulo já se comprometeu a cobrir.
- **Objetivo** — a capacidade que o leitor terá ao fim do subcapítulo. Os conceitos juntos têm que entregar isso.
- **Fontes utilizadas** — referências do subcapítulo.

Os conceitos **devem respeitar** o recorte fixado no `CONTENT.md` do subcapítulo e o perfil do leitor fixado no `INTRODUCTION.md` do livro. Não invente conceitos sobre temas que o subcapítulo não promete; não rebaixe nem inflacione o nível em relação ao perfil do leitor.

## Pesquisa de contexto (obrigatória)

Mesmo com as quatro fontes em mãos, faça **de 3 a 6 buscas na web** para identificar as ideias atômicas que o campo reconhece como fundamentais no tema do subcapítulo. Boas buscas:

- `"<tema do subcapítulo> explained"` — explicações completas costumam listar, implícita ou explicitamente, os conceitos que a pessoa precisa dominar.
- `"<tema do subcapítulo> interview questions"` — perguntas de entrevista são um ótimo proxy para **"quais ideias atômicas existem neste tópico"**.
- `"<tema do subcapítulo> common mistakes"` ou `"... gotchas"` — cada armadilha comum esconde um conceito que deveria ter sido aprendido isoladamente.
- `"<tema do subcapítulo> FAQ"` — as dúvidas recorrentes revelam conceitos que se confundem (e portanto precisam de atenção separada).

### Idioma da pesquisa

Calibre o idioma das queries pelo perfil do tema, não pelo idioma da conversa:

- **Tema técnico-global** (frameworks, linguagens, padrões de engenharia, matemática, ciência) → **inglês como idioma primário**. A literatura canônica e as confusões clássicas vivem em inglês; busca em pt-BR costuma trazer traduções rasas.
- **Tema cultural ou regulatório-BR** (direito brasileiro, contabilidade local, geografia/história do Brasil, normas ABNT) → **pt-BR como idioma primário**. Fontes em inglês descrevem outro ordenamento.
- **Tema híbrido** (ex: "SQL para análise de dados num banco que existe só no Brasil", "Godot com tutoriais em pt-BR fortes") → **misture**: 1–2 queries em inglês para o núcleo técnico, 1–2 em pt-BR para vocabulário e armadilhas locais.

Quando em dúvida, comece em inglês — é mais fácil descobrir que faltava perspectiva BR do que o contrário.

Use as buscas para:

- Descobrir conceitos que são **óbvios para especialistas mas invisíveis para iniciantes**.
- Identificar **confusões clássicas** (dois conceitos que aprendizes misturam) — essas confusões viram conceitos separados na sua lista.
- Calibrar a granularidade certa: o que é "pequeno o suficiente para ser atômico" mas "grande o suficiente para ser ensinável".

Não cite as fontes na lista impressa em chat. As URLs relevantes ficam na seção `## Fontes utilizadas` que `CONCEPTS.md` **vai ganhar mais tarde** (quando `estudo-explicar-conceito` rodar). Por enquanto, esta skill só anota o esqueleto.

## O que gerar (lista + materialização)

A skill tem duas fases.

### Fase 1 — Listagem em chat

Gere e imprima no chat uma lista **numerada**, em **sequência de dependência** (conceitos que servem de base vêm antes). **Sem piso nem teto rígidos:** o número de conceitos é função única da cobertura do `## Estrutura` + `## Objetivo` do subcapítulo, sem inflar. Não existe "faixa típica" e não existe número-alvo. Subcapítulos densos pedem 10–12 conceitos com naturalidade; subcapítulos de fechamento ou recapitulação podem cair em 3 conceitos densos sem que isso seja preguiça — o que importa é a regra anti-linguiça abaixo. Forçar a lista a caber em 6 só porque os vizinhos têm 6 é tão errado quanto inflar para 12 quando 7 bastam: em ambos os casos, o que falha é a fidelidade ao subcapítulo.

**Regra anti-linguiça** (aplique antes de imprimir): para cada conceito candidato, pergunte "se eu cortar este, o leitor ainda atinge o `## Objetivo` do subcapítulo?". Se a resposta for sim, o conceito é linguiça — corte. Se for não, o conceito é necessário — mantenha mesmo que estoure qualquer expectativa de tamanho.

Formato:

```
Conceitos do Subcapítulo "<nome do subcapítulo>"
(Capítulo "<nome do capítulo>", Livro "<título do livro>"):

1. <Conceito 1> — <descrição em 1 linha>
2. <Conceito 2> — <descrição em 1 linha>
...
```

Numere os conceitos simplesmente como `1.`, `2.`, etc. (não use notação `N.M.K`).

#### Convenção de numeração — zero-padding quando N ≥ 10

A numeração no `## Roteiro` (lista Markdown) e em `## Conceitos` no `CONTENT.md` do subcapítulo segue o estilo natural do Markdown: `1.`, `2.`, …, `10.`, `11.`. Não há necessidade de zero-padding aqui — o renderer cuida da ordem visual.

Já as **seções `## N.`** que `estudo-explicar-conceito` vai anexar **devem usar zero-padding sempre que `N ≥ 10`**, para que ferramentas que ordenam alfabeticamente (sumários automáticos, índices laterais, parsers que listam headings) não coloquem `## 10.` entre `## 1.` e `## 2.`. Regra: **largura fixa = `len(str(N))`**.

- Se o subcapítulo tem **9 ou menos conceitos**: as seções viram `## 1.`, `## 2.`, … `## 9.`.
- Se tem **10 a 99 conceitos**: as seções viram `## 01.`, `## 02.`, … `## 10.`, `## 11.`, …
- Se tem **100 ou mais** (raríssimo): `## 001.`, `## 002.`, ….

Esta skill **não** escreve as seções `## N.` (isso é trabalho do `estudo-explicar-conceito`), mas **fixa a convenção** que o consumidor deve seguir. O número total `N` é conhecido nesta etapa (vem do tamanho do roteiro), portanto a largura de padding é determinada aqui e respeitada nas iterações seguintes.

#### O que é um conceito atômico

Um conceito atômico:

- **Pode ser explicado em 3–10 minutos** sem precisar abrir muitos outros conceitos como pré-requisito dentro do mesmo subcapítulo.
- **Tem nome concreto** — "Ordem de execução de GROUP BY em relação a WHERE", não "Conceitos sobre GROUP BY".
- **É testável** — dá pra imaginar uma pergunta que verifique se a pessoa entendeu.
- **É uma ideia, não um comando/sintaxe solto** — prefira "A intuição por trás de LEFT JOIN" em vez de "Sintaxe de LEFT JOIN" (exceto quando a sintaxe em si é o ponto central do subcapítulo).

#### Critérios para a lista

1. **Cobertura completa do subcapítulo** — após aprender todos os conceitos da lista, a pessoa entende o subcapítulo inteiro.
2. **Sem sobreposição** — dois conceitos não devem cobrir a mesma ideia com nomes diferentes.
3. **Sequência de dependência** — se o conceito B depende do A, A vem antes. Essa ordem é especialmente crítica nesta versão da skill, porque a explicação de cada conceito vai **construir literalmente em cima da explicação do anterior** num mesmo arquivo: trocar a ordem depois sai caro.
4. **Granularidade uniforme** — evite misturar conceito gigante com conceito trivial.
5. **Formulação clara** — o nome do conceito, sozinho, deve deixar claro o que será aprendido. Prefira nomes descritivos a nomes crípticos.
6. **Fidelidade ao escopo do subcapítulo** — não adicione conceitos que pertencem a outro subcapítulo do mesmo capítulo (consulte o `STRUCT.md` e os irmãos para confirmar).
7. **Encaixe no `STRUCT.md`** — antes de imprimir, faça uma checagem silenciosa contra a árvore: o **nível de granularidade** (não o tamanho) dos seus conceitos é compatível com o dos vizinhos? Se você está descendo a sintaxe pura num livro que opera em "ideias mecanicamente ensináveis" (ou subindo a meta-conceitos vagos num livro mecânico), recalibre o tipo de ideia. **Não recalibre o tamanho**: o número de conceitos é função única da cobertura do `## Estrutura` + `## Objetivo` deste subcapítulo.

### Fase 2 — Materialização no disco

A materialização é simples e **não cria nenhum subdiretório** no subcapítulo. Tudo cabe em dois arquivos: o `CONCEPTS.md` esqueleto e a edição do `CONTENT.md` do subcapítulo.

#### Etapa A — Escrever o esqueleto de `CONCEPTS.md`

No próprio diretório do subcapítulo (`<book-dir>/<NN-cap>/<MM-sub>/`), crie o arquivo `CONCEPTS.md` usando exatamente este template:

```markdown
# Conceitos: <Título do subcapítulo, idêntico ao H1 de CONTENT.md>

> _Aula contínua dos conceitos atômicos deste subcapítulo. Cada conceito vira uma seção `## N.` (ou `## 0N.` quando o roteiro tem 10+ conceitos) preenchida em sequência pela skill `estudo-explicar-conceito`. Cada nova iteração lê o que já foi escrito e dá continuidade — sem repetir vocabulário, sem reapresentar exemplos, sem saltos de tom._

## Roteiro

1. <Nome do Conceito 1> — <descrição em 1 linha>
2. <Nome do Conceito 2> — <descrição em 1 linha>
   ...

<!-- ROTEIRO-END -->

<!-- PENDENTE-START -->
> _Pendente: 0 / N conceitos preenchidos._
<!-- PENDENTE-END -->

<!-- AULAS-START -->
<!-- AULAS-END -->
```

Detalhes do template:

- O **H1 do `CONCEPTS.md`** segue o padrão `# Conceitos: <Título do subcapítulo>`. O título depois dos dois pontos é o mesmo H1 do `CONTENT.md` do subcapítulo.
- A seção `## Roteiro` é a **mesma lista numerada** que entra em `## Conceitos` no `CONTENT.md` do subcapítulo. Mantê-la dentro do `CONCEPTS.md` deixa o arquivo auto-suficiente — quem abrir só ele vê o plano antes da aula começar.
- A linha `_Pendente: 0 / N conceitos preenchidos._` é um marcador simples: um humano olha e sabe quantos conceitos faltam. A skill `estudo-explicar-conceito` atualiza esse contador a cada iteração.
- **Marcadores HTML estáveis** delimitam as três regiões editáveis do arquivo. **Escreva-os exatamente como mostrado** (literalmente, com os hífens e espaços) — eles são o contrato que `estudo-explicar-conceito` usa para localizar onde editar e onde anexar:
  - `<!-- ROTEIRO-END -->` fecha a seção `## Roteiro`. Garante que o consumidor não confunda itens do roteiro com seções de aula.
  - `<!-- PENDENTE-START -->` … `<!-- PENDENTE-END -->` envolvem **só** o blockquote `> _Pendente: K / N conceitos preenchidos._`. A cada iteração, o consumidor faz uma substituição cirúrgica do bloco inteiro entre os dois marcadores — sem precisar de regex sobre o texto livre.
  - `<!-- AULAS-START -->` … `<!-- AULAS-END -->` envolvem a região onde as seções `## N.` (preenchidas pelo consumidor) vão sendo anexadas. A skill atual deixa essa região **vazia** (apenas os dois marcadores em linhas consecutivas, separados por uma linha em branco). A contagem de aulas preenchidas vira: "número de headings `## ` entre `AULAS-START` e `AULAS-END`".
- **Não escreva nenhuma seção `## 1. ...`, `## 2. ...` agora.** Estas só nascem quando `estudo-explicar-conceito` for invocado para cada conceito, e devem ser inseridas **dentro da região `<!-- AULAS-START -->` … `<!-- AULAS-END -->`**.
- **Não inclua `![capa](...)` em `CONCEPTS.md`.** Não há capa por conceito nem por arquivo de aula — a capa do subcapítulo (`cover.png` no mesmo diretório) já cobre o visual.

**Exemplo do esqueleto renderizado** (subcapítulo "O Mapa do Livro"):

```markdown
# Conceitos: O Mapa do Livro

> _Aula contínua dos conceitos atômicos deste subcapítulo. Cada conceito vira uma seção `## N.` (ou `## 0N.` quando o roteiro tem 10+ conceitos) preenchida em sequência pela skill `estudo-explicar-conceito`. Cada nova iteração lê o que já foi escrito e dá continuidade — sem repetir vocabulário, sem reapresentar exemplos, sem saltos de tom._

## Roteiro

1. Os 4 blocos do livro — fundamentos, sistemas Pokémon-like, online, pipeline com AI
2. Por que fundamentos vêm primeiro — abrir engine antes de mecânica de jogo evita retrabalho
3. Por que single-player precede online — multiplayer assume mecânica funcionando offline
4. Por que pipeline com AI fecha o livro — depende dos sistemas estarem prontos para receber assets
5. A lógica das dependências entre blocos — o que cada bloco assume do anterior
6. Anti-padrão "começar pelo multiplayer" — por que tentar inverter a ordem trava o projeto

<!-- ROTEIRO-END -->

<!-- PENDENTE-START -->
> _Pendente: 0 / 6 conceitos preenchidos._
<!-- PENDENTE-END -->

<!-- AULAS-START -->
<!-- AULAS-END -->
```

Se já existir um `CONCEPTS.md` no subcapítulo, **substitua-o** por este esqueleto novo apenas se o usuário pediu explicitamente para resetar. Caso contrário, **interrompa e avise**: "Já existe `CONCEPTS.md` neste subcapítulo. Preserve o conteúdo ou rode com `--force` (peça confirmação ao usuário)." Esta skill nunca apaga aulas já escritas em silêncio.

#### Etapa B — Atualizar o `CONTENT.md` do subcapítulo

Edite `<book-dir>/<NN-cap>/<MM-sub>/CONTENT.md` para inserir uma nova seção **antes** de `## Fontes utilizadas`:

```markdown
## Conceitos

A explicação completa destes conceitos vive em [`CONCEPTS.md`](CONCEPTS.md), construída sequencialmente pela skill `estudo-explicar-conceito`.

1. <Nome do Conceito 1> — <descrição em 1 linha>
2. <Nome do Conceito 2> — <descrição em 1 linha>
   ...
```

Pontos importantes:

- A frase de cabeçalho aponta para o `CONCEPTS.md` no mesmo diretório — link relativo simples.
- A lista numerada **não tem links por item** (não há subdiretórios para apontar). É só nome + descrição.
- A ordem dos itens **deve** bater com o `## Roteiro` de `CONCEPTS.md`.
- Se já existir uma seção `## Conceitos`, substitua-a integralmente (idempotência — permite re-rodar a skill sem duplicar).

As demais seções (`# Título`, `![capa]`, `## Sobre este subcapítulo`, `## Estrutura`, `## Objetivo`, `## Fontes utilizadas`) **não devem ser alteradas**.

## Encerramento

Após criar o `CONCEPTS.md` esqueleto e atualizar o `CONTENT.md` do subcapítulo, encerre com:

> _`CONCEPTS.md` esqueleto criado em `./<book-dir>/<NN-cap>/<MM-sub>/CONCEPTS.md` (N conceitos no roteiro). `CONTENT.md` do subcapítulo atualizado. Próximo passo: rodar `estudo-explicar-conceito <book-dir>/<NN-cap>/<MM-sub>` em sequência (uma vez por conceito) para preencher a aula._

## Exemplo

**Entrada:** `godot-para-um-rpg-2d-online-estilo-pokemon/01-introducao/05-o-mapa-do-livro`

**Fluxo:**

1. Lê `STRUCT.md` (panorama do livro), `INTRODUCTION.md` (perfil do leitor, lista de capítulos), `01-introducao/CONTENT.md` (escopo do capítulo, lista de subcapítulos irmãos), `01-introducao/05-o-mapa-do-livro/CONTENT.md` (escopo do subcapítulo).
2. Faz 3–6 buscas web (roadmaps de gamedev, organização típica de livros de Godot/RPG).
3. Imprime lista no chat:

```
Conceitos do Subcapítulo "O Mapa do Livro"
(Capítulo "Introdução", Livro "Godot para um RPG 2D Online Estilo Pokémon"):

1. Os 4 blocos do livro — fundamentos, sistemas Pokémon-like, online, pipeline com AI
2. Por que fundamentos vêm primeiro — abrir engine antes de mecânica de jogo evita retrabalho
3. Por que single-player precede online — multiplayer assume mecânica funcionando offline
4. Por que pipeline com AI fecha o livro — depende dos sistemas estarem prontos para receber assets
5. A lógica das dependências entre blocos — o que cada bloco assume do anterior
6. Anti-padrão "começar pelo multiplayer" — por que tentar inverter a ordem trava o projeto

*Próximo passo: `estudo-explicar-conceito <subcap-path>` em sequência.*
```

4. Materializa no disco:
   - `./godot-para-.../01-introducao/05-o-mapa-do-livro/CONCEPTS.md` (esqueleto com `## Roteiro` listando os 6 conceitos e marcador `Pendente: 0 / 6 conceitos preenchidos.`).
5. Atualiza `./godot-para-.../01-introducao/05-o-mapa-do-livro/CONTENT.md` inserindo `## Conceitos` (com link para `CONCEPTS.md` e a mesma lista numerada) antes de `## Fontes utilizadas`.
6. Encerra com a linha de fechamento.

## O que evitar

- **Não** crie conceitos que são, na prática, subcapítulos ("Tudo sobre HAVING" é subcapítulo; "Por que HAVING filtra após a agregação" é conceito).
- **Não** liste sintaxe pura como conceito, a menos que o subcapítulo seja explicitamente sobre sintaxe.
- **Não** encha linguiça nem corte conceitos necessários para caber numa faixa — a régua é a cobertura mínima do subcapítulo, não o número. Se o subcapítulo realmente pede 12, dê 12; se pede 3 conceitos densos, dê 3.
- **Não** preencha as seções `## 1. ...` em `CONCEPTS.md` aqui — a aula é tarefa de `estudo-explicar-conceito`. Esta skill só escreve `## Roteiro` e o marcador `Pendente: 0 / N`.
- **Não** sobrescreva um `CONCEPTS.md` que já tem aulas escritas sem confirmação explícita do usuário — perde-se trabalho.
