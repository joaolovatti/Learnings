# O Problema da Sessão em Sistemas Agênticos

![capa](cover.png)

## Sobre este capítulo

Antes de qualquer implementação, é preciso entender o que exatamente falha quando um agente não tem sessão — e por que essa falha não é óbvia até que o sistema esteja em produção. Este capítulo de abertura estabelece o vocabulário e o modelo mental fundamentais que percorrerão todo o livro: o que distingue uma sessão de uma conversa, o que é um turn versus um run, e por que a ausência de estado persistido transforma um agente autônomo num chatbot glorificado. É o capítulo que justifica a existência dos demais.

A posição deste capítulo no início é intencional: ele não pressupõe familiaridade com os padrões de sessão que virão depois, mas pressupõe que o leitor já operou um sistema com tool calling e já se deparou — mesmo que sem nomear — com os sintomas que a ausência de sessão cria. O objetivo é fazer com que o leitor reconheça esses sintomas no seu próprio projeto e chegue ao final com um diagnóstico preciso do que precisa ser construído.

## Estrutura

Os grandes blocos são: (1) anatomia de uma falha stateless — exemplos concretos de como um agente sem sessão perde contexto entre tool calls, repete perguntas já respondidas, e toma decisões contraditórias em turnos consecutivos; (2) vocabulário fundamental — definições precisas de session (container de estado de longa duração), turn (um ciclo usuário→agente), run (uma execução completa do loop agêntico dentro de um turn), thread (sequência linear de turns numa mesma sessão) e como esses termos se mapeiam para o código existente do leitor; (3) o espectro stateless→stateful — posicionamento de diferentes arquiteturas nesse espectro, desde o Lambda stateless puro até agentes com memória episódica completa; (4) diagnóstico do projeto atual — como identificar os pontos de perda de estado no projeto existente (Lambda + MongoDB para histórico) e o que já funciona versus o que ainda falta.

## Objetivo

Ao terminar este capítulo, o leitor será capaz de nomear com precisão o que falta no seu sistema atual em termos de gestão de sessão, distinguir os conceitos de session/turn/run/thread sem ambiguidade, e usar esse vocabulário como base para as decisões de design que virão nos capítulos seguintes. O leitor chegará ao capítulo 2 com um diagnóstico claro — não apenas uma sensação vaga de que "algo está errado" — e com motivação técnica concreta para investir na camada de sessão.

## Subcapítulos

1. [O Agente sem Sessão não é um Agente](01-o-agente-sem-sessao-nao-e-um-agente/CONTENT.md) — por que o problema da sessão é central em sistemas agênticos e o que distingue um chatbot glorificado de um agente real
2. [Anatomia de uma Falha Stateless](02-anatomia-de-uma-falha-stateless/CONTENT.md) — exemplos concretos de perda de contexto entre tool calls, perguntas repetidas e decisões contraditórias em turnos consecutivos
3. [Vocabulário Fundamental: Session, Turn, Run e Thread](03-vocabulario-fundamental-session-turn-run-e-thread/CONTENT.md) — definições precisas dos quatro conceitos e mapeamento direto para o código Lambda/Haystack existente do leitor
4. [O Espectro Stateless→Stateful](04-o-espectro-stateless-stateful/CONTENT.md) — posicionamento de diferentes arquiteturas nesse espectro, do Lambda stateless puro até agentes com memória episódica completa
5. [Diagnóstico do Projeto Atual](05-diagnostico-do-projeto-atual/CONTENT.md) — como identificar os pontos de perda de estado no sistema Lambda + MongoDB existente e o que já funciona versus o que ainda falta

## Fontes utilizadas

- [Stateful Agents: The Missing Link in LLM Intelligence — Letta](https://www.letta.com/blog/stateful-agents)
- [Building an Agent Architecture: How Sessions, State, Events, Context, and Runner Work Together](https://medium.com/@aktooall/building-an-agent-architecture-how-sessions-state-events-context-and-runner-work-together-d8dbdb64d52b)
- [Stateful vs Stateless AI Agents: Architecture Patterns That Matter](https://www.ruh.ai/blogs/stateful-vs-stateless-ai-agents)
- [Agent State Management: Why AI Systems Need Persistent Context Across Sessions](https://hendricks.ai/insights/agent-state-management-persistent-context-ai-systems)
- [A Complete Guide to AI Agent Architecture in 2026 — Lindy](https://www.lindy.ai/blog/ai-agent-architecture)
