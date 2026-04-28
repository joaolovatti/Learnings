# Joins Multi-Tabela: Inner, Outer, Self e Anti-Join

![capa](cover.png)

## Sobre este capítulo

Joins são onde a entrevista de SQL realmente começa a separar candidatos. Todo analista sabe escrever `INNER JOIN` em duas tabelas — mas o que cai em prova é a forma menos coberta no dia a dia: `LEFT JOIN` deliberado para construir anti-joins (`LEFT JOIN ... WHERE b.id IS NULL`), self-joins para comparar a mesma tabela contra si mesma em problemas temporais ("quem comprou hoje e tinha comprado também ontem?"), `FULL OUTER JOIN` para reconciliar duas fontes parcialmente sobrepostas, e o cuidado obsessivo com a granularidade resultante de joins M:N (que tipicamente quadruplica a contagem da agregação que vem depois).

Este capítulo segue diretamente o de `GROUP BY` porque a maioria dos bugs de query de candidato é `JOIN ... GROUP BY` onde o `JOIN` duplicou linhas que ninguém percebeu, e a agregação saiu inflada. A promessa central é que o leitor saia com mapa visual de cada tipo de join (linhas que sobram à esquerda, à direita, em ambos), com os arquétipos de problema onde cada variante é a resposta certa, e com o instinto de pensar "quantas linhas esse join produz por linha da tabela maior?" antes mesmo de escrever a cláusula `ON`.

## Estrutura

Os blocos do capítulo são: (1) o modelo mental de joins como produto cartesiano filtrado — entender o `CROSS JOIN` como base, e as variantes `INNER`/`LEFT`/`RIGHT`/`FULL` como filtros sobre ele; (2) `INNER JOIN` e a escolha consciente da chave — joins por ID vs join por composição de colunas, joins com condição de range (`BETWEEN` no `ON`), e joins com `OR` na condição (e por que costumam ser bug); (3) `LEFT JOIN` para preservar e o anti-join idiomático — `LEFT JOIN ... WHERE b.id IS NULL` para "X que não tem Y", o equivalente com `NOT EXISTS` e quando preferir um ao outro em entrevista; (4) `SELF JOIN` para comparações temporais e hierárquicas — "comprou hoje e ontem", "funcionário e seu chefe", "cliente A e cliente B com mesmo CEP", e o cuidado com o alias duplicado; (5) joins multi-tabela e a explosão de cardinalidade — quando o segundo `JOIN` introduz duplicatas que a query inicial não tinha, e como diagnosticar isso com `COUNT(DISTINCT)`; (6) `FULL OUTER JOIN` e set operations cruzadas — reconciliação de duas fontes, e o uso menos óbvio para encontrar diferenças simétricas.

## Objetivo

Ao terminar, o leitor reconhecerá em segundos qual variante de join um enunciado pede, escreverá anti-joins idiomaticamente nos dois estilos (`LEFT JOIN ... IS NULL` e `NOT EXISTS`), dominará self-joins temporais e hierárquicos sem confundir aliases, e terá radar permanente para a granularidade pós-`JOIN` que envenena agregações. Isso prepara o terreno para o capítulo de subqueries (cap. 4), onde algumas dessas mesmas perguntas reaparecem com ferramentas alternativas que o entrevistador pode pedir explicitamente.

## Fontes utilizadas

- [Ultimate SQL Interview Guide for Data Scientists & Data Analysts (DataLemur)](https://datalemur.com/blog/sql-interview-guide)
- [SQL 50 — Study Plan (LeetCode)](https://leetcode.com/studyplan/top-sql-50/)
- [Leetcode and HackerRank Problems You Need to Practice for the Data Engineering SQL Interview — Sean Coyne (Medium)](https://medium.com/@seancoyne/leetcode-and-hackerrank-problems-you-need-to-practice-for-the-data-engineering-sql-interview-dddef57e7549)
- [SQL for Data Analysis: Advanced Techniques for Transforming Data into Insights — Cathy Tanimura (O'Reilly)](https://www.oreilly.com/library/view/sql-for-data/9781492088776/)
- [Mais de 100 perguntas e exercícios práticos sobre SQL (LearnSQL)](https://learnsql.com/blog/sql-interview-questions-guide/)
- [Oracle Database SQL Certified Associate (1Z0-071) — Exam Topics](https://education.oracle.com/oracle-database-sql/pexam_1Z0-071)
