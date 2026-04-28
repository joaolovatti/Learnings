# SQL para Entrevistas Técnicas de Analista de Dados

![capa](cover.png)

## Sobre este livro

Este livro é um treino dirigido para passar nas entrevistas técnicas de SQL que separam um candidato a analista de dados do crachá. A proposta não é "aprender SQL do zero" nem "ser um expert em internals" — é construir, sobre uma base intermediária já existente, o repertório específico que cai em prova: padrões de problema que se repetem em LeetCode, HackerRank, StrataScratch e DataLemur, formatos de pergunta que recrutadores de empresas como Amazon, Meta, Google, Stripe e fintechs brasileiras fazem na vida real, e a forma de articular a resposta em voz alta, raciocinando sobre joins, agregações e janelas sem travar.

O recorte escolhido é o de "biblioteca de padrões + protocolo de entrevista". A maioria das entrevistas de SQL para analista não testa criatividade pura — testa reconhecimento: o entrevistador apresenta uma situação e espera que o candidato identifique, em segundos, que aquilo é "top-N por grupo", "running total", "gaps and islands", "funil", "retenção" ou "self-join temporal". Conhecer o catálogo dessas situações e ter uma solução de referência na ponta da língua é o que transforma uma entrevista de 45 minutos com pausas constrangedoras em uma conversa fluida onde o candidato direciona o ritmo. Esse livro existe para construir esse catálogo.

## Estrutura

Os grandes blocos são: (1) o modelo mental da entrevista de SQL — o que de fato é avaliado, como pensar em voz alta, como pedir esclarecimentos sobre o schema, como assumir e validar premissas sobre dados; (2) os padrões nucleares que aparecem em quase toda entrevista — `GROUP BY` com agregações, joins multi-tabela, subqueries correlacionadas, CTEs, set operators e `CASE WHEN` para lógica condicional; (3) o domínio das `window functions` aplicadas a entrevista — `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LEAD`/`LAG`, `SUM`/`AVG` com janelas, frames e `PARTITION BY`, com foco nos problemas que sempre caem (top-N, running totals, deduplicação, comparação row-a-row); (4) os padrões avançados de problema — gaps and islands, funis de conversão, análise de retenção/coorte, sessões de usuário, séries temporais com gaps preenchidos, problemas de hierarquia com CTEs recursivos; (5) a fluência operacional sob pressão — leitura rápida de schema, escolha entre alternativas equivalentes, cuidado com `NULL`, ordem lógica de avaliação (`WHERE` vs `HAVING` vs `QUALIFY`), e o que fazer quando travar; (6) um plano de prática estruturado por plataforma — quais listas de problemas atacar no LeetCode SQL 50, no HackerRank, no StrataScratch e no DataLemur, em que ordem, e como simular entrevistas cronometradas.

## Objetivo

Ao terminar, o leitor terá um catálogo internalizado dos ~15 a 20 padrões de problema que dominam entrevistas de SQL para analista de dados, com uma solução de referência idiomática para cada um e o vocabulário para reconhecê-los rapidamente sob pressão. Estará apto a resolver, em tempo hábil, problemas de nível "medium" e a maioria dos "hard" do LeetCode SQL 50 e equivalentes, a verbalizar a estratégia de solução antes de escrever a query, a antecipar perguntas de follow-up do entrevistador (o que muda se a tabela tiver duplicatas? e se o ranking permitir empates? e se houver `NULL` na coluna de ordenação?) e a identificar quando uma certificação como Oracle 1Z0-071 ou Microsoft DP-900 agrega valor concreto ao seu CV ou apenas distrai. O livro é a ponte entre "sei SQL" e "passo na entrevista" — duas coisas relacionadas mas distintas.

## Sobre o leitor

O leitor é um profissional com domínio intermediário de SQL focado em análise de dados. Ele já escreve queries com joins, agregações e subqueries no dia a dia, mas reconhece que o repertório que tem hoje não é o mesmo que destrava entrevistas técnicas de empresas que levam SQL a sério — há um delta entre "resolver problemas de trabalho com tempo livre" e "resolver problemas categorizados como 'medium' do LeetCode em 15 minutos enquanto explica o raciocínio em voz alta para um entrevistador".

Ele não trouxe, na entrevista de calibração, experiência adjacente em Python/pandas, Excel avançado, modelagem de dados ou outras tecnologias correlatas — sua bagagem é centrada em SQL mesmo. Isso significa que o livro não pode se apoiar em analogias com DataFrames, fórmulas de planilha ou modelos relacionais teóricos como atalho — toda a explicação precisa ficar dentro do próprio SQL, com queries de ida e volta sendo a mídia primária do raciocínio.

O objetivo declarado é triplo e convergente: passar em entrevistas técnicas, conquistar uma certificação reconhecida no mercado e usar isso para conseguir/avançar em uma posição profissional. Os três objetivos pedem o mesmo tipo de preparação — fluência em padrões reconhecíveis, segurança em sintaxe que não cai no dia a dia mas é cobrada em prova (subqueries no `FROM`, set operators, semantics de `NULL` em todas as cláusulas), e a disciplina de resolver problemas cronometrados até virar reflexo. O livro foi calibrado para servir esse leitor específico: alguém que já entende SQL o suficiente para saber o que está procurando, e quer um caminho denso e direto até a fluência de entrevista.

## Capítulos

1. [O Modelo Mental da Entrevista de SQL](01-o-modelo-mental-da-entrevista-de-sql/CONTENT.md) — como o entrevistador realmente avalia, pensar em voz alta, esclarecer schema e validar premissas sobre dados sujos
2. [Pensamento em Conjuntos: GROUP BY, Agregações e HAVING sob Pressão](02-pensamento-em-conjuntos-group-by-agregacoes-e-having-sob-pressao/CONTENT.md) — agregações idiomáticas, cardinalidade pós-agrupamento e os ataques clássicos de "conta por categoria"
3. [Joins Multi-Tabela: Inner, Outer, Self e Anti-Join](03-joins-multi-tabela-inner-outer-self-e-anti-join/CONTENT.md) — as variantes que caem em prova, autojoins temporais, anti-joins via LEFT JOIN ... IS NULL e armadilhas com NULL em colunas-chave
4. [Subqueries, Subqueries Correlacionadas e Set Operators](04-subqueries-subqueries-correlacionadas-e-set-operators/CONTENT.md) — quando subquery vence CTE, EXISTS vs IN vs JOIN, e UNION/INTERSECT/EXCEPT como ferramenta de comparação
5. [CTEs e CASE WHEN: Estruturando Queries Legíveis](05-ctes-e-case-when-estruturando-queries-legiveis/CONTENT.md) — quebrar problemas em estágios nomeados, lógica condicional dentro de SELECT/WHERE/ORDER BY e o estilo que entrevistadores leem em voz alta
6. [Window Functions — Fundamentos: PARTITION BY, ORDER BY e Frames](06-window-functions-fundamentos-partition-by-order-by-e-frames/CONTENT.md) — o modelo mental da janela, ROWS vs RANGE, default frames e como ler uma window function de trás para frente
7. [Ranking e Top-N por Grupo: ROW_NUMBER, RANK, DENSE_RANK](07-ranking-e-top-n-por-grupo-row-number-rank-dense-rank/CONTENT.md) — a família de ranking, o desempate consciente, top-N e bottom-N, e o filtro pós-window via CTE/QUALIFY
8. [LEAD, LAG e Comparações Row-a-Row](08-lead-lag-e-comparacoes-row-a-row/CONTENT.md) — diferenças entre linhas consecutivas, detecção de mudanças, IGNORE NULLS e o problema de "primeira ocorrência depois de X"
9. [Running Totals, Médias Móveis e Janelas Agregadas](09-running-totals-medias-moveis-e-janelas-agregadas/CONTENT.md) — SUM/AVG/COUNT com janela, frames customizados, médias móveis de N dias e cumulativos por grupo
10. [Gaps and Islands e Sequências Consecutivas](10-gaps-and-islands-e-sequencias-consecutivas/CONTENT.md) — a técnica do row_number diferencial, ilhas de atividade, streaks de login e detecção de períodos contínuos
11. [Funis de Conversão e Análise de Coorte/Retenção](11-funis-de-conversao-e-analise-de-coorte-retencao/CONTENT.md) — passos sequenciais de funil, cálculo de retenção D1/D7/D30 e construção de matriz de coorte direto em SQL
12. [Sessões de Usuário e Séries Temporais com Gaps](12-sessoes-de-usuario-e-series-temporais-com-gaps/CONTENT.md) — sessionização por timeout, GENERATE_SERIES/recursão para preencher datas faltantes e densidade temporal
13. [Hierarquia e CTEs Recursivos](13-hierarquia-e-ctes-recursivos/CONTENT.md) — árvores organizacionais, caminhos pai-filho, profundidade de nó e os limites de quando o recursivo é melhor que self-join repetido
14. [NULL, Ordem Lógica de Avaliação e QUALIFY: Detalhes que Travam Candidatos](14-null-ordem-logica-de-avaliacao-e-qualify/CONTENT.md) — semantics de NULL em todas as cláusulas, WHERE vs HAVING vs QUALIFY e a ordem real de execução que muda a query
15. [Plano de Prática por Plataforma e Decisão sobre Certificações](15-plano-de-pratica-por-plataforma-e-decisao-sobre-certificacoes/CONTENT.md) — sequência ótima no LeetCode SQL 50, HackerRank, StrataScratch e DataLemur, simulação cronometrada e quando 1Z0-071 ou DP-900 agregam ao CV

## Fontes utilizadas

- [SQL 50 — Study Plan (LeetCode)](https://leetcode.com/studyplan/top-sql-50/)
- [Ultimate SQL Interview Guide for Data Scientists & Data Analysts (DataLemur)](https://datalemur.com/blog/sql-interview-guide)
- [Leetcode and HackerRank Problems You Need to Practice for the Data Engineering SQL Interview — Sean Coyne (Medium)](https://medium.com/@seancoyne/leetcode-and-hackerrank-problems-you-need-to-practice-for-the-data-engineering-sql-interview-dddef57e7549)
- [How To Use LeetCode For Data Science SQL Interviews (StrataScratch)](https://www.stratascratch.com/blog/how-to-use-leetcode-for-data-science-sql-interviews)
- [SQL for Data Analysis: Advanced Techniques for Transforming Data into Insights — Cathy Tanimura (O'Reilly)](https://www.oreilly.com/library/view/sql-for-data/9781492088776/)
- [T-SQL Window Functions: For Data Analysis and Beyond — Itzik Ben-Gan (Microsoft Press)](https://www.microsoftpressstore.com/store/t-sql-window-functions-for-data-analysis-and-beyond-9780135861448)
- [Oracle Database SQL Certified Associate (1Z0-071) — Exam Topics](https://education.oracle.com/oracle-database-sql/pexam_1Z0-071)
- [SQL Roadmap — roadmap.sh](https://roadmap.sh/sql)
