# O Espectro Stateless→Stateful

![capa](cover.png)

## Sobre este subcapítulo

A decisão entre stateless e stateful não é binária — é um espectro de trade-offs com posições bem definidas, cada uma com custos e capacidades diferentes. Este subcapítulo mapeia esse espectro de forma ordenada: do Lambda stateless puro que processa cada mensagem como se fosse a primeira, passando pelo padrão híbrido de stateless frontend com backend persistente, até agentes com memória episódica completa e contexto de longa duração. O leitor precisa saber onde cada arquitetura fica nesse espectro antes de poder decidir onde quer estar — e por quê.

Este subcapítulo também conecta o espectro à realidade da AWS: onde o Lambda puro vive, onde o padrão Lambda + DynamoDB/MongoDB fica posicionado, e o que seria necessário para subir mais no espectro na direção de um agente com sessão persistente real. Essa ancoragem na infraestrutura do leitor transforma o espectro de framework conceitual em ferramenta de decisão concreta.

## Estrutura

Os blocos são: (1) o polo stateless puro — Lambda sem armazenamento externo, cada invocação independente, escalabilidade máxima, zero continuidade; casos de uso legítimos onde isso é suficiente; (2) stateless com histórico externo — o padrão atual do leitor (Lambda + MongoDB para histórico de chat); por que isso não é o mesmo que ter sessão; onde o estado vai e onde ele se perde; (3) stateful com session explícita — um session object persistido e carregado a cada turn; a diferença entre "passar o histórico" e "ter um estado estruturado"; (4) agentes com memória episódica completa — arquiteturas como Letta/MemGPT que gerenciam múltiplos tipos de memória (episódica, semântica, procedural); quando esse nível de complexidade se justifica; (5) o ponto de decisão — como identificar em qual posição do espectro o projeto atual está e qual a próxima posição racional a atingir, sem pular níveis.

## Objetivo

Ao terminar este subcapítulo, o leitor será capaz de posicionar qualquer arquitetura agêntica nesse espectro com critérios objetivos, entender onde o seu sistema atual está posicionado e qual a próxima posição racional a alcançar. Isso prepara diretamente o subcapítulo de diagnóstico, onde o espectro vira uma ferramenta de avaliação aplicada ao código real.

## Conceitos

1. [O Polo Stateless Puro](01-o-polo-stateless-puro/CONTENT.md) — Lambda sem armazenamento externo: cada invocação é independente, o que isso garante e o que impossibilita, com os casos de uso legítimos onde essa posição é suficiente
2. [Por que "Passar Histórico" não é ter Sessão](02-por-que-passar-historico-nao-e-ter-sessao/CONTENT.md) — a diferença semântica entre injetar histórico de chat a cada chamada e manter um estado estruturado persistente; por que o padrão Lambda + MongoDB é stateless com histórico externo, não stateful
3. [Stateful com Session Explícita](03-stateful-com-session-explicita/CONTENT.md) — o que muda quando existe um session object persistido e carregado a cada turn: quais campos ele carrega e por que isso é qualitativamente diferente da posição anterior
4. [Agentes com Memória Episódica Completa](04-agentes-com-memoria-episodica-completa/CONTENT.md) — arquiteturas como Letta/MemGPT que gerenciam múltiplos tipos de memória (episódica, semântica, procedural); quando esse nível de complexidade é justificado e quando é overengineering
5. [O Critério de Posicionamento no Espectro](05-o-criterio-de-posicionamento-no-espectro/CONTENT.md) — como identificar objetivamente em qual posição do espectro um sistema está, e qual a próxima posição racional a atingir sem pular níveis

## Fontes utilizadas

- [Stateful vs Stateless AI Agents: Architecture Patterns That Matter — Ruh.ai](https://www.ruh.ai/blogs/stateful-vs-stateless-ai-agents)
- [Stateful Agents: The Missing Link in LLM Intelligence — Letta](https://www.letta.com/blog/stateful-agents)
- [AI agent memory: types, architecture and implementation — Redis Blog](https://redis.io/blog/ai-agent-memory-stateful-systems/)
- [From Stateless LLMs to Stateful Agents: Building Production-Grade Memory with MongoDB and Voyage AI](https://tldrecap.tech/posts/2026/mongodb-local-sf/agentic-application-building-strategies/)
- [Stateful vs. stateless agents: Why stateful architecture is essential for agentic AI — ZBrain](https://zbrain.ai/building-stateful-agents-with-zbrain/)
- [State Management for AI Agents: Stateless vs Persistent — By AI Team](https://byaiteam.com/blog/2025/12/14/state-management-for-ai-agents-stateless-vs-persistent/)
