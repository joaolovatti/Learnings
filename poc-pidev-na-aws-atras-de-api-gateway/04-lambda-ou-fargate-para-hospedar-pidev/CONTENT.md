# Lambda ou Fargate Para Hospedar Pi.dev

![capa](cover.png)

## Sobre este capítulo

Hospedar o pi.dev na AWS significa escolher onde o processo do harness roda entre turnos de uma conversa — e essa escolha tem implicações profundas em custo, latência, complexidade de deployment e viabilidade da persistência de sessão. Lambda oferece escala automática e custo zero quando idle, mas o modelo de execução efêmero e o limite de 15 minutos tensionam o harness de um jeito específico. Fargate oferece processo de longa duração, estado em memória entre turnos e sem limite de runtime, mas tem custo idle e complexidade de orquestração de containers.

Esta calibragem não é genérica — é específica para o harness pi.dev. O capítulo usa os trade-offs concretos levantados nos capítulos anteriores (modo RPC precisa de processo vivo, árvore JSONL precisa de storage persistente, tools precisam de filesystem ou rede) para tornar a decisão Lambda vs Fargate defensável num nível técnico, não por intuição.

## Estrutura

O capítulo cobre: (1) **modelo de execução Lambda** — cold start, warm start, limite de tempo de execução de 15 min, memória efêmera em `/tmp`, response streaming com Function URLs, custo pay-per-invocation; (2) **modelo de execução Fargate** — container de longa duração, processo vivo entre turnos, EFS mount nativo, custo de idle, deploy via ECS Task Definition; (3) **friction points específicos do pi.dev em Lambda** — processo RPC não sobrevive entre invocações (obriga SDK embed), `/tmp` de 512MB-10GB para sessões mas não compartilhado, cold start de container com harness completo; (4) **friction points específicos do pi.dev em Fargate** — gerenciamento do ciclo de vida do processo, escalabilidade horizontal de sessões concorrentes, custo quando POC está parada; (5) **decisão para a POC** — a escolha recomendada com o raciocínio completo, incluindo o cenário em que Lambda + EFS vence e o cenário em que Fargate vence, e como a POC pode começar num e migrar para o outro sem reescrever o wiring do API Gateway.

## Objetivo

Ao terminar este capítulo, o leitor saberá articular os trade-offs entre Lambda e Fargate especificamente para o harness pi.dev, terá feito a escolha para a sua POC com raciocínio técnico documentado, e estará pronto para configurar o runtime escolhido nos capítulos seguintes. O encaixe com o capítulo 5 (SDK vs RPC) é direto: a escolha de runtime aqui pré-determina parcialmente a forma de embarcar o harness.

## Fontes utilizadas

- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
- [Lambda, Fargate, AgentCore — Which serverless option to choose for your Agentic pattern? — Loïc Labeye](https://medium.com/@loic.labeye/lambda-fargate-agentcore-which-severless-option-to-choose-for-your-agentic-pattern-aaf68cb99700)
- [Fargate vs Lambda: How To Choose The Right Serverless Compute — CloudZero](https://www.cloudzero.com/blog/fargate-vs-lambda/)
- [Designing a modern serverless application with AWS Lambda and AWS Fargate — Nathan Peck](https://medium.com/containers-on-aws/designing-a-modern-serverless-application-with-aws-lambda-and-aws-fargate-83f4c5fac573)
- [Response streaming for Lambda functions — AWS Lambda docs](https://docs.aws.amazon.com/lambda/latest/dg/configuration-response-streaming.html)
- [Developers guide to using Amazon EFS with Amazon ECS and AWS Fargate — AWS Containers Blog](https://aws.amazon.com/blogs/containers/developers-guide-to-using-amazon-efs-with-amazon-ecs-and-aws-fargate-part-1/)
