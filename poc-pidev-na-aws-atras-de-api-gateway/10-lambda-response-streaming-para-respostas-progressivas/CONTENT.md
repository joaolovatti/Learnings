# Lambda Response Streaming Para Respostas Progressivas

![capa](cover.png)

## Sobre este capítulo

Um agente que demora 8 segundos para responder e devolve tudo de uma vez é percebido pelo cliente como travado. O mesmo agente que começa a enviar tokens em 800ms e vai completando progressivamente na tela é percebido como responsivo. A diferença é puramente de apresentação — o trabalho do LLM é o mesmo — e Lambda Response Streaming é o mecanismo que torna esse comportamento possível sem precisar de WebSocket ou de uma arquitetura push.

Este capítulo converte o handler síncrono do capítulo 6 (rota `POST /sessions/{sessionId}/turns`) em um handler de streaming que devolve os chunks de texto do agente conforme o pi.dev os emite. A entrega progressiva é o diferencial de UX mais visível da POC — e o cliente vai notar.

## Estrutura

O capítulo cobre: (1) **Lambda Response Streaming — o modelo** — como funciona response streaming no Lambda (`awslambda.streamifyResponse`, o `responseStream`, o 8-null-byte delimiter, content-type `application/vnd.awslambda.http-integration-response`); (2) **habilitando streaming no API Gateway** — a diferença entre REST API e HTTP API para streaming, configuração de `response transfer mode: STREAM`, por que Function URLs são mais simples para streaming e quando API Gateway é necessário; (3) **integrando com os eventos do pi.dev** — como o SDK emite eventos de texto chunk, como o handler escreve cada chunk no `responseStream` à medida que chega, flush e backpressure; (4) **Server-Sent Events como formato de transporte** — como formatar os chunks como SSE (`data: <chunk>\n\n`), como o cliente JavaScript usa `EventSource` para receber, vantagens sobre raw streaming para reconexão automática; (5) **limites e timeouts** — o limite de 15 minutos do Lambda, o limite de 1MB por chunk, como detectar e encerrar gracefully quando o agente demora mais do que o esperado.

## Objetivo

Ao terminar este capítulo, o leitor terá a rota de turno do API Gateway retornando respostas progressivas via Lambda Response Streaming formatado como SSE, e saberá implementar o client-side em JavaScript para exibir os chunks conforme chegam. Isso completa a experiência de usuário da POC — o cliente vê o agente "pensando" em tempo real.

## Fontes utilizadas

- [Introducing AWS Lambda response streaming — AWS Compute Blog](https://aws.amazon.com/blogs/compute/introducing-aws-lambda-response-streaming/)
- [Response streaming for Lambda functions — AWS Lambda docs](https://docs.aws.amazon.com/lambda/latest/dg/configuration-response-streaming.html)
- [Building responsive APIs with Amazon API Gateway response streaming — AWS Compute Blog](https://aws.amazon.com/blogs/compute/building-responsive-apis-with-amazon-api-gateway-response-streaming/)
- [Server-Sent Events with AWS Lambda response streaming — Johannes Geiger, Medium](https://medium.com/@johannesfloriangeiger/server-sent-events-with-aws-lambda-response-streaming-c460b0944c89)
- [Stream the integration response for your proxy integrations in API Gateway — AWS docs](https://docs.aws.amazon.com/apigateway/latest/developerguide/response-transfer-mode.html)
- [Real-Time Data Streaming with AWS Lambda and Server-Sent Events — Business Compass LLC](https://businesscompassllc.com/real-time-data-streaming-with-aws-lambda-and-server-sent-events-across-multiple-languages/)
