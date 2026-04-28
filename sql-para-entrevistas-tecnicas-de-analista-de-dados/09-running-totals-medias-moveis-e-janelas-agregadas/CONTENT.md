# Running Totals, Médias Móveis e Janelas Agregadas

![capa](cover.png)

## Sobre este capítulo

`SUM`, `AVG`, `COUNT`, `MIN` e `MAX` ganham um significado completamente novo quando vão para dentro de uma `OVER (...)`. Em vez de colapsar todas as linhas em uma só, passam a calcular um agregado *cumulativo* ou *deslizante* preservando a granularidade original do resultado. Esse mecanismo é o que viabiliza, em uma única query legível, três famílias de problema clássicas em entrevista: running total ("soma acumulada de receita por cliente ao longo do tempo"), média móvel ("média dos últimos 7 dias por usuário") e estatísticas relativas ("a receita deste mês representa quanto do total do ano?"). Cada uma dessas famílias é o coração de pelo menos um problema "medium" do LeetCode SQL 50 e aparece em entrevistas de empresas que vão de fintechs brasileiras a Big Tech.

Este capítulo fecha o bloco de window functions oferecendo a generalização final: enquanto ranking olha para o conjunto inteiro do grupo e `LAG`/`LEAD` olham para uma linha vizinha, agregadas com janela olham para um intervalo configurável de linhas vizinhas — definido pelo frame. A promessa central é que o leitor escreva running totals por reflexo, controle frames `ROWS BETWEEN N PRECEDING AND CURRENT ROW` para médias móveis, calcule percentuais de total dentro do grupo com `SUM(...) OVER (PARTITION BY ...)`, e diagnostique a armadilha clássica do frame default em running totals com ties no `ORDER BY`.

## Estrutura

Os blocos do capítulo são: (1) running totals canônicos — `SUM(valor) OVER (PARTITION BY user ORDER BY data)`, com discussão da diferença entre o frame default `RANGE` (que pode dobrar valores em ties) e o `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` que produz o resultado esperado; (2) médias móveis — `AVG(valor) OVER (PARTITION BY user ORDER BY data ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` para média de 7 dias, e a calibração de janelas (3, 7, 14, 30 dias) por contexto; (3) percentuais sobre o total do grupo — `valor / SUM(valor) OVER (PARTITION BY grupo)` para "share dentro do grupo", e a variante com `OVER ()` (sem partição) para "share sobre o total geral"; (4) `COUNT(*) OVER (PARTITION BY ...)` como ferramenta de deduplicação consciente — contar quantas linhas existem no grupo sem colapsar, padrão para resolver "o pedido de cliente que tem mais de um pedido no mesmo dia"; (5) frames customizados na fronteira — `ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING` para janelas centradas, `RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW` para janelas baseadas em tempo (PostgreSQL), e suporte por SGBD; (6) os padrões clássicos da entrevista — "receita acumulada por mês até virada do ano", "média móvel de transações por usuário", "primeiro mês em que o cliente passou de R$ 10k acumulados", "share da categoria sobre o total do dia".

## Objetivo

Ao terminar, o leitor escreverá running totals com o frame correto por reflexo, dominará médias móveis com janelas configuráveis, calculará percentuais sobre total dentro e fora de grupo, e evitará a armadilha do frame default em running totals com ties. Isso completa o bloco de window functions e fornece todas as ferramentas necessárias para o bloco seguinte de padrões avançados (caps. 10 a 13), onde gaps and islands, funis, sessões e hierarquias serão construídos compondo as três famílias de window function aprendidas até aqui.

## Fontes utilizadas

- [T-SQL Window Functions: For Data Analysis and Beyond — Itzik Ben-Gan (Microsoft Press)](https://www.microsoftpressstore.com/store/t-sql-window-functions-for-data-analysis-and-beyond-9780135861448)
- [12 SQL Window Functions Interview Questions (DataLemur)](https://datalemur.com/blog/sql-window-functions-interview-questions)
- [SQL Window Functions Explained: The Complete Visual Guide (SQLNoir)](https://www.sqlnoir.com/blog/sql-window-functions)
- [SQL for Data Analysis: Advanced Techniques for Transforming Data into Insights — Cathy Tanimura (O'Reilly)](https://www.oreilly.com/library/view/sql-for-data/9781492088776/)
- [Practice SQL Window Functions — Free Exercises for Interview Prep](https://www.practicewindowfunctions.com/)
- [SQL 50 — Study Plan (LeetCode)](https://leetcode.com/studyplan/top-sql-50/)
