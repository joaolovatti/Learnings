# O Modelo Mental da Entrevista de SQL

![capa](cover.png)

## Sobre este capítulo

Antes de qualquer query, a entrevista técnica de SQL é vencida ou perdida no primeiro minuto: na forma de receber o enunciado, decompor o schema, validar premissas sobre os dados e verbalizar a estratégia de solução. Este capítulo abre o livro porque os capítulos seguintes ensinam *o que* responder, mas só rendem na prova se o leitor souber *como* responder — e o "como" é um protocolo. Recrutadores experientes confirmam que candidatos com SQL técnico equivalente são separados pela qualidade do raciocínio em voz alta, pela velocidade em pedir esclarecimentos sobre cardinalidade e `NULL`, e pela disciplina de não escrever a query antes de ter o esqueleto da solução desenhado mentalmente.

A promessa central deste capítulo é instalar esse protocolo como reflexo: ler o enunciado de um problema "medium" e, em 30 a 60 segundos, ter classificado o padrão (top-N por grupo, running total, gaps and islands, funil), nomeado as ferramentas que vai usar (window function vs CTE recursivo vs self-join), antecipado os ataques do entrevistador (e se houver duplicatas? e se a coluna for `NULL`? e se houver empate?) e iniciado a fala da estratégia em voz alta antes de tocar no editor. Sem esse protocolo, os capítulos técnicos viram conhecimento ocioso; com ele, viram instrumento de palco.

## Estrutura

Os blocos do capítulo são: (1) o que de fato é avaliado em uma entrevista de SQL — reconhecimento de padrão, fluência sintática, raciocínio sobre dados sujos, comunicação técnica em voz alta, antecipação de follow-ups; (2) o protocolo de leitura do enunciado em 5 passos — extrair o output esperado, mapear o schema implícito ou explícito, identificar a granularidade do resultado, classificar o padrão arquetípico e nomear as cláusulas SQL correspondentes; (3) como pedir esclarecimentos sobre o schema sem soar inseguro — perguntas de cardinalidade ("a relação user-order é 1:N ou M:N?"), perguntas de qualidade ("`order_date` pode ser `NULL`?"), perguntas de regra de negócio ("trial conta como assinatura ativa?"); (4) o catálogo das premissas que precisam ser declaradas em voz alta antes de escrever a query — duplicatas, ordenação estável, empates em ranking, fuso horário, fronteiras de período; (5) a anatomia da fala-modelo de candidato sênior — abertura, esqueleto da solução, query, validação manual com 2-3 linhas de exemplo, follow-up proativo; (6) o que fazer quando travar — reduzir o problema a um caso menor, escrever pseudo-SQL antes de SQL real, pedir o output esperado para 3 linhas e voltar do output ao input.

## Objetivo

Ao terminar este capítulo, o leitor terá um protocolo operacional para os primeiros 60 segundos de qualquer problema de entrevista de SQL — saberá ler o enunciado de forma estruturada, identificar e declarar premissas críticas, classificar o padrão arquetípico antes de tocar no editor, e iniciar a fala da estratégia em voz alta com naturalidade. Isso prepara o terreno para os capítulos seguintes, onde cada padrão técnico (joins, CTEs, window functions, gaps and islands, funis, sessões) será associado a um gatilho de reconhecimento que se encaixa diretamente nesse protocolo.

## Fontes utilizadas

- [Ultimate SQL Interview Guide for Data Scientists & Data Analysts (DataLemur)](https://datalemur.com/blog/sql-interview-guide)
- [How To Use LeetCode For Data Science SQL Interviews (StrataScratch)](https://www.stratascratch.com/blog/how-to-use-leetcode-for-data-science-sql-interviews)
- [SQL 50 — Study Plan (LeetCode)](https://leetcode.com/studyplan/top-sql-50/)
- [Data Analyst Interview Preparation (DataCamp)](https://www.datacamp.com/blog/how-to-prepare-for-a-data-analyst-interview)
- [SQL Data Analyst Interview Preparation Guide (Coursera)](https://www.coursera.org/resources/sql-interview-prep-guide)
- [Dicas para Entrevistas de Emprego em SQL (Clarify)](https://clarify.com.br/blog/dicas-para-entrevistas-de-emprego-em-sql-como-se-preparar-e-se-destacar/)
