# Vocabulário Fundamental: Session, Turn, Run e Thread

![capa](cover.png)

## Sobre este subcapítulo

Problemas de arquitetura mal nomeados são problemas que não conseguem ser resolvidos com consistência. Este subcapítulo fixa o vocabulário que o livro inteiro vai usar: os quatro termos — session, turn, run e thread — com definições precisas, distinções entre eles e, crucialmente, mapeamento direto para o código que o leitor já tem rodando. O objetivo não é criar jargão pelo jargão, mas garantir que, quando o leitor encontrar "session" nos capítulos 2 a 12, saiba exatamente a que estrutura de dados e responsabilidade isso se refere.

Este subcapítulo ocupa a terceira posição da sequência porque o leitor chega aqui com dois insumos: a convicção de que o problema é real (subcapítulo 1) e o reconhecimento dos sintomas concretos (subcapítulo 2). Agora é o momento de nomear com precisão o que causou esses sintomas — e esses nomes vão servir de coordenadas para todo o restante do livro.

## Estrutura

Os blocos são: (1) session — o container de estado de longa duração que persiste entre invocações; o que ele contém (histórico, metadados, estado do agente) e o que não contém (a janela de contexto do modelo, que é efêmera); (2) turn — um ciclo completo usuário→agente, da mensagem do usuário à resposta final entregue de volta; como um turn mapeia para uma invocação HTTP no sistema existente do leitor; (3) run — uma execução completa do loop agêntico dentro de um turn; por que um único turn pode conter múltiplos runs quando há tool calls encadeados; (4) thread — uma sequência linear de turns dentro de uma mesma session; o que diferencia thread de session e por que essa distinção importa quando o sistema suporta múltiplas threads por sessão (ex: sessões com ramificações ou contextos paralelos); (5) mapeamento para o código existente — como esses quatro conceitos se projetam sobre a API Gateway + Lambda + MongoDB + Haystack que o leitor já opera, identificando onde cada um existe parcialmente e onde está ausente.

## Objetivo

Ao terminar este subcapítulo, o leitor será capaz de usar session, turn, run e thread sem ambiguidade em discussões de design, code reviews e decisões de arquitetura. Mais importante: conseguirá apontar no próprio código onde cada um desses conceitos está implementado, onde está implícito mas não estruturado, e onde está simplesmente ausente — preparando o terreno para o subcapítulo de diagnóstico.

## Conceitos

1. [Por que nomear antes de implementar](01-por-que-nomear-antes-de-implementar/CONTENT.md) — a distinção entre ter um sintoma e ter um vocabulário técnico preciso; por que a imprecisão de linguagem perpetua bugs de arquitetura
2. [Session: o container de estado de longa duração](02-session-o-container-de-estado-de-longa-duracao/CONTENT.md) — o que a session contém (histórico, metadados, estado do agente), o que ela não contém (janela de contexto efêmera) e o que a torna diferente de "histórico de chat"
3. [Turn: o ciclo usuário→agente](03-turn-o-ciclo-usuario-agente/CONTENT.md) — a unidade de interação vista do lado externo; como um turn se delimita do ponto de vista de quem chama a API e como mapeia para uma invocação HTTP no sistema do leitor
4. [Run: a execução interna do loop agêntico](04-run-a-execucao-interna-do-loop-agentico/CONTENT.md) — o que acontece dentro de um turn quando há tool calls encadeados; por que um único turn pode conter múltiplos ciclos de raciocínio-ação-observação
5. [Thread: sequência linear de turns numa sessão](05-thread-sequencia-linear-de-turns-numa-sessao/CONTENT.md) — o que distingue thread de session; por que a distinção importa em sistemas que suportam ramificações ou contextos paralelos dentro de uma mesma sessão
6. [Session vs Thread: a distinção que mais confunde](06-session-vs-thread-a-distincao-que-mais-confunde/CONTENT.md) — os dois termos que frameworks distintos usam de forma intercambiável; como fixar a diferença com precisão e quando a confusão leva a bugs reais
7. [Mapeamento para o código existente](07-mapeamento-para-o-codigo-existente/CONTENT.md) — como session, turn, run e thread se projetam sobre a stack Lambda + MongoDB + Haystack do leitor: onde cada conceito existe, onde está implícito e onde está ausente

## Fontes utilizadas

- [Building an Agent Architecture: How Sessions, State, Events, Context, and Runner Work Together — Medium](https://medium.com/@aktooall/building-an-agent-architecture-how-sessions-state-events-context-and-runner-work-together-d8dbdb64d52b)
- [What Is the AI Agent Loop? — Oracle Developers Blog](https://blogs.oracle.com/developers/what-is-the-ai-agent-loop-the-core-architecture-behind-autonomous-ai-systems)
- [Multi-turn Conversations with Agents: Building Context Across Dialogues — Medium](https://medium.com/@sainitesh/multi-turn-conversations-with-agents-building-context-across-dialogues-f0d9f14b8f64)
- [A Practical Guide to Memory for Autonomous LLM Agents — Towards Data Science](https://towardsdatascience.com/a-practical-guide-to-memory-for-autonomous-llm-agents/)
- [Microsoft Agent Framework Overview — Microsoft Learn](https://learn.microsoft.com/en-us/agent-framework/overview/)
