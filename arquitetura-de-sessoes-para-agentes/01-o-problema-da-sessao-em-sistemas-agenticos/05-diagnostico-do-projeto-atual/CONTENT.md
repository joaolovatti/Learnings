# Diagnóstico do Projeto Atual

![capa](cover.png)

## Sobre este subcapítulo

Todo o capítulo converge para este ponto: aplicar o vocabulário e o espectro aprendidos nos subcapítulos anteriores ao sistema real do leitor. O projeto existente — API Gateway + Lambda + Gemini via Vertex AI + Haystack + MongoDB para histórico + tool calling com Slack, ClickUp e MCP — não é uma tela em branco. Ele tem partes que já funcionam corretamente, partes que implementam a sessão de forma incompleta, e partes que estão simplesmente ausentes. Este subcapítulo ensina a distinguir essas três categorias com precisão cirúrgica.

A posição deste subcapítulo no final do capítulo é deliberada: o diagnóstico só é possível porque o leitor chega aqui com o vocabulário (session/turn/run/thread), os sintomas reconhecíveis (perda de contexto, repetição, contradição) e o espectro (onde o projeto está vs. onde quer chegar). O resultado esperado é um diagnóstico escrito — não uma sensação — que o leitor pode levar para o capítulo 2 como ponto de partida concreto.

## Estrutura

Os blocos são: (1) o que já funciona — o MongoDB como armazenamento de histórico de chat já resolve parte do problema de persistência; o tool calling com Haystack já cria uma estrutura parcial de runs; a API Gateway já dá o contorno de session implícita; (2) o que está incompleto — o histórico de chat não é o mesmo que um session object estruturado; não há session_id explícito rastreado entre turns; o estado do agente (tool calls em andamento, decisões intermediárias) não é persistido; (3) o que está ausente — mecanismo de compactação de contexto; state machine de ciclo de vida da sessão; serialização estruturada de ChatMessage e ToolCall como eventos da sessão; suporte a sessões que excedem o timeout do Lambda; (4) como fazer o diagnóstico — um checklist operacional de perguntas que o leitor pode fazer sobre qualquer sistema agêntico para posicioná-lo no espectro e identificar as lacunas; (5) o próximo passo — o que o capítulo 2 (Substrato Persistente e Janela de Contexto) vai construir sobre esse diagnóstico, e por que o diagnóstico deste capítulo é o pré-requisito para o design do subcapítulo seguinte.

## Objetivo

Ao terminar este subcapítulo — e por extensão, este capítulo —, o leitor terá um diagnóstico preciso do seu sistema atual em termos de gestão de sessão: o que já existe, o que está incompleto e o que ainda precisa ser construído. Esse diagnóstico não é uma lista de tarefas, mas um mapa de decisões que vai guiar as escolhas de design nos próximos capítulos. O leitor chega ao capítulo 2 com motivação técnica concreta e coordenadas claras — não com uma sensação vaga de que "algo está errado".

## Conceitos

1. [O que o MongoDB como histórico de chat já resolve](01-o-que-o-mongodb-como-historico-de-chat-ja-resolve/CONTENT.md) — o que a camada de persistência atual entrega e onde ela para: persistência de mensagens entre invocações, mas sem session object estruturado
2. [O que o Haystack e o tool calling entregam parcialmente](02-o-que-o-haystack-e-o-tool-calling-entregam-parcialmente/CONTENT.md) — como o framework cria estrutura implícita de runs sem session_id explícito rastreado entre turns
3. [O que a API Gateway contribui implicitamente](03-o-que-a-api-gateway-contribui-implicitamente/CONTENT.md) — como o contorno HTTP da API Gateway cria fronteiras de sessão implícitas, e por que isso não é suficiente
4. [As lacunas estruturais do sistema atual](04-as-lacunas-estruturais-do-sistema-atual/CONTENT.md) — o que está completamente ausente: session_id explícito persistido, estado do agente entre runs, compactação de contexto, suporte a sessões além do timeout do Lambda
5. [O checklist operacional de diagnóstico](05-o-checklist-operacional-de-diagnostico/CONTENT.md) — o conjunto de perguntas que o leitor pode aplicar a qualquer sistema agêntico para posicioná-lo no espectro e identificar cada categoria de lacuna com precisão
6. [O diagnóstico como documento de decisão](06-o-diagnostico-como-documento-de-decisao/CONTENT.md) — como transformar o inventário (o que funciona / incompleto / ausente) num mapa de decisões que alimenta o design do capítulo 2, sem transformá-lo numa lista de tarefas

## Fontes utilizadas

- [Session Management in AWS Lambda: Guide — AWS for Engineers](https://awsforengineers.com/blog/session-management-in-aws-lambda-guide/)
- [From Stateless LLMs to Stateful Agents: Building Production-Grade Memory with MongoDB — TLDRcap](https://tldrecap.tech/posts/2026/mongodb-local-sf/agentic-application-building-strategies/)
- [Design principles in AWS Lambda: Implementing statelessness in functions — Orchestra](https://www.getorchestra.io/guides/design-principles-in-aws-lambda-implementing-statelessness-in-functions)
- [Building an Agent Architecture: How Sessions, State, Events, Context, and Runner Work Together — Medium](https://medium.com/@aktooall/building-an-agent-architecture-how-sessions-state-events-context-and-runner-work-together-d8dbdb64d52b)
- [Agent State Management: Why AI Systems Need Persistent Context — Hendricks AI](https://hendricks.ai/insights/agent-state-management-persistent-context-ai-systems)
- [Why Your "Stateless" Services Are Lying to You — DZone](https://dzone.com/articles/why-your-stateless-services-are-lying-to-you)
