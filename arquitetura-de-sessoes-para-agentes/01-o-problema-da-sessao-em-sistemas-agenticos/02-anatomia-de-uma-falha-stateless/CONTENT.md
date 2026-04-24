# Anatomia de uma Falha Stateless

![capa](cover.png)

## Sobre este subcapítulo

Teoria sem caso concreto não cria diagnóstico — cria sensação vaga. Este subcapítulo traduz o problema da ausência de sessão em exemplos específicos e rastreáveis: o agente que pede ao usuário uma informação já fornecida dois turnos atrás, o agente que emite dois tool calls contraditórios porque não lembra qual ação tomou primeiro, o agente que executa a metade de uma tarefa multi-step e, numa invocação subsequente do Lambda, começa do zero sem saber que já tinha progredido. Esses exemplos não são hipotéticos — são os sintomas exatos que emergem num sistema como o do leitor (API Gateway + Lambda + tool calling) quando a sessão está ausente ou incompleta.

A posição deste subcapítulo na sequência é intencional: o leitor já sabe que o problema é arquitetural (subcapítulo anterior), e agora precisa reconhecer os sintomas no próprio código. O objetivo não é desanimar, mas criar o reconhecimento de padrão que tornará o diagnóstico do capítulo inteiro possível.

## Estrutura

Os blocos são: (1) perda de contexto entre tool calls — o que acontece quando um tool retorna um resultado e a próxima invocação não tem acesso a esse resultado; exemplos com Slack e ClickUp; (2) repetição de perguntas — por que o agente repergunta informações já fornecidas pelo usuário em turnos anteriores, e como isso destrói a experiência em workflows reais de múltiplos passos; (3) decisões contraditórias em turnos consecutivos — exemplos de agente que em turn N decide criar uma tarefa e em turn N+1, sem memória do turn anterior, decide criar a mesma tarefa novamente; (4) a falha silenciosa do Lambda stateless — como a natureza stateless do Lambda amplifica esses três problemas, pois cada invocação começa com estado zerado mesmo quando o desenvolvedor acha que está passando "histórico" suficiente.

## Objetivo

Ao terminar este subcapítulo, o leitor conseguirá reconhecer cada um dos três padrões de falha (perda de contexto, repetição, contradição) no seu próprio sistema, e terá vocabulário para descrevê-los com precisão técnica em vez de "o agente está se comportando de forma estranha". Esse reconhecimento de padrão é o pré-requisito para o vocabulário formal do próximo subcapítulo.

## Conceitos

1. [Perda de contexto entre tool calls](01-perda-de-contexto-entre-tool-calls/CONTENT.md) — o que acontece quando o resultado de um tool call não persiste e a próxima invocação começa sem acesso a esse resultado
2. [O mecanismo da pergunta repetida](02-o-mecanismo-da-pergunta-repetida/CONTENT.md) — por que o agente repergunta informações já fornecidas pelo usuário em turnos anteriores e como isso destrói a experiência em workflows multi-step
3. [Decisões contraditórias em turnos consecutivos](03-decisoes-contraditorias-em-turnos-consecutivos/CONTENT.md) — como a ausência de memória entre turns faz o agente criar, em N+1, algo que já criou em N
4. [A falha silenciosa do Lambda stateless](04-a-falha-silenciosa-do-lambda-stateless/CONTENT.md) — como a natureza stateless do Lambda amplifica os três padrões anteriores, já que cada invocação começa com estado zerado mesmo quando o desenvolvedor acredita estar passando histórico suficiente
5. [Reconhecimento de padrão vs. diagnóstico vago](05-reconhecimento-de-padrao-vs-diagnostico-vago/CONTENT.md) — a distinção entre "o agente está se comportando de forma estranha" e ter vocabulário técnico preciso para nomear cada tipo de falha

## Fontes utilizadas

- [Why AI Agents Break: A Field Analysis of Production Failures — Arize](https://arize.com/blog/common-ai-agent-failures/)
- [Context Engineering: The Real Reason AI Agents Fail in Production — Inkeep](https://inkeep.com/blog/context-engineering-why-agents-fail)
- [7 AI Agent Failure Modes and How To Fix Them — Galileo](https://galileo.ai/blog/agent-failure-modes-guide)
- [Stateful vs Stateless AI Agents: Architecture Guide — Tacnode](https://tacnode.io/post/stateful-vs-stateless-ai-agents-practical-architecture-guide-for-developers)
- [Multi-Agent System Reliability: Failure Patterns — Maxim](https://www.getmaxim.ai/articles/multi-agent-system-reliability-failure-patterns-root-causes-and-production-validation-strategies/)
- [Why do multi agent LLM systems fail — Future AGI](https://futureagi.substack.com/p/why-do-multi-agent-llm-systems-fail)
