---
name: estudo-listar-capitulos
description: Gera uma sequência pedagógica de capítulos de um livro de estudo já materializado pela skill `estudo-listar-dominios` e materializa cada capítulo no disco (subdiretório, capa 1536x1024 e `CONTENT.md`), além de atualizar o `INTRODUCTION.md` do livro com links para os capítulos. Use quando o usuário apresentar o **nome do diretório de um livro** (ex: `sql-para-analise-de-dados`) e pedir "gera os capítulos", "monta o sumário", "quebra esse livro em capítulos", "estrutura esse livro", "materializa os capítulos", ou simplesmente invocar a skill passando o slug do livro. Também dispare se o usuário disser "já tenho o livro X pronto, agora quero os capítulos". Antes de gerar, a skill lê o `INTRODUCTION.md` do diretório do livro como contexto obrigatório e pesquisa fontes reais na internet para ancorar a sequência. Esta é a **segunda etapa** do método de estudo estruturado.
---

# estudo-listar-capitulos

Segunda etapa do método de estudo estruturado. Recebe o diretório de um livro já materializado (pela skill `estudo-listar-dominios`), desdobra-o em capítulos pedagogicamente ordenados, e **materializa cada capítulo no disco** como um subdiretório do livro com capa e `CONTENT.md`. Por fim, atualiza o `INTRODUCTION.md` do livro com links para cada capítulo na ordem.

## Quando usar

O usuário já tem um livro materializado (diretório com `cover.png` + `INTRODUCTION.md`) e quer a próxima camada: o sumário expandido em capítulos concretos, com seus próprios artefatos. A saída alimenta a skill `estudo-listar-subcapitulos`.

## Entrada

O **nome do diretório do livro** (relativo ao diretório de trabalho atual). Exemplos:

- `sql-para-analise-de-dados`
- `godot-para-um-rpg-2d-online-estilo-pokemon`
- `direito-tributario-aplicado-a-pessoa-juridica`

Se o usuário não trouxer o diretório, pergunte uma única vez: _"Qual é o diretório do livro (ex: `sql-para-analise-de-dados`) que você quer destrinchar em capítulos?"_

Valide que o diretório existe e contém `INTRODUCTION.md`. Se não, avise e interrompa — a skill depende do artefato gerado por `estudo-listar-dominios`.

## Contexto obrigatório (duas fontes)

Antes de qualquer pesquisa ou geração, leia as duas fontes na ordem abaixo:

### 1. `<book-dir>/STRUCT.md` — panorama rápido do livro

Carrega o mapa visual completo do livro (gerado pela skill `estudo-atualizar-struct`): título do livro e quaisquer capítulos/subcapítulos/conceitos já materializados em rodadas anteriores. Use isso para se localizar **rapidamente** sem precisar abrir vários CONTENT.md. Em particular, se a skill estiver sendo re-rodada sobre um livro que já tem capítulos, o `STRUCT.md` mostra o estado atual antes de você decidir o que regenerar.

Se `STRUCT.md` ainda não existe (livro recém-materializado por `estudo-listar-dominios` que tenha pulado o passo), siga em frente — você vai criá-lo no fim.

### 2. `<book-dir>/INTRODUCTION.md` — o contrato do livro

Leia por completo. Ele contém todos os insumos que calibram os capítulos:

- **Título completo do livro** (H1)
- **Sobre este livro** — a proposta e o recorte escolhido
- **Estrutura** — os grandes blocos de conteúdo (isso vira a espinha dorsal dos capítulos)
- **Objetivo** — a promessa de capacidade ao fim do livro
- **Sobre o leitor** — nível, experiências adjacentes, objetivo declarado (calibra a profundidade e a linguagem de cada capítulo)
- **Fontes utilizadas** — referências que já ancoraram o recorte do livro

Os capítulos **devem respeitar** o recorte e o perfil do leitor já fixados no `INTRODUCTION.md`. Não invente escopos que o livro não promete; não rebaixe a densidade para um nível que contraria o perfil descrito em "Sobre o leitor".

## Pesquisa de contexto (obrigatória)

Mesmo com o `INTRODUCTION.md` em mãos, faça **de 2 a 5 buscas na web** para ancorar a sequência de capítulos em trilhas reais de ensino. Boas buscas:

- `"<título do livro> table of contents"` / `"<título similar> sumário"` — sumários de livros próximos são goldmine.
- `"<tema do livro> syllabus"` / `"<tema> ementa"` — cursos reais revelam a sequência didática aceita.
- `"<tema do livro> roadmap <ano atual>"` — roadmaps comunitários (roadmap.sh, etc.) mostram ordem canônica.
- `"learn <tema do livro> step by step"` / `"trilha de <tema>"` — tutoriais consolidados revelam o arco pedagógico.

Use as buscas para verificar ordem canônica, descobrir capítulos que você poderia estar esquecendo, e calibrar terminologia. As URLs relevantes serão reaproveitadas nas seções "Fontes utilizadas" dos `CONTENT.md` dos capítulos.

Ao escrever o `CONTENT.md` de cada capítulo, **só dispare busca adicional quando as fontes do livro comprovadamente não cobrem o subtema do capítulo**. A regra existe porque "1–2 buscas extras × 12 capítulos = até 24 chamadas web sem necessidade" — multiplicar buscas é caro e quase sempre redundante quando o `INTRODUCTION.md` já trouxe 5–8 fontes pedagogicamente densas.

Critério prático antes de buscar:

1. Liste mentalmente as fontes do `INTRODUCTION.md` do livro.
2. Pergunte: **3 ou mais delas tratam diretamente do subtema deste capítulo** (não só do tema geral)? Se sim → reaproveite-as e **não** faça busca extra.
3. Se não — ex: as fontes do livro são todas roadmaps genéricos de SQL e o capítulo é "Window Functions" especificamente — então **1 busca alvo basta** (ex: `"window functions" tutorial postgres`). Não rode duas só para "ter mais opções".

Se mesmo a busca alvo trouxer pouco sinal, prefira marcar a fonte como "[a complementar]" e seguir, em vez de gastar buscas em cascata. Você terá outra rodada de pesquisa nas etapas seguintes do método (`estudo-listar-subcapitulos`, `estudo-listar-conceitos`) já no nível certo de granularidade.

### Idioma das queries — regra explícita

A escolha de idioma depende da natureza do tema. Vá onde está o sinal real do nicho, não onde é mais fácil pesquisar.

- **Tema técnico-global** (SQL, machine learning, Godot, Kubernetes, React, system design, DevOps, observability): primárias em **inglês** — sumários, syllabi e roadmaps internacionais dominam o sinal. Inclua **1 busca em pt-BR** para capturar terminologia local e cursos brasileiros.
- **Tema cultural / local / regulatório / setorial-BR** (Direito Tributário Brasileiro, Cozinha Mineira, ENEM, CLT, Reforma Tributária, História do Brasil, MEI/Simples Nacional, OAB, SUS): primárias em **pt-BR** — a vertente local concentra o sinal real; o inglês traz pouco ou nada. Use inglês só se o tema tem variante internacional comparável (ex: "comparative tax law").
- **Tema misto** (Direito Comparado, Estatística aplicada à pesquisa em saúde no SUS, História do Direito): equilibre — ~2 em pt-BR + ~2 em inglês.

### Sinal fraco — segunda rodada de busca

Após as buscas iniciais, conte quantas trouxeram **sinal real**: ementa de curso reconhecido, sumário de livro estabelecido, roadmap publicado, syllabus universitário (`site:edu`, `site:usp.br`, `site:mit.edu`), post consolidado de profissionais do nicho. **Não conte** posts de blog genéricos, conteúdo claramente gerado por IA, indexadores SEO ou listas rasas.

**Se < 3 fontes deram sinal real**, rode uma **segunda rodada** com queries reformuladas:

- Troque sinônimos (ex: `ementa` → `programa de ensino` → `plano de aula`; `roadmap` → `trilha` → `learning path`; `syllabus` → `curriculum` → `course outline`).
- Troque o idioma — se a primeira foi em pt-BR, tente em inglês; e vice-versa (mesmo violando a regra acima — se o sinal está fraco, vale tatear).
- Tente plataformas diferentes: `site:reddit.com`, `site:dev.to`, `site:medium.com`, `site:edu`, `site:gov.br`, `site:github.com`, fóruns específicos do nicho (Stack Overflow, Kaggle, JusBrasil, conjur.com.br…).

**Se mesmo após a segunda rodada o sinal continuar fraco** (< 3 fontes reais), pare e peça orientação ao usuário:

> _O tema "<X>" tem cobertura web fraca — não consegui ancorar a sequência em fontes públicas robustas. Você consegue indicar 2–3 referências (livros, cursos, syllabi, profissionais que admira) que devo usar como espinha dorsal? Sem isso, a sequência sai inventada._

Não force a geração com sinal fraco. Um pedido de orientação ancorado vale mais que um sumário plausível mas sem lastro.

## O que gerar (lista + materialização)

A skill tem duas fases:

### Fase 1 — Listagem em chat

Gere e imprima no chat uma lista **numerada** em **sequência pedagógica rigorosa** (um capítulo não depende de nada que venha depois).

**Faixa típica: 8 a 15 capítulos.** Livros amplos e maduros (ex: "Machine Learning para Engenheiros") podem chegar a 18–20; livros focados fecham em 8.

**Mínimo aceitável: 6.** Se você está chegando a 5 ou menos sem inflar artificialmente, **pare e sinalize ao usuário antes de gerar**: o tema provavelmente é pequeno demais para sustentar um livro próprio (talvez devesse ser um capítulo dentro de um livro vizinho, ou ser fundido com outro recorte). Mensagem sugerida:

> _O recorte "<X>" parece render só ~5 capítulos sem forçar — é sinal de que o tema é mais um **capítulo** do que um livro inteiro. Quer que eu (a) prossiga assim mesmo com 5–6 capítulos enxutos, (b) sugira um recorte vizinho mais amplo que englobe esse, ou (c) cancele para você ajustar o livro lá em `estudo-listar-dominios`?_

Não há teto rígido, mas inflar com "Conclusão", "Glossário" ou capítulos-irmão duplicados para bater 8 viola o critério #2 (verossimilhança) e #3 (recortes distintos) abaixo.

Formato:

```
Capítulos do livro "<título do livro>":

1. <Capítulo 1> — <descrição em 1 linha>
2. <Capítulo 2> — <descrição em 1 linha>
...
```

#### Critérios para a sequência

1. **Ordem do simples ao complexo** — fundamentos antes, especializações depois.
2. **Pré-requisitos respeitados** — o capítulo N não pode usar algo que só aparece em capítulos > N.
3. **Fechamento com aplicação** — os últimos capítulos costumam ser integração, prática ou tópicos avançados.
4. **Aderência ao recorte** — respeite a promessa do título e o perfil do leitor fixado no `INTRODUCTION.md`.
5. **Granularidade equilibrada — antecipando subcapítulos.** Nada de um capítulo gigante ao lado de um minúsculo. Como régua de calibração olhando para a próxima etapa do método: **cada capítulo deve render ~5 a 8 subcapítulos** quando `estudo-listar-subcapitulos` rodar sobre ele. Use isso para detectar capítulos mal-dimensionados antes de materializar:
   - **Renderia só 2–3 subcapítulos** → fino demais. Funda com o capítulo vizinho ou promova um dos subcapítulos do vizinho a este lugar.
   - **Renderia 12+ subcapítulos** → amplo demais. Quebre em dois capítulos seguidos no mesmo bloco temático (ex: "Joins — Fundamentos" + "Joins — Casos Avançados" em vez de "Joins" único).
   - Faça esse exercício mental para cada item da lista antes de imprimir. É barato e evita retrabalho a jusante.
6. **Arco pedagógico típico**: fundamentos → blocos técnicos centrais → composição/integração → casos avançados → prática e fechamento. Capítulo de "introdução e motivação" entra **só** quando o `## Sobre o leitor` descreve leitor genuinamente iniciante no tema. Quando o leitor é experiente e o livro é prático/aplicado (POC, MVP, "feature em produção", "trilha hands-on", "X aplicado a Y"), **abra direto com o primeiro bloco técnico** — o `INTRODUCTION.md` já motivou o livro, replicar isso em capítulo é redundância.
7. **Terminologia técnica idiomática** — mantenha cada termo no idioma em que ele é realmente usado pelo nicho. Se o profissional da área diz `JOIN`, `framework`, `deadlock`, `retry`, `throttling`, `observability`, `syscall`, `websocket`, `signal`, `tilemap`, `endpoint`, `pipeline`, `state machine`, **não traduza**. Traduza apenas quando o pt-BR já tem termo consagrado de fato no campo (ex: `compilador` em vez de `compiler`; `fila` em vez de `queue` no dia a dia; `depuração` só se a equipe usa, senão `debug`). A regra é descritiva: o critério é o que o leitor real do nicho usaria conversando com um colega, não o que parece "mais português". Aplica-se aos títulos, descrições e ao texto dos `CONTENT.md`.
8. **Densidade prática — cada capítulo agrega conhecimento técnico/prático novo.** Esta é a régua mais importante quando o `## Sobre o leitor` descreve leitor experiente e o livro promete entrega prática. Capítulos cujo conteúdo é **apenas framing** — reformular o recorte do livro, definir o critério de pronto, mapear o público-alvo, listar o que fica fora, descrever a lógica da sequência, antecipar o checkpoint final, "conhecendo a tecnologia X" sem ensinar nada concreto — **não cabem como capítulos**. Esse material já vive no `INTRODUCTION.md` (em `## Sobre este livro`, `## Estrutura`, `## Objetivo`, `## Sobre o leitor`); replicá-lo em capítulo é encher linguiça. Critério prático para cada item da lista: pergunte "**que conhecimento técnico, conceito, prática, decisão de implementação ou trade-off concreto o leitor sai sabendo depois deste capítulo que ele não sabia antes?**". Se a resposta é "ele entende melhor o recorte do livro" / "ele sabe o que será construído" / "ele tem o arco mapeado" / "ele sabe quem é o cliente da POC" → **capítulo banido**, esse material é do `INTRODUCTION.md`. Se a resposta é "ele entende os 4 modos de execução do pi.dev e quando usar cada um" / "ele sabe configurar um JWT authorizer no API Gateway" / "ele entende o trade-off entre EFS e S3 para sessões pi.dev" → capítulo válido. Quando o livro é introdutório e o leitor é iniciante, capítulos que estabelecem vocabulário e mapa mental podem caber — mas mesmo assim devem **introduzir conceitos técnicos do tema**, nunca apenas o livro em si.

#### Validação cruzada antes de imprimir a lista

Antes de imprimir a lista no chat, faça **duas checagens** contra o `INTRODUCTION.md` do livro. Elas não são opcionais — sem isso, a lista pode estar plausível mas desalinhada com o que o livro prometeu.

**Checagem 1 — cobertura dos blocos da `## Estrutura`.** A seção `## Estrutura` do `INTRODUCTION.md` enumera os grandes blocos do livro `(1) ... ; (2) ... ; (3) ...`. Esses blocos são o contrato de escopo. Monte mentalmente uma matriz `bloco × capítulos`:

```
Bloco (1) ........................ → cap. 02, 03, 04
Bloco (2) ........................ → cap. 05, 06
Bloco (3) ........................ → cap. 07, 08, 09, 10
Bloco (4) ........................ → cap. 11, 12
Bloco órfão? (sem capítulo)        → ✗ — falha
Capítulo órfão? (fora dos blocos)  → ✗ — falha
```

Regras:

- **Cada bloco precisa ter ≥ 1 capítulo correspondente.** Se um bloco fica sem capítulo, ou você esqueceu de cobrir um pedaço da promessa do livro, ou o bloco em si é supérfluo (e nesse caso o `INTRODUCTION.md` é que está errado — sinalize ao usuário).
- **Cada capítulo precisa cair em pelo menos um bloco.** Se um capítulo é órfão, ou ele invade escopo de outro livro (descarte), ou a `## Estrutura` do livro está incompleta (sinalize ao usuário antes de prosseguir, oferecendo ajustar a seção).
- Capítulos de "Introdução" e "Hands-on/fechamento" tipicamente atravessam blocos — está OK marcá-los como "transversal" em vez de associar a um bloco único.

**Checagem 2 — cobertura do `## Objetivo` do livro.** A seção `## Objetivo` declara a capacidade que o leitor terá ao terminar o livro inteiro. Pergunte: **se o leitor estudar de cabo a rabo todos os capítulos da minha lista, ele consegue fazer/entender o que o Objetivo promete?**

- Se **sim** → segue.
- Se **não, falta capacidade Y** → insira o(s) capítulo(s) que cobre(m) Y, na posição pedagógica certa, antes de imprimir.
- Se **sim, mas com sobra desnecessária** → revise se algum capítulo está fora da promessa (vai além do que o livro prometeu) — esse capítulo provavelmente pertence a outro livro.

Faça as duas checagens **silenciosamente**, sem expor a matriz ao usuário (a lista impressa em chat fica enxuta). Se uma checagem falhar e exigir intervenção do usuário (bloco órfão, capítulo órfão, lacuna no Objetivo que você não consegue resolver sozinho), pare e pergunte antes de imprimir a lista.

### Fase 2 — Materialização no disco

Materialize todos os capítulos seguindo **exatamente** esta ordem de etapas. A ordem importa: a geração da capa só pode rodar depois que o diretório de destino existe, senão o script falha ao salvar.

**Etapa A — Criar todos os subdiretórios primeiro.** Em `<book-dir>/`, crie de uma vez todos os subdiretórios dos capítulos, prefixados pela ordem zero-padded:

- Formato: `NN-slug-do-capitulo/` onde `NN` é `01, 02, …, 10, 11`.
- Regras do slug: minúsculas, espaços viram `-`, remova acentos (`ç`→`c`, `á`→`a`), remova pontuação (`—`, `:`, `,`, `.`).
- Exemplos: `01-introducao/`, `06-joins-combinando-tabelas/`.

Um único `mkdir -p <dir1> <dir2> ...` resolve todos de uma vez. Só avance para a etapa B depois que os 15+ diretórios existirem.

**Etapa B — Resolver a raiz absoluta do projeto uma vez.** Antes de disparar qualquer geração de capa, identifique `<REPO_ROOT>` — o diretório que contém o `<book-dir>`. Você vai precisar dele para montar os paths absolutos da etapa C. Costuma bastar um `pwd` na raiz de trabalho (o cwd padrão do harness); em último caso, suba de `<book-dir>` até achar a pasta `.claude/`.

**Etapa C — Gerar as capas 1536x1024 em paralelo.** Para cada capítulo, descreva mentalmente uma cena **metafórica** que represente o conceito (não ilustração literal). Prompt sempre em **inglês**.

**Antes de gerar qualquer capa, fixe a paleta-base do livro.** Abra `<book-dir>/cover.png` (a capa do livro inteiro, gerada por `estudo-listar-dominios`) e observe-a como referência visual: identifique 2 a 4 cores dominantes e a temperatura geral (quente/fria/neutra). Verbalize-a numa frase reaproveitável para todos os capítulos — ex: `deep teal and warm amber palette with ivory accents`, `indigo and pale-gold palette`, `muted earth tones with a single emerald accent`. **Essa é a paleta-base do livro**, e todas as capas dos capítulos derivam dela. Resultado pretendido: ao olhar a estante de capas (`cover.png` do livro + `01-.../cover.png` + `02-.../cover.png` + ...), o leitor reconhece imediatamente que pertencem ao mesmo livro.

A variação entre capítulos vem de **outros slots** (sujeito, iluminação, composição) e de **acentos sutis** dentro da própria paleta — não de trocar a paleta inteira. Exemplos válidos de variação:

- Capítulo de fundamentos: paleta-base mais "fria" e contida — `deep teal and warm amber palette, teal-dominant with restrained amber`.
- Capítulo de aplicação prática: mesma paleta com acento mais quente — `deep teal and warm amber palette, amber-dominant with teal as accent`.
- Capítulo intermediário: equilíbrio neutro entre as duas cores principais.

Não inventar cores novas (nada de `purple` num livro construído sobre `teal+amber`), não trocar a temperatura (não pular de fria para quente entre capítulos), não introduzir uma terceira cor forte que não esteja na capa do livro. Acentos discretos (um único reflexo, uma fagulha) são OK.

**Esqueleto fixo do prompt** — siga essa ordem; ela mantém consistência visual entre os capítulos do livro e entre livros do repositório:

```
<subject metáfora>, in <style>, <palette>, <lighting>, <composition>, no text, no letters, no words, no typography, no captions, no labels
```

Os 5 slots:

1. **`<subject metáfora>`** — a cena central como **metáfora visual**, não ilustração literal. Pense em "o que esse conceito *parece*?", não "como esse conceito *é desenhado em diagrama*". Exemplos: para "JOIN em SQL" → pontes luminosas conectando ilhas; para "state machine" → engrenagens que acendem em sequência; nunca um diagrama-textual ou um print de código.
2. **`<style>`** — fixe um estilo e mantenha. Opções testadas: `detailed digital painting`, `cinematic concept art illustration`, `isometric digital painting`, `clean vector-style illustration`, `ink illustration with watercolor wash`. **Não misture** ("watercolor cinematic photo" confunde o modelo).
3. **`<palette>`** — **use a paleta-base do livro fixada acima**, com a variação sutil descrita para o capítulo (dominância, equilíbrio, acento). Não invente paleta nova por capítulo — isso quebra a identidade visual do livro. Se faltar palavra para descrever a variação, repita a paleta-base literal e deixe a diferença vir dos outros slots.
4. **`<lighting>`** — uma frase. Ex: `soft cinematic backlighting`, `rim light from upper-left, deep shadows`, `diffuse overcast lighting`, `volumetric god rays through dust`.
5. **`<composition>`** — formato e enquadramento. Ex: `wide cinematic landscape composition, centered subject`, `low-angle hero shot, subject on the right third`, `top-down isometric view, subject grounded in lower half`.

E a **trava obrigatória de texto** no fim — esse modelo tende a inserir letras aleatórias se a trava não estiver explícita.

**Dois exemplos completos** (capítulos reais do repositório):

Capítulo "GDScript e Sinais" (Godot — comunicação por sinais):

```
Glowing signal beams traveling through a constellation of luminous nodes suspended in a serene digital cosmos, in detailed digital painting, deep teal and warm amber palette, soft cinematic backlighting with subtle volumetric glow, wide cinematic landscape composition with the central node slightly off-center, no text, no letters, no words, no typography, no captions, no labels
```

Capítulo "O Modelo Relacional em 10 Minutos" (SQL — tabelas e relacionamentos):

```
Floating crystalline grids of interconnected hexagonal cells linked by golden threads above a calm geometric plane, in isometric digital painting, indigo and pale-gold palette with ivory accents, soft directional lighting from upper-left casting long thin shadows, wide centered composition with the grids stacked at varying heights, no text, no letters, no words, no typography, no captions, no labels
```

Padrões recorrentes nesses exemplos: metáfora **espacial/luminosa**, paleta sóbria com 2 cores fortes + 1 acento, iluminação direcional clara, composição landscape com sujeito ligeiramente descentralizado. Quando o tema for muito abstrato, prefira **objetos físicos imaginários** (cristais, redes, mecanismos) a símbolos UI (caixas, setas, ícones).

**Use paths absolutos para `python ...generate_image.py` e para `--output`** — nunca relativos. Tarefas `Bash` executadas em paralelo ou em background no harness podem resolver o cwd em um diretório diferente do esperado (ex.: o diretório do capítulo em vez da raiz do projeto), e aí `.claude/skills/gerar-imagem/scripts/generate_image.py` simplesmente não existe naquele ponto — o Python falha com `No such file or directory` e a capa nunca é gerada. Path absoluto elimina essa dependência implícita de cwd.

Monte os dois caminhos absolutos a partir do `<REPO_ROOT>` resolvido na etapa B:

- `<REPO_ROOT>/.claude/skills/gerar-imagem/scripts/generate_image.py`
- `<REPO_ROOT>/<book-dir>/NN-slug-do-capitulo/cover.png`

```bash
python "<REPO_ROOT>/.claude/skills/gerar-imagem/scripts/generate_image.py" \
  --prompt "<prompt em ingles>" \
  --output "<REPO_ROOT>/<book-dir>/NN-slug-do-capitulo/cover.png" \
  --size 1536x1024
```

Exemplo concreto no Windows (paths com barras normais funcionam no bash do Git/WSL):

```bash
python "C:/Users/joaop/Desktop/development/teste/aprendizado/.claude/skills/gerar-imagem/scripts/generate_image.py" \
  --prompt "Digital painting of ..." \
  --output "C:/Users/joaop/Desktop/development/teste/aprendizado/meu-livro/01-introducao/cover.png" \
  --size 1536x1024
```

**Dica de performance**: dispare as gerações de capa de múltiplos capítulos em **paralelo** no mesmo turno (várias chamadas `Bash` numa única resposta, idealmente com `run_in_background=true`), pois cada chamada é independente. Isso reduz o tempo total significativamente — mas só funciona de forma confiável com paths absolutos e com os diretórios já criados na etapa A.

**Etapa D — Escrever `CONTENT.md`** dentro do subdiretório de cada capítulo, com a estrutura abaixo. Os `Write` podem ser disparados em paralelo com as capas da etapa C, já que só dependem da etapa A.

### Formato de `CONTENT.md`

Quatro seções obrigatórias, nesta ordem exata (espelham o `INTRODUCTION.md` do livro, escopadas para o capítulo — sem "Sobre o leitor", que é propriedade do livro inteiro):

```markdown
# <Nome completo do capítulo>

![capa](cover.png)

## Sobre este capítulo

<1 a 2 parágrafos densos respondendo: qual a proposta deste capítulo dentro do livro? Que recorte do tema ele cobre, por que esse recorte aparece nesta posição da sequência pedagógica, e qual a promessa central que justifica sua existência como capítulo autônomo.>

## Estrutura

<1 parágrafo nomeando os grandes blocos/subtópicos que o capítulo vai abordar, normalmente como uma enumeração inline `(1) ... ; (2) ... ; (3) ...`. Cada bloco com o nome do subtema e 2-5 exemplos concretos do que será coberto dentro dele. Essa seção é prévia do que virá quando a skill `estudo-listar-subcapitulos` rodar sobre este capítulo.>

## Objetivo

<1 parágrafo descrevendo o que se espera que o leitor consiga fazer/entender ao terminar este capítulo. Foco em capacidades tangíveis e no encaixe com o capítulo seguinte.>

## Fontes utilizadas

<Lista das referências reais pesquisadas que ancoraram a organização deste capítulo. Inclua URLs, livros, roadmaps, syllabi específicos para este capítulo. 3 a 8 itens.>

- [Título/descrição da fonte](url)
- ...
```

**Importante**:
- O recorte, a densidade e a linguagem devem respeitar o perfil do leitor fixado em `<book-dir>/INTRODUCTION.md` — não repita essa seção aqui, mas use-a como calibrador silencioso.
- Fontes citadas devem ser as que realmente informaram a organização deste capítulo, não uma cópia literal das fontes do livro.

### Atualização do `INTRODUCTION.md`

Após materializar todos os capítulos, edite `<book-dir>/INTRODUCTION.md` para inserir uma nova seção **antes** de `## Fontes utilizadas`:

```markdown
## Capítulos

1. [<Nome do Capítulo 1>](NN-slug-do-capitulo-1/CONTENT.md) — <descrição de 1 linha>
2. [<Nome do Capítulo 2>](NN-slug-do-capitulo-2/CONTENT.md) — <descrição de 1 linha>
...
```

- Use links relativos (`NN-slug/CONTENT.md`), sem barra inicial.
- A ordem dos itens **deve** bater com a ordem dos diretórios (o prefixo `NN` garante que `ls` também ordene igual).
- A descrição de 1 linha pode ser reaproveitada da lista impressa em chat.
- Se já existir uma seção `## Capítulos`, substitua-a integralmente (idempotência — permite re-rodar a skill sem duplicar).

As demais seções (`# Título`, `![capa]`, `## Sobre este livro`, `## Estrutura`, `## Objetivo`, `## Sobre o leitor`, `## Fontes utilizadas`) **não devem ser alteradas**.

## Encerramento

Após materializar diretórios + capas + `CONTENT.md`s e atualizar o `INTRODUCTION.md`, encerre com uma única linha factual:

> _Capítulos materializados em `./<book-dir>/NN-slug-do-capitulo/` (N capítulos, com capa e `CONTENT.md`). `INTRODUCTION.md` atualizado com os links._

**Não sugira** rodar a próxima skill, não anuncie próximos passos, não recomende continuação. A skill termina aqui — qualquer continuação do método é decisão do usuário. A reconstrução do `STRUCT.md` é responsabilidade do orquestrador (skill `estudo-atualizar-struct`), não desta skill.

## Exemplo

**Entrada:** `sql-para-analise-de-dados`

**Fluxo:**

1. Lê `./sql-para-analise-de-dados/INTRODUCTION.md`.
2. Faz 2–5 buscas web (ementas, sumários, roadmaps).
3. Imprime lista no chat:

```
Capítulos do livro "SQL para Análise de Dados":

1. Introdução — O que é SQL e por que ele domina a análise de dados, mesmo em 2026
2. O Modelo Relacional em 10 Minutos — tabelas, linhas, colunas, chaves e pensamento em conjuntos
3. SELECT, WHERE e os Filtros Essenciais — a query mais fundamental e as cláusulas de filtro do dia a dia
...
```

4. Materializa para cada capítulo:
   - `./sql-para-analise-de-dados/01-introducao/cover.png` + `CONTENT.md`
   - `./sql-para-analise-de-dados/02-o-modelo-relacional-em-10-minutos/cover.png` + `CONTENT.md`
   - `./sql-para-analise-de-dados/03-select-where-e-os-filtros-essenciais/cover.png` + `CONTENT.md`
   - ...

5. Atualiza `INTRODUCTION.md` inserindo a seção `## Capítulos` com links relativos, antes de `## Fontes utilizadas`.

6. Encerra com a linha de fechamento factual (sem sugerir próximas skills).

## O que evitar

- **Não** pule a leitura do `INTRODUCTION.md`. Ele é o contrato do livro — todos os capítulos descendem dele.
- **Não** pule a pesquisa web. Ela diferencia um sumário verossímil de um inventado.
- **Não** gere o `CONTENT.md` sem a capa, ou a capa sem o `CONTENT.md` — os dois artefatos são pareados.
- **Não** use números romanos ou formatação exótica. Use `1.`, `2.`, `3.` e prefixo `NN` (zero-padded).
- **Não** misture capítulos em níveis de granularidade muito diferentes.
- **Não** escreva capítulos genéricos ("Conclusão", "Referências"). Cada capítulo deve agregar conteúdo de aprendizado real.
- **Não** crie capítulo-prefácio que apenas reformule o `INTRODUCTION.md` ("Introdução à travessia", "Definindo o critério de pronto", "O recorte do livro", "Os livros vizinhos do método", "A lógica do arco", "Conhecendo a tecnologia X"). Quando o `## Sobre o leitor` descreve leitor experiente e o livro é prático/aplicado, **abra direto com o primeiro capítulo técnico** que ataca a lacuna específica nomeada em `## Sobre o leitor`. Replicar o framing do `INTRODUCTION.md` num capítulo só infla a árvore (ver critério #8 — densidade prática).
- **Não** altere seções do `INTRODUCTION.md` além da seção `## Capítulos`.
- **Não** duplique a seção `## Capítulos` se a skill rodar duas vezes — substitua.
- **Não** inclua texto dentro das imagens de capa (sempre `no text, no letters, no words`).
- **Não** traga a seção "Sobre o leitor" para dentro do `CONTENT.md` — ela vive só no `INTRODUCTION.md`.
- **Não** traduza termos técnicos consagrados em inglês só por traduzir (ver critério 7 da seção "Critérios para a sequência").
- **Não** sugira nem auto-encadeie a próxima skill do método no encerramento — a skill termina com a linha factual e ponto.
- **Não** invoque `/estudo-atualizar-struct` nem rode `build_struct.py` daqui — a reconstrução do `STRUCT.md` é responsabilidade do orquestrador (que chama a skill `estudo-atualizar-struct` no momento certo).
