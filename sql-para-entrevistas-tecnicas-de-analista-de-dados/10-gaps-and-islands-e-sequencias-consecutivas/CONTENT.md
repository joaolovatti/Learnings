# Gaps and Islands e Sequências Consecutivas

![capa](cover.png)

## Sobre este capítulo

"Gaps and islands" é o padrão avançado que mais aparece em entrevistas de empresas que levam SQL a sério — Stripe, Meta, fintechs brasileiras com produto data-heavy, qualquer empresa que precise contar streaks, sessões, períodos de assinatura ativa, ou qualquer outra noção de "sequência ininterrupta". O nome é descritivo: uma *island* é uma corrida contígua de linhas relacionadas (ex: dias consecutivos com login); um *gap* é o intervalo entre duas islands. O padrão tem uma solução canônica de elegância surpreendente — a técnica do `ROW_NUMBER` diferencial, que transforma um problema temporal complexo em um simples `GROUP BY` sobre uma chave derivada — mas exige que o candidato a tenha visto antes para encaixar sob pressão.

Este capítulo abre o bloco de padrões avançados porque é o que mais densifica retorno por minuto de estudo: uma única técnica destranca uma família grande de problemas que parecem distintos no enunciado mas colapsam na mesma resolução. A promessa central é que o leitor reconheça gaps and islands por sintoma — "datas consecutivas", "streak", "período contínuo", "sessões com base em timeout fixo" — e escreva a solução canônica em CTE de três estágios (`row_number_global`, `row_number_per_group`, `island_id = global - per_group`, depois `GROUP BY island_id`) por reflexo.

## Estrutura

Os blocos do capítulo são: (1) anatomia do problema — definição formal de island e gap, exemplos clássicos (login streak, dias consecutivos com venda, período contínuo de assinatura ativa, períodos sem mudança de status), e o radar para reconhecer pelo enunciado; (2) a técnica canônica do `ROW_NUMBER` diferencial — `ROW_NUMBER() OVER (ORDER BY data)` menos `ROW_NUMBER() OVER (PARTITION BY user ORDER BY data)` produz uma chave constante dentro de cada island, e `GROUP BY` essa chave entrega `MIN(data)`, `MAX(data)` e `COUNT(*)` da island; (3) variante com `LAG` e flag de início — `CASE WHEN LAG(data) OVER (...) <> data - 1 THEN 1 ELSE 0 END` marca o início de cada island, e `SUM` cumulativo dessa flag dá o island_id; (4) gaps and islands com critério não-temporal — "linhas com mesmo status consecutivas" em vez de "linhas com data consecutiva", abstração da técnica para qualquer ordenação; (5) os arquétipos canônicos — login streak mais longo, mês com mais dias consecutivos de venda, período mais longo de assinatura ativa, datas consecutivas em uma agenda, e o problema clássico do LeetCode "Human Traffic of Stadium"; (6) variantes de follow-up — "e se permitirmos um gap de até 1 dia?" (ilhas relaxadas), "e se quisermos só ilhas com tamanho >= N?" (filtro pós-agregação), "e se houver duplicatas no mesmo dia?" (deduplicação prévia).

## Objetivo

Ao terminar, o leitor reconhecerá gaps and islands por sintoma do enunciado em segundos, escreverá a técnica do `ROW_NUMBER` diferencial por reflexo, dominará a variante com `LAG` para casos com critério não-temporal, e responderá com naturalidade as follow-ups sobre relaxamento de gaps e tamanho mínimo de ilha. Isso prepara o terreno para o capítulo de funis e coortes (cap. 11), onde a mesma sensibilidade temporal aparece com outra estrutura — sequência de eventos rotulados em vez de continuidade temporal pura.

## Fontes utilizadas

- [Gaps and Islands in SQL: Techniques & Examples (Simple Talk / Redgate)](https://www.red-gate.com/simple-talk/databases/sql-server/t-sql-programming-sql-server/introduction-to-gaps-and-islands-analysis/)
- [How to Solve Gaps and Islands SQL Interview Questions with LAG and ROW_NUMBER (sqlpad.io)](https://sqlpad.io/tutorial/how-to-solve-gaps-and-islands-sql-interview-questions-with-lag-and-row-number/)
- [SQL Interview Patterns You Must Know! Part 1 — Gaps and Islands (Medium)](https://medium.com/@mvanshika23/sql-interview-patterns-you-must-know-part-1-n-gaps-and-islands-e9db5c97140f)
- [Practice SQL Window Functions — Free Exercises for Interview Prep (Gap and Island)](https://www.practicewindowfunctions.com/learn/gap_and_island)
- [T-SQL Window Functions: For Data Analysis and Beyond — Itzik Ben-Gan (Microsoft Press)](https://www.microsoftpressstore.com/store/t-sql-window-functions-for-data-analysis-and-beyond-9780135861448)
- [Understanding Gaps and Islands in SQL (Medium)](https://medium.com/@dinkalchug18/understanding-gaps-and-islands-in-sql-99c77e1a696a)
