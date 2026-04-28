# NULL, Ordem Lógica de Avaliação e QUALIFY: Detalhes que Travam Candidatos

![capa](cover.png)

## Sobre este capítulo

Os capítulos 1 a 13 cobriram o repertório de padrões. Este capítulo cobre o conjunto pequeno mas letal de detalhes que fazem candidatos com a query *quase* correta tropeçarem na entrevista — quando a follow-up do entrevistador é "e se houver `NULL` na coluna do `ORDER BY`?", "por que essa cláusula está no `HAVING` e não no `WHERE`?", "se eu tirar o `ORDER BY` da window function, o que acontece?", "qual a diferença entre `NOT IN` e `NOT EXISTS` quando a subquery pode retornar `NULL`?". Esses não são truques — são consequências naturais da semântica de `NULL` e da ordem lógica de execução do SQL. Mas são consequências que o trabalho do dia a dia raramente força a internalizar, porque os bugs que produzem são silenciosos (a query roda, retorna resultado, e está sutilmente errada).

A promessa central deste capítulo é eliminar essa zona cinzenta. Ao final, o leitor responderá em voz alta, sem hesitar, perguntas sobre semantics de `NULL` em qualquer cláusula, justificará a escolha de `WHERE` vs `HAVING` vs `QUALIFY` apontando para a fase de execução, e antecipará proativamente as follow-ups antes que o entrevistador as faça — o que vira sinal forte de senioridade. Este capítulo aparece após os blocos técnicos porque é o contexto que dá sentido a uma série de "porques" que ficaram em aberto nos capítulos anteriores.

## Estrutura

Os blocos do capítulo são: (1) `NULL` como valor desconhecido — não é zero, não é string vazia, não é igual a si mesmo (`NULL = NULL` retorna `NULL`, não `TRUE`), e a regra "qualquer operação com `NULL` retorna `NULL` exceto `IS NULL`/`IS NOT NULL`/`COALESCE`/`CASE`"; (2) `NULL` em `WHERE`, `JOIN`, `GROUP BY`, `ORDER BY`, agregações — comportamento em cada cláusula, `WHERE col = NULL` que nunca casa, `JOIN ON a.x = b.x` que ignora linhas com `NULL`, `GROUP BY` que junta `NULL`s no mesmo grupo, `ORDER BY` cuja posição de `NULL` (first ou last) varia por SGBD, e `COUNT(col)` que ignora `NULL` enquanto `COUNT(*)` não; (3) a armadilha clássica de `NOT IN` com subquery que pode retornar `NULL` — por que `WHERE x NOT IN (SELECT y FROM t)` retorna nada quando algum `y` é `NULL`, e por que `NOT EXISTS` é a forma segura; (4) ordem lógica de execução do SQL — `FROM` → `JOIN` → `WHERE` → `GROUP BY` → `HAVING` → window functions → `SELECT` → `DISTINCT` → `ORDER BY` → `LIMIT`, e as consequências práticas (não pode usar alias do `SELECT` no `WHERE`, não pode filtrar window function no `WHERE`, pode no `HAVING` só se for agregada); (5) `QUALIFY` — onde existe (Snowflake, BigQuery, Teradata, Databricks), a sintaxe que permite filtrar window function diretamente sem CTE intermediária, e o equivalente portável (CTE + `WHERE`); (6) checklist mental antes de submeter a query — `NULL` em colunas-chave de `JOIN`? `NULL` em coluna do `ORDER BY` da window function? Empates no ranking que mudam com `ROW_NUMBER` vs `RANK`? Filtro de window function no lugar errado?

## Objetivo

Ao terminar, o leitor responderá com naturalidade follow-ups do entrevistador sobre `NULL` em qualquer cláusula, justificará escolhas de `WHERE`/`HAVING`/`QUALIFY` em função da ordem lógica de execução, evitará a armadilha de `NOT IN` com `NULL`, e adquirirá o hábito de rodar mentalmente um checklist antes de afirmar "está pronto". Isso completa a fluência operacional do livro e prepara o terreno para o último capítulo — o plano de prática estruturado que transforma esse repertório em reflexo cronometrado.

## Fontes utilizadas

- [Ultimate SQL Interview Guide for Data Scientists & Data Analysts (DataLemur)](https://datalemur.com/blog/sql-interview-guide)
- [SQL for Data Analysis: Advanced Techniques for Transforming Data into Insights — Cathy Tanimura (O'Reilly)](https://www.oreilly.com/library/view/sql-for-data/9781492088776/)
- [T-SQL Window Functions: For Data Analysis and Beyond — Itzik Ben-Gan (Microsoft Press)](https://www.microsoftpressstore.com/store/t-sql-window-functions-for-data-analysis-and-beyond-9780135861448)
- [Oracle Database SQL Certified Associate (1Z0-071) — Exam Topics](https://education.oracle.com/oracle-database-sql/pexam_1Z0-071)
- [Free SQL Tutorial for Data Analysts & Data Scientists (DataLemur)](https://datalemur.com/sql-tutorial)
- [Mais de 100 perguntas e exercícios práticos sobre SQL (LearnSQL)](https://learnsql.com/blog/sql-interview-questions-guide/)
