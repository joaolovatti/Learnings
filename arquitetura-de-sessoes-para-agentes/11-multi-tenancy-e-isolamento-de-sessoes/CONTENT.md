# Multi-Tenancy e Isolamento de Sessões

![capa](cover.png)

## Sobre este capítulo

Um sistema agêntico que funciona para um usuário numa demo raramente funciona corretamente para cem usuários simultâneos em produção — não porque o modelo seja pior, mas porque o isolamento entre sessões de usuários diferentes é mais difícil do que parece. Vazamento de contexto entre sessões, TTL mal configurado que expira sessões ativas, falta de controle de quem pode retomar qual sessão: esses são os bugs de produção que este capítulo ensina a prevenir. O capítulo também cobre o modelo de sessão do Pi.dev como referência de UX — não para copiar a interface, mas para entender as decisões de produto que informam a arquitetura técnica de sessões com branch e retomada.

Este capítulo introduz a dimensão de produto da sessão — até aqui, o livro tratou sessão como um problema de engenharia; a partir daqui, ela também é uma feature com semântica para o usuário final.

## Estrutura

Os grandes blocos são: (1) isolamento por usuário e organização — namespacing de session_id, autorização de acesso (o usuário A não pode acessar a sessão do usuário B), e como implementar isso no MongoDB com índices e validação no layer de serviço; (2) TTL e expiração — política de expiração de sessões inativas (TTL index no MongoDB), distinção entre SUSPENDED (pausada intencionalmente) e EXPIRED (abandonada), e o que fazer com o estado de uma sessão expirada (arquivar vs. deletar); (3) branch de sessão — criar um fork de uma sessão existente a partir de um ponto no histórico, preservando o substrato original e iniciando um novo thread de exploração; casos de uso (testar abordagens alternativas, colaboração); implementação com copy-on-write do substrato; (4) retomada de sessão — o protocolo de reconexão: autenticar, carregar substrato, reconstruir contexto, verificar estado na state machine e retomar ou criar novo turno; (5) o modelo Pi.dev como referência — análise das decisões de UX do Pi.dev (árvore de sessões navegável, exportação de sessão, compartilhamento) e como cada decisão de UX mapeia para uma decisão técnica na camada de sessão.

## Objetivo

Ao terminar este capítulo, o leitor será capaz de implementar isolamento correto de sessões num ambiente multi-tenant, configurar TTL e políticas de expiração, implementar branch básico de sessão, e traduzir as decisões de UX de um produto como o Pi.dev em requisitos técnicos concretos para a sua plataforma.

## Fontes utilizadas

- [Stateful Agents — Agent Communication Protocol](https://agentcommunicationprotocol.dev/core-concepts/stateful-agents)
- [AI Agent Architecture Patterns: Single & Multi-Agent Systems — Redis](https://redis.io/blog/ai-agent-architecture-patterns/)
- [7 State Persistence Strategies for Long-Running AI Agents in 2026 — Indium Tech](https://www.indium.tech/blog/7-state-persistence-strategies-ai-agents-2026/)
- [Architecting the Agent Gateway: Unifying the Agentic Stack — TrueFoundry](https://www.truefoundry.com/blog/agent-gateway-series-part-1-of-7-truefoundry-agent-gateway)
- [Building Multi-Turn Conversations with AI Agents: The 2026 Playbook](https://medium.com/ai-simplified-in-plain-english/building-multi-turn-conversations-with-ai-agents-the-2026-playbook-45592425d1db)
