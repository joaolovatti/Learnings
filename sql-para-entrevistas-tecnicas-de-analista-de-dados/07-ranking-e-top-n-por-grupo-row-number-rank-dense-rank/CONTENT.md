# Ranking e Top-N por Grupo: ROW_NUMBER, RANK, DENSE_RANK

![capa](cover.png)

## Sobre este capítulo

"Top-N por grupo" é o padrão de problema mais frequente em entrevistas técnicas de SQL para analistas. O enunciado vem em mil formas — "os 3 produtos mais vendidos por categoria", "o pedido mais recente de cada cliente", "os 5 funcionários mais bem pagos por departamento", "o segundo maior salário", "o vencedor de cada partida" — e a resposta canônica é sempre a mesma combinação: window function de ranking dentro de uma CTE, e filtro `WHERE rank <= N` na query externa. Dominar essa combinação até o reflexo, com pleno entendimento das diferenças entre `ROW_NUMBER`, `RANK` e `DENSE_RANK`, é o ganho mais alavancado do livro inteiro — uma única técnica que destranca dezenas de problemas de prova.

Este capítulo entra logo após os fundamentos de window function porque é a aplicação que mais aparece em prova e o entrevistador frequentemente faz follow-ups específicos sobre as três variantes ("e se houver empate? `ROW_NUMBER` ou `RANK`?", "e se quisermos numeração consecutiva sem buracos? `DENSE_RANK`"). A promessa central é que o leitor escolha entre as três funções de ranking conscientemente em segundos, escreva o padrão "CTE com `ROW_NUMBER` + filtro externo" como reflexo, e antecipe as variações de follow-up (top-N com empate, top-N permitindo empate, bottom-N, "quem ficou em segundo lugar").

## Estrutura

Os blocos do capítulo são: (1) a família de ranking e suas semantics — `ROW_NUMBER` numera 1,2,3,4 ignorando empates; `RANK` dá o mesmo número para empates e pula os seguintes (1,2,2,4); `DENSE_RANK` dá o mesmo número para empates e não pula (1,2,2,3); o critério para escolher entre as três; (2) o padrão canônico "top-N por grupo" — `ROW_NUMBER() OVER (PARTITION BY grupo ORDER BY métrica DESC)` dentro de CTE, filtro `WHERE rn <= N` na query externa, com discussão de quando `RANK` é mais adequado (top-N permitindo empate); (3) o padrão "primeira/última ocorrência" — caso especial de top-N com N=1, e a comparação com `MIN`/`MAX` + self-join (a forma pré-window function); (4) `NTILE(N)` para quantização — distribuição em quartis, decis e percentis, padrão que aparece em problemas de "qual é o quartil de receita deste cliente"; (5) `QUALIFY` (Snowflake, BigQuery, Teradata) — a alternativa moderna ao "CTE + filtro externo", que filtra direto sobre a window function; (6) follow-ups clássicos do entrevistador — "e se houver `NULL` na coluna do `ORDER BY`? como ordenar `NULL` first/last?", "e se o desempate precisar de uma segunda chave?", "e se for o segundo maior salário, considerando empates?".

## Objetivo

Ao terminar, o leitor escolherá entre `ROW_NUMBER`, `RANK` e `DENSE_RANK` instantaneamente baseado no enunciado, escreverá o padrão "top-N por grupo" como reflexo (CTE + filtro externo), e responderá com naturalidade as follow-ups sobre empates e ordenação de `NULL`. Isso prepara o terreno para o capítulo de `LEAD`/`LAG` (cap. 8), onde a ideia de "olhar para a linha vizinha" complementa a de "ranquear vizinhos".

## Fontes utilizadas

- [T-SQL Window Functions: For Data Analysis and Beyond — Itzik Ben-Gan (Microsoft Press)](https://www.microsoftpressstore.com/store/t-sql-window-functions-for-data-analysis-and-beyond-9780135861448)
- [12 SQL Window Functions Interview Questions (DataLemur)](https://datalemur.com/blog/sql-window-functions-interview-questions)
- [SQL Window Functions Explained: The Complete Visual Guide (SQLNoir)](https://www.sqlnoir.com/blog/sql-window-functions)
- [SQL 50 — Study Plan (LeetCode)](https://leetcode.com/studyplan/top-sql-50/)
- [Leetcode and HackerRank Problems You Need to Practice for the Data Engineering SQL Interview — Sean Coyne (Medium)](https://medium.com/@seancoyne/leetcode-and-hackerrank-problems-you-need-to-practice-for-the-data-engineering-sql-interview-dddef57e7549)
- [Practice SQL Window Functions — Free Exercises for Interview Prep](https://www.practicewindowfunctions.com/)
