---
name: criar-livro
description: Primeira etapa do método de estudo estruturado. A partir de um tema, entrevista o usuário, pesquisa fontes na web e gera uma lista de recortes-livro calibrada ao nível dele; depois materializa o livro escolhido (diretório, capa, INTRODUCTION.md, STRUCT.md, entrada no README). Dispare em "quero aprender/estudar X", "trilhas/domínios de Y", "por onde começar Z".
---

# criar-livro

Primeira etapa do método de estudo estruturado. Transforma um tema amplo em uma lista de títulos-livro, cada um representando um recorte pedagógico distinto do tema e calibrado para o nível de experiência do usuário.

## Quando usar esta skill

O usuário chega com um tema (uma palavra, uma tecnologia, um assunto) e quer entender em quais frentes pode atacá-lo.

## Entrada

Um tema qualquer. Exemplos: `SQL`, `Machine Learning`, `Guitarra`, `Direito Tributário`, `Filosofia Analítica`, `Cozinha Italiana`.

Se o usuário não fornecer tema, pergunte uma única vez, de forma direta: _"Qual tema você quer estudar?"_

## Disambiguação prévia (quando o tema for amplo demais)

Antes de partir para a entrevista, avalie se o tema entregue é manifestamente **amplo demais** para gerar uma lista útil sem afunilar. Tópicos como `Python`, `Inteligência Artificial`, `Marketing`, `Direito`, `Música` cabem inteiros em estantes — qualquer lista produzida sem afunilar vai parecer rasa ou genérica.

Quando esse for o caso, faça **uma pergunta-flash** antes da entrevista:

> _"<Tema>" é vasto e tem recortes muito diferentes (ex: <subrecorte 1>, <subrecorte 2>, <subrecorte 3>). Você já tem algum desses em mente, ou quer que eu abra o leque inteiro?_

A resposta orienta o resto:

- **Se o usuário aponta um recorte** ("quero Python para automação", "AI generativa especificamente") → trate o recorte como o novo tema e siga para a entrevista normal.
- **Se o usuário pede "abrir o leque"** → siga para a entrevista, mas a lista final terá recortes mais largos e diversos para cobrir as várias frentes do tema.

Se o tema **já chega afunilado** ("SQL para BI", "guitarra blues", "TypeScript em monorepos") pule esta etapa — a disambiguação seria fricção desnecessária. Use bom senso: a régua é "essa palavra cobre 5 livros distintos ou 50?".

## Entrevista de expertise (obrigatória antes de gerar)

Antes de produzir qualquer lista, você **precisa** entender o ponto de partida do usuário. Faça uma única mensagem contendo 3 perguntas curtas:

1. **Nível atual no tema** — zero, iniciante, intermediário, avançado? Se o usuário quiser, peça um auto-exemplo ("consigo fazer uma query SELECT simples mas joins me embaralham").
2. **Experiências relacionadas** — o que ele já estudou ou praticou que se conecta com isso? Pode ser tangencial. Ofereça exemplos variados para estimular a resposta:
   - **Tecnologia/programação**: "sei Python mas nunca mexi em banco de dados", "trabalho com frontend e quero entender backend", "uso Excel avançado", "já programei em Java há anos", "conheço Git mas nunca usei Docker"
   - **Dados/análise**: "faço análises em pandas", "trabalho com planilhas complexas", "já usei Power BI/Tableau", "sei estatística básica", "mexi com R na faculdade"
   - **Acadêmico/teórico**: "tenho background em matemática", "estudei lógica formal", "li textos soltos sobre o tema", "fiz disciplina afim na graduação"
   - **Prático/criativo**: "toco outro instrumento há anos", "cozinho em casa toda semana", "já escrevi alguns contos", "pinto como hobby", "faço marcenaria amadora"
   - **Profissional adjacente**: "sou analista de negócios", "sou advogado de outra área", "atuo como PM", "trabalho como designer e quero entender código"
   - **Idiomas/humanidades**: "falo inglês fluente", "estudei filosofia antiga", "leio bastante história"
   - **Tangencial/nada**: "nada relacionado, puramente curiosidade", "nunca toquei no assunto"
3. **Objetivo** — o que ele quer fazer com esse conhecimento? (Trabalho? Projeto pessoal? Curiosidade? Prova/certificação?)

Não invente resposta pelo usuário. Espere a resposta antes de seguir. Se o usuário já tiver mencionado algum desses pontos espontaneamente, pule a pergunta correspondente e pergunte só o que falta.

### Por que isso importa

O mesmo tema ("SQL") gera listas radicalmente diferentes conforme o nível:

- **Iniciante** — priorizar recortes de fundamentos, leitura acessível, trilha linear ("SQL do Zero", "Fundamentos de Bancos Relacionais").
- **Intermediário** — priorizar recortes por aplicação/caso de uso ("SQL para Análise de Dados", "SQL para Backend").
- **Avançado** — priorizar recortes de profundidade e fronteira ("Otimização de Queries em OLTP de Alta Carga", "Internals do Query Planner do PostgreSQL").

Objetivo também muda tudo: alguém estudando pra entrevista técnica recebe recortes diferentes de quem estuda por curiosidade intelectual.

## Inventário de livros existentes (obrigatório antes da pesquisa)

Antes de pesquisar e gerar a lista, escaneie a raiz do diretório de trabalho atrás de **livros já materializados** — diretórios que contêm um `INTRODUCTION.md`. Use o glob `*/INTRODUCTION.md` (ou equivalente) para listar.

Para cada livro encontrado, leia o H1 do `INTRODUCTION.md` (basta as primeiras linhas) e anote: **título do livro** + **slug do diretório**. Esse mini-inventário tem dois usos:

1. **Evitar recortes redundantes na lista.** Se o tema atual tem proximidade com livros já materializados, ajuste a lista para não propor recortes que dupliquem livros existentes. Você pode até listar o livro existente como item já-pronto, marcado, para o usuário ter visibilidade — mas não o conte como recorte novo.
2. **Detectar colisão de slug antes da materialização.** Quando o usuário escolher um título, o slug derivado dele não pode colidir com um livro existente (a menos que seja deliberado — ver passo de idempotência).

Se a raiz não tiver nenhum livro materializado, registre isso mentalmente e siga em frente. Não exponha esse inventário ao usuário a menos que seja relevante para a decisão dele.

## Pesquisa de contexto (obrigatória)

Antes de escrever a lista final, faça **de 3 a 5 buscas na web** para ancorar os recortes em realidade. Boas buscas para esta skill:

- `"<tema> roadmap <ano atual>"` — encontra roadmaps públicos, que revelam recortes consolidados na prática.
- `"best books on <tema>"` ou `"melhores livros sobre <tema>"` — sumários de livros reais são goldmine de títulos verossímeis.
- `"<tema> syllabus <site:edu OR coursera OR edx>"` — ementas acadêmicas revelam recortes didaticamente reconhecidos.
- `"learn <tema> for <objetivo do usuário>"` — se o usuário deu um objetivo específico, busque abordagens alinhadas.

**Idioma das queries — escolha pelo perfil do tema, não pelo idioma do usuário:**

- **Tema cultural / local / regulatório** (Direito Tributário Brasileiro, Cozinha Mineira, ENEM, CLT, Concursos, História do Brasil) → **primárias em pt-BR**. Buscar em inglês traz pouco sinal e fontes que não cobrem a especificidade local. Use as palavras-chave que a comunidade brasileira da área usa.
- **Tema técnico-global** (SQL, Machine Learning, Godot, React, AWS) → **primárias em inglês** (a literatura, roadmaps, syllabi e docs oficiais quase sempre estão em inglês), com **1 query em pt-BR** para captar a comunidade brasileira (livros traduzidos, vídeos, artigos locais, jargão consagrado).
- **Tema híbrido** (UX Design, Marketing Digital, Gestão de Produto) → mix 50/50. Há literatura forte em ambos os idiomas e termos consagrados em cada um.

A regra acima vale para a etapa de pesquisa. **A lista numerada final continua no idioma do usuário** (padrão pt-BR), respeitando o critério #6 sobre termos técnicos no idioma de origem.

Use as buscas para:

- Validar que os recortes que você está propondo **existem mesmo** como trilhas ensinadas por aí.
- Descobrir recortes que você não teria pensado sozinho.
- Calibrar a linguagem/jargão do campo (certos temas têm nomenclatura específica que um iniciante espera ver).

**Importante — guarde as URLs.** Não cite as fontes na lista numerada (ela é enxuta por design), mas **registre internamente** as URLs encontradas: cada uma que ancorou a calibração de um recorte é uma forte candidata à seção `Fontes utilizadas` do `INTRODUCTION.md` (etapa 3 da materialização). Reaproveitar essas URLs evita uma rodada redundante de pesquisa e garante que as fontes citadas tenham relação real com o título escolhido. Para que sobre material suficiente para a seção (3 a 8 itens), faça pelo menos 3 buscas mesmo quando 2 pareceriam bastar.

### Retry quando o sinal das buscas for fraco

Após a primeira rodada de 3-5 buscas, faça uma checagem honesta: **quantas fontes deram sinal real** para calibrar recortes? Sinal real = fontes que efetivamente discutem o tema com profundidade pedagógica (livros publicados, syllabi acadêmicos, roadmaps maduros, artigos densos), não SEO genérico ou listas rasas.

- **Se 3+ fontes deram sinal real** → siga para a geração da lista. Cobertura suficiente.
- **Se menos de 3 fontes deram sinal real** → **não feche a lista ainda**. Rode uma segunda rodada com queries reformuladas:
  - Tente sinônimos/termos alternativos do campo (jargão diferente, mesmo conceito).
  - Troque o idioma da query (pt-BR ↔ inglês), respeitando o perfil do tema definido acima.
  - Mude a plataforma-alvo (de roadmap → syllabus, de "best books" → cursos universitários, de search aberta → site específico do nicho).
  - Adicione a faceta do objetivo do usuário se ainda não estava nas queries.
- **Se a segunda rodada também falhar** → o tema tem cobertura web fraca. **Não invente para preencher a lacuna**. Sinalize ao usuário:

  > _"<Tema>" tem cobertura web rasa nas minhas buscas — encontrei poucas fontes pedagógicas sólidas para calibrar recortes. Você consegue me indicar 1-2 referências (autor, livro, curso, comunidade) que vê como autoridade no tema? Com isso eu fecho uma lista mais confiável._

  Esperar 1-2 fontes do usuário antes de prosseguir é melhor que entregar lista grounded em vento.

## O que gerar

Uma lista **numerada**, com tamanho calibrado pelo nível do usuário e pela maturidade do tema. Faixas-alvo por nível:

- **Iniciante (zero ou quase-zero)** — 5 a 8 itens. Listas longas paralisam quem ainda não tem mapa mental do tema; melhor focar em fundamentos sólidos e poucos ângulos práticos.
- **Intermediário** — 7 a 12 itens. Já existe vocabulário; o usuário consegue descartar recortes que não interessam e escolher por aplicação.
- **Avançado** — 10 a 15+ itens. Há fome por especialização; recortes de fronteira, ecossistemas específicos e profundidades distintas justificam o volume.

Essas faixas são guias, não algemas. Um tema nicho pode fechar abaixo do mínimo; um tema vasto e maduro (ex: "Machine Learning") para um avançado pode passar de 15. **Deixe o tema mandar** — mas use a faixa do nível como ponto de partida e só extrapole quando houver razão clara.

Cada item contém:

- **Nome do título-livro** (antes de um travessão longo `—`)
- **Breve descrição de 1 linha** (depois do travessão) explicando o ângulo/escopo/público-alvo do recorte

### Quality bar da descrição de 1 linha

A descrição precisa ter **especificidade lexical** — substantivos concretos do campo, não adjetivos genéricos. Se a descrição também caberia em qualquer outro título da lista trocando uma palavra, ela é fraca.

|         | Exemplo                                                                                                                                      |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| ❌ Ruim | _SQL para Análise — foco em queries, ideal para iniciantes._                                                                                 |
| ❌ Ruim | _Modelagem Dimensional — fundamentos importantes da área._                                                                                   |
| ✅ Bom  | _SQL para Análise de Dados — extrai insights de bases existentes via queries analíticas, agregações, joins e window functions._              |
| ✅ Bom  | _Modelagem Dimensional e Data Warehousing com SQL — star schema, fatos, dimensões e a lógica de BI moderno aplicada em queries de produção._ |

A heurística rápida: a descrição boa cita **3-5 substantivos técnicos específicos** que aparecem nos sumários de livros reais sobre aquele recorte; a ruim só usa categorias largas ("queries", "fundamentos", "tópicos avançados").

### Critérios para a lista

Os critérios estão **ordenados por prioridade decrescente**. Em conflito real (não dá para satisfazer todos), prevalece sempre o critério de **número menor** — ele veta o de número maior. O #7 (Linguagem do usuário) é uma constraint ortogonal: não compete com os outros, sempre se aplica.

1. **Aderência ao nível do usuário** — a proporção de recortes de fundamentos vs. avançados deve refletir o nível informado na entrevista. Para iniciante, mais fundamentos; para avançado, mais especializações. _Em conflito_: melhor uma lista enxuta e bem-calibrada ao nível do que uma lista variada que mistura recortes incompatíveis com o ponto de partida do usuário.
2. **Títulos verossímeis** — o nome deve soar como um livro real que alguém poderia escrever e publicar. _Em conflito_: melhor sacrificar variedade ou balanceamento do que incluir um título inventado/genérico só para preencher cota.
3. **Recortes realmente distintos** — dois itens não devem cobrir a mesma coisa com nomes diferentes. _Em conflito_: prefira uma lista mais curta a uma lista que infla com itens redundantes para bater o número-alvo.
4. **Variedade de ângulos** — teórico, prático, por caso de uso, por nível, por ferramenta, por contexto profissional. _Em conflito_: aplica-se depois que aderência, verossimilhança e distinção estão garantidas.
5. **Balanceamento entre categorias** — cruze a lista contra os "Tipos de recorte que costumam funcionar" abaixo e garanta variedade real: nenhuma única categoria deve concentrar mais de ~40% dos itens. Listas com 6 de 10 itens em "por aplicação" e nada em "fundamentos" ou "metodológico" violam o critério de variedade (#4). Quando perceber concentração, troque o item mais fraco da categoria dominante por algo de uma categoria sub-representada — _desde que_ o substituto também passe nos critérios #1-#4.
6. **Cobertura do espectro** — mesmo calibrando pro nível do usuário, inclua 1 item um nível acima e 1 um nível abaixo, pra ele ter rota de evolução e rota de reforço. **Exceção nos extremos**: para iniciante absoluto (zero), não force um item "abaixo" — não há; ofereça só rota de evolução. Para avançado de fronteira (já dominando o estado da arte), não force um item "acima" sintético; nesse caso, foque em recortes laterais (especializações vizinhas, ecossistemas adjacentes) em vez de inventar um nível superior fictício. _Em conflito_: este é o critério de prioridade mais baixa entre os de qualidade — sacrifique a cobertura do espectro antes de violar qualquer um dos cinco anteriores.
7. **Linguagem do usuário** (constraint ortogonal) — os títulos seguem o idioma em que o usuário pediu (padrão pt-BR). **Termos técnicos consagrados ficam SEMPRE no idioma de origem** (geralmente inglês). Não traduza `Window Functions`, `prompt caching`, `event loop`, `data warehouse`, `dependency injection`, `tool calling`, `query planner`, `garbage collection`, etc. — esses circulam em pt-BR exatamente como o original e traduzir soa amador. A regra é: se a comunidade brasileira da área usa o termo em inglês na conversa do dia a dia, você usa em inglês também. Só traduza quando há um termo pt-BR consagrado de fato (ex: "banco de dados", "fila", "ponteiro").

### Tipos de recorte que costumam funcionar

- **Fundamentos** — "X: Fundamentos e Comandos Iniciais", "Introdução a X"
- **Por aplicação / caso de uso** — "X para Análise de Dados", "X para Desenvolvimento Web"
- **Por público-alvo** — "X para Desenvolvedores Backend", "X para Cientistas de Dados"
- **Avançado / especialização** — "X Avançado — Performance e Otimização"
- **Por ecossistema** — "X no Ecossistema PostgreSQL", "X em Ambientes de Nuvem"
- **Metodológico / conceitual** — "Fundamentos Teóricos de X", "A Filosofia do X"
- **Histórico / panorâmico** — "Uma História de X", "Panorama Contemporâneo de X"

## Formato de saída

```
Domínios de estudo sobre "<tema>" (calibrados para nível <nível> e objetivo <objetivo>):

1. <Título-livro 1> — <descrição em 1 linha>
2. <Título-livro 2> — <descrição em 1 linha>
3. <Título-livro 3> — <descrição em 1 linha>
...
```

Após a lista, uma única linha:

> _Escolha um destes para eu materializar o livro (diretório + capa + INTRODUCTION.md + STRUCT.md inicial + entrada no README do repositório)._

## Quando o usuário rejeita a lista (re-list dirigido)

Se o usuário responder com algo como "não gostei", "refaça", "não é isso que eu quero", **não regenere no escuro** — o risco é repetir o mesmo erro de calibração e queimar mais buscas web. Faça **uma única pergunta dirigida** antes de refazer:

> _O que ajustar na lista? (a) mais avançado / mais aplicado / mais teórico, (b) outro idioma de títulos, (c) mais ou menos itens, (d) algum recorte específico que faltou ou sobrou, (e) outra calibração que faria mais sentido?_

Use a resposta como sinal direcional concreto: refaça apenas as buscas e os recortes afetados, mantendo o que estava bom. Se o usuário reverter parcialmente ("os 3 primeiros estão ok, troca os outros"), preserve os itens aceitos e regere só o resto.

Se a rejeição for genérica e o usuário não der sinal claro mesmo após a pergunta, releia a entrevista — é provável que algo na resposta original tenha sido mal interpretado (nível subestimado, objetivo mal capturado). Reverifique a calibração antes de simplesmente refazer.

## Materialização do livro escolhido (obrigatória após a escolha)

Quando o usuário escolher um dos títulos da lista, esta skill **não termina** — ela entra numa segunda fase: criar o artefato físico do livro no disco.

### 0. Confirmar a escolha e checar idempotência

Antes de qualquer criação no disco, dois micro-passos defensivos:

**(a) Disambiguação da escolha.** O usuário tipicamente responde de forma curta ("o de PostgreSQL", "o número 5", "o terceiro") em vez de copiar o título exato. Antes de avançar, ecoe explicitamente:

> _Você escolheu **"<Título completo do item N>"** — slug derivado: `<slug>`. Pode confirmar? (sim / outro)_

Só prossiga após confirmação explícita. Se o usuário corrigir, recompute o slug e confirme de novo.

**(b) Idempotência.** Antes de criar diretório, capa ou `INTRODUCTION.md`, verifique se já existem artefatos no slug escolhido:

- Se `<slug>/` não existir → siga para o passo 1 normalmente.
- Se `<slug>/` existir mas estiver vazio → siga normalmente.
- Se `<slug>/INTRODUCTION.md`, `<slug>/cover.png` ou `<slug>/STRUCT.md` já existirem → **pare** e pergunte:

> _Já existe um livro materializado em `<slug>/` (arquivos: <lista>). Quer (1) sobrescrever tudo, (2) regenerar só o que falta, ou (3) cancelar?_

Não sobrescreva nada sem decisão explícita do usuário. Em caso de "regenerar só o que falta", processe apenas os artefatos ausentes nos passos 1–4 abaixo.

### 1. Criar o diretório do livro

No diretório de trabalho atual, crie uma pasta com o **slug** do nome do livro:

- Minúsculas
- Espaços viram `-`
- Remova acentos e caracteres especiais (`ç` → `c`, `á` → `a`)
- Remova pontuação (`—`, `:`, `,`, `.`)

Exemplos:

- "SQL para Análise de Dados" → `sql-para-analise-de-dados`
- "Da Pandas ao SQL" → `da-pandas-ao-sql`

### 2. Gerar a capa (proporção 1536x1024) via skill `gerar-imagem`

Esta skill **não** implementa geração de imagem — ela delega para a skill dedicada `gerar-imagem`, que é reutilizável e centraliza a integração com a OpenAI.

A capa usa o tamanho `1536x1024` apenas como **proporção** (mais larga do que alta, adequada para abrir o `INTRODUCTION.md`). Isso é uma especificação de dimensão da imagem — **não** é uma instrução de conteúdo. Não force o prompt a ser uma "paisagem" / cena de natureza só por causa do tamanho; o conteúdo da capa deve ser dirigido pela metáfora do livro, qualquer que seja o motivo visual.

Descreva mentalmente uma cena **metafórica** que represente o conceito do livro (não ilustração literal do tema). O prompt deve ser em **inglês** e seguir o template abaixo (todos os 6 campos obrigatórios, na ordem):

```
<SUBJECT — metáfora visual central, 1 a 2 frases>, <STYLE — termo técnico>,
<PALETTE — paleta de cores específica>, <LIGHTING — qualidade e direção da luz>,
<COMPOSITION — enquadramento e foco>, no text, no letters, no words, no typography, no captions, no labels
```

**Por campo:**

- **SUBJECT** — metáfora, não ilustração literal. Em vez de "a guitar with strings" para um livro de guitarra, algo como "a single hand reaching toward a luminous chord of light suspended in air". Diga o que está acontecendo na cena.
- **STYLE** — termo concreto reconhecível: `digital painting`, `isometric illustration`, `ink illustration`, `stylized vector art`, `low-poly 3D render`, `chiaroscuro oil painting`, `flat editorial illustration`. Evite "beautiful art" / "amazing".
- **PALETTE** — 2 a 4 cores nomeadas + qualidade ("muted earthy tones with deep teal", "warm amber and charcoal").
- **LIGHTING** — qualidade + direção: "soft volumetric light from upper-left", "dim ambient with rim lighting", "high-contrast sidelight".
- **COMPOSITION** — onde fica o sujeito, o que envolve a cena: "centered subject, low horizon, atmospheric depth", "off-center subject with negative space to the right".
- **No-text mandate** — sempre presente, literalmente como acima. Se o gerador entregar uma imagem com texto/letras, **regenere uma vez**; se insistir, ajuste o prompt removendo qualquer palavra que possa ser lida como pedido de tipografia (ex: "book cover" → "editorial illustration") e tente uma terceira vez. Após 3 falhas, alerte o usuário antes de prosseguir.

**Exemplos completos** (do nível esperado):

> _Livro: "SQL para Análise de Dados"_
> `A solitary cartographer drawing constellations of glowing data points across a dark blue table, connecting them with delicate luminous lines, digital painting, deep navy and warm amber accents, soft volumetric light from above-left, centered subject with atmospheric depth and negative space at the edges, no text, no letters, no words, no typography, no captions, no labels`

> _Livro: "Arquitetura de Sessões para Agentes"_
> `A series of interconnected glass vessels suspended in a dim chamber, each holding a softly pulsing ember, threads of light passing between them like a continuous current, isometric illustration, muted graphite and electric cyan palette, low-key dramatic lighting with rim light from the right, off-center composition with depth, no text, no letters, no words, no typography, no captions, no labels`

Invoque a skill executando o script diretamente:

```bash
python .claude/skills/gerar-imagem/scripts/generate_image.py \
  --prompt "<prompt em ingles>" \
  --output "<slug-do-livro>/cover.png" \
  --size 1536x1024
```

A imagem será salva em `<slug-do-livro>/cover.png`. A credencial OpenAI é lida automaticamente do `.env` do projeto pelo script.

### 3. Escrever `INTRODUCTION.md`

Dentro do diretório do livro, crie `INTRODUCTION.md` com **cinco seções obrigatórias, nesta ordem exata**:

```markdown
# <Nome completo do livro>

![capa](cover.png)

## Sobre este livro

<1 a 2 parágrafos densos respondendo: qual a proposta deste livro? Que recorte do tema ele cobre, por que esse recorte foi escolhido como frente de estudo, e qual a promessa central que justifica sua existência. Foque na proposta — os blocos de conteúdo e os objetivos têm seções próprias.>

## Estrutura

<1 parágrafo nomeando os grandes blocos de conceitos que serão abordados, normalmente como uma enumeração inline `(1) ... ; (2) ... ; (3) ...`. Cada bloco com o nome do tema e 2-5 exemplos concretos de subtemas dentro dele, no estilo do exemplo abaixo.>

> Exemplo: "Os grandes blocos são: (1) fundamentos da arquitetura do Godot que importam para um RPG 2D — nós, cenas, scripts, sinais, recursos; (2) os sistemas centrais de um Pokémon-like — movimento em grid, tilemaps de mundo, NPCs e diálogos, combate por turnos, inventário e party; (3) a camada online — modelo cliente-servidor, autoridade do servidor, sincronização e persistência; (4) a integração com a pipeline de assets gerados por AI (sprites, tilesets e trilhas)."

## Objetivo

<1 parágrafo descrevendo o que se espera que o leitor consiga fazer/entender ao terminar o livro. Foco em capacidades tangíveis e no encaixe com os próximos passos do método de estudo.>

> Exemplo: "Ao terminar, o leitor terá uma compreensão funcional e prática do Godot 4 suficiente para sustentar um projeto pessoal de longa duração, terá uma decisão técnica fundamentada sobre o uso da engine para esse tipo de jogo, e estará apto a continuar nos livros sobre arquitetura de MMOs, pipeline de arte com AI e mecânicas de RPG sem precisar revisitar fundamentos."

## Sobre o leitor

<2 a 3 parágrafos densos, em terceira pessoa, respondendo:

- Quem é o leitor (perfil profissional/pessoal, contexto)
- Quais experiências ele já trouxe (tecnologias, áreas adjacentes, contextos profissionais — exatamente como ele descreveu na entrevista)
- Qual o objetivo dele com este livro (objetivo declarado na entrevista)
- Qual o ponto de partida dele neste tema específico (nível atual, gaps, pré-conhecimento)

Não invente nem extrapole. Se o leitor disse "trabalho com mobile e dados e nunca abri uma engine", essa é a base — não promova ele a "expert em frontend" nem invente afinidade com C#. A função desta seção é tornar explícito o perfil para o qual o livro foi calibrado, ancorando todas as decisões editoriais e servindo de contexto para os próximos livros/capítulos do método.>

## Fontes utilizadas

<Lista das referências reais pesquisadas na etapa de contexto que ancoraram o título e a proposta do livro. Inclua URLs, nomes de livros, roadmaps, syllabi. 3 a 8 itens.>

- [Título/descrição da fonte](url)
- ...
```

**Importante**: diferente da lista inicial (onde fontes não são citadas), o `INTRODUCTION.md` **deve** listar as fontes — elas justificam a legitimidade do recorte escolhido e servem ao leitor como ponto de partida se quiser ir além.

**Sobre a separação em 5 seções**: cada seção responde a uma pergunta diferente e fica fácil de localizar — proposta (Sobre este livro), conteúdo (Estrutura), promessa de capacidade (Objetivo), perfil-alvo (Sobre o leitor), legitimidade (Fontes). Resista à tentação de fundir seções em parágrafos longos: o valor da estrutura é deixar cada dimensão visível por si só, especialmente para skills posteriores do método que consultam o `INTRODUCTION.md` como contexto.

### 4. Reconstruir o `STRUCT.md` via skill `estudo-atualizar-struct`

Por fim, **invoque a skill `estudo-atualizar-struct`** passando o `<slug-do-livro>` como argumento, para criar o `STRUCT.md` inicial na raiz do livro (nesta etapa ainda só com a linha do livro — capítulos, subcapítulos e conceitos serão adicionados pelas skills seguintes). Use o slash command `/estudo-atualizar-struct <slug-do-livro>` ou o Skill tool — não rode `build_struct.py` diretamente daqui.

Por que delegar à skill em vez de chamar o script:

- **Ponto único de orquestração** — qualquer melhoria futura na geração do `STRUCT.md` (novo formato de árvore, novos níveis, fallbacks) se propaga automaticamente sem precisar reescrever esta skill.
- **Contrato estável** — esta skill se compromete só com "criar o STRUCT.md inicial no fim", não com o caminho exato do script.
- **Coerência com as outras etapas** do método — todas as skills do método encerram delegando à `estudo-atualizar-struct`.

`STRUCT.md` é o índice em árvore do livro inteiro; ele será usado como contexto rápido por todas as skills posteriores do método e atualizado por elas.

### 5. Atualizar o `README.md` da raiz do repositório

A regra de organização do repositório (definida no `CLAUDE.md` raiz) exige que **todo livro novo apareça no `README.md`** como sub-seção sob `## Livros`, no formato canônico:

```markdown
### [<Título completo do livro>](<slug>/INTRODUCTION.md)

![capa](<slug>/cover.png)

<parágrafo-gancho de 2 a 4 linhas, em prosa compacta, derivado das seções "Sobre este livro" + "Estrutura" + "Objetivo" do `INTRODUCTION.md` — destila o livro como gancho de leitura, NÃO cola literal>
```

Procedimento:

1. **Leia** o `README.md` da raiz para conferir o estado atual (cabeçalho, lista de livros existentes, ordem).
2. **Sintetize** o parágrafo-gancho a partir do `INTRODUCTION.md` que você acabou de escrever. Reescreva em prosa compacta — não copie períodos inteiros do `INTRODUCTION.md`, ele já está linkado. O gancho deve dar ao leitor o sabor do livro em uma respiração.
3. **Insira** a nova sub-seção respeitando a ordem do índice (a regra do `CLAUDE.md` define: ordem cronológica/lógica do método, livros fundamentais primeiro; sem ordem óbvia, alfabética por slug). Quando em dúvida, anexe ao final.
4. **Edite** o `README.md` preservando todo o conteúdo já existente (cabeçalho, livros anteriores). Use `Edit` cirúrgico — nunca reescreva o arquivo inteiro.

Se o livro com esse slug já tem entrada no `README.md` (caso de regeneração via passo 0), atualize a entrada existente em vez de criar uma nova.

### 6. Delegar a criação dos capítulos ao agente `criador-de-capitulos`

Com o livro materializado (diretório, capa, `INTRODUCTION.md`, `STRUCT.md` e entrada no `README.md`), invoque o agente `criador-de-capitulos` (definido em `.claude/agents/criador-de-capitulos.md`) passando o slug do livro. O agente roda em contexto isolado, lê o `INTRODUCTION.md` recém-escrito como contrato, executa o protocolo da skill `estudo-listar-capitulos` (pesquisa web + lista de 8 a 15 capítulos + materialização de subdiretórios `NN-slug/` com capa e `CONTENT.md`), atualiza a seção `## Capítulos` no `INTRODUCTION.md` e reconstrói o `STRUCT.md` no fim.

Use o `Agent` tool com `subagent_type: "criador-de-capitulos"` e prompt mínimo:

```
Livro: <slug-do-livro>
```

**Aguarde** o agente terminar antes de seguir para o encerramento. Tratamento das três respostas possíveis:

- `CONCLUÍDO: <N> capítulos materializados...` → siga para o encerramento.
- `BLOQUEADO: <motivo>. Pergunta a fazer ao usuário: <texto>.` → repasse a pergunta literalmente ao usuário, colete a resposta, e re-invoque o agente com o esclarecimento embutido no prompt (ex: `Livro: <slug>\nEsclarecimento: <resposta do usuário>`).
- `ERRO: <descrição>...` → mostre o erro ao usuário e pare. Não tente recuperar sozinho — o livro já está materializado, faltam só os capítulos, e o usuário pode invocar o agente manualmente quando o problema for resolvido.

**Por que delegar a um agente em vez de inlinear o protocolo de capítulos.** O protocolo de `estudo-listar-capitulos` tem ~360 linhas, dispara 2–5 buscas web e gera 8–15 capas em paralelo. Inlinear isso aqui faria a janela de contexto da `criar-livro` (que já consumiu espaço com a entrevista, a pesquisa do tema e a materialização do livro) explodir bem na metade da geração de capítulos. O agente isola esse trabalho pesado e devolve só o veredito.

### Encerramento

Após o agente `criador-de-capitulos` retornar `CONCLUÍDO`, encerre com:

> _Livro materializado em `./<slug-do-livro>/` com capa, introdução, `STRUCT.md`, entrada no `README.md` e <N> capítulos com capa e `CONTENT.md` esqueleto._

## Exemplo

**Entrada inicial:** "Quero aprender SQL"

**Sua primeira resposta (entrevista):**

> Pra calibrar os recortes certos, me conta rapidinho:
>
> 1. Seu nível atual em SQL — zero, iniciante, intermediário, avançado?
> 2. Já teve experiência com algo relacionado? (Python, Excel avançado, outro banco, modelagem de dados...)
> 3. Qual seu objetivo? (Trabalho? Projeto pessoal? Entrevista? Curiosidade?)

**Resposta do usuário:** "Intermediário. Uso Python e pandas no trabalho pra análise. Objetivo é me virar em dashboards de BI e dar menos trabalho pros analistas."

**Sua saída (após 3-5 buscas web):**

```
Domínios de estudo sobre "SQL" (calibrados para nível intermediário e objetivo analítico/BI):

1. SQL para Análise de Dados — foco em extrair insights de bases existentes, com ênfase em queries analíticas, agregações, joins e window functions
2. SQL para Business Intelligence e Dashboards — foco em queries otimizadas para ferramentas como Metabase, Looker, Power BI, e em modelagem de métricas
3. Da Pandas ao SQL — transição estruturada para quem pensa em DataFrames e quer traduzir para SQL idiomático
4. Modelagem Dimensional e Data Warehousing com SQL — foco em star schema, fatos, dimensões e a lógica de BI moderno
5. SQL Avançado — Performance e Otimização de Consultas Analíticas — foco em índices, planos de execução e anti-patterns em queries pesadas
6. SQL para Engenharia de Dados — foco em pipelines, batch jobs, integração com dbt/airflow
7. SQL: Fundamentos Revisitados — recorte de reforço, pra fechar lacunas de base que intermediários costumam ter
8. SQL em PostgreSQL — recorte aprofundado em um motor específico, com CTEs recursivos, tipos avançados e funções nativas

*Escolha um destes para eu materializar o livro.*
```

## O que evitar

- **Não** pule a entrevista de expertise. Ela é obrigatória.
- **Não** pule a pesquisa web. Mesmo que você tenha conhecimento do tema, 3-5 buscas calibram a lista e geram fontes para o `INTRODUCTION.md`.
- **Não** numere com formatos exóticos (`I.`, `a)`) — use `1.`, `2.`, `3.`.
- **Não** invente recortes genéricos que servem pra qualquer tema sem esforço (ex: "Tópicos Gerais de X"). Cada título deve ter um ângulo real.
- **Não** encerre com parágrafos extensos de contextualização. A skill é enxuta por design.
- **Não** limite artificialmente o tamanho da lista. Se o tema pede 12, dê 12. Se pede 5, dê 5.
- **Não** cite URLs ou fontes específicas na saída — elas serviram só pra calibrar.
