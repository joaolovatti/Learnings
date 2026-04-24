# Gerenciamento de Contexto e Compactação

![capa](cover.png)

## Sobre este capítulo

Uma sessão que dura mais de algumas trocas começa a acumular mais conteúdo do que a janela de contexto do modelo consegue absorver — e se o sistema simplesmente truncar as mensagens mais antigas, o agente perde informação crítica de forma silenciosa. A solução não é aumentar o contexto indefinidamente (custo e latência explodem), mas implementar uma política de compactação inteligente: sumarizar, descartar com critério, e manter apenas o que é necessário para que o próximo turno seja coerente com a história da sessão. Este capítulo cobre as principais estratégias de compactação, quando aplicá-las e como implementá-las sem quebrar o fluxo do agente.

Este capítulo vem após a definição do schema de persistência (cap. 4) porque a compactação opera diretamente sobre o substrato persistido — ela lê o que está armazenado, transforma, e grava de volta. Só faz sentido abordar compactação depois que o leitor sabe onde o estado vive.

## Estrutura

Os grandes blocos são: (1) o problema do token budget — como calcular o token count de uma sessão em andamento, quando o budget está em risco e a distinção entre truncagem burra e compactação inteligente; (2) estratégias de compactação — sliding window (manter os últimos N turns intactos), summarization (sumarizar blocos mais antigos com uma chamada LLM separada), relevance scoring (manter apenas mensagens acima de um threshold de relevância para o objetivo atual) e progressive summarization (sumários em cascata para sessões muito longas); (3) quando compactar — triggers baseados em token count, em número de turns ou em transição de estado da sessão (o estado COMPACTING da state machine do cap. 3); (4) implementação com Haystack — como integrar uma compactação assíncrona no fluxo do `ChainOfThoughts` existente sem bloquear a resposta ao usuário; (5) preservação de coerência — garantir que o sumário retém tool calls, decisões e objetivos relevantes, e como testar que o agente pós-compactação ainda se comporta consistentemente.

## Objetivo

Ao terminar este capítulo, o leitor será capaz de implementar pelo menos duas estratégias de compactação no seu projeto, configurar triggers automáticos baseados em token budget, e integrar o estado COMPACTING na state machine da sessão sem impactar a latência de resposta ao usuário. O leitor chegará ao capítulo 6 com uma sessão que pode durar indefinidamente sem explodir o token budget.

## Fontes utilizadas

- [Context Engineering for AI Agents: Lessons from Building Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
- [Dynamic Context Assembly and Projection Patterns for LLM Agent Runtimes — Zylos Research](https://zylos.ai/research/2026-03-17-dynamic-context-assembly-projection-llm-agent-runtimes)
- [Context Management Strategies for OpenCode — Alex Merced](https://tuts.alexmercedcoder.dev/2026/2026-03-ctx-10-context-management-strategies-for-opencode-a-complete-guide/)
- [A-MEM: Agentic Memory for LLM Agents — arXiv](https://arxiv.org/abs/2502.12110)
- [Agent Memory: Building Memory-Aware Agents — DeepLearning.AI](https://www.deeplearning.ai/short-courses/agent-memory-building-memory-aware-agents/)
