# SessionManager Customizado Backed Por S3

![capa](cover.png)

## Sobre este capítulo

EFS resolve a persistência de sessão de forma transparente para o harness, mas carrega um custo estrutural: requer VPC, mount targets por AZ, e latência de filesystem em rede que impacta cold start e latência do primeiro turno. Para POCs que precisam funcionar fora de VPC, que têm restrição de custo de idle, ou onde o time de plataforma não quer gerenciar EFS, a alternativa é implementar um `SessionManager` customizado que usa S3 como backend — serializando e desserializando a árvore JSONL no início e no fim de cada invocação.

A tensão central deste capítulo é que S3 é object storage, não filesystem: não tem append-only nativo, não tem locking, e a leitura de um objeto retorna o objeto inteiro. Mapear a semântica append-only da árvore JSONL do pi.dev para put/get de objetos S3 sem perder fork e branch é o problema técnico que o capítulo resolve.

## Estrutura

O capítulo cobre: (1) **interface `SessionManager` do SDK pi.dev** — as operações que o SDK expõe para customizar o backend de sessão (`read`, `write`, `list`, `delete`), o contrato de cada operação em termos de JSONL; (2) **estratégia de serialização para S3** — mapear uma sessão para um objeto S3 (`s3://<bucket>/<userId>/<sessionId>.jsonl`), ler o objeto inteiro no início do turno, fazer append in-memory, escrever o objeto inteiro de volta ao fim; (3) **preservando fork e branch** — como o modelo de árvore (nós com `id`/`parentId`) sobrevive à serialização completa, o que diferencia fork seguro de fork que perde dados se duas invocações paralelas escreverem; (4) **locking otimista com S3** — conditional put via ETag para detectar conflito de escrita, estratégia de retry, quando usar DynamoDB para lock coordenado; (5) **comparação com EFS** — tabela de trade-offs (latência, custo, complexidade, VPC, concorrência) e quando S3 vence e quando EFS vence para diferentes perfis de POC.

## Objetivo

Ao terminar este capítulo, o leitor saberá implementar um `SessionManager` customizado backed por S3 que preserva fork e branch do pi.dev, entenderá os riscos de concorrência e como mitigá-los, e terá critérios claros para escolher entre EFS (capítulo 8) e S3 (este capítulo) para o perfil específico da sua POC.

## Fontes utilizadas

- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
- [Pi Coding Agent — README oficial, seção SessionManager](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [GitHub — serithemage/serverless-openclaw (S3 session persistence pattern)](https://github.com/serithemage/serverless-openclaw)
- [How We Built Secure, Scalable Agent Sandbox Infrastructure — Browser Use](https://browser-use.com/posts/two-ways-to-sandbox-agents)
- [AWS re:Invent 2025 — Serverless and Agentic AI Takeaways — Ran the Builder](https://ranthebuilder.cloud/blog/aws-re-invent-2025-my-serverless-agentic-ai-takeaways/)
