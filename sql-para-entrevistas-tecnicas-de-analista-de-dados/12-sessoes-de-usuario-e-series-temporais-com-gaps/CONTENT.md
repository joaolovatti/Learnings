# Sessões de Usuário e Séries Temporais com Gaps

![capa](cover.png)

## Sobre este capítulo

Sessionização — agrupar eventos contínuos do mesmo usuário em "sessões" usando um critério de timeout (ex: 30 minutos sem atividade encerra a sessão e começa outra) — é um dos problemas mais característicos da entrevista de SQL para empresas de produto digital. O enunciado vem como "definir sessões de uso a partir do log de eventos" ou "qual o número médio de eventos por sessão" e a solução canônica combina `LAG`, `CASE WHEN` para detectar quebra, e soma cumulativa para gerar o `session_id`. É um padrão em três passos que precisa estar internalizado para sair em 5 minutos sob pressão.

Em paralelo, séries temporais com gaps (datas faltantes na sequência) são o oposto da sessionização: em vez de agrupar eventos densos, é preciso *preencher* o que está ausente. "Calcule a receita por dia para todos os dias do mês, mesmo nos dias sem venda" exige `GENERATE_SERIES` (PostgreSQL) ou uma `CALENDAR` table ou um `RECURSIVE CTE` para gerar a régua de datas e fazer `LEFT JOIN` contra os dados reais. Este capítulo agrupa os dois temas porque ambos lidam com a mesma questão estrutural: a tabela tem uma granularidade temporal que não é suficiente para a pergunta — ou demais (precisa agrupar) ou de menos (precisa preencher).

## Estrutura

Os blocos do capítulo são: (1) definição de sessão por timeout — eventos do mesmo usuário com gap menor que N minutos pertencem à mesma sessão, eventos com gap maior iniciam nova sessão, e a tradução em SQL com `LAG(event_ts) OVER (PARTITION BY user ORDER BY event_ts)` + `CASE WHEN event_ts - lag_ts > INTERVAL '30 min' THEN 1 ELSE 0 END` como flag; (2) o idioma "soma cumulativa de flag = session_id" — `SUM(flag) OVER (PARTITION BY user ORDER BY event_ts)` produz um identificador único de sessão por usuário, sobre o qual se faz `GROUP BY` para métricas por sessão; (3) métricas por sessão — duração (`MAX(ts) - MIN(ts)`), número de eventos (`COUNT(*)`), eventos distintos (`COUNT(DISTINCT event_type)`), e métricas inter-sessão (tempo médio entre sessões); (4) preenchimento de séries temporais com gaps — `GENERATE_SERIES(start_date, end_date, '1 day')` em PostgreSQL, `WITH RECURSIVE` em SGBDs sem `GENERATE_SERIES`, e tabelas de calendário pré-existentes em data warehouses; (5) `LEFT JOIN` contra a régua de datas com `COALESCE(metric, 0)` para zerar dias ausentes — padrão obrigatório em queries de "métrica por dia/semana/mês"; (6) follow-ups clássicos do entrevistador — "e se o timeout for diferente por usuário?", "e se quisermos sessões por dispositivo dentro do mesmo usuário?", "e se houver dias sem nenhum evento na régua de datas — devo descartar ou manter?".

## Objetivo

Ao terminar, o leitor escreverá sessionização por timeout em três passos canônicos por reflexo (`LAG` para diff, `CASE WHEN` para flag, `SUM` cumulativo para session_id), calculará métricas agregadas por sessão e inter-sessão, dominará `GENERATE_SERIES`/recursão para gerar réguas de datas, e fará `LEFT JOIN` com `COALESCE` como padrão para preenchimento. Isso prepara o terreno para o capítulo de hierarquia (cap. 13), que generaliza o uso de `WITH RECURSIVE` de "gerar régua de datas" para "atravessar relações pai-filho".

## Fontes utilizadas

- [SQL for Data Analysis: Advanced Techniques for Transforming Data into Insights — Cathy Tanimura (O'Reilly)](https://www.oreilly.com/library/view/sql-for-data/9781492088776/)
- [T-SQL Window Functions: For Data Analysis and Beyond — Itzik Ben-Gan (Microsoft Press)](https://www.microsoftpressstore.com/store/t-sql-window-functions-for-data-analysis-and-beyond-9780135861448)
- [12 SQL Window Functions Interview Questions (DataLemur)](https://datalemur.com/blog/sql-window-functions-interview-questions)
- [How To Use LeetCode For Data Science SQL Interviews (StrataScratch)](https://www.stratascratch.com/blog/how-to-use-leetcode-for-data-science-sql-interviews)
- [Practice SQL Window Functions — Free Exercises for Interview Prep](https://www.practicewindowfunctions.com/)
- [Ultimate SQL Interview Guide for Data Scientists & Data Analysts (DataLemur)](https://datalemur.com/blog/sql-interview-guide)
