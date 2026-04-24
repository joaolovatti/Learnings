# Esquemas de Persistência de Estado

![capa](cover.png)

## Sobre este capítulo

Definidos o modelo mental (cap. 2) e o ciclo de vida (cap. 3), chegou a hora de escolher onde e como persistir o estado da sessão. Esta não é uma decisão trivial: MongoDB, DynamoDB e S3 têm trade-offs radicalmente diferentes em latência, custo, capacidade de query e atomicidade de escrita — e a escolha errada se manifesta como lentidão, custo explosivo ou bugs sutis de concorrência que só aparecem sob carga. Este capítulo faz o comparativo técnico honesto entre as três opções, propõe um schema concreto de documento de sessão e cobre a serialização de `ChatMessage` e `ToolCall` do Haystack para formatos persistíveis.

O leitor já usa MongoDB para histórico de chat — este capítulo parte desse ativo e mostra como evoluir o schema existente para suportar a camada de sessão completa, em vez de começar do zero.

## Estrutura

Os grandes blocos são: (1) comparativo MongoDB vs DynamoDB vs S3 — latência de leitura/escrita, custo por operação, suporte a queries ad-hoc, atomicidade de updates parciais e adequação para diferentes partes do substrato (mensagens vs metadados vs arquivos grandes); (2) schema do documento de sessão no MongoDB — design do documento principal (session_id, state, turns, runs, tool_events, compaction_log, metadata), índices recomendados e estratégias de sharding por usuário; (3) serialização de artefatos do Haystack — como converter `ChatMessage`, `ToolCall` e `ToolCallResult` para BSON/JSON persistível e de volta para objetos Haystack na reconstrução do contexto; (4) estratégia híbrida — usar MongoDB para estado quente (últimos N turns) e S3 para arquivo de longa duração, com política de migração automática.

## Objetivo

Ao terminar este capítulo, o leitor será capaz de projetar o schema MongoDB de uma sessão agêntica completa, implementar a serialização/deserialização dos artefatos Haystack existentes no seu projeto, e tomar uma decisão fundamentada sobre quando adicionar DynamoDB ou S3 como camadas complementares. O schema definido aqui será o substrato concreto usado nos capítulos 5 (compactação) e 10 (integração com o loop agêntico).

## Fontes utilizadas

- [7 State Persistence Strategies for Long-Running AI Agents in 2026 — Indium Tech](https://www.indium.tech/blog/7-state-persistence-strategies-ai-agents-2026/)
- [Effectively building AI agents on AWS Serverless — AWS Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
- [AI agent memory: types, architecture & implementation — Redis](https://redis.io/blog/ai-agent-memory-stateful-systems/)
- [Letta: Building Stateful AI Agents with In-Context Learning and Memory Management — ZenML](https://www.zenml.io/llmops-database/building-stateful-ai-agents-with-in-context-learning-and-memory-management)
- [Agent Memory: Building Memory-Aware Agents — DeepLearning.AI](https://www.deeplearning.ai/short-courses/agent-memory-building-memory-aware-agents/)
