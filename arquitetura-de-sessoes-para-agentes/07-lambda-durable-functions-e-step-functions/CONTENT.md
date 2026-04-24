# Lambda Durable Functions e Step Functions

![capa](cover.png)

## Sobre este capítulo

AWS Lambda Durable Functions, anunciado no re:Invent 2025, introduz um modelo de checkpoint-and-replay diretamente no Lambda — permitindo que uma função pause, persista seu estado, e retome exatamente de onde parou, removendo o limite de 15 minutos para workflows que toleram interrupção. Para o leitor que já opera num Lambda e quer o menor passo incremental possível em direção a sessões longas, esta é a rota mais natural. O AWS Step Functions, por outro lado, existe há anos e oferece orquestração explícita de múltiplos Lambdas como um workflow visual e auditável. Este capítulo cobre ambos: quando cada um se aplica, como implementar um loop agêntico sobre eles, e onde cada abordagem mostra suas costuras.

A posição aqui — após o diagnóstico dos limites do Lambda (cap. 6) e antes da alternativa de containerização (cap. 8) — segue a ordem natural de escalada: primeiro tente ficar no serverless com ferramentas mais poderosas; só então migre para infraestrutura com estado nativo.

## Estrutura

Os grandes blocos são: (1) Lambda Durable Functions em detalhe — o modelo de checkpoint-and-replay, como o estado é serializado entre checkpoints, limitações remanescentes (payload de estado, latência de retomada) e o caso de uso ideal para agentes; (2) implementando um loop agêntico com Durable Functions — estrutura de uma função durável que executa o ReAct loop, faz checkpoint antes de cada tool call e retoma após o resultado, com código Python de exemplo; (3) AWS Step Functions para orquestração multi-step — quando o workflow é mais um pipeline de passos bem definidos do que um loop aberto, e como modelar isso com State Machine Language; integração com Lambda para cada step; (4) comparativo direto — Durable Functions vs Step Functions para agentes: latência, observabilidade, custo, complexidade de implementação e o critério de escolha; (5) limites de ambos — o que ainda não se resolve com nenhuma das duas abordagens e que aponta para o capítulo 8.

## Objetivo

Ao terminar este capítulo, o leitor será capaz de implementar um loop agêntico básico usando Lambda Durable Functions com checkpoint antes de cada tool call, modelar um workflow de agente multi-step em Step Functions, e escolher entre as duas abordagens com base nos requisitos concretos do seu projeto. O leitor chegará ao capítulo 8 com clareza sobre quando Fargate/ECS é genuinamente necessário.

## Fontes utilizadas

- [AWS Introduces Durable Functions: Stateful Logic Directly in Lambda Code — InfoQ](https://www.infoq.com/news/2025/12/aws-lambda-durable-functions/)
- [AWS Lambda Durable Functions: Building Reliable Stateful Workflows Without Step Functions](https://www.dataa.dev/2026/02/10/aws-lambda-durable-functions-stateful-workflows-2/)
- [Build a serverless conversational AI agent using Claude with LangGraph and SageMaker AI — AWS Blog](https://aws.amazon.com/blogs/machine-learning/build-a-serverless-conversational-ai-agent-using-claude-with-langgraph-and-managed-mlflow-on-amazon-sagemaker-ai/)
- [Serverless Streaming Architectures on AWS Lambda in 2026 — Medium](https://medium.com/@aditya.ganti95/serverless-streaming-architectures-on-aws-lambda-in-2026-aab4facca7de)
- [Architecting for agentic AI development on AWS — AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/architecting-for-agentic-ai-development-on-aws/)
