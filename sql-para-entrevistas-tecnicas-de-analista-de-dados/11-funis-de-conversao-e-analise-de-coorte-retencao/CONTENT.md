# Funis de Conversão e Análise de Coorte/Retenção

![capa](cover.png)

## Sobre este capítulo

Funil e coorte são as duas perguntas de produto que toda empresa orientada a dados quer ver o candidato resolver no whiteboard — porque medem, respectivamente, o cerne da aquisição (quantos usuários passam do passo X para o passo Y) e o cerne da fidelidade (quantos usuários do mês N ainda estão ativos no mês N+30). Em entrevistas de Meta, Stripe, Nubank, iFood e qualquer empresa de produto, esses são os dois padrões mais reusados. O leitor já entende o conceito de funil e coorte como métrica de produto; o que cai em prova é a tradução desses conceitos em SQL idiomático — uma única query estruturada em CTEs que computa todas as taxas do funil de uma vez, ou que produz a matriz `coorte × período` que vira o gráfico de retenção.

Este capítulo segue gaps and islands porque a sequência temporal de eventos rotulados — `signup` → `first_session` → `purchase` → `repurchase` — é uma generalização do "ordenar e olhar consecutivos" que o capítulo anterior estabeleceu. A promessa central é que o leitor escreva funis multi-passo com `LEFT JOIN` ou `MIN(CASE WHEN event_type = X THEN ts END)` por reflexo, construa matrizes de retenção D1/D7/D30 em poucas linhas usando `DATEDIFF` e `GROUP BY`, e antecipe os follow-ups clássicos sobre janela de conversão (em quanto tempo o passo Y conta?) e definição de coorte (data de signup, primeiro evento, primeiro pagamento?).

## Estrutura

Os blocos do capítulo são: (1) anatomia de um funil de conversão — sequência ordenada de eventos rotulados com janela de conversão entre eles, e a tradução padrão em SQL: uma CTE por passo, `LEFT JOIN` encadeado pelo `user_id` com filtro de data; (2) o idioma `MIN(CASE WHEN event = X THEN ts END) OVER (PARTITION BY user)` — calcula o timestamp do passo X para cada usuário em uma única passada, e habilita comparações inter-passo (ex: `purchase_ts - signup_ts <= 7 days`); (3) cálculo de taxas em uma query — `COUNT(passo_2) / COUNT(passo_1) AS taxa_2_sobre_1`, `COUNT(passo_3) / COUNT(passo_2)`, etc., com `NULLIF` para evitar divisão por zero; (4) anatomia de coorte — agrupamento de usuários pelo período do primeiro evento (data de signup) e medição da atividade desses usuários em períodos subsequentes; (5) matriz de retenção D1/D7/D30 — `DATEDIFF(activity_date, cohort_date)` como eixo, `cohort_month` como linhas, e o uso de `COUNT DISTINCT user_id` para garantir que cada usuário conte uma vez por célula; (6) follow-ups e variações — coorte por canal de aquisição, retenção rolling (em vez de fixed-window), funis com passos opcionais, e a discussão sobre quando o entrevistador espera o cálculo direto vs uma estrutura de pivô.

## Objetivo

Ao terminar, o leitor escreverá funis multi-passo com `MIN(CASE WHEN ...) OVER (...)` ou com `LEFT JOIN` encadeado dependendo do que o problema pede, calculará taxas inter-passo com `NULLIF` por reflexo, construirá matrizes de coorte D1/D7/D30 em uma query estruturada em 2-3 CTEs, e responderá com naturalidade follow-ups sobre janelas de conversão e definição de coorte. Isso prepara o terreno para o capítulo de sessões e séries temporais (cap. 12), onde a estrutura "evento sequencial" se generaliza para "como definir um agrupamento de eventos que não vem com chave explícita".

## Fontes utilizadas

- [SQL for Data Analysis: Advanced Techniques for Transforming Data into Insights — Cathy Tanimura (O'Reilly)](https://www.oreilly.com/library/view/sql-for-data/9781492088776/)
- [SQL Cohort Analysis and Retention Interview Questions (Let's Data Science)](https://letsdatascience.com/blog/sql-cohort-retention-interview-questions)
- [Ultimate SQL Interview Guide for Data Scientists & Data Analysts (DataLemur)](https://datalemur.com/blog/sql-interview-guide)
- [12 SQL Window Functions Interview Questions (DataLemur)](https://datalemur.com/blog/sql-window-functions-interview-questions)
- [How To Use LeetCode For Data Science SQL Interviews (StrataScratch)](https://www.stratascratch.com/blog/how-to-use-leetcode-for-data-science-sql-interviews)
- [SQL 50 — Study Plan (LeetCode)](https://leetcode.com/studyplan/top-sql-50/)
