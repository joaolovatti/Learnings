# Estrutura do Livro

> Mapa rapido da organizacao do livro: capitulos, subcapitulos e conceitos. Mantido automaticamente pela skill `estudo-atualizar-struct` — nao edite a mao.

```
sql-para-entrevistas-tecnicas-de-analista-de-dados/ — SQL para Entrevistas Técnicas de Analista de Dados
├── 01-o-modelo-mental-da-entrevista-de-sql/ — como o entrevistador realmente avalia, pensar em voz alta, esclarecer schema e validar premissas sobre dados sujos
├── 02-pensamento-em-conjuntos-group-by-agregacoes-e-having-sob-pressao/ — agregações idiomáticas, cardinalidade pós-agrupamento e os ataques clássicos de "conta por categoria"
├── 03-joins-multi-tabela-inner-outer-self-e-anti-join/ — as variantes que caem em prova, autojoins temporais, anti-joins via LEFT JOIN ... IS NULL e armadilhas com NULL em colunas-chave
├── 04-subqueries-subqueries-correlacionadas-e-set-operators/ — quando subquery vence CTE, EXISTS vs IN vs JOIN, e UNION/INTERSECT/EXCEPT como ferramenta de comparação
├── 05-ctes-e-case-when-estruturando-queries-legiveis/ — quebrar problemas em estágios nomeados, lógica condicional dentro de SELECT/WHERE/ORDER BY e o estilo que entrevistadores leem em voz alta
├── 06-window-functions-fundamentos-partition-by-order-by-e-frames/ — o modelo mental da janela, ROWS vs RANGE, default frames e como ler uma window function de trás para frente
├── 07-ranking-e-top-n-por-grupo-row-number-rank-dense-rank/ — a família de ranking, o desempate consciente, top-N e bottom-N, e o filtro pós-window via CTE/QUALIFY
├── 08-lead-lag-e-comparacoes-row-a-row/ — diferenças entre linhas consecutivas, detecção de mudanças, IGNORE NULLS e o problema de "primeira ocorrência depois de X"
├── 09-running-totals-medias-moveis-e-janelas-agregadas/ — SUM/AVG/COUNT com janela, frames customizados, médias móveis de N dias e cumulativos por grupo
├── 10-gaps-and-islands-e-sequencias-consecutivas/ — a técnica do row_number diferencial, ilhas de atividade, streaks de login e detecção de períodos contínuos
├── 11-funis-de-conversao-e-analise-de-coorte-retencao/ — passos sequenciais de funil, cálculo de retenção D1/D7/D30 e construção de matriz de coorte direto em SQL
├── 12-sessoes-de-usuario-e-series-temporais-com-gaps/ — sessionização por timeout, GENERATE_SERIES/recursão para preencher datas faltantes e densidade temporal
├── 13-hierarquia-e-ctes-recursivos/ — árvores organizacionais, caminhos pai-filho, profundidade de nó e os limites de quando o recursivo é melhor que self-join repetido
├── 14-null-ordem-logica-de-avaliacao-e-qualify/ — semantics de NULL em todas as cláusulas, WHERE vs HAVING vs QUALIFY e a ordem real de execução que muda a query
└── 15-plano-de-pratica-por-plataforma-e-decisao-sobre-certificacoes/ — sequência ótima no LeetCode SQL 50, HackerRank, StrataScratch e DataLemur, simulação cronometrada e quando 1Z0-071 ou DP-900 agregam ao CV
```
