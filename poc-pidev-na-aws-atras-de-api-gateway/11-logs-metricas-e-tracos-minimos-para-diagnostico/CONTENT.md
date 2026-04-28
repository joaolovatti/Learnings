# Logs, Métricas e Traços Mínimos Para Diagnóstico

![capa](cover.png)

## Sobre este capítulo

Uma POC que dá ruim em produção e o desenvolvedor não consegue diagnosticar em menos de 5 minutos está tecnicamente quebrada — mesmo que o código esteja correto. Instrumentação mínima não é hardening de produção: é o mínimo que permite ao desenvolvedor entender o que aconteceu quando o cliente diz "não funcionou" sem poder reproduzir localmente. Este capítulo define e implementa esse mínimo para a POC do pi.dev.

O objetivo deliberado é leveza e praticidade: CloudWatch Logs com structured JSON, 2-3 métricas customizadas que capturam os failure modes mais prováveis do pi.dev na AWS (cold start lento, sessão não encontrada, turno sem resposta), e X-Ray tracing suficiente para correlacionar uma chamada do cliente com o que aconteceu dentro do Lambda. Nada de dashboards elaborados ou alertas — isso é território do livro de observabilidade.

## Estrutura

O capítulo cobre: (1) **structured logging com CloudWatch** — formato JSON para logs de Lambda, campos obrigatórios (`requestId`, `sessionId`, `userId`, `duration`, `error`), como usar `console.log` com JSON em Node.js e o que o Lambda Insights captura automaticamente; (2) **métricas customizadas via EMF** — Embedded Metrics Format para emitir métricas customizadas sem custo de PutMetricData separado, as 3 métricas que importam para a POC (`SessionNotFound`, `TurnTimeout`, `HarnessColdStart`); (3) **X-Ray tracing** — habilitar X-Ray na Lambda Function e no API Gateway, criar subsegmentos para as operações do pi.dev (sessão load, harness invoke, sessão save), como correlacionar o `traceId` com o log do cliente; (4) **alarmes mínimos** — 1 alarme de erro rate para ser notificado quando a POC está quebrando mais do que o esperado, configuração de SNS para email; (5) **runbook de diagnóstico** — sequência de passos para diagnosticar os 5 problemas mais comuns da POC (cliente recebe 500, streaming para no meio, sessão some após restart, cold start acima de 10s, auth rejeitando token válido).

## Objetivo

Ao terminar este capítulo, o leitor terá instrumentação suficiente para diagnosticar qualquer problema comum da POC em menos de 5 minutos via console da AWS, com logs estruturados correlacionados por `sessionId` e `requestId`, 3 métricas customizadas cobrindo os failure modes centrais, e um runbook de diagnóstico prático para usar quando o cliente reportar problema.

## Fontes utilizadas

- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
- [AWS Lambda Powertools for TypeScript — observability utilities](https://docs.powertools.aws.dev/lambda/typescript/latest/)
- [AWS re:Invent 2025 — Serverless and Agentic AI Takeaways — Ran the Builder](https://ranthebuilder.cloud/blog/aws-re-invent-2025-my-serverless-agentic-ai-takeaways/)
- [Streamlined multi-tenant application development with tenant isolation mode in AWS Lambda — AWS Blog](https://aws.amazon.com/blogs/aws/streamlined-multi-tenant-application-development-with-tenant-isolation-mode-in-aws-lambda/)
- [GitHub — serithemage/serverless-openclaw](https://github.com/serithemage/serverless-openclaw)
