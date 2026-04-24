# WebSocket API Gateway e Steering em Tempo Real

![capa](cover.png)

## Sobre este capítulo

A diferença entre um agente que responde e um agente com o qual o usuário colabora está no canal de comunicação. HTTP request-response força o usuário a esperar o agente terminar; WebSocket permite que o agente transmita seu raciocínio token a token e, mais importante, que o usuário interrompa, redirecione ou aprove ações *enquanto o agente ainda está executando*. Esse padrão — que o Pi.dev chama de steering — é a diferença de experiência entre um processo opaco e um agente transparente e controlável. Este capítulo implementa essa arquitetura na AWS usando API Gateway WebSocket, Lambda (ou Fargate), e define o protocolo de mensagens do canal de controle.

Este capítulo vem após a infraestrutura de longa duração (cap. 8) porque o WebSocket persistente é mais natural com um container de longa duração — mas também cobre a variante Lambda com reconexão, para o leitor que não quer migrar para Fargate ainda.

## Estrutura

Os grandes blocos são: (1) arquitetura WebSocket na AWS — API Gateway WebSocket com rotas ($connect, $disconnect, $default e rotas customizadas), Lambda de gestão de conexão, e como mapear connection_id para session_id no MongoDB; (2) streaming de tokens — como transmitir a resposta do Gemini token a token para o cliente via `postToConnection`, o padrão de chunking e o tratamento de reconexão sem perda de tokens; (3) o canal de controle e o padrão de steering — mensagens do usuário que chegam enquanto o agente está em execução: como o agente detecta a mensagem de steering, interrompe o loop atual de forma limpa, incorpora a nova instrução e retoma; casos concretos (cancelar, redirecionar, aprovar um tool call antes de executar); (4) aprovação de tool calls — o padrão human-in-the-loop onde o agente pausa antes de executar uma ação crítica, notifica o usuário via WebSocket e aguarda aprovação/rejeição; implementação com o estado AWAITING_APPROVAL na state machine; (5) tratamento de desconexão — o que acontece com a sessão quando o WebSocket cai; buffer de mensagens não entregues, reconexão e replay.

## Objetivo

Ao terminar este capítulo, o leitor será capaz de implementar a arquitetura WebSocket completa na AWS (API Gateway + Lambda/Fargate), transmitir tokens do Gemini em tempo real para o cliente, e implementar o padrão de steering básico (interrupção + redirecionamento). O capítulo 10 integrará este canal com o loop agêntico completo.

## Fontes utilizadas

- [How to stream LLM responses using AWS API Gateway Websocket and Lambda — amlanscloud](https://amlanscloud.com/llmstreampost/)
- [Serverless strategies for streaming LLM responses — AWS Compute Blog](https://aws.amazon.com/blogs/compute/serverless-strategies-for-streaming-llm-responses/)
- [Streaming LLM Responses from AWS Lambda — AWS in Plain English](https://aws.plainenglish.io/streaming-llm-responses-from-aws-lambda-46ed5cb25bee)
- [Stateful Continuation for AI Agents: Why Transport Layers Now Matter — InfoQ](https://www.infoq.com/articles/ai-agent-transport-layer/)
- [Building Multi-Turn Conversations with AI Agents: The 2026 Playbook](https://medium.com/ai-simplified-in-plain-english/building-multi-turn-conversations-with-ai-agents-the-2026-playbook-45592425d1db)
