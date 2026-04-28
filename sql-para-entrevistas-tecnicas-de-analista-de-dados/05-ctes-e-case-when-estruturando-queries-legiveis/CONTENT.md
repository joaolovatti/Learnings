# CTEs e CASE WHEN: Estruturando Queries Legíveis

![capa](cover.png)

## Sobre este capítulo

`CTE` (`WITH ... AS`) e `CASE WHEN` são as duas ferramentas que mais elevam a percepção de senioridade na entrevista. Não porque resolvem problemas que joins e subqueries não resolvem — eles raramente fazem isso — mas porque organizam a query em estágios nomeados que o entrevistador consegue ler em voz alta junto com o candidato. Uma query de 40 linhas escrita como subquery aninhada quádrupla é tecnicamente correta e ilegível; a mesma lógica em três CTEs nomeadas (`monthly_revenue`, `top_customers`, `final_summary`) vira uma narrativa que o avaliador acompanha sem esforço. Em problemas "medium" e "hard" do LeetCode SQL 50, CTEs são tipicamente o estilo recomendado nas soluções de referência.

`CASE WHEN`, por sua vez, é o canivete suíço da lógica condicional dentro de uma query — vive no `SELECT` (criar colunas derivadas), no `WHERE` (filtros condicionais), no `GROUP BY` (agrupar por categoria derivada), no `ORDER BY` (ordenação customizada) e dentro de agregações (`SUM(CASE WHEN ... THEN 1 ELSE 0 END)` para contagem condicional, padrão repetido em quase toda entrevista). Este capítulo fecha o bloco de "padrões nucleares" do livro, consolidando o estilo de query que os capítulos seguintes vão adotar como default.

## Estrutura

Os blocos do capítulo são: (1) `CTE` como estágio nomeado — sintaxe `WITH x AS (...)`, encadeamento de múltiplas CTEs (`WITH x AS (...), y AS (...)`), e quando uma CTE é "materializada" vs inline em diferentes SGBDs; (2) o estilo de query em CTEs como técnica de comunicação — quebrar problemas longos em 2-4 estágios com nomes que descrevem o que cada estágio entrega; (3) `CASE WHEN` no `SELECT` — categorização derivada, bucketing numérico (`CASE WHEN age < 18 THEN 'menor' ...`), default `ELSE` e o cuidado com `NULL`; (4) `CASE WHEN` dentro de agregações — `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` para contagem condicional, `AVG(CASE WHEN ... THEN col END)` para média condicional ignorando os outros, e por que essa forma vence `COUNT(*) FILTER (WHERE ...)` em portabilidade; (5) `CASE WHEN` no `WHERE`, `GROUP BY` e `ORDER BY` — filtros condicionais legíveis, agrupamento por categoria derivada, ordenação customizada (ex: domingo no fim em vez de no começo); (6) CTEs vs subqueries vs views temporárias — o trade-off de cada um, e o estilo idiomático em SGBDs comuns (PostgreSQL, MySQL 8+, SQL Server, Snowflake).

## Objetivo

Ao terminar, o leitor escreverá queries longas em CTEs encadeadas com nomes descritivos por reflexo, dominará `CASE WHEN` em todas as cláusulas onde ele cabe, e usará `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` como idioma padrão para contagem condicional. Isso fecha o bloco de padrões nucleares do livro e prepara o terreno para o bloco de window functions (caps. 6 a 9), onde CTEs serão usadas para isolar a window function antes do filtro final — padrão obrigatório porque window functions não podem ser referenciadas diretamente no `WHERE`.

## Fontes utilizadas

- [Ultimate SQL Interview Guide for Data Scientists & Data Analysts (DataLemur)](https://datalemur.com/blog/sql-interview-guide)
- [SQL 50 — Study Plan (LeetCode)](https://leetcode.com/studyplan/top-sql-50/)
- [SQL for Data Analysis: Advanced Techniques for Transforming Data into Insights — Cathy Tanimura (O'Reilly)](https://www.oreilly.com/library/view/sql-for-data/9781492088776/)
- [Free SQL Tutorial for Data Analysts & Data Scientists (DataLemur)](https://datalemur.com/sql-tutorial)
- [SQL Roadmap — roadmap.sh](https://roadmap.sh/sql)
- [Mais de 100 perguntas e exercícios práticos sobre SQL (LearnSQL)](https://learnsql.com/blog/sql-interview-questions-guide/)
