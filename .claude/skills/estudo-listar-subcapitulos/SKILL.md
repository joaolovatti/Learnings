---
name: estudo-listar-subcapitulos
description: Gera uma sequência pedagógica de subcapítulos a partir do **caminho de um capítulo já materializado** pela skill `estudo-listar-capitulos` (ex: `godot-para-um-rpg-2d-online-estilo-pokemon/09-npcs-dialogos-e-eventos-de-mundo/`) e materializa cada subcapítulo no disco (subdiretório, capa 1536x1024 e `CONTENT.md`), além de atualizar o `CONTENT.md` do capítulo com links para os subcapítulos. Use quando o usuário apresentar o **caminho de um capítulo** (livro/capítulo) e pedir "quebra esse capítulo em subcapítulos", "gera os subcapítulos", "destrincha esse capítulo", "estrutura esse capítulo", "materializa os subcapítulos", "abre esse capítulo em partes", ou simplesmente invocar a skill passando o caminho. Antes de gerar, a skill lê o `INTRODUCTION.md` do livro-pai, os nomes dos capítulos irmãos e o `CONTENT.md` do capítulo como contexto obrigatório, e pesquisa fontes reais na internet para ancorar a subdivisão. Esta é a **terceira etapa** do método de estudo estruturado.
---

# estudo-listar-subcapitulos

Terceira etapa do método de estudo estruturado. Recebe o **caminho de um capítulo já materializado** (pela skill `estudo-listar-capitulos`), desdobra-o em subcapítulos pedagogicamente ordenados, e **materializa cada subcapítulo no disco** como um subdiretório do capítulo com capa e `CONTENT.md`. Por fim, atualiza o `CONTENT.md` do capítulo com links para cada subcapítulo na ordem.

## Quando usar

O usuário já tem um capítulo materializado (subdiretório do livro com `cover.png` + `CONTENT.md`) e quer a próxima camada: o capítulo expandido em subcapítulos concretos, com seus próprios artefatos.

## Entrada

O **caminho do diretório do capítulo** (relativo ao diretório de trabalho atual), no formato `<book-dir>/<NN-slug-do-capitulo>/`. Exemplos:

- `godot-para-um-rpg-2d-online-estilo-pokemon/09-npcs-dialogos-e-eventos-de-mundo/`
- `sql-para-analise-de-dados/06-joins-combinando-tabelas/`
- `direito-tributario-aplicado-a-pessoa-juridica/04-icms-e-substituicao-tributaria/`

Esse caminho carrega implicitamente os dois contextos obrigatórios: o **livro-pai** (`<book-dir>/`) e o **capítulo** (`<NN-slug-do-capitulo>/`).

Se o usuário não trouxer o caminho, pergunte uma única vez: _"Qual é o caminho do capítulo (ex: `godot-para-um-rpg-2d-online-estilo-pokemon/09-npcs-dialogos-e-eventos-de-mundo/`) que você quer destrinchar em subcapítulos?"_

Valide que o caminho existe e contém `CONTENT.md`, e que o diretório-pai contém `INTRODUCTION.md`. Se algo falhar, avise e interrompa — a skill depende dos artefatos das duas etapas anteriores.

## Contexto obrigatório (quatro fontes)

Antes de qualquer pesquisa ou geração, leia **as quatro fontes na ordem abaixo**. Elas calibram juntas o recorte e a granularidade dos subcapítulos.

### 1. `<book-dir>/STRUCT.md` — o mapa estrutural do livro (referência primária para a criação)

Carrega o mapa visual completo do livro (gerado pela skill `estudo-atualizar-struct`): título do livro, todos os capítulos com descrição de 1 linha, e quaisquer subcapítulos/conceitos já materializados em capítulos vizinhos. Esta é a **árvore de arquivos canônica** do livro — o que existe em disco hoje e o que está sendo construído sobre ela. Use-o em duas frentes:

1. **Como localizador rápido**: você se posiciona no livro inteiro sem abrir vários CONTENT.md.
2. **Como referência estrutural para a sua criação** (o uso central nesta skill): a árvore deixa visível a forma que o livro adotou — quantos subcapítulos costumam abrir um capítulo, qual o nível de granularidade dos slugs, quais convenções de nomeação foram usadas em capítulos vizinhos. Os subcapítulos que você vai criar devem **encaixar** nessa árvore como continuação coerente, não como ilha estranha. Antes de imprimir a lista da Fase 1, leia os ramos dos capítulos vizinhos do `STRUCT.md` e confira:
   - **Quantidade**: a faixa de subcapítulos por capítulo está coerente com a deste? Se vizinhos rodam 5–7 subcapítulos e você está propondo 12, ou o capítulo é genuinamente mais denso, ou você inflou.
   - **Granularidade dos slugs**: os slugs de subcapítulos vizinhos têm escopo comparável ao que os seus prometem? Subcapítulos vizinhos com slug `02-sistema-de-dialogo/` denunciam que `04-detalhes-de-tipografia-da-caixa-de-texto/` está fino demais para o livro.
   - **Cobertura cruzada**: algum subcapítulo proposto **já existe** em outro capítulo (visível no `STRUCT.md`) com nome equivalente? Se sim, descarte daqui ou redirecione o leitor; o livro não duplica território materializado.

Se `STRUCT.md` ainda não existe (livro recém-criado, este é o primeiro capítulo a ganhar subcapítulos), siga em frente — você vai recriá-lo no fim via `estudo-atualizar-struct`. Mas se existe, leia-o.

### 2. `<book-dir>/INTRODUCTION.md` — o contrato do livro detalhado

Carrega o quadro maior:

- **Título completo do livro** e seu recorte ("para Análise de Dados", "para um RPG 2D Online Estilo Pokémon").
- **Sobre este livro**, **Estrutura**, **Objetivo** — a promessa global que o capítulo está atendendo.
- **Sobre o leitor** — nível, experiências adjacentes, objetivo declarado. Calibra a profundidade e a linguagem dos subcapítulos.
- **Capítulos** — a lista completa dos capítulos do livro com suas descrições. Use isso para entender **o que pertence a este capítulo e o que pertence a outro**: se um possível subcapítulo é, na verdade, o tema central de outro capítulo do mesmo livro, ele não cabe aqui.
- **Fontes utilizadas** — referências que ancoraram o recorte do livro inteiro (algumas podem ser reutilizadas como fontes do capítulo).

### 3. Nomes dos diretórios irmãos do capítulo

Liste o conteúdo de `<book-dir>/` e capture os nomes dos demais subdiretórios `NN-slug-*/`. Eles complementam a seção "Capítulos" do `INTRODUCTION.md` com a forma canônica em disco e revelam a posição relativa deste capítulo na trilha (qual capítulo veio antes, qual vem depois). Isso ajuda a respeitar **pré-requisitos já cobertos** (não reexplique o que o capítulo anterior já cobriu) e **evitar invadir** o território do próximo capítulo.

### 4. `<book-dir>/<NN-slug-do-capitulo>/CONTENT.md` — o contrato do capítulo

Carrega as restrições mais finas e específicas:

- **Título do capítulo** (H1).
- **Sobre este capítulo** — a proposta exata do recorte deste capítulo dentro do livro.
- **Estrutura** — esta seção é frequentemente uma **prévia explícita dos subcapítulos** (no formato `(1) ... ; (2) ... ; (3) ...`). Use-a como **âncora primária**: os blocos enumerados ali são candidatos naturais a virar subcapítulos. Se precisar refinar, pode subdividir um bloco em dois subcapítulos, fundir dois blocos, ou inserir um subcapítulo de fechamento — mas **nunca contradiga** o que o capítulo já se comprometeu a cobrir.
- **Objetivo** — a capacidade que o leitor terá ao fim do capítulo. Os subcapítulos juntos têm que entregar isso.
- **Fontes utilizadas** — referências do capítulo, base inicial das fontes que vão para os `CONTENT.md` dos subcapítulos.

Os subcapítulos **devem respeitar** o recorte fixado no `CONTENT.md` do capítulo e o perfil do leitor fixado no `INTRODUCTION.md` do livro. Não invente subcapítulos sobre temas que o capítulo não promete; não rebaixe a densidade para um nível que contraria o perfil descrito em "Sobre o leitor".

## Pesquisa de contexto (obrigatória)

Mesmo com as quatro fontes em mãos, faça **de 2 a 5 buscas na web** para ancorar a subdivisão em estruturas reais de ensino.

### Idioma das queries (regra explícita)

A escolha do idioma vem da **natureza do tema**, não do idioma do usuário:

- **Tema técnico-global** (programação, ferramentas com docs em inglês, ciência exata, ML, engines, frameworks): **primárias em inglês** — onde está o grosso de tutoriais, docs oficiais, syllabi, roadmaps. Adicione **1 busca em pt-BR** para capturar tutorial brasileiro consagrado, série de vídeo em português, ou termo localizado relevante.
- **Tema cultural / local / regulatório** (Direito Tributário Brasileiro, ENEM, CLT, Cozinha Mineira, Histórico do Futebol Brasileiro, sistema de saúde do SUS): **primárias em pt-BR** — em inglês esses temas vêm com cobertura genérica e errada de jurisdição. Adicione 1 busca em inglês só se houver vertente acadêmica internacional comparada.
- **Tema híbrido** (ex: SaaS para PMEs no Brasil, marketing digital com foco no mercado nacional): faça **3 em pt-BR + 2 em inglês**, e privilegie a fonte que tiver mais aderência ao recorte do livro.

### Padrões de busca úteis

- `"<tema do capítulo> tutorial"` / `"<tema do capítulo> tutorial passo a passo"` — tutoriais bons já carregam a subdivisão implícita que funciona.
- `"<tema do capítulo> explained"` / `"<tema do capítulo> guide"` / `"guia de <tema>"` — guias completos revelam as subseções naturais.
- `"<tema do capítulo>" site:docs.<ferramenta relevante>` — para capítulo sobre tecnologia, a doc oficial dá a subdivisão canônica.
- `"how to learn <tema do capítulo>"` / `"como aprender <tema>"` — artigos pedagógicos mostram onde os aprendizes tropeçam.
- Para temas regulatórios/locais, prefira fontes oficiais: `site:gov.br`, `site:planalto.gov.br`, `site:receita.fazenda.gov.br`, conselhos profissionais, instituições de ensino reconhecidas.

Use as buscas para:

- Descobrir **subseções que costumam ser ensinadas juntas** por tradição didática.
- Identificar **pegadinhas específicas do capítulo** que merecem subcapítulo próprio (um bom capítulo dedica uma seção às armadilhas clássicas).
- Calibrar se a divisão natural é por conceito, por sintaxe, por caso de uso, ou por nível de dificuldade.

### Retry quando o sinal é fraco

Após a primeira rodada, **avalie a qualidade do sinal**: contou no mínimo **3 fontes com conteúdo real e específico** (tutorial estruturado, doc oficial, syllabus, capítulo de livro reconhecido)? Resultados que são só listagens superficiais, conteúdo gerado por IA óbvio, ou rolinhos de SEO **não contam**.

Se ficou abaixo de 3 fontes-sinal:

1. **Rode uma segunda rodada** com queries reformuladas. Mude:
   - **Sinônimos do tema** (ex: "diálogo ramificado" → "branching dialogue", "dialogue tree", "narrative graph").
   - **Idioma alternativo** ao da primeira rodada (se rodou em inglês, vá pt-BR; se rodou pt-BR, vá inglês — útil para temas híbridos).
   - **Plataformas diferentes** (de Google genérico → `site:youtube.com`, `site:reddit.com/r/<sub>`, `site:medium.com`, `site:dev.to`, fóruns oficiais da ferramenta, anais acadêmicos).
   - **Ângulo pedagógico** (ex: "<tema> for beginners", "common mistakes in <tema>", "<tema> cheat sheet").

2. Se a segunda rodada **ainda não trouxer 3 fontes-sinal**, **pare e avise o usuário**:

   > _O tema deste capítulo tem cobertura web fraca para ancorar uma subdivisão pedagogicamente sólida. Encontrei só `<N>` fonte(s) de qualidade após duas rodadas de busca (`<liste o que encontrou>`). Pode me orientar com:_
   > - _Algum livro, curso, syllabus ou referência específica que eu deva usar como base?_
   > - _Um tutorial ou playlist de vídeos confiável?_
   > - _Notas suas sobre como você acha que o capítulo deveria se subdividir?_
   >
   > _Sem isso, eu vou inventar uma subdivisão que pode não bater com a prática real do campo._

   **Não force** uma lista de subcapítulos a partir de fontes fracas — é melhor pausar do que entregar uma estrutura desancorada.

Ao escrever o `CONTENT.md` de cada subcapítulo, **só dispare busca adicional quando as fontes do capítulo comprovadamente não cobrem o subtema do subcapítulo**. A regra existe porque "1–2 buscas extras × N subcapítulos" multiplica chamadas web sem necessidade quando o `CONTENT.md` do capítulo já trouxe 5–8 fontes pedagogicamente densas.

Critério prático antes de buscar:

1. Liste mentalmente as fontes do `CONTENT.md` do capítulo.
2. Pergunte: **3 ou mais delas tratam diretamente do subtema deste subcapítulo** (não só do tema geral do capítulo)? Se sim → reaproveite-as e **não** faça busca extra.
3. Se não — ex: as fontes do capítulo são todas tutoriais genéricos de "NPCs em Godot" e o subcapítulo é "Diálogos Ramificados" especificamente — então **1 busca alvo basta** (ex: `branching dialogue tree godot`). Não rode duas só para "ter mais opções".

Se mesmo a busca alvo trouxer pouco sinal, prefira marcar a fonte como "[a complementar]" e seguir, em vez de gastar buscas em cascata. Você terá outra rodada de pesquisa em etapas posteriores do método já no nível certo de granularidade.

## O que gerar (lista + materialização)

A skill tem duas fases.

### Fase 1 — Listagem em chat

Gere e imprima no chat uma lista **numerada** em **ordem pedagógica dentro do escopo do capítulo**.

**Faixa típica: 5 a 8 subcapítulos.** Capítulos densos com tema amplo podem chegar a 9–10; capítulos focados fecham em 5.

**Mínimo aceitável: 5.** Se você está chegando a 4 ou menos sem inflar artificialmente, **pare e sinalize ao usuário antes de gerar**: o capítulo provavelmente é fino demais para sustentar a divisão (talvez devesse ser fundido com um capítulo vizinho, ou um dos blocos foi capturado pelo capítulo anterior). Mensagem sugerida:

> _O capítulo "<X>" parece render só ~4 subcapítulos sem forçar — é sinal de que o recorte ficou fino demais para sustentar uma divisão pedagogicamente saudável. Quer que eu (a) prossiga assim mesmo com 4 subcapítulos enxutos, (b) sugira fundir este capítulo com um vizinho, ou (c) cancele para você ajustar o capítulo lá em `estudo-listar-capitulos`?_

Não há teto rígido, mas inflar com subcapítulos artificiais (genéricos do tipo "Conclusão", "Recapitulação") para bater 8 viola o critério de granularidade abaixo.

Formato:

```
Subcapítulos do Capítulo "<nome do capítulo>"
do livro "<título do livro>":

1. <Subcapítulo 1> — <descrição em 1 linha>
2. <Subcapítulo 2> — <descrição em 1 linha>
...
```

Numere os subcapítulos simplesmente como `1.`, `2.`, etc. (não use notação `N.M`).

#### Critérios para a sequência

1. **Fidelidade ao escopo do capítulo** — não adicione subcapítulos que deveriam estar em outro capítulo do livro. Se parecer que algo transborda, é sinal de que o capítulo em si está mal-delimitado; sinalize ao usuário em vez de forçar.
2. **Coerência com o livro-pai** — o recorte do livro ("para Análise de Dados", "para um RPG 2D Online") e o perfil do leitor pesam na escolha. Mesmo capítulo, livros diferentes → subcapítulos diferentes.
3. **Aderência à seção "Estrutura" do capítulo** — a enumeração `(1) ... ; (2) ... ;` ali é a coluna vertebral natural dos subcapítulos. Use-a como ponto de partida e refine.
4. **Ordem interna lógica** — o subcapítulo 2 pode depender do 1, mas não o contrário.
5. **Granularidade equilibrada — antecipando conceitos atômicos.** Todos os subcapítulos devem ter peso comparável dentro do capítulo (nada de um gigante ao lado de um minúsculo). Como régua de calibração olhando para a próxima etapa do método: **cada subcapítulo deve render ~3 a 7 conceitos atômicos** quando os conceitos forem listados. **Conceito atômico** = ideia indivisível, ensinável de forma autocontida em uma única passada, com dependência **linear** sobre os conceitos anteriores do mesmo subcapítulo (e nunca circular). Use isso para detectar subcapítulos mal-dimensionados antes de materializar:
   - **Renderia só 1–2 conceitos atômicos** → fino demais. Funda com o subcapítulo vizinho ou puxe conceitos de um vizinho largo demais.
   - **Renderia 10+ conceitos atômicos** → amplo demais. Quebre em dois subcapítulos seguidos no mesmo bloco temático (ex: "Diálogos — Caixa de Texto e Avanço" + "Diálogos — Ramificação e Variáveis" em vez de "Sistema de Diálogo" único).
   - **Conceitos não seriam atômicos entre si** — dois candidatos a conceito do mesmo subcapítulo se sobrepõem, dependem mutuamente, ou só fazem sentido juntos: sinal de que o subcapítulo está agrupando temas que pediam ser dois subcapítulos distintos, ou que um dos "dois conceitos" é na verdade um só. Atomicidade entre conceitos do mesmo subcapítulo é **inegociável** — ela é o que permite que `estudo-explicar-conceito` ensine cada conceito como uma aula autocontida em ordem linear.
   - Faça esse exercício mental para cada item da lista antes de imprimir. É barato e evita retrabalho a jusante.
6. **Ensino, não índice remissivo** — subcapítulos são blocos de aprendizado, não entradas de glossário. Evite subcapítulo de 1 conceito só, a menos que o conceito seja mesmo central.
7. **Densidade prática — cada subcapítulo agrega conceito técnico/prático novo.** Régua mais importante quando o livro é prático/aplicado (POC, MVP, "feature em produção", "trilha hands-on", "X aplicado a Y") e o `## Sobre o leitor` descreve leitor experiente. Subcapítulos cujo conteúdo é **apenas framing do capítulo** — definir o critério de pronto, mapear o público-alvo, listar o que entra e o que fica fora, descrever a lógica da sequência, antecipar o checkpoint final, "introduzindo a tecnologia" sem ensinar nada concreto — **não cabem como subcapítulos**. Esse material já vive em `## Sobre este capítulo` e `## Estrutura` do `CONTENT.md` do capítulo; quebrá-lo em 5–6 subcapítulos meta é encher linguiça. Critério prático para cada item da lista: pergunte "**qual conceito técnico, prática, decisão de implementação, trade-off concreto, ou sintaxe específica o leitor vai entender depois deste subcapítulo que ele não entendia antes?**". Se a resposta é "ele entende qual é o critério de pronto" / "ele sabe quem é o cliente da POC" / "ele tem o arco do capítulo mapeado" / "ele entende o que fica fora" → **subcapítulo banido**. Se a resposta é "ele entende o trade-off entre Lambda response streaming e WebSocket" / "ele sabe configurar um JWT authorizer no API Gateway" / "ele entende como pi.dev modela id/parentId numa árvore JSONL" / "ele sabe exatamente quais campos do Resource de NPC são obrigatórios" → subcapítulo válido. Mesmo num capítulo introdutório, todos os subcapítulos devem agregar conceito/prática nova — nunca reformular o framing do capítulo.

#### Termos técnicos (idioma)

A lista (e os títulos dos subcapítulos materializados) é em pt-BR, mas **termos técnicos seguem o uso idiomático do campo**:

- **Mantenha em inglês** quando essa é a forma consagrada na prática profissional/acadêmica do campo: `signal`, `state machine`, `tilemap`, `JOIN`, `pipeline`, `delta time`, `merge request`, `endpoint`, `embedding`, `prompt`, `tick rate`. Traduzir esses termos soa amador e descola o leitor da literatura real.
- **Traduza para pt-BR** apenas quando há termo brasileiro genuinamente consagrado e usado no dia-a-dia do campo: "árvore de cena" (não "scene tree"), "diálogo ramificado" (não "branching dialogue") em contexto de gamedev brasileiro, "imposto sobre serviços" (não "service tax"), "junção" só se o livro inteiro adotou essa convenção e está coerente.
- **Não invente** traduções de termo que ninguém usa. Se ficar em dúvida, mantenha em inglês entre o vernáculo pt-BR — é a forma mais legível e mais fiel à literatura ("o `signal` dispara quando…").
- **Coerência intra-livro**: se um termo já apareceu em capítulos anteriores em uma forma (ex: capítulo 4 usa `signal`), mantenha a mesma forma aqui. Verifique consultando o `STRUCT.md` ou os irmãos.

Essa regra vale tanto na lista impressa em chat quanto nos `CONTENT.md` (Sobre, Estrutura, Objetivo) dos subcapítulos.

#### Validação cruzada antes de imprimir a lista

Antes de imprimir a lista no chat, faça **três checagens** contra os contextos já lidos. Elas não são opcionais — sem isso, a lista pode estar plausível mas desalinhada com o que o capítulo prometeu (Checagens 1 e 2) ou invadir o território de capítulos irmãos (Checagem 3).

**Checagem 1 — cobertura dos blocos da `## Estrutura` do capítulo.** A seção `## Estrutura` do `CONTENT.md` do capítulo enumera os grandes blocos do capítulo `(1) ... ; (2) ... ; (3) ...`. Esses blocos são o contrato de escopo do capítulo. Monte mentalmente uma matriz `bloco × subcapítulos`:

```
Bloco (1) ........................ → sub. 01, 02
Bloco (2) ........................ → sub. 03
Bloco (3) ........................ → sub. 04, 05, 06
Bloco órfão? (sem subcapítulo)        → ✗ — falha
Subcapítulo órfão? (fora dos blocos)  → ✗ — falha
```

Regras:

- **Cada bloco precisa ter ≥ 1 subcapítulo correspondente.** Se um bloco fica sem subcapítulo, ou você esqueceu de cobrir um pedaço da promessa do capítulo, ou o bloco em si é supérfluo (e nesse caso o `CONTENT.md` do capítulo é que está errado — sinalize ao usuário antes de prosseguir).
- **Cada subcapítulo precisa cair em pelo menos um bloco.** Se um subcapítulo é órfão, ou ele invade escopo de outro capítulo (descarte), ou a `## Estrutura` do capítulo está incompleta (sinalize ao usuário antes de prosseguir, oferecendo ajustar a seção).
- Subcapítulos do tipo "Hands-on/fechamento" tipicamente atravessam blocos — está OK marcá-los como "transversal" em vez de associar a um bloco único.

**Checagem 2 — cobertura do `## Objetivo` do capítulo.** A seção `## Objetivo` declara as capacidades que o leitor terá ao terminar o capítulo inteiro. Cobrir os blocos da `## Estrutura` é necessário, mas **não suficiente** — capacidades declaradas no `## Objetivo` precisam ter subcapítulo responsável por ensiná-las.

**Como executar a checagem** (mentalmente, antes de imprimir a lista):

1. Extraia do `## Objetivo` do capítulo cada **capacidade tangível** declarada (ex: "saber configurar um NPC com state machine", "ser capaz de escrever uma cutscene scriptada de fim", "entender quando usar Resource e quando usar JSON").
2. Para cada capacidade, identifique **qual subcapítulo da lista a entrega** (pode ser um subcapítulo, ou a combinação de dois adjacentes — mas tem que ficar claro qual é).
3. **Lacuna** → capacidade sem subcapítulo correspondente: adicione subcapítulo, expanda escopo do mais próximo, ou (se for capacidade pequena demais) sinalize ao usuário que o `## Objetivo` está mais largo do que os subcapítulos suportam.
4. **Excesso** → subcapítulo que não contribui para nenhuma capacidade do `## Objetivo`: questione se ele cabe aqui, se invade outro capítulo, ou se o `## Objetivo` do capítulo está sub-especificado e precisa ser revisto antes.

**Checagem 3 — não invasão de capítulos irmãos.** Os nomes dos diretórios irmãos lidos na Fonte 3 já dizem qual capítulo veio antes e qual vem depois deste. Para **cada subcapítulo da lista**, pergunte: este subtema cabe melhor aqui, ou é território declarado do capítulo anterior (já coberto) ou do capítulo seguinte (tema central dele)?

- **Subtema já coberto pelo capítulo anterior** → descarte ou reduza a uma menção de revisão de uma linha dentro de outro subcapítulo. Não reabra o que o leitor já viu na trilha.
- **Subtema é, na prática, o título central de um capítulo seguinte** (basta o nome do diretório irmão para confirmar) → o subcapítulo invade outro território. Descarte e sinalize ao usuário, já que pode ser sinal de que o `CONTENT.md` deste capítulo está com `## Estrutura` larga demais e precisa ser apertado antes de prosseguir.
- **Fronteira genuína** (subtema cabe parcialmente nos dois capítulos) → fica no capítulo que **abre** o assunto, não no que aprofunda. Se este capítulo abre, fica aqui; se o irmão abre, vai para o irmão.

Quando o nome do diretório irmão não bastar para julgar a fronteira (ex: dois capítulos próximos com títulos amplos), abra o `CONTENT.md` do irmão fronteiriço — anterior ou seguinte, conforme o caso — e leia a `## Estrutura` dele para conferir o escopo declarado. Faça isso só quando a dúvida persistir após ler os nomes; não é uma leitura sistemática para todos os subcapítulos.

**Checagem 4 — encaixe estrutural com o `STRUCT.md`.** Se o `STRUCT.md` já existe (capítulos vizinhos já abertos em subcapítulos), use-o como **gabarito** da forma do livro:

- **Quantidade comparável**: a faixa de subcapítulos por capítulo deste livro está visível na árvore. Se vizinhos rodam 6 subcapítulos e você está propondo 12, justifique (capítulo genuinamente mais denso) ou recalibre — fugir da forma do livro sem motivo desorienta o leitor que navega o `STRUCT.md`.
- **Granularidade dos slugs**: pegue 2–3 subcapítulos de capítulos vizinhos no `STRUCT.md` e compare o escopo dos seus com o escopo deles. Slugs muito mais finos ou muito mais grossos do que a média do livro são sinal de calibração errada.
- **Sem duplicar nó já existente**: se algum subcapítulo proposto bate (em escopo, não em slug literal) com um subcapítulo já materializado em outro capítulo, descarte aqui. O livro mantém uma única casa para cada tema.

Faça as quatro checagens **silenciosamente**, sem expor as matrizes ao usuário (a lista impressa em chat fica enxuta). Se alguma das checagens falhar e exigir intervenção do usuário (bloco órfão, subcapítulo órfão, lacuna no Objetivo que você não consegue resolver sozinho, invasão de capítulo irmão que sugere ajustar a `## Estrutura` do capítulo, descompasso forte com a forma do livro vista no `STRUCT.md`), **pause e pergunte antes de imprimir a lista** — pode ser sinal de que o `CONTENT.md` do capítulo (ou de um irmão) precisa ser ajustado primeiro.

### Fase 2 — Materialização no disco

Materialize todos os subcapítulos seguindo **exatamente** esta ordem de etapas. A ordem importa: a geração da capa só pode rodar depois que o diretório de destino existe, senão o script falha ao salvar.

**Etapa A — Criar todos os subdiretórios primeiro.** Em `<book-dir>/<NN-slug-do-capitulo>/`, crie de uma vez todos os subdiretórios dos subcapítulos, prefixados pela ordem zero-padded:

- Formato: `MM-slug-do-subcapitulo/` onde `MM` é `01, 02, …, 10, 11`.
- Regras do slug: minúsculas, espaços viram `-`, remova acentos (`ç`→`c`, `á`→`a`), remova pontuação (`—`, `:`, `,`, `.`).
- Exemplos: `01-anatomia-de-um-npc/`, `04-eventos-de-cutscene/`.

Um único `mkdir -p <dir1> <dir2> ...` resolve todos de uma vez. Só avance para a etapa B depois que todos os subdiretórios existirem.

**Etapa B — Resolver a raiz absoluta do projeto uma vez.** Antes de disparar qualquer geração de capa, identifique `<REPO_ROOT>` — o diretório que contém o `<book-dir>`. Você vai precisar dele para montar os paths absolutos da etapa C. Costuma bastar um `pwd` na raiz de trabalho (o cwd padrão do harness); em último caso, suba de `<book-dir>` até achar a pasta `.claude/`.

**Etapa C — Gerar as capas 1536x1024 em paralelo.** Para cada subcapítulo, descreva mentalmente uma cena **metafórica** que represente o conceito (não ilustração literal). Prompt sempre em **inglês**.

**Antes de gerar qualquer capa, fixe a paleta-base do capítulo.** Abra `<book-dir>/<NN-slug-do-capitulo>/cover.png` (a capa do capítulo, gerada por `estudo-listar-capitulos`) e observe-a como referência visual: identifique 2 a 4 cores dominantes e a temperatura geral. Verbalize-a em uma frase reaproveitável para todos os subcapítulos — ex: `deep teal and warm amber palette with ivory accents`. **Essa é a paleta-base que todos os subcapítulos deste capítulo herdam**, derivada por sua vez da paleta-base do livro inteiro. Resultado pretendido: ao olhar a estante de capas (livro → capítulo → subcapítulos), o leitor reconhece imediatamente a cadeia de pertencimento.

A variação entre subcapítulos vem de **outros slots** (sujeito, iluminação, composição) e de **acentos sutis** dentro da própria paleta — não de trocar a paleta inteira. Não inventar cores novas, não trocar a temperatura, não introduzir terceira cor forte que não esteja na capa do capítulo.

**Esqueleto fixo do prompt** — siga essa ordem; ela mantém consistência visual entre subcapítulos do mesmo capítulo e entre todos os livros do repositório:

```
<subject metáfora>, in <style>, <palette>, <lighting>, <composition>, no text, no letters, no words, no typography, no captions, no labels
```

Os 5 slots:

1. **`<subject metáfora>`** — a cena central como **metáfora visual**, não ilustração literal. Pense em "o que esse subtema *parece*?", não "como ele é desenhado em diagrama". Exemplos: para "Sistema de diálogo ramificado" → uma árvore luminosa cujos galhos se bifurcam em correntes de luz; para "JOIN entre tabelas" → pontes luminosas conectando ilhas; nunca um diagrama-textual ou print de código/UI.
2. **`<style>`** — fixe um estilo e mantenha. Opções testadas: `detailed digital painting`, `cinematic concept art illustration`, `isometric digital painting`, `clean vector-style illustration`, `ink illustration with watercolor wash`. **Não misture** ("watercolor cinematic photo" confunde o modelo). Idealmente, o estilo é o mesmo do capítulo-pai.
3. **`<palette>`** — **use a paleta-base do capítulo fixada acima**, com variação sutil (dominância, equilíbrio, acento). Não invente paleta nova por subcapítulo — isso quebra a identidade visual do capítulo e do livro.
4. **`<lighting>`** — uma frase. Ex: `soft cinematic backlighting`, `rim light from upper-left, deep shadows`, `diffuse overcast lighting`, `volumetric god rays through dust`.
5. **`<composition>`** — formato e enquadramento. Ex: `wide cinematic landscape composition, centered subject`, `low-angle hero shot, subject on the right third`, `top-down isometric view, subject grounded in lower half`.

E a **trava obrigatória de texto** no fim — esse modelo tende a inserir letras aleatórias se a trava não estiver explícita.

**Dois exemplos completos** (subcapítulos reais do repositório):

Subcapítulo "Sistema de Diálogo" (capítulo "NPCs, Diálogos e Eventos de Mundo" — Godot):

```
A glowing speech ribbon unrolling letter-by-letter from a small luminous orb above a wooden lectern in a quiet pixel-art-inspired forest clearing, in detailed digital painting, deep teal and warm amber palette, soft cinematic backlighting with subtle volumetric glow on the ribbon, wide cinematic landscape composition with the lectern slightly off-center to the right, no text, no letters, no words, no typography, no captions, no labels
```

Subcapítulo "Joins de Múltiplas Tabelas" (capítulo "Joins, Combinando Tabelas" — SQL):

```
Three floating crystalline grids of hexagonal cells connected by golden threads weaving in and out at multiple heights above a calm geometric plane, in isometric digital painting, indigo and pale-gold palette with ivory accents, soft directional lighting from upper-left casting long thin shadows, wide centered composition with the middle grid as the visual anchor, no text, no letters, no words, no typography, no captions, no labels
```

Padrões recorrentes nesses exemplos: metáfora **espacial/luminosa**, paleta sóbria com 2 cores fortes + 1 acento, iluminação direcional clara, composição landscape com sujeito ligeiramente descentralizado. Quando o tema for muito abstrato, prefira **objetos físicos imaginários** (cristais, redes, mecanismos, ribbons, partículas) a símbolos UI (caixas, setas, ícones).

**Trava de texto obrigatória** ao final: `no text, no letters, no words, no typography, no captions, no labels`. Sem ela, o modelo costuma inserir letras aleatórias.

**Use paths absolutos para `python ...generate_image.py` e para `--output`** — nunca relativos. Tarefas `Bash` executadas em paralelo ou em background no harness podem resolver o cwd em um diretório diferente do esperado, e aí `.claude/skills/gerar-imagem/scripts/generate_image.py` simplesmente não existe naquele ponto — o Python falha com `No such file or directory` e a capa nunca é gerada. Path absoluto elimina essa dependência implícita de cwd.

Monte os dois caminhos absolutos a partir do `<REPO_ROOT>` resolvido na etapa B:

- `<REPO_ROOT>/.claude/skills/gerar-imagem/scripts/generate_image.py`
- `<REPO_ROOT>/<book-dir>/<NN-slug-do-capitulo>/MM-slug-do-subcapitulo/cover.png`

```bash
python "<REPO_ROOT>/.claude/skills/gerar-imagem/scripts/generate_image.py" \
  --prompt "<prompt em ingles>" \
  --output "<REPO_ROOT>/<book-dir>/<NN-slug-do-capitulo>/MM-slug-do-subcapitulo/cover.png" \
  --size 1536x1024
```

Exemplo concreto no Windows (paths com barras normais funcionam no bash do Git/WSL):

```bash
python "C:/Users/joaop/Desktop/development/teste/aprendizado/.claude/skills/gerar-imagem/scripts/generate_image.py" \
  --prompt "Digital painting of ..." \
  --output "C:/Users/joaop/Desktop/development/teste/aprendizado/godot-para-um-rpg-2d-online-estilo-pokemon/09-npcs-dialogos-e-eventos-de-mundo/01-anatomia-de-um-npc/cover.png" \
  --size 1536x1024
```

**Dica de performance**: dispare as gerações de capa de múltiplos subcapítulos em **paralelo** no mesmo turno (várias chamadas `Bash` numa única resposta, idealmente com `run_in_background=true`), pois cada chamada é independente. Isso reduz o tempo total significativamente — mas só funciona de forma confiável com paths absolutos e com os diretórios já criados na etapa A.

**Etapa D — Escrever `CONTENT.md`** dentro do subdiretório de cada subcapítulo, com a estrutura abaixo. Os `Write` podem ser disparados em paralelo com as capas da etapa C, já que só dependem da etapa A.

### Formato de `CONTENT.md` do subcapítulo

Quatro seções obrigatórias, nesta ordem exata (espelham o `CONTENT.md` do capítulo, escopadas para o subcapítulo):

```markdown
# <Nome completo do subcapítulo>

![capa](cover.png)

## Sobre este subcapítulo

<1 a 2 parágrafos densos respondendo: qual a proposta deste subcapítulo dentro do capítulo? Que recorte do tema do capítulo ele cobre, por que esse recorte aparece nesta posição da sequência, e qual a promessa central que justifica sua existência como subcapítulo autônomo.>

## Estrutura

<1 parágrafo nomeando os grandes blocos/conceitos que o subcapítulo vai abordar, normalmente como uma enumeração inline `(1) ... ; (2) ... ; (3) ...`. Cada bloco com o nome do subtema e 2-5 exemplos concretos do que será coberto dentro dele. Essa seção é prévia dos conceitos atômicos que ficarão dentro deste subcapítulo.>

## Objetivo

<1 parágrafo descrevendo o que se espera que o leitor consiga fazer/entender ao terminar este subcapítulo. Foco em capacidades tangíveis e no encaixe com o subcapítulo seguinte (ou com o fechamento do capítulo, se for o último).>

## Fontes utilizadas

<Lista das referências reais pesquisadas que ancoraram a organização deste subcapítulo. Inclua URLs, livros, roadmaps, syllabi específicos para este subcapítulo. 3 a 8 itens.>

- [Título/descrição da fonte](url)
- ...
```

**Importante**:

- O recorte, a densidade e a linguagem devem respeitar o perfil do leitor fixado em `<book-dir>/INTRODUCTION.md` — não repita essa seção aqui, mas use-a como calibrador silencioso.
- Fontes citadas devem ser as que realmente informaram a organização deste subcapítulo, não uma cópia literal das fontes do capítulo. Reaproveite as do capítulo apenas se forem genuinamente específicas para este subcapítulo.

### Atualização do `CONTENT.md` do capítulo

Após materializar todos os subcapítulos, edite `<book-dir>/<NN-slug-do-capitulo>/CONTENT.md` para inserir uma nova seção **antes** de `## Fontes utilizadas`:

```markdown
## Subcapítulos

1. [<Nome do Subcapítulo 1>](MM-slug-do-subcapitulo-1/CONTENT.md) — <descrição de 1 linha>
2. [<Nome do Subcapítulo 2>](MM-slug-do-subcapitulo-2/CONTENT.md) — <descrição de 1 linha>
   ...
```

- Use links relativos (`MM-slug/CONTENT.md`), sem barra inicial — o `CONTENT.md` do capítulo está no mesmo nível dos subdiretórios de subcapítulo.
- A ordem dos itens **deve** bater com a ordem dos diretórios (o prefixo `MM` garante que `ls` também ordene igual).
- A descrição de 1 linha pode ser reaproveitada da lista impressa em chat.
- Se já existir uma seção `## Subcapítulos`, substitua-a integralmente (idempotência — permite re-rodar a skill sem duplicar).

As demais seções (`# Título`, `![capa]`, `## Sobre este capítulo`, `## Estrutura`, `## Objetivo`, `## Fontes utilizadas`) **não devem ser alteradas**.

Esse padrão espelha exatamente o que `estudo-listar-capitulos` faz com `INTRODUCTION.md` (`## Capítulos` antes de `## Fontes utilizadas`), só que um nível abaixo.

### Etapa E — Reconstruir o `STRUCT.md` via skill `estudo-atualizar-struct` (OBRIGATÓRIA)

**Esta etapa é obrigatória e não-pulável.** Toda execução desta skill — sem exceção, mesmo quando a materialização foi parcial, mesmo quando você quer apenas re-emitir uma capa, mesmo quando o usuário não pediu explicitamente — termina invocando a skill `estudo-atualizar-struct` passando o `<book-dir>` (a raiz do livro, não o diretório do capítulo) como argumento. Use o slash command `/estudo-atualizar-struct <book-dir>` ou o Skill tool — **não** rode `build_struct.py` diretamente daqui.

**Trate esta etapa como parte indissociável do encerramento.** Você não terminou a skill enquanto o `STRUCT.md` não tiver sido reconstruído. Se a invocação da skill falhar, sinalize o erro ao usuário em vez de encerrar silenciosamente — o estado do disco fica inconsistente (subcapítulos materializados mas índice desatualizado) e a próxima skill do método vai operar sobre contexto velho.

> **Observação sobre orquestração paralela**: quando o orquestrador dispara múltiplas instâncias desta skill em paralelo (uma por capítulo do mesmo livro), cada uma ainda invoca `/estudo-atualizar-struct` no fim. O script `build_struct.py` reconstrói o `STRUCT.md` lendo o estado completo do disco a cada execução, então o pior caso é "last-writer-wins" produzindo o índice mais atualizado — aceitável e auto-corretivo.

Por que delegar à skill em vez de chamar o script:

- **Ponto único de orquestração** — qualquer melhoria futura na geração do `STRUCT.md` (novo formato de árvore, novos níveis, fallbacks) se propaga automaticamente sem precisar reescrever esta skill.
- **Contrato estável** — esta skill se compromete só com "atualizar o STRUCT.md no fim", não com o caminho exato do script.
- **Coerência com as outras etapas** do método — todas as skills do método encerram delegando à `estudo-atualizar-struct`.

`STRUCT.md` é o índice em árvore do livro inteiro; mantê-lo atualizado a cada etapa do método garante que qualquer leitura ou skill subsequente receba um panorama coerente do livro como contexto rápido.

## Encerramento

Após materializar diretórios + capas + `CONTENT.md`s, atualizar o `CONTENT.md` do capítulo e refrescar o `STRUCT.md`, encerre com:

> _Subcapítulos materializados em `./<book-dir>/<NN-slug-do-capitulo>/MM-slug-do-subcapitulo/` (N subcapítulos, com capa e `CONTENT.md`). `CONTENT.md` do capítulo atualizado com os links e `STRUCT.md` do livro reconstruído._

**Não sugira** rodar a próxima skill, não anuncie próximos passos, não recomende continuação. A skill termina aqui — qualquer continuação do método é decisão do usuário.

## Exemplo

**Entrada:** `godot-para-um-rpg-2d-online-estilo-pokemon/09-npcs-dialogos-e-eventos-de-mundo/`

**Fluxo:**

1. Lê `./godot-para-um-rpg-2d-online-estilo-pokemon/INTRODUCTION.md` (contexto do livro, perfil do leitor, lista de capítulos irmãos).
2. Lista o diretório `./godot-para-um-rpg-2d-online-estilo-pokemon/` (capítulos irmãos: `08-cameras-...`, `10-combate-...`).
3. Lê `./godot-para-um-rpg-2d-online-estilo-pokemon/09-npcs-dialogos-e-eventos-de-mundo/CONTENT.md` (contrato do capítulo — a seção "Estrutura" já enumera (1) anatomia de um NPC; (2) sistema de diálogo; (3) dialogue como dados; (4) eventos de cutscene; (5) flags globais; (6) hands-on).
4. Faz 2–5 buscas web (tutoriais Godot de NPC/diálogo, docs oficiais).
5. Imprime lista no chat:

```
Subcapítulos do Capítulo "NPCs, Diálogos e Eventos de Mundo"
do livro "Godot para um RPG 2D Online Estilo Pokémon":

1. Anatomia de um NPC — ResourceCharacter, sprite, Area2D de interação e a state machine idle/patrol/talking
2. Sistema de Diálogo — caixa de texto com digitação, avanço por input, sinais de início e fim
3. Diálogos Ramificados e Escolhas do Jogador — árvores de decisão, retorno a nós anteriores e variáveis de estado
4. Diálogo como Dados (Resources) — modelar cada linha e cada ramo como Resource para facilitar escrita e tradução
5. Eventos de Cutscene — desabilitar input do jogador, mover NPC programaticamente, emitir sinal de fim
6. Flags Globais de Mundo — Autoload GameState com Dictionary[String, Variant] e disparo condicional de eventos
7. Hands-on — Construindo um NPC Reativo — criar do zero um NPC que pede ajuda e só volta a falar após uma condição
```

6. Materializa para cada subcapítulo:
   - `./godot-para-um-rpg-2d-online-estilo-pokemon/09-npcs-dialogos-e-eventos-de-mundo/01-anatomia-de-um-npc/cover.png` + `CONTENT.md`
   - `./godot-para-um-rpg-2d-online-estilo-pokemon/09-npcs-dialogos-e-eventos-de-mundo/02-sistema-de-dialogo/cover.png` + `CONTENT.md`
   - ...

7. Atualiza `./godot-para-um-rpg-2d-online-estilo-pokemon/09-npcs-dialogos-e-eventos-de-mundo/CONTENT.md` inserindo a seção `## Subcapítulos` com links relativos, antes de `## Fontes utilizadas`.

8. Encerra com a linha de fechamento.

## O que evitar

- **Não** pule a leitura das quatro fontes de contexto (STRUCT.md, INTRODUCTION.md, irmãos, CONTENT.md do capítulo). Cada uma calibra um aspecto diferente.
- **Não** pule a pesquisa web. Ela diferencia uma subdivisão verossímil de uma inventada.
- **Não** gere o `CONTENT.md` do subcapítulo sem a capa, ou a capa sem o `CONTENT.md` — os dois artefatos são pareados.
- **Não** use números romanos ou formatação exótica. Use `1.`, `2.`, `3.` e prefixo `MM` (zero-padded).
- **Não** misture subcapítulos em níveis de granularidade muito diferentes.
- **Não** invada o escopo de capítulos vizinhos. Se um suposto subcapítulo é, na verdade, o tema central do próximo capítulo, descarte-o ou sinalize ao usuário.
- **Não** crie subcapítulo-prefácio que apenas destrinche o framing do capítulo ("O Que É 'X'", "O Cliente Como Audiência", "A Fronteira Explícita", "O Que Fica Fora", "Os Livros Vizinhos do Método", "A Lógica do Arco", "O Checkpoint Final", "Definindo o Critério", "Calibrando Expectativas"). Esse conteúdo já vive em `## Sobre este capítulo` e `## Estrutura` do `CONTENT.md` do capítulo — replicá-lo em 5–6 subcapítulos meta é encher linguiça. Mesmo num capítulo introdutório, todos os subcapítulos devem agregar conceito técnico/prático novo (ver critério #7 — densidade prática). Se o capítulo realmente não sustenta 5 subcapítulos com densidade prática, isso é sinal de que o capítulo em si não devia existir e deve ser fundido com o próximo — sinalize ao usuário antes de inflar.
- **Não** gere menos de 5 subcapítulos. Se o capítulo parece não suportar 5, ele é pequeno demais e provavelmente devia ter sido fundido com outro — sinalize.
- **Não** altere seções do `CONTENT.md` do capítulo além da seção `## Subcapítulos`.
- **Não** duplique a seção `## Subcapítulos` se a skill rodar duas vezes — substitua.
- **Não** inclua texto dentro das imagens de capa (sempre `no text, no letters, no words`).
- **Não** traga a seção "Sobre o leitor" para dentro do `CONTENT.md` do subcapítulo — ela vive só no `INTRODUCTION.md` do livro.
- **Não** cite URLs na lista impressa em chat (URLs vivem nas seções "Fontes utilizadas" dos `CONTENT.md`s).
- **Não** traduza termos técnicos de uso idiomático em inglês para um pt-BR inventado (`signal` ≠ "sinal" forçado, `state machine` ≠ "máquina de estado" se o resto do livro usa o original). Mantenha coerência com como o termo aparece nos capítulos irmãos.
- **Não** force uma lista de subcapítulos a partir de fontes web fracas. Se a pesquisa em duas rodadas (com idiomas e plataformas variados) não trouxer 3 fontes-sinal, **pause e peça orientação ao usuário** em vez de inventar uma estrutura desancorada.
- **Não** finalize a Fase 1 sem checar que a soma dos subcapítulos entrega o `## Objetivo` do capítulo. Cobrir os blocos da `## Estrutura` é necessário, mas não suficiente — capacidades declaradas no `## Objetivo` precisam ter subcapítulo responsável.
- **Não** invente paleta de cores nova em capa de subcapítulo. Herde a paleta-base do `cover.png` do capítulo (que por sua vez herda do livro), e varie apenas em sujeito, iluminação e composição.
- **Não** rode `build_struct.py` direto na Etapa E — sempre delegue à skill `/estudo-atualizar-struct <book-dir>`. É o ponto único de orquestração do índice do livro.
- **Não pule, sob nenhuma circunstância, a Etapa E (`/estudo-atualizar-struct`).** Mesmo que a execução tenha sido parcial, mesmo que você só tenha regenerado uma capa, mesmo que o usuário não tenha pedido — esta skill **sempre** encerra invocando `/estudo-atualizar-struct <book-dir>`. Pular essa etapa deixa o `STRUCT.md` inconsistente com o disco e contamina todas as skills subsequentes do método.
- **Não** sugira nem auto-encadeie a próxima skill do método no encerramento — a skill termina com a linha factual e ponto.
