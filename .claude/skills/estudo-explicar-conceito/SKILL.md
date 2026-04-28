---
name: estudo-explicar-conceito
description: Recebe o **caminho de um subcapítulo cujo `CONCEPTS.md` já foi esqueletizado** pela skill `estudo-listar-conceitos` (ex: `godot-para-um-rpg-2d-online-estilo-pokemon/01-introducao/05-o-mapa-do-livro`) e **incrementa o `CONCEPTS.md` com a explicação do próximo conceito pendente do roteiro**. Cada invocação avança um conceito: a skill lê o que já foi escrito (para dar continuidade de leitura, vocabulário e tom), pesquisa fontes na web, e anexa uma nova seção `## N. <Nome do conceito>` com prosa fluída — sem cabeçalhos internos, enriquecida com tabelas, blocos de código e diagramas Mermaid quando clarificam — encerrando com um bloco `**Fontes utilizadas:**` escopado àquele conceito (não há mais lista global consolidada). Após escrever, valida os blocos Mermaid via `validate_mermaid.py`. Quando o último conceito do roteiro é preenchido, anexa o link de navegação para o próximo subcapítulo/capítulo. Para preencher todos os conceitos pendentes de um subcapítulo de uma vez, o orquestrador delega sequencialmente ao agente `estudo-explicar-conceito` — ver `CLAUDE.md` na raiz do repositório. Esta é a **quinta e última etapa** do método de estudo estruturado — é onde o aprendizado de fato acontece.
---

# estudo-explicar-conceito

Quinta e última etapa do método de estudo estruturado. Recebe **o caminho de um subcapítulo** cujo `CONCEPTS.md` já foi esqueletizado pela skill `estudo-listar-conceitos`, identifica o próximo conceito pendente no roteiro, pesquisa fontes autoritativas e **anexa a explicação desse conceito ao mesmo `CONCEPTS.md`** — não cria arquivo novo, não cria subdiretório, não gera imagem. O resultado é uma aula contínua que cresce a cada iteração, com cada conceito construindo sobre o anterior.

Conceitos vivem como **seções H2 dentro de um único `CONCEPTS.md`** no diretório do subcapítulo. A skill lê o `CONCEPTS.md` inteiro (que já contém o roteiro e todos os conceitos previamente preenchidos), pesquisa, e **anexa** uma nova seção. Sem capa por conceito, sem reescrita destrutiva.

> **Escopo**: um conceito por invocação (auto-incremento — a skill detecta sozinha qual é o próximo pendente). Se o usuário pedir para completar **todos** os conceitos de um subcapítulo de uma vez, a orquestração acontece via agentes sequenciais — ver [CLAUDE.md](../../../CLAUDE.md) na raiz do repositório.

## Quando usar

O usuário tem um subcapítulo com `CONCEPTS.md` esqueleto (com `## Roteiro` listando N conceitos e marcador `Pendente: K / N`) e quer **avançar uma posição na aula**. Esta é a única skill do método que produz conteúdo de aprendizado em si; as outras só estruturam o caminho.

## Entrada

O **caminho do diretório do subcapítulo** (relativo ao diretório de trabalho atual ou absoluto), no formato `<book-dir>/<NN-cap>/<MM-sub>/`. Exemplos:

- `godot-para-um-rpg-2d-online-estilo-pokemon/01-introducao/05-o-mapa-do-livro`
- `sql-para-analise-de-dados/05-agregacoes-e-group-by/01-a-clausula-group-by`

Aceita `/` ou `\` como separador; barra final opcional.

Esse caminho carrega implicitamente os três níveis de contexto: **livro-pai** (`<book-dir>/`), **capítulo** (`<NN-cap>/`) e **subcapítulo** (`<MM-sub>/`) — e todo o estado da aula está dentro do `CONCEPTS.md` do subcapítulo.

Se o usuário não trouxer o caminho, pergunte uma única vez: _"Qual é o caminho do subcapítulo (ex: `godot-para-um-rpg-2d-online-estilo-pokemon/01-introducao/05-o-mapa-do-livro`) cujo próximo conceito você quer estudar a fundo?"_

## Validação inicial

Antes de qualquer pesquisa ou escrita, valide:

1. O subcapítulo existe e contém **dois** arquivos: `CONTENT.md` (com seção `## Conceitos`) e `CONCEPTS.md` (com seção `## Roteiro`). Se só `CONTENT.md` existe, oriente: _"Rode antes a skill `estudo-listar-conceitos` para gerar o `CONCEPTS.md` esqueleto."_
2. O `CONCEPTS.md` tem um `## Roteiro` numerado (`1. Conceito A — ...`, `2. Conceito B — ...`).
3. Determine o **próximo conceito pendente** comparando o roteiro com as seções `## N.` já presentes no arquivo:
   - Se o roteiro tem N entradas e existem K seções `## N.` (para `N = 1..K`), o próximo conceito é o de índice **K+1**.
   - Se K == N: a aula está completa. Avise o usuário e **não escreva nada**: _"Todos os N conceitos do subcapítulo já estão explicados em `CONCEPTS.md`. Nada a fazer."_
   - Se a contagem de seções `## N.` está fora de ordem ou pula índices, avise o usuário antes de escrever — algo foi editado manualmente e a skill não vai "consertar" sem confirmação.

4. Em caso de erro de validação, encerre com mensagem objetiva. Não adivinhe.

## Contexto obrigatório (até cinco fontes)

Antes de qualquer pesquisa ou geração, leia **as fontes na ordem abaixo**. Elas calibram juntas a profundidade, a linguagem e a continuidade da aula.

### 1. `<book-dir>/STRUCT.md` — o mapa estrutural do livro (referência primária para a aula)

Carrega o mapa visual completo do livro — a **árvore de arquivos canônica** com todos os capítulos e subcapítulos materializados, e descrição de 1 linha em cada nó. Use-o em duas frentes:

1. **Como localizador**: você posiciona este subcapítulo dentro do todo. Vê de relance qual capítulo veio antes e qual vem depois, quais subcapítulos vizinhos existem e o que cada um cobriu.
2. **Como referência para a sua aula** (uso central nesta skill):
   - **Pré-requisitos cobertos**: tudo que aparece em ramos anteriores ao deste subcapítulo (capítulo anterior inteiro, e subcapítulos anteriores deste capítulo) já é bagagem do leitor. **Pode (e deve) referenciar pelo nome** — "como vimos em `<nome do conceito anterior>` no subcapítulo `<MM-slug>`" — em vez de reexplicar. Construa por cima do que o `STRUCT.md` mostra que já está disponível.
   - **Território a não invadir**: ramos posteriores (capítulo seguinte, subcapítulos seguintes do mesmo capítulo, conceitos seguintes do mesmo subcapítulo se ainda estão pendentes no roteiro) são compromissos futuros do livro. Não antecipe a aula deles. Se o conceito atual encosta num tema que o `STRUCT.md` reserva para depois, sinalize "voltaremos a isso em `<nome do nó>`" sem desenvolver.
   - **Vocabulário consagrado pelo livro**: a árvore expõe os nomes que o livro adotou (slugs de subcapítulos, nomes de conceitos vizinhos). Se o livro está usando `signal` (e não "sinal"), `state machine` (e não "máquina de estado"), use o mesmo termo aqui — coerência intra-livro vale mais que preferência pessoal.
   - **Tom narrativo do livro**: o que aparece em ramos vizinhos do mesmo subcapítulo já tem um tom, uma densidade e um padrão de exemplos. Sua aula precisa entrar nesse fluxo, não como artigo independente.

### 2. `<book-dir>/INTRODUCTION.md` — o contrato do livro

- **Recorte do livro** — calibra o tipo de exemplo a usar (negócio? engenharia? RPG? análise?).
- **Sobre o leitor** — perfil, nível, experiências adjacentes, objetivo. Calibra a profundidade técnica e o que pode ser assumido como bagagem.

### 3. `<book-dir>/<NN-cap>/CONTENT.md` — o contrato do capítulo

Recorte do capítulo dentro do livro. Útil para escolher a **angulação** da explicação.

### 4. `<book-dir>/<NN-cap>/<MM-sub>/CONTENT.md` — o contrato do subcapítulo

- **Sobre este subcapítulo** — proposta exata.
- **Estrutura** — preview dos conceitos.
- **Conceitos** — listagem numerada (deve bater com o `## Roteiro` de `CONCEPTS.md`).
- **Objetivo** — capacidade que o subcapítulo entrega.

### 5. `<book-dir>/<NN-cap>/<MM-sub>/CONCEPTS.md` — o estado atual da aula (a fonte mais importante)

Esta é a fonte que diferencia a nova versão da skill da antiga. Leia o arquivo **inteiro** para:

- Pegar o `## Roteiro` e identificar o conceito a explicar (o índice `K+1`).
- Ler **todas** as seções `## 1.`, `## 2.`, …, `## K.` já preenchidas. Esse é o texto que o leitor já "leu" — você está dando continuidade.
  - Não resuma o que já foi dito; apenas conecte-se. Use o vocabulário introduzido. Referencie exemplos quando útil. Contraste quando o conceito atual diverge de um anterior. Construa em cima.
- Ler os blocos `**Fontes utilizadas:**` ao fim de cada `## N.` já preenchida (escopo por conceito). Eles informam o que cada conceito anterior consultou — útil como contexto, mas você **não mescla** com as URLs do conceito atual: cada `## N.` mantém sua própria lista. Se o arquivo ainda estiver no formato antigo (com `## Fontes utilizadas` global ao fim), guarde essas URLs em memória para fazer a migração descrita no passo 3 da reorganização (anexar dedupadas ao bloco do conceito atual).

Se K = 0 (primeiro conceito do subcapítulo), você não tem conceitos anteriores no mesmo subcapítulo. Pode usar como contexto o último subcapítulo do mesmo capítulo (ou subcapítulos anteriores) se for útil para conexão — mas não é obrigatório.

## Pesquisa de contexto (obrigatória)

Pesquise na web antes de escrever a aula — dispare buscas em paralelo no mesmo turno. **Não há quota fixa**: busque até atingir o critério mínimo abaixo, depois pare.

**Critério de parada:** **precisão técnica validada** — pelo menos uma fonte autoritativa (docs oficiais, RFC, paper, livro de referência) confirma a mecânica que você vai descrever. Se as fontes divergem, busque mais até resolver.

Conceitos triviais (uma definição direta, sem nuance) podem fechar com 1-2 buscas. Conceitos profundos ou contraintuitivos podem exigir mais — siga até a precisão técnica fechar, não pare antes.

Boas buscas para começar:

- `"<nome do conceito>" definition` / `... explained` — fontes autoritativas (docs oficiais).
- `"<nome do conceito>" how it works` / `... mechanics` — mecânica passo a passo.
- `"<nome do conceito>" example` / `... worked example` — casos realistas.
- `site:stackoverflow.com "<nome do conceito>"` — respostas upvoted.
- Docs oficiais da ferramenta quando o conceito é específico dela.

URLs relevantes vão para um bloco `**Fontes utilizadas:**` **dentro da seção do conceito que você está escrevendo** — escopadas àquele conceito, não em uma lista global ao fim do arquivo (ver "Forma da nova seção do conceito" abaixo).

## Escrita do conceito — anexar uma nova seção a `CONCEPTS.md`

Sua tarefa central é **anexar** uma nova seção ao `CONCEPTS.md` existente, mantendo o resto do arquivo intacto. As fontes vivem **dentro de cada seção do conceito** — não há mais lista global ao fim do arquivo. A operação é **append + reorganização do final**:

1. Leia o `CONCEPTS.md` inteiro.
2. Identifique e remova temporariamente do final:
   - O bloco de navegação `**Próximo subcapítulo** → ...` ou `**Próximo capítulo** → ...` ou `_Fim do livro..._` (se existir).
   - O marcador `> _Pendente: K / N conceitos preenchidos._` (se existir).
3. **Compatibilidade com formato antigo (lista consolidada).** Se houver uma seção `## Fontes utilizadas` global ao fim do arquivo (legado), remova-a também e **guarde as URLs em memória**. Anexe-as (de-duplicadas) ao bloco `**Fontes utilizadas:**` do conceito que você está escrevendo agora — a skill não tem como saber a procedência original, então fica como melhor-esforço de migração. Em iterações seguintes não haverá mais lista global a migrar.
4. Anexe a nova seção `## <K+1>. <Nome do conceito do roteiro>` com a aula em prosa fluída e, **ao fim dela**, o bloco `**Fontes utilizadas:**` listando as URLs que você consultou para escrever este conceito (ver "Forma da nova seção do conceito" abaixo).
5. Reanexe o marcador atualizado: `> _Pendente: <K+1> / <N> conceitos preenchidos._`.
6. **Se K+1 == N** (este foi o último conceito), rode `compute_next_link.py --apply` para anexar o bloco de navegação (regra detalhada mais abaixo).
7. **Sempre, depois de escrever**, rode `validate_mermaid.py` no `CONCEPTS.md` resultante. Se o script reportar violações, corrija o(s) bloco(s) Mermaid no `CONCEPTS.md` e rode de novo até o script passar com exit 0. **Não encerre com violações pendentes.**

### Forma da nova seção do conceito

````markdown
## <K+1>. <Nome do conceito, exatamente como aparece no roteiro>

<Prosa objetiva e densa. Comece direto pela motivação — o problema ou a pergunta que o conceito resolve, em uma ou duas frases — e siga para o que é e como funciona tecnicamente. Sem aquecimento, sem "neste conceito vamos ver", sem reapresentação do tema. O leitor já sabe pelo título o que está estudando; o primeiro parágrafo entrega valor, não cerimônia.

Cada frase precisa carregar informação técnica nova. Se uma frase só reformula a anterior, repete o que já foi dito num conceito prévio, ou serve de ponte ornamental ("é importante notar que", "vale destacar", "como podemos ver"), corte. Densidade > volume: prefira o texto enxuto que entrega o conceito a um texto longo que dilui a mesma ideia em três páginas.

Conecte-se aos conceitos anteriores (`## 1.` até `## K.`) sem repetir o que já foi dito — referencie pelo nome ("vimos em `## K.` que ...") quando o gancho importa, e construa por cima. O texto deve soar como continuação de leitura, não como artigo independente.

Use markdown rico quando ele substitui prosa que seria mais longa e menos clara:

- **Tabelas** para comparações, mapeamentos, propriedades lado a lado, trade-offs.
- **Blocos de código** com syntax highlighting (`gdscript, `python, `bash, `json, ```sql etc.) para trechos de código, configurações, pseudocódigo ou exemplos de terminal.
- **Diagramas Mermaid** (```mermaid) para fluxos, sequências, estados ou dependências que seriam confusos em prosa. As regras do parser são checadas pelo `validate_mermaid.py` (ver "Validação pós-escrita") — escreva e deixe o lint pegar.

Esses elementos entram onde substituem prosa mais longa com mais clareza — não para decorar nem para parecer completo.>

<Se um exemplo concreto genuinamente ilumina o conceito além do que a prosa já explica, inclua-o como continuação natural do texto. Se a explicação acima já for auto-suficiente, omita — exemplo redundante é gordura, não didática.>

**Fontes utilizadas:**

- [Título da fonte 1](url1)
- [Título da fonte 2](url2)
- ...
````

O bloco `**Fontes utilizadas:**` é parte estrutural da seção do conceito — não é cabeçalho `###` (não polui a TOC), é uma linha em **negrito** seguida de bullets. Ele encerra a seção e precede a próxima `## <K+2>. ...` (ou o marcador `Pendente`, se este foi o último).

### Princípios de escrita

- **Aderência obrigatória ao contrato do livro/capítulo/subcapítulo.** Os detalhes técnicos abordados na explicação **devem necessariamente** fazer sentido com:
  - **`INTRODUCTION.md` do livro** — recorte, perfil do leitor, objetivo geral. Se o livro é "RPG 2D em Godot para iniciante em engines", não puxe internals de C++ do engine; se é "SQL para análise de dados", não desça para tuning de buffer pool do PostgreSQL. O escopo do livro define o teto de profundidade e a lente que a explicação assume.
  - **`CONTENT.md` do capítulo** — recorte do capítulo dentro do livro, angulação. O capítulo decide _por que ângulo_ atacar o conceito (mecânica? trade-off? design? aplicação?). Não troque a angulação do capítulo por outra que você ache mais interessante.
  - **`CONTENT.md` do subcapítulo** — proposta exata, "Estrutura", "Objetivo". A proposta do subcapítulo é o contrato literal do que essa aula entrega. Cada detalhe técnico que você inclui precisa servir ao "Objetivo" declarado; se não serve, não entra — mesmo que o conteúdo seja correto e interessante.
  - **`STRUCT.md` do livro** — vizinhança de capítulos/subcapítulos/conceitos. O `STRUCT.md` define o que já foi coberto (não reexplique), o que vem depois (não antecipe) e qual nó cobre cada tema (mande o leitor para o nó certo em vez de invadir).
  Antes de incluir qualquer mecânica, exemplo, tabela ou diagrama, faça o teste: _isto serve à proposta deste subcapítulo dentro deste capítulo dentro deste livro, ou é tangente que eu acharia legal mostrar?_ Se for tangente, corte — por mais correta que seja. Curiosidade do autor não vence escopo do contrato.
- **Objetividade é a regra-mestra.** O texto vence por densidade técnica, não por extensão. Quando estiver em dúvida entre duas formulações, escolha a mais curta que preserve a precisão. "Faz sentido didático" não significa longo — significa que o leitor entende o mecanismo e sai capaz de aplicar; isso quase sempre cabe em menos texto do que o instinto pede. Texto enxuto que entrega o conceito > texto longo que o dilui.
- **Sem cabeçalhos internos no corpo do conceito.** Dentro de `## <K+1>. ...` o texto flui como prosa, segmentado só por parágrafos — nada de `### O que é?`, `### Explicação`, `### Síntese`, `### Resumo`, `### Conclusão` ou variações. Os únicos `##` em `CONCEPTS.md` são `## Roteiro` e as `## N. <Nome>`. **Fechamento permitido — recapitulação não:** o último parágrafo pode amarrar os fios _se_ adicionar conexão (com o conceito anterior, com algo à frente na árvore, ou com a motivação inicial); se for só repetir em outras palavras, corte.
- **Sem preâmbulo, sem cerimônia.** O primeiro parágrafo entra direto na motivação técnica. Proibido: "Neste conceito vamos ver...", "Antes de começar é importante entender...", "Como já discutimos anteriormente, podemos agora...", "Vale destacar que...", "É importante notar que...", "Cabe ressaltar...". O leitor abriu a seção pelo título — não precisa de aviso prévio do que vem.
- **Sem qualificadores vazios.** Corte advérbios e expressões que não mudam o conteúdo: "essencialmente", "basicamente", "fundamentalmente", "naturalmente", "claramente", "obviamente", "de certa forma", "de modo geral". Ou a afirmação é técnica e direta, ou é hesitação disfarçada — em qualquer caso, sai.
- **Sem reformulação.** Cada frase carrega informação nova. Se a próxima frase só reescreve a anterior em outras palavras "para reforçar", corte uma das duas. Idem para parágrafos: dois parágrafos que dizem a mesma coisa de ângulos diferentes viram um.
- **Continuidade obrigatória.** Referencie explicitamente o vocabulário/exemplos/critérios estabelecidos nos conceitos anteriores do mesmo `CONCEPTS.md`, sem repetir. Quem lê de cima a baixo deve sentir uma aula só.
- **Ancoragem na árvore do livro.** Use o `STRUCT.md` como mapa: para temas já cobertos antes, **referencie pelo nome do nó** ("como visto no subcapítulo `<MM-slug>`, conceito `N. <Nome>`") em vez de reexplicar; para temas reservados para nó posterior, **sinalize o ponteiro** ("voltaremos a isso em `<NN-cap>/<MM-sub>`") em vez de antecipar.
- **Detalhamento técnico real, sem rodeio.** Densidade não é antônimo de profundidade — é o oposto de diluição. Cada afirmação técnica importante é explicada mecanicamente (como funciona por baixo, não só o que faz), em texto direto. Profundidade vem de explicar o mecanismo, não de adicionar parágrafos sobre o mesmo ponto.
- **Markdown rico quando substitui prosa mais longa.** Tabelas, blocos de código com syntax highlight e diagramas Mermaid são obrigatórios quando o conteúdo pede comparação, fluxo ou código — porque uma tabela de 5 linhas substitui um parágrafo confuso de 15 linhas. Não use para decorar nem para inflar a aparência de completude.
- **Exemplo apenas quando necessário.** Critério: o leitor ganha insight real que não teria sem o exemplo? Se não, corte. Nada de exemplos fake e vazios; nada de exemplo que só ilustra o que a prosa já deixou claro.
- **Analogias com ressalva** — sinalize onde quebram, ou não use.
- **Prosa direta.** Voz ativa, zero gordura. Nível do leitor calibrado por "Sobre o leitor" no `INTRODUCTION.md`. Idioma do livro (padrão pt-BR); termos técnicos em inglês ficam em inglês.
- **URLs só no bloco `**Fontes utilizadas:**`** ao fim da seção — nunca no corpo da prosa.

### Forma do bloco `**Fontes utilizadas:**` (por conceito)

Ao fim de cada seção `## N.`, antes da próxima `## <N+1>.` (ou do marcador `Pendente`, se for o último), escreva:

```markdown
**Fontes utilizadas:**

- [Título/descrição da fonte 1](url1)
- [Título/descrição da fonte 2](url2)
- ...
```

Regras:

- O bloco vive **dentro** da seção do conceito — escopo por conceito, não global. Cada `## N.` tem o seu.
- Liste apenas as URLs que você efetivamente consultou para escrever **este** conceito.
- Se uma mesma URL foi consultada de novo para este conceito, **é OK repeti-la** mesmo que já apareça em conceito anterior. Escopo por conceito vence dedup global — a rastreabilidade URL→conceito é o objetivo.
- Não use cabeçalho (`### Fontes` ou `#### Fontes`): é uma linha em **negrito** seguida de bullets, para não poluir a TOC.
- Na primeira execução sobre um arquivo em formato antigo (com `## Fontes utilizadas` global), as URLs herdadas entram aqui dedupadas (ver passo 3 da reorganização).

## Atualizar o marcador de progresso

Logo após o bloco `**Fontes utilizadas:**` da seção `## <K+1>. ...` que você acabou de escrever, escreva:

```markdown
> _Pendente: <K+1> / <N> conceitos preenchidos._
```

Onde `K+1` é o índice do conceito que você acabou de escrever e `N` é o total no roteiro. Esse marcador é descartado e reescrito a cada iteração.

## Bloco de navegação — só no último conceito

**Apenas quando `K+1 == N`** (você acabou de explicar o último conceito do subcapítulo), anexe ao fim de `CONCEPTS.md` um link para a próxima leitura. Para resolver o destino correto, rode o helper:

```bash
python "<REPO_ROOT>/.claude/skills/estudo-explicar-conceito/scripts/compute_next_link.py" \
  "<REPO_ROOT>/<book-dir>/<NN-cap>/<MM-sub>" --apply
```

> O script `compute_next_link.py` aceita **um caminho de subcapítulo**. Ele resolve, nesta ordem:
>
> 1. **Próximo subcapítulo** no mesmo capítulo → `**Próximo subcapítulo** → [H1 do próximo subcap](../<MM+1-slug>/CONTENT.md)`.
> 2. **Próximo capítulo** no livro (se este é o último subcap) → `**Próximo capítulo** → [H1 do próximo cap](../../<NN+1-slug>/CONTENT.md)`.
> 3. **Fim do livro** → `_Fim do livro. Parabéns pela jornada._`.
>
> O bloco é anexado ao `CONCEPTS.md`. O script é idempotente: reaplicá-lo substitui o bloco anterior em vez de duplicar.

Em iterações intermediárias (`K+1 < N`), **não** rode `compute_next_link.py`. O bloco de navegação só nasce quando a aula do subcapítulo está completa — antes disso, ele só atrapalharia.

## Validação pós-escrita: lint dos blocos Mermaid

**Sempre, depois de escrever** o `CONCEPTS.md` (em qualquer iteração — não só na última), rode o validador:

```bash
python "<REPO_ROOT>/.claude/skills/estudo-explicar-conceito/scripts/validate_mermaid.py" \
  "<REPO_ROOT>/<book-dir>/<NN-cap>/<MM-sub>/CONCEPTS.md"
```

O script extrai todos os blocos ` ```mermaid ` e checa as armadilhas que a skill historicamente gerava com frequência:

1. Palavras reservadas (`loop`, `alt`, `opt`, `par`, `critical`, `break`, `rect`, `note`) como nome de `participant`/`actor`.
2. Hífen no id de `participant`/`actor` (Mermaid só aceita `[A-Za-z_][A-Za-z0-9_]*` — para label visível use `as "..."`).
3. Literal `\n` dentro de labels.
4. Ponto-e-vírgula `;` dentro de texto de `Note over ...`.
5. Setas inválidas em `sequenceDiagram` (variantes com dashes/chevrons em número errado, ex: `->>>`, `--->>`).

**Comportamento por exit code:**

- **Exit 0** — sem violações. Encerre normalmente.
- **Exit 1** — uma ou mais violações listadas no stderr. **Corrija o(s) bloco(s) Mermaid no `CONCEPTS.md`** seguindo a indicação do script (renomear participant, encurtar/dividir label, trocar `;` por vírgula) e **rode o validador de novo**. Repita até passar com exit 0. **Não encerre com violações pendentes.**
- **Exit 2** — arquivo não encontrado / erro de I/O. Verifique o caminho.

Por que validar mesmo sem Mermaid? O custo é desprezível (regex sobre o markdown) e o script não emite ruído — sem blocos Mermaid, retorna 0 silenciosamente. Rodar incondicionalmente elimina a categoria de bugs em vez de depender de boa intenção.

## Encerramento

Após anexar o conceito (e, se aplicável, anexar o bloco de navegação), encerre com:

> _Conceito `<K+1>. <Nome>` anexado a `./<book-dir>/<NN-cap>/<MM-sub>/CONCEPTS.md`. Progresso: <K+1>/<N>._

E, se foi o último:

> _Última aula do subcapítulo. Bloco de navegação adicionado. Boa leitura._

## Exemplo (forma curta)

**Entrada:** `godot-para-um-rpg-2d-online-estilo-pokemon/01-introducao/05-o-mapa-do-livro`

**Estado inicial de `CONCEPTS.md` (já preenchido até o conceito 2):**

```markdown
# Conceitos: O Mapa do Livro

> _Aula contínua..._

## Roteiro

1. Os 4 blocos do livro — ...
2. Por que fundamentos vêm primeiro — ...
3. Por que single-player precede online — ...
   ... (6 itens no total)

## 1. Os 4 blocos do livro

<aula completa>

**Fontes utilizadas:**

- [Godot Engine Docs — Getting started](https://docs.godotengine.org/...)
- ...

## 2. Por que fundamentos vêm primeiro

<aula completa, conectando-se ao conceito 1>

**Fontes utilizadas:**

- [Godot — Manual best practices](https://docs.godotengine.org/...)
- ...

> _Pendente: 2 / 6 conceitos preenchidos._
```

**Fluxo:**

1. Lê `STRUCT.md`, `INTRODUCTION.md`, `CONTENT.md` do capítulo, `CONTENT.md` do subcapítulo e o `CONCEPTS.md` inteiro. Identifica K=2 → próximo é o conceito 3 ("Por que single-player precede online").
2. Dispara buscas web em paralelo até a precisão técnica fechar com fonte autoritativa.
3. Anexa a nova seção `## 3. Por que single-player precede online` em prosa fluída, conectando-se ao que os conceitos 1 e 2 estabeleceram, e termina a seção com um bloco `**Fontes utilizadas:**` listando as URLs deste conceito.
4. Atualiza marcador para `Pendente: 3 / 6 conceitos preenchidos.`.
5. Como K+1 = 3 < 6, **não** roda `compute_next_link.py`. Só roda quando preencher o conceito 6.
6. Roda `validate_mermaid.py` no `CONCEPTS.md`. Sem violações (ou conceito sem Mermaid) → segue.
7. Encerra: _"Conceito 3. Por que single-player precede online anexado a `CONCEPTS.md`. Progresso: 3/6."_

## O que evitar

- **Não** pule a leitura das cinco fontes de contexto (incluindo `CONCEPTS.md` na íntegra) nem a pesquisa web — a precisão importa aqui.
- **Não** mude o título (H1) de `CONCEPTS.md` nem o `## Roteiro`; **não** edite as seções `## 1.` até `## K.` já existentes — só anexe a `## K+1. ...`.
- **Não** crie subdiretório `KK-slug/` nem `cover.png` para o conceito — a capa do subcapítulo basta.
- **Não** crie ou recrie uma seção `## Fontes utilizadas` global ao fim do arquivo — o formato atual é por conceito (bloco `**Fontes utilizadas:**` dentro de cada `## N.`). Se encontrar formato antigo, faça a migração descrita no passo 3 da reorganização.
- **Não** inclua detalhe técnico que não sirva ao contrato do livro/capítulo/subcapítulo. Antes de cada bloco técnico (mecânica, exemplo, tabela, diagrama, comparação), faça o teste: _isto serve à proposta declarada em `INTRODUCTION.md` + `CONTENT.md` do capítulo + `CONTENT.md` do subcapítulo, e respeita o que o `STRUCT.md` mostra como vizinhança?_ Se a resposta é não — porque é tangente, porque desce abaixo do nível do leitor, porque invade outro subcapítulo, porque puxa profundidade que o livro não promete — corte. Aderência ao contrato bate "isto seria interessante de mostrar".
- **Não** comece pela definição formal pura — comece pela motivação ou pelo elo com o conceito anterior.
- **Não** abra com preâmbulo/cerimônia. Frases como "Neste conceito vamos ver...", "Antes de entrarmos a fundo...", "Cabe agora discutir...", "Como vimos até aqui, podemos finalmente..." são gordura — corte e entre direto na motivação técnica.
- **Não** use qualificadores vazios (`essencialmente`, `basicamente`, `fundamentalmente`, `claramente`, `obviamente`, `de certa forma`, `vale destacar`, `é importante notar`). Se a afirmação é verdadeira, ela se sustenta sem o qualificador.
- **Não** reformule a mesma ideia em duas frases consecutivas "para reforçar". Cada frase precisa carregar informação técnica nova; senão, corte.
- **Não** confunda volume com profundidade. Densidade técnica vence extensão — um parágrafo objetivo que explica o mecanismo bate três parágrafos que orbitam o conceito sem entrar nele.
- **Não** invente conexões com conceitos que não existem no `STRUCT.md` ou no roteiro.
- **Não** rode `compute_next_link.py` em iterações intermediárias — só no último conceito.
- **Não** pule a execução do `validate_mermaid.py` ao fim, mesmo "tendo certeza" de que o Mermaid está correto — o histórico mostra que armadilhas escapam. Para as regras específicas que ele checa, ver "Validação pós-escrita".
