# LEAD, LAG e Comparações Row-a-Row

![capa](cover.png)

## Sobre este capítulo

`LEAD` e `LAG` são as window functions que olham para os vizinhos — `LAG` para a linha anterior, `LEAD` para a próxima — sem precisar de self-join. Em entrevista, esse par é a resposta canônica para uma família inteira de problemas: diferença entre dias consecutivos, detecção de mudança de status, "o tempo entre o pedido X e o seguinte do mesmo cliente", "este cliente comprou em dois dias seguidos?", "qual foi o último valor não-`NULL`". Antes das window functions, esses problemas eram resolvidos com self-joins acrobáticos sobre `ROW_NUMBER` ou `MIN(date) WHERE date > current.date` — soluções que funcionam mas comunicam pouca senioridade ao entrevistador. `LAG`/`LEAD` viraram o idioma esperado.

Este capítulo segue ranking porque completa a outra metade do "olhar para a vizinhança" da janela: ranking compara cada linha com as outras dentro do grupo; `LAG`/`LEAD` comparam cada linha com sua linha imediatamente vizinha. A promessa central é que o leitor reconheça em segundos quando o enunciado pede comparação entre linhas consecutivas, escreva `LAG(col, 1) OVER (PARTITION BY grupo ORDER BY tempo)` por reflexo, domine o `IGNORE NULLS` (onde suportado) para "último valor conhecido", e use o padrão "diff = atual - LAG(atual)" como ponte para o capítulo de gaps and islands à frente.

## Estrutura

Os blocos do capítulo são: (1) `LAG(col, n, default)` e `LEAD(col, n, default)` — sintaxe completa, o offset opcional (default 1), o valor de default opcional para a primeira/última linha, e por que essas duas funções precisam obrigatoriamente de `ORDER BY` dentro do `OVER`; (2) o arquétipo "diferença entre linhas consecutivas" — `valor_atual - LAG(valor)` para deltas de receita, dias entre pedidos, segundos entre eventos, e o pattern como precursor de funis e sessões; (3) detecção de mudança de status — "quando este cliente mudou de plano?", "qual a primeira linha em que o status virou `ACTIVE`?", resolvido com `LAG(status) <> status`; (4) `IGNORE NULLS` e o padrão "último valor conhecido" — backfill de séries esparsas, último preço observado antes de hoje, último login antes do evento atual, com nota sobre suporte por SGBD; (5) `FIRST_VALUE` e `LAST_VALUE` como variantes para "valor da primeira/última linha do frame" — a armadilha clássica do `LAST_VALUE` que retorna o que parece a "última linha vista até agora" devido ao frame default, e como corrigir com `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`; (6) padrões compostos — `LAG` aninhado em `CASE WHEN` para classificar transições, `LEAD` para "próxima ocorrência depois de X" e o problema "tempo até o próximo evento".

## Objetivo

Ao terminar, o leitor escreverá `LAG`/`LEAD` por reflexo para qualquer comparação entre linhas consecutivas, dominará o padrão "diff = atual - LAG(atual)", saberá quando usar `IGNORE NULLS` para backfill, e evitará a armadilha do `LAST_VALUE` com frame default. Isso prepara o terreno para o capítulo de janelas agregadas (cap. 9), onde a ideia de "olhar para uma vizinhança" se generaliza de "uma linha vizinha" para "um intervalo de N linhas vizinhas".

## Fontes utilizadas

- [T-SQL Window Functions: For Data Analysis and Beyond — Itzik Ben-Gan (Microsoft Press)](https://www.microsoftpressstore.com/store/t-sql-window-functions-for-data-analysis-and-beyond-9780135861448)
- [12 SQL Window Functions Interview Questions (DataLemur)](https://datalemur.com/blog/sql-window-functions-interview-questions)
- [SQL Window Functions Explained: The Complete Visual Guide (SQLNoir)](https://www.sqlnoir.com/blog/sql-window-functions)
- [How to Solve Gaps and Islands SQL Interview Questions with LAG and ROW_NUMBER (sqlpad.io)](https://sqlpad.io/tutorial/how-to-solve-gaps-and-islands-sql-interview-questions-with-lag-and-row-number/)
- [SQL for Data Analysis: Advanced Techniques for Transforming Data into Insights — Cathy Tanimura (O'Reilly)](https://www.oreilly.com/library/view/sql-for-data/9781492088776/)
- [SQL 50 — Study Plan (LeetCode)](https://leetcode.com/studyplan/top-sql-50/)
