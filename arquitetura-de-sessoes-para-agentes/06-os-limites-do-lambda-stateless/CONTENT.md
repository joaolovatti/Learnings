# Os Limites do Lambda Stateless

![capa](cover.png)

## Sobre este capítulo

AWS Lambda é uma plataforma excelente para muitas coisas — e uma plataforma fundamentalmente inadequada para outras. Agentes de longa duração estão na segunda categoria, mas a linha exata onde o Lambda começa a falhar não é óbvia: não é simplesmente o timeout de 15 minutos, porque há workarounds; é um conjunto de limitações estruturais que se acumulam quando o agente precisa de estado persistente, execuções longas e comunicação bidirecional simultânea. Este capítulo mapeia esses limites com honestidade — não para convencer o leitor a abandonar o Lambda, mas para equipá-lo a fazer essa decisão com dados, não com intuição.

Este capítulo vem antes das alternativas (caps. 7 e 8) porque o diagnóstico precede a prescrição. O leitor que entende exatamente o que falha e por quê consegue escolher a solução proporcional ao problema — em vez de migrar para ECS porque "Lambda tem limites" sem saber se esses limites afetam o seu caso específico.

## Estrutura

Os grandes blocos são: (1) o catálogo de hard limits — timeout máximo (15min), tamanho de payload de request/response (6MB síncrono, 256KB assíncrono), memória máxima (10GB), cold start e seu impacto em sessões que precisam restaurar estado volumoso; (2) o que falha primeiro num agente real — análise de cenários concretos: uma sessão que requer múltiplos rounds de tool calling, um agente que precisa esperar por aprovação humana, uma sessão retomada horas depois; (3) padrões de workaround dentro do Lambda — continuation tokens (invocar o próprio Lambda recursivamente via SNS/SQS), externalização agressiva de estado, chunking de respostas longas, e os trade-offs de cada abordagem; (4) o ponto de ruptura — critérios objetivos para identificar quando um workaround vira gambiarra e a migração para uma arquitetura com estado nativo se justifica.

## Objetivo

Ao terminar este capítulo, o leitor será capaz de mapear os limites do Lambda que efetivamente impactam o seu projeto atual, implementar pelo menos um workaround de continuation para estender o ciclo de vida de um agente além do timeout padrão, e articular com clareza os critérios que, se atingidos, justificariam a migração para Lambda Durable Functions (cap. 7) ou Fargate (cap. 8).

## Fontes utilizadas

- [Effectively building AI agents on AWS Serverless — AWS Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
- [Stateful vs Stateless AI Agents: Architecture Patterns That Matter — ruh.ai](https://www.ruh.ai/blogs/stateful-vs-stateless-ai-agents)
- [Lambda, Fargate, Bedrock Agent — Which serverless option for your Agentic pattern?](https://medium.com/@loic.labeye/lambda-fargate-agentcore-which-severless-option-to-choose-for-your-agentic-pattern-aaf68cb99700)
- [Serverless strategies for streaming LLM responses — AWS Compute Blog](https://aws.amazon.com/blogs/compute/serverless-strategies-for-streaming-llm-responses/)
- [Architecting for agentic AI development on AWS — AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/architecting-for-agentic-ai-development-on-aws/)
