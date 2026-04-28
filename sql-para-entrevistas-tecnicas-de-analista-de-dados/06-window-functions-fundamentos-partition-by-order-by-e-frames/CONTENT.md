# Window Functions — Fundamentos: PARTITION BY, ORDER BY e Frames

![capa](cover.png)

## Sobre este capítulo

`Window functions` são a ferramenta que mais separa um candidato "sei SQL" de um candidato "passo na entrevista". Quase todo problema "medium" e "hard" de SQL em entrevista — top-N por grupo, running total, deduplicação posicional, comparação row-a-row, gaps and islands, sessões — colapsa em uma window function bem escolhida. O leitor já viu `OVER (PARTITION BY ...)` no trabalho, mas a entrevista cobra um nível de modelo mental diferente: entender que a window function é avaliada *antes* do `ORDER BY` final mas *depois* do `WHERE`, saber distinguir `ROWS` de `RANGE` (e por que o frame default não é o que parece), entender que `PARTITION BY` reset o cálculo a cada grupo, e ler uma `OVER (PARTITION BY user ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` da direita para a esquerda como uma frase técnica.

Este capítulo abre o bloco de window functions porque os três capítulos seguintes (ranking, lead/lag, agregadas com janela) dependem de o leitor ter o modelo mental do frame internalizado. A promessa central é que ao terminar, o leitor não confunda mais `PARTITION BY` com `GROUP BY`, saiba o que muda quando se adiciona `ORDER BY` dentro do `OVER`, e tenha o hábito de pensar "qual é o frame implícito ou explícito?" antes de avaliar o resultado de qualquer window function.

## Estrutura

Os blocos do capítulo são: (1) o modelo mental da window function — uma função que enxerga linhas vizinhas sem colapsá-las, em contraste com `GROUP BY` que colapsa; (2) `PARTITION BY` e o reset por grupo — como ler "para cada partição, calcule X" e a equivalência mental com "subquery por grupo"; (3) `ORDER BY` dentro do `OVER` — define a sequência sobre a qual a função opera, é diferente do `ORDER BY` final da query, e é obrigatório para funções como `ROW_NUMBER`, `LEAD`/`LAG`, `RANK`; (4) os frames `ROWS` vs `RANGE` — como `ROWS BETWEEN N PRECEDING AND M FOLLOWING` define um frame físico, como `RANGE` opera sobre valores e não sobre posições, e por que o frame default `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` causa surpresas em running totals quando há ties no `ORDER BY`; (5) a posição da window function na ordem lógica de execução — avaliada após `WHERE`/`GROUP BY`/`HAVING` mas antes de `ORDER BY` final, com a consequência de que não pode ser usada no `WHERE` (precisa de CTE ou subquery, ou `QUALIFY` quando o SGBD suporta); (6) ler uma window function da direita para a esquerda — exercício de "narrar em voz alta" o que cada cláusula faz, treinado contra exemplos progressivamente mais complexos.

## Objetivo

Ao terminar, o leitor terá o modelo mental de window function consolidado — distinguirá `PARTITION BY` de `GROUP BY`, entenderá o papel do `ORDER BY` interno, escolherá entre `ROWS` e `RANGE` conscientemente, e narrará em voz alta o que uma window function complexa faz, da função de fora para dentro. Isso é o pré-requisito explícito para os três capítulos seguintes — ranking (cap. 7), lead/lag (cap. 8) e janelas agregadas (cap. 9) — onde cada família específica de window function ganha sua biblioteca de padrões de entrevista.

## Fontes utilizadas

- [T-SQL Window Functions: For Data Analysis and Beyond — Itzik Ben-Gan (Microsoft Press)](https://www.microsoftpressstore.com/store/t-sql-window-functions-for-data-analysis-and-beyond-9780135861448)
- [SQL Window Functions Explained: The Complete Visual Guide (SQLNoir)](https://www.sqlnoir.com/blog/sql-window-functions)
- [Practice SQL Window Functions — Free Exercises for Interview Prep](https://www.practicewindowfunctions.com/learn/gap_and_island)
- [12 SQL Window Functions Interview Questions (DataLemur)](https://datalemur.com/blog/sql-window-functions-interview-questions)
- [SQL for Data Analysis: Advanced Techniques for Transforming Data into Insights — Cathy Tanimura (O'Reilly)](https://www.oreilly.com/library/view/sql-for-data/9781492088776/)
- [SQL 50 — Study Plan (LeetCode)](https://leetcode.com/studyplan/top-sql-50/)
