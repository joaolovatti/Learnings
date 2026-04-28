# Subqueries, Subqueries Correlacionadas e Set Operators

![capa](cover.png)

## Sobre este capítulo

Subqueries são a ferramenta que um candidato precisa dominar mas raramente usa no trabalho diário — em produção, CTEs e joins resolvem quase tudo. A entrevista, por outro lado, frequentemente força o uso de subquery: ou porque o problema pede expressamente uma comparação contra um agregado global ("clientes que gastaram mais que a média"), ou porque o entrevistador quer ver fluência em `EXISTS`/`NOT EXISTS`/`IN`/`NOT IN` para cobrir as armadilhas de `NULL` que diferenciam essas três sintaxes, ou porque deseja avaliar se o candidato consegue raciocinar sobre uma subquery correlacionada — aquela que executa "uma vez por linha externa" e cuja semântica é menos óbvia que um `JOIN` direto.

Este capítulo aparece após joins porque resolve, com sintaxe alternativa, vários dos problemas que o capítulo anterior atacou — e porque o entrevistador pode pedir explicitamente "agora resolva sem `JOIN`" ou "agora resolva com `EXISTS`". A promessa central é que o leitor saiba reconhecer quando uma subquery é a solução natural (não apenas plausível), distinga as três famílias (`scalar`, `IN`/`EXISTS`, correlacionada), e domine os set operators `UNION`/`UNION ALL`/`INTERSECT`/`EXCEPT` como ferramenta legítima de comparação entre conjuntos — algo que cai em problemas de "presente em A mas não em B" e similares.

## Estrutura

Os blocos do capítulo são: (1) os três tipos de subquery — `scalar` (retorna 1 valor, vai no `SELECT` ou no `WHERE`), `IN`/`EXISTS` (retorna conjunto, vai no `WHERE`), correlacionada (referencia a query externa, executa uma vez por linha); (2) subqueries no `FROM` (derived tables) — a alternativa pré-CTE, ainda exigida em provas que excluem CTEs ou em SGBDs antigos; (3) `EXISTS` vs `IN` vs `JOIN` em problemas de "tem/não tem" — a equivalência semântica, a diferença com `NULL` (`NOT IN` com `NULL` é a armadilha clássica), e o que cada estilo comunica ao entrevistador; (4) subqueries correlacionadas como antecessor das window functions — "para cada cliente, o pedido mais recente" resolvido com correlacionada antes de virar `ROW_NUMBER`, mostrando fluência nos dois estilos; (5) os set operators `UNION` (com e sem `ALL`), `INTERSECT`, `EXCEPT`/`MINUS` — quando aparecem em entrevista, a regra de tipos compatíveis, e o uso para "comparar duas listas de IDs"; (6) o trade-off subquery vs CTE vs join — qual escolher quando o problema admite os três, e como justificar a escolha em voz alta.

## Objetivo

Ao terminar, o leitor saberá quando uma subquery é a ferramenta natural (não apenas viável), distinguirá as armadilhas de `NULL` em `IN`/`NOT IN`/`EXISTS`/`NOT EXISTS` e responderá corretamente as follow-ups clássicas do entrevistador sobre essa diferença, e dominará set operators como ferramenta de comparação entre listas. Isso prepara o terreno para o capítulo de CTEs (cap. 5), onde a mesma estrutura aninhada de subquery vai ganhar um nome legível e se tornar a forma preferida de organizar queries longas.

## Fontes utilizadas

- [Ultimate SQL Interview Guide for Data Scientists & Data Analysts (DataLemur)](https://datalemur.com/blog/sql-interview-guide)
- [SQL 50 — Study Plan (LeetCode)](https://leetcode.com/studyplan/top-sql-50/)
- [SQL for Data Analysis: Advanced Techniques for Transforming Data into Insights — Cathy Tanimura (O'Reilly)](https://www.oreilly.com/library/view/sql-for-data/9781492088776/)
- [Free SQL Tutorial for Data Analysts & Data Scientists (DataLemur)](https://datalemur.com/sql-tutorial)
- [Oracle Database SQL Certified Associate (1Z0-071) — Exam Topics](https://education.oracle.com/oracle-database-sql/pexam_1Z0-071)
- [Mais de 100 perguntas e exercícios práticos sobre SQL (LearnSQL)](https://learnsql.com/blog/sql-interview-questions-guide/)
