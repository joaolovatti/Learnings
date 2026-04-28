# API Gateway na Frente — Rotas Para Criar Sessão, Enviar Turno e Listar Sessões

![capa](cover.png)

## Sobre este capítulo

O API Gateway é o que transforma a POC num endpoint público que o cliente consegue chamar. Este capítulo desenha as três rotas mínimas que fazem a POC funcionar ponta-a-ponta: criar uma sessão nova (o equivalente a "começar uma conversa"), enviar um turno dentro de uma sessão existente (o equivalente a "falar com o agente"), e listar as sessões de um usuário (para que o cliente retome onde parou). Cada rota tem seu próprio contrato de request/response, seu próprio handler Lambda, e suas próprias implicações de latência e streaming.

Este capítulo é o ponto de convergência de tudo que veio antes: o modo de execução do harness (capítulos 1 e 5), o modelo de sessão (capítulo 2), e o runtime escolhido (capítulo 4). O API Gateway é onde o cliente toca o sistema — e o desenho das rotas determina o que o cliente vai conseguir ou não conseguir fazer.

## Estrutura

O capítulo cobre: (1) **rota `POST /sessions`** — criação de sessão, geração de `sessionId`, inicialização do storage (stub para o capítulo 8/9), resposta com o `sessionId` e o primeiro turno opcional; (2) **rota `POST /sessions/{sessionId}/turns`** — envio de um turno, localização da sessão no storage, invocação do pi.dev, retorno da resposta (síncrono agora, streaming no capítulo 10); (3) **rota `GET /sessions`** — listagem das sessões do usuário autenticado, paginação simples, resposta com metadados de cada sessão; (4) **integração HTTP Proxy vs Lambda Proxy** — por que Lambda Proxy é a escolha para a POC, como configurar no console e em IaC (CDK ou SAM), o que o API Gateway injeta no `event` e o que o handler precisa devolver; (5) **mapeamento de erros** — como transformar erros do pi.dev (sessão não encontrada, turno inválido, timeout do harness) em respostas HTTP com status codes corretos e corpo de erro estruturado.

## Objetivo

Ao terminar este capítulo, o leitor terá as três rotas da POC definidas e implementadas em handlers Lambda conectados ao API Gateway, com contratos de request/response documentados e tratamento de erro básico. O capítulo seguinte (autenticação) assume que essas rotas já existem e adiciona o authorizer na frente delas.

## Fontes utilizadas

- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
- [Building responsive APIs with Amazon API Gateway response streaming — AWS Compute Blog](https://aws.amazon.com/blogs/compute/building-responsive-apis-with-amazon-api-gateway-response-streaming/)
- [Stream the integration response for your proxy integrations in API Gateway — AWS docs](https://docs.aws.amazon.com/apigateway/latest/developerguide/response-transfer-mode.html)
- [How to Build a Custom Agent Framework with PI — Nader Dabit](https://gist.github.com/dabit3/e97dbfe71298b1df4d36542aceb5f158)
- [GitHub — serithemage/serverless-openclaw (padrão de rotas para agente serverless)](https://github.com/serithemage/serverless-openclaw)
