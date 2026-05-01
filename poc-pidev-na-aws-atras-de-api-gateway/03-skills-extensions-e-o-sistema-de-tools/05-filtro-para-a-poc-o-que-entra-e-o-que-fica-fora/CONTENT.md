# Filtro para a POC — O Que Entra e O Que Fica Fora

![capa](cover.png)

## Sobre este subcapítulo

Com o inventário das sete tools nativas (subcapítulo 01) e o entendimento de como extensions e custom tools funcionam (subcapítulos 02 e 03), chega o momento de aplicar o critério de corte: qual é o conjunto de tools que vai entrar na POC, e por que cada uma foi aprovada ou rejeitada?

O critério é único e não-negociável para esta entrega: a tool deve funcionar de forma headless em Lambda ou Fargate, sem shell interativo persistente, sem dependência de filesystem local entre invocações, e sem chamadas de rede não gerenciadas. Esse filtro não é conservador por comodidade — ele é o que garante que a POC seja reproduzível e não exploda silenciosamente durante uma demonstração ao cliente.

## Estrutura

O subcapítulo cobre: (1) **o critério de corte formal** — headless-compatível (sem TTY, sem dependência de `ctx.hasUI`), stateless entre invocações (sem escrita em filesystem local que precisa sobreviver ao container drain), e com dependências de rede declaradas (nenhuma chamada a endpoint externo implícita não-gerenciada); (2) **análise de cada tool nativa** — `read` e `write` (entram, com a condição de que o path aponta para EFS ou `/tmp` — coberto nos capítulos 8 e 9), `edit` (entra com a mesma condição de `read`/`write`), `bash` (entra com restrições: sem shell persistente entre turnos, comandos devem ser stateless, não há pty), `grep` e `find` (entram sem restrição adicional), `ls` (entra sem restrição adicional); (3) **tools e extensions que ficam de fora** — web fetch (dependência de rede implícita, sem controle IAM), image analysis (requer integração com modelo de visão separado, fora do escopo da POC), qualquer extension que depende de descoberta em disco (`~/.pi/extensions/`), tools que fazem chamadas interativas ao usuário (`ask_user`); (4) **o conjunto final aprovado** — a lista explícita de tools que entram na POC com a justificativa de cada uma, e a forma como esse conjunto será passado via `--tools` ou `customTools` na configuração do handler.

## Objetivo

Ao terminar este subcapítulo, o leitor terá um inventário definitivo do que o agente pode e não pode fazer dentro da POC, com a justificativa técnica de cada decisão. Esse inventário é o input direto para o mapa de IAM do subcapítulo 06 e para as decisões de runtime nos capítulos 4, 6 e 7.

## Conceitos

A explicação completa destes conceitos vive em [`CONCEPTS.md`](CONCEPTS.md), construída sequencialmente pela skill `estudo-explicar-conceito`.

1. O critério de corte formal — headless-compatível, stateless entre invocações, e dependências de rede declaradas
2. `bash` na POC — o que funciona sem TTY, ausência de shell persistente entre turnos, e o que fica fora por ser stateful
3. `read`, `write` e `edit` na POC — entram com a condição de path apontando para EFS ou /tmp, e o que acontece quando o container drain limpa /tmp
4. `grep`, `find` e `ls` na POC — entram sem restrição adicional e por quê seu comportamento headless é idêntico ao interativo
5. Tools que ficam de fora — web fetch (rede implícita), image analysis (modelo separado), tools interativas que dependem de ctx.hasUI
6. O conjunto final aprovado e como passá-lo — a lista explícita de tools aprovadas e como configurar via --tools na CLI e via customTools no SDK

## Fontes utilizadas

- [Pi Coding Agent README — flags --tools e --no-builtin-tools](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
- [Lambda, Fargate, AgentCore — Which serverless option to choose for your Agentic pattern? — Loïc Labeye](https://medium.com/@loic.labeye/lambda-fargate-agentcore-which-severless-option-to-choose-for-your-agentic-pattern-aaf68cb99700)
- [Pi integration architecture — OpenClaw docs](https://docs.openclaw.ai/pi)
- [pi-mono extensions.md — ctx.hasUI e comportamento sem TTY](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)
