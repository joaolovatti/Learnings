# Append-Only Como Contrato de Persistência — EFS vs S3

![capa](cover.png)

## Sobre este subcapítulo

O append-only não é apenas uma característica de implementação do pi.dev — é o contrato de persistência sobre o qual toda a estratégia de armazenamento externo precisa ser construída. Cada nova entrada é adicionada ao final do arquivo; nenhuma linha existente é modificada ou removida em condições normais. Esse contrato tem implicações diretas e assimétricas sobre EFS e S3: EFS suporta append nativo como operação de sistema de arquivos; S3 não tem append nativo e exige reescrita completa do objeto (ou multipart upload com fusão ao final). Este subcapítulo explora essas implicações de forma direta, sem implementar a solução — a implementação é território dos capítulos 8 e 9.

A questão central aqui é: dado o que sabemos sobre o formato JSONL com append-only e árvore de `id`/`parentId`, quais são as restrições concretas que esse contrato impõe sobre qualquer mecanismo de storage externo? Responder isso é o objetivo deste subcapítulo.

## Estrutura

O subcapítulo cobre: (1) **o que "continuar uma sessão" significa em termos de arquivo** — o harness lê o arquivo do início ao fim na abertura, constrói o índice in-memory de `id → entrada`, e então escreve novas entradas no final; continuar significa reabrir o mesmo arquivo e acrescentar; (2) **append-only e EFS** — EFS suporta `open(O_APPEND)` nativo, o que faz append ser atômico ao nível de linha mesmo com múltiplos processos; por que isso é natural para hospedar sessões pi.dev e qual é a única tensão (latência de propagação em acesso multi-AZ); (3) **append-only e S3** — S3 não tem append nativo; qualquer nova entrada exige ou reescrita completa do objeto (simples mas caro em I/O e em condições de race condition) ou um pattern de acumulação + flush periódico; por que a ordem das linhas no arquivo não pode ser ignorada ao reconstruir o objeto no S3; (4) **read-after-write e consistência** — o harness assume que ao reabrir o arquivo ele vai ver todas as escritas anteriores; EFS garante isso; S3 em modo eventual consistency pode não garantir; o que isso significa para sessões com múltiplos turnos rápidos.

## Objetivo

Ao terminar este subcapítulo, o leitor conseguirá descrever com precisão as restrições que o contrato append-only impõe sobre EFS e S3, saberá por que a ordem das linhas no arquivo de sessão não pode ser ignorada ao serializar para object storage, e entenderá a diferença de consistência entre EFS e S3 no contexto de sessões pi.dev. Esse entendimento é o pré-requisito direto para os capítulos 8 (EFS multi-tenant) e 9 (SessionManager customizado sobre S3).

## Conceitos

A explicação completa destes conceitos vive em [`CONCEPTS.md`](CONCEPTS.md), construída sequencialmente pela skill `estudo-explicar-conceito`.

1. O ciclo de vida do arquivo de sessão na abertura — como o harness lê o arquivo inteiro para reconstruir o índice in-memory e depois abre em append; o que "continuar uma sessão" significa em termos de operações de arquivo
2. O_APPEND no POSIX e por que EFS o suporta nativamente — a semântica de `open(O_APPEND)` como garantia de offset atômico ao final do arquivo, e por que EFS (sistema de arquivos POSIX sobre NFS4) herda esse comportamento
3. A tensão de latência multi-AZ no EFS — por que EFS é natural para sessões pi.dev mas a propagação de escritas entre Availability Zones tem latência mensurável, e quando isso vira problema real
4. Por que S3 não tem append nativo e os dois patterns de contorno — imutabilidade do objeto em buckets padrão, reescrita completa vs acumulação + flush periódico, e o trade-off de cada abordagem
5. A ordem das linhas JSONL não pode ser ignorada ao serializar para S3 — por que a semântica de árvore (id/parentId) torna a ordem de append parte da estrutura lógica, e o que acontece se o merge de partes for feito fora de ordem
6. Read-after-write: EFS garante, S3 é fortemente consistente mas o race condition de reescrita ainda existe — a diferença entre consistência de leitura e atomicidade de escrita concorrente no contexto de sessões com múltiplos turnos rápidos

## Fontes utilizadas

- [Pi session-format — pi.dev/docs/latest](https://pi.dev/docs/latest/session-format)
- [Session Management and Persistence — DeepWiki (agentic-dev-io/pi-agent)](https://deepwiki.com/agentic-dev-io/pi-agent/2.4-session-management-and-persistence)
- [Append-only Log — QuestDB Glossary](https://questdb.com/glossary/append-only-log/)
- [Data Lake: JSONL in Amazon S3 — Transcend.io](https://transcend.io/integrations/s3-jsonl)
- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
- [Developers guide to using Amazon EFS with Amazon ECS and AWS Fargate — AWS Containers Blog](https://aws.amazon.com/blogs/containers/developers-guide-to-using-amazon-efs-with-amazon-ecs-and-aws-fargate-part-1/)
