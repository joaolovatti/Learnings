# O Subset que Importa Para a POC Headless

![capa](cover.png)

## Sobre este subcapítulo

Com os quatro modos mapeados nos subcapítulos anteriores, este subcapítulo fecha o capítulo fazendo o corte explícito: o que sobra quando o ambiente é headless, a invocação é programática, e o contrato é sessão multi-turno persistente. TUI e Print/JSON são eliminados por raciocínio técnico direto — não por intuição. RPC e SDK entram como as duas apostas reais, e o leitor sai daqui com clareza sobre quais flags, quais classes e quais eventos de cada um efetivamente aparecem no handler da POC.

Este subcapítulo não faz a decisão entre RPC e SDK — essa análise de trade-offs é o tema central do capítulo 5. O que ele faz é preparar o terreno: com os dois candidatos identificados e o subset concreto de cada um definido, o leitor chega ao capítulo 4 (Lambda vs Fargate) e ao capítulo 5 (SDK vs RPC) com o contexto técnico necessário para avaliar trade-offs, não apenas seguir recomendações.

## Estrutura

O subcapítulo cobre: (1) **eliminação de TUI** — o argumento técnico completo: ausência de TTY em Lambda/Fargate, consequência direta (crash ou hang), por que não há workaround viável para POC de produção; (2) **eliminação de Print/JSON** — o argumento técnico: sessão única por invocação versus exigência de múltiplos turnos com contexto preservado, por que mesmo `--mode json` não resolve o problema de estado; (3) **o subset de RPC que entra na POC** — as flags de invocação (`--mode rpc`), o subconjunto de tipos de evento que o handler precisa consumir (`text_chunk`, `status`, `tool_call` com aprovação automática), e o que pode ser ignorado neste momento; (4) **o subset de SDK que entra na POC** — as classes mínimas (`createAgentSession`, `SessionManager`, `AuthStorage`, `ModelRegistry`), os parâmetros obrigatórios versus os que podem ser omitidos, e quais eventos o handler precisa consumir no loop mínimo; (5) **o gancho para os capítulos seguintes** — como esse corte alimenta a decisão Lambda vs Fargate (capítulo 4) e a comparação SDK vs RPC no handler (capítulo 5), com o que cada modo implica para o runtime de hosting.

## Objetivo

Ao terminar este subcapítulo — e com ele o capítulo inteiro — o leitor conseguirá articular por que a POC headless descarta TUI e Print com argumentos técnicos precisos, saberá identificar o conjunto mínimo de flags, classes e eventos de RPC e SDK que entram no handler, e estará pronto para avaliar os trade-offs de capítulos 4 e 5 com base em raciocínio próprio, não em receita.

## Conceitos

A explicação completa destes conceitos vive em [`CONCEPTS.md`](CONCEPTS.md), construída sequencialmente pela skill `estudo-explicar-conceito`.

1. Por que o TUI é descartado tecnicamente — ausência de TTY em Lambda/Fargate, o crash ou hang no harness como consequência direta, e por que não existe workaround viável para POC de produção
2. Por que o Print/JSON é descartado tecnicamente — sessão única por invocação vs exigência de múltiplos turnos com contexto preservado, e por que mesmo `--mode json` não resolve o problema de estado
3. O subset de RPC que entra no handler da POC — a flag `--mode rpc`, os tipos de evento que o handler precisa consumir (`text_delta`, `status`, `tool_call` com aprovação automática), e o que pode ser ignorado neste momento
4. O subset de SDK que entra no handler da POC — as classes mínimas (`createAgentSession`, `SessionManager`, `AuthStorage`, `ModelRegistry`), parâmetros obrigatórios vs opcionais, e os eventos do loop mínimo
5. O gancho para os capítulos 4 e 5 — como esse corte alimenta a decisão Lambda vs Fargate e a comparação SDK vs RPC no handler, com o que cada modo implica para o runtime de hosting

## Fontes utilizadas

- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [RPC Mode — docs/rpc.md (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/rpc.md)
- [SDK Mode — docs/sdk.md (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
- [Pi integration architecture — OpenClaw docs](https://docs.openclaw.ai/pi)
- [Pi Coding Agent — Sandbox Analysis Report (Agent Safehouse)](https://agent-safehouse.dev/docs/agent-investigations/pi)
