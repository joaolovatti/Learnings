# Substrato Persistente e Janela de Contexto

![capa](cover.png)

## Sobre este capítulo

A separação entre o que o agente *sabe* e o que o modelo *vê* é o insight arquitetural mais importante deste livro — e o mais contraintuitivo para quem vem de frameworks como LangGraph, onde essas duas coisas se misturam implicitamente. Este capítulo introduz o padrão substrato/projeção: o substrato é o repositório permanente de tudo que o agente acumulou ao longo da sessão; a janela de contexto é uma projeção efêmera, construída sob demanda a partir do substrato para cada chamada de inferência. Entender essa separação é o que permite gerenciar token budget sem destruir memória, escalar sessões sem explodir custos e implementar compactação sem perder coerência.

Este capítulo vem imediatamente após o diagnóstico do capítulo 1 porque oferece o modelo mental que guia todas as decisões de implementação seguintes. Antes de falar em MongoDB, DynamoDB ou compactação, o leitor precisa entender *por que* essas escolhas existem e qual problema cada uma resolve dentro desse modelo dual.

## Estrutura

Os grandes blocos são: (1) o padrão substrato/projeção em detalhe — definição formal, analogias concretas (banco de dados vs query result), e por que frameworks que misturam as duas camadas criam problemas em produção; (2) anatomia do substrato agêntico — quais elementos compõem o substrato de uma sessão (mensagens históricas, resultados de tool calls, metadados de runs, estado de objetivos, preferências do usuário) e como cada elemento tem lifecycle e política de retenção diferentes; (3) montagem dinâmica da janela de contexto — o processo de context assembly: selecionar do substrato, priorizar, comprimir, ordenar e injetar no prompt; políticas de seleção (recência, relevância, importância declarada); (4) implicações práticas para o projeto existente — como o MongoDB atual do leitor se encaixa como substrato parcial e o que está faltando para completar o modelo.

## Objetivo

Ao terminar este capítulo, o leitor será capaz de desenhar o substrato de uma sessão agêntica (quais campos, com que lifecycle), descrever o processo de montagem da janela de contexto como uma operação de projeção sobre o substrato, e identificar no seu projeto atual o que está sendo usado como substrato implícito — e o que precisa ser explicitado. Esses conceitos serão aplicados diretamente nos capítulos 4 (persistência) e 5 (compactação).

## Fontes utilizadas

- [Dynamic Context Assembly and Projection Patterns for LLM Agent Runtimes — Zylos Research](https://zylos.ai/research/2026-03-17-dynamic-context-assembly-projection-llm-agent-runtimes)
- [CaveAgent: Transforming LLMs into Stateful Runtime Operators](https://arxiv.org/html/2601.01569v1)
- [Context Engineering for AI Agents: Lessons from Building Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
- [Context Engineering for Personalization — OpenAI Cookbook](https://developers.openai.com/cookbook/examples/agents_sdk/context_personalization)
- [AI agent memory: types, architecture & implementation — Redis](https://redis.io/blog/ai-agent-memory-stateful-systems/)
