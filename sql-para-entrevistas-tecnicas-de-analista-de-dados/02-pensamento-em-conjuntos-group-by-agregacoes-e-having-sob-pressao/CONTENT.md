# Pensamento em Conjuntos: GROUP BY, Agregações e HAVING sob Pressão

![capa](cover.png)

## Sobre este capítulo

`GROUP BY` é a primeira ferramenta a sair na entrevista. Quase toda pergunta de SQL para analista começa com "para cada cliente / produto / dia / categoria, calcule X" — e a tradução dessa frase em SQL é uma agregação por grupo. O leitor já usa `GROUP BY` no dia a dia, mas a entrevista cobra um nível de precisão que o trabalho não cobra: distinguir `COUNT(*)` de `COUNT(coluna)` de `COUNT(DISTINCT coluna)` instantaneamente, saber por que `COUNT` ignora `NULL` em uma coluna mas `COUNT(*)` não, escolher conscientemente entre `WHERE` e `HAVING`, e diagnosticar em segundos quando uma agregação está "errada" porque a granularidade do `JOIN` anterior duplicou linhas.

Este capítulo aparece logo após o capítulo de modelo mental porque é o substrato técnico mais reusado de todos os blocos seguintes — joins (cap. 3), subqueries (cap. 4) e window functions (cap. 6+) todos voltam a `GROUP BY` em algum momento, seja como solução, seja como contraponto. A promessa central é que o leitor saia com um catálogo mental dos arquétipos de problema que usam agregação simples, com a sintaxe idiomática para cada um e com radar para as armadilhas que entrevistadores adoram explorar.

## Estrutura

Os blocos do capítulo são: (1) o modelo mental de "para cada X, calcule Y" — como ler o enunciado e identificar imediatamente a coluna do `GROUP BY` e a agregação do `SELECT`; (2) a família das agregações e suas semantics em entrevista — `COUNT(*)` vs `COUNT(col)` vs `COUNT(DISTINCT col)`, `SUM` com `CASE WHEN` para contagem condicional, `AVG` e o problema da média de médias, `MIN`/`MAX` em colunas não-numéricas; (3) `WHERE` vs `HAVING` — a diferença de fase de execução, quando filtrar antes vs depois da agregação, e a armadilha de filtrar uma agregação dentro do `WHERE` (erro clássico de candidato); (4) granularidade pós-`GROUP BY` — entender que cada linha do resultado representa um grupo, e o que pode ou não aparecer no `SELECT` (a regra "tudo no `SELECT` é coluna do `GROUP BY` ou função agregada"); (5) os arquétipos canônicos da entrevista — "quantos itens por categoria com pelo menos N", "média por grupo acima do global", "categorias sem nenhum item", "primeiro pedido de cada cliente sem usar window function"; (6) `GROUP BY` com múltiplas colunas e `GROUPING SETS`/`ROLLUP`/`CUBE` — quando aparecem em entrevistas mais maduras e como reconhecê-los.

## Objetivo

Ao terminar, o leitor terá fluência reflexiva em `GROUP BY` para entrevista — identificará a coluna de agrupamento e a função agregada em segundos, evitará as armadilhas de `NULL` e duplicatas, escolherá `WHERE` vs `HAVING` sem hesitar, e dominará o idiomático `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` para contagem condicional. Isso prepara o terreno para o capítulo de joins (cap. 3), onde a granularidade pós-`JOIN` se torna a fonte número um de bugs em queries de candidato.

## Fontes utilizadas

- [Ultimate SQL Interview Guide for Data Scientists & Data Analysts (DataLemur)](https://datalemur.com/blog/sql-interview-guide)
- [SQL 50 — Study Plan (LeetCode)](https://leetcode.com/studyplan/top-sql-50/)
- [SQL for Data Analysis: Advanced Techniques for Transforming Data into Insights — Cathy Tanimura (O'Reilly)](https://www.oreilly.com/library/view/sql-for-data/9781492088776/)
- [Free SQL Tutorial for Data Analysts & Data Scientists (DataLemur)](https://datalemur.com/sql-tutorial)
- [Perguntas de entrevista sobre SQL para analistas de dados (LearnSQL)](https://learnsql.com/blog/sql-interview-questions-for-data-analyst/)
- [SQL Roadmap — roadmap.sh](https://roadmap.sh/sql)
