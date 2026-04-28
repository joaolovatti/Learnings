# learnings

Método de estudo estruturado em livros. Cada livro vive num diretório próprio e se decompõe em capítulos → subcapítulos → conceitos, com `cover.png` (capa didática), `INTRODUCTION.md` (apresentação) e `STRUCT.md` (índice hierárquico completo).

## Livros

### [POC End-to-End — Pi.dev Atrás de API Gateway na AWS Para Validação Com Cliente](poc-pidev-na-aws-atras-de-api-gateway/INTRODUCTION.md)

![capa](poc-pidev-na-aws-atras-de-api-gateway/cover.png)

Travessia de um engenheiro sênior — avançado em AWS e LLMs, zero em pi.dev — até uma POC pública na AWS que o cliente consegue testar via API Gateway sem suporte do dev. Foco deliberadamente prático: pi.dev tratado como runtime pronto, decisões de hospedagem (Lambda vs Fargate, EFS vs S3, SDK vs RPC) calibradas para o caso específico do harness, sessões persistidas fora do disco local, e empacotamento da entrega (URL pública, credencial de teste, instruções) como objetivo final. Não cobre hardening de produção — esse recorte fica para os livros seguintes do método.

### [SQL para Entrevistas Técnicas de Analista de Dados](sql-para-entrevistas-tecnicas-de-analista-de-dados/INTRODUCTION.md)

![capa](sql-para-entrevistas-tecnicas-de-analista-de-dados/cover.png)

Treino dirigido para um profissional de SQL intermediário focado em análise de dados que precisa, ao mesmo tempo, passar em entrevistas técnicas, conquistar uma certificação reconhecida e usar isso para avançar profissionalmente. Constrói o catálogo dos 15 a 20 padrões de problema que dominam entrevistas reais — top-N por grupo, running totals, gaps and islands, funis, retenção, sessões, hierarquias com CTEs recursivos — com `window functions` ocupando o centro do palco. Cobre também o protocolo da entrevista (pensar em voz alta, validar premissas, antecipar follow-ups) e um plano de prática estruturado por LeetCode SQL 50, HackerRank, StrataScratch e DataLemur, com ponte para a certificação Oracle 1Z0-071.
