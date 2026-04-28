# Hierarquia e CTEs Recursivos

![capa](cover.png)

## Sobre este capítulo

`WITH RECURSIVE` é o último grande padrão técnico do livro — a ferramenta que destranca problemas de hierarquia (organogramas, árvores de categoria, grafo de seguidores, manager → manager → manager até o CEO) e qualquer problema cuja solução envolva iterar sobre um conjunto que cresce a cada passo. Em entrevista, recursivo aparece em duas situações características: árvores organizacionais ("liste todos os subordinados diretos e indiretos do funcionário X" ou "qual o nível hierárquico de cada funcionário?") e grafos de relação ("o caminho mais curto entre dois nós", "todas as categorias-filho de uma raiz"). É um padrão menos frequente que window functions — pode passar uma rodada inteira de entrevistas sem aparecer — mas quando aparece, descobre o candidato que só sabe SQL "plano".

Este capítulo encerra o bloco de padrões avançados porque é o tipo de padrão que requer uma mudança de modelo mental: em vez de "um conjunto de linhas processado em uma passada", o leitor precisa pensar em "um conjunto que cresce iterativamente até estabilizar". A promessa central é que o leitor escreva o esqueleto canônico do `WITH RECURSIVE` (anchor + recursive member + `UNION ALL`) por reflexo, identifique quando o problema *é* recursivo (precisa atravessar relação pai-filho/anterior-próximo de profundidade desconhecida), e saiba o limiar onde "self-join repetido" deixa de ser viável e o recursivo é a única saída.

## Estrutura

Os blocos do capítulo são: (1) anatomia de um `WITH RECURSIVE` — anchor member (a query base que retorna o ponto de partida), recursive member (a query que se referencia a si mesma e adiciona uma camada por iteração), `UNION ALL` entre os dois, e a regra de terminação implícita (quando a recursive member retorna 0 linhas); (2) árvore organizacional clássica — `employee(id, manager_id, name)`, "todos os subordinados diretos e indiretos de X", profundidade hierárquica (`level + 1` no recursive member); (3) caminho ascendente — "do funcionário X até o CEO", construindo o caminho como `path || '->' || name` na recursão; (4) árvore de categoria de produto — categorias que têm subcategorias, listar todos os produtos dentro de uma raiz incluindo descendentes; (5) o trade-off recursivo vs self-join repetido — quando a profundidade é conhecida e pequena (1, 2, 3 níveis), `JOIN` repetido vence; quando a profundidade é desconhecida ou grande, recursivo é obrigatório, e a justificativa em voz alta para o entrevistador; (6) follow-ups clássicos — "e se houver ciclo na hierarquia?" (precaução com termination), "e se for um grafo em vez de árvore?" (cuidado com revisita de nós), "e o limite de recursão configurável?" (`MAXRECURSION` no SQL Server, `SET LOCAL max_stack_depth` em outros).

## Objetivo

Ao terminar, o leitor escreverá o esqueleto `WITH RECURSIVE` canônico por reflexo, resolverá árvores organizacionais (descendentes, ascendentes, profundidade) sem hesitar, identificará em segundos quando o problema é recursivo vs quando self-join encadeado basta, e responderá com naturalidade follow-ups sobre ciclos e profundidade máxima. Isso fecha o bloco de padrões avançados e prepara o terreno para os dois últimos capítulos — fluência operacional sob pressão (cap. 14) e plano de prática (cap. 15) — que consolidam o repertório montado nos capítulos 1 a 13.

## Fontes utilizadas

- [SQL for Data Analysis: Advanced Techniques for Transforming Data into Insights — Cathy Tanimura (O'Reilly)](https://www.oreilly.com/library/view/sql-for-data/9781492088776/)
- [T-SQL Window Functions: For Data Analysis and Beyond — Itzik Ben-Gan (Microsoft Press)](https://www.microsoftpressstore.com/store/t-sql-window-functions-for-data-analysis-and-beyond-9780135861448)
- [Ultimate SQL Interview Guide for Data Scientists & Data Analysts (DataLemur)](https://datalemur.com/blog/sql-interview-guide)
- [SQL 50 — Study Plan (LeetCode)](https://leetcode.com/studyplan/top-sql-50/)
- [Oracle Database SQL Certified Associate (1Z0-071) — Exam Topics](https://education.oracle.com/oracle-database-sql/pexam_1Z0-071)
- [SQL Roadmap — roadmap.sh](https://roadmap.sh/sql)
