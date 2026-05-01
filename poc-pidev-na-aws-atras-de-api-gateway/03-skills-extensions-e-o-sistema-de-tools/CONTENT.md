# Skills, Extensions e o Sistema de Tools

![capa](cover.png)

## Sobre este capítulo

Pi.dev vem com um sistema de skills embutidas (operações sobre arquivos, execução de shell, navegação web) e aceita extensions que plugam tools externas via protocolo definido. Para a POC, isso levanta uma questão concreta imediata: o que já está disponível out-of-the-box, o que precisa ser configurado explicitamente, e o que fica completamente fora do escopo desta entrega? Um agente que tenta rodar com skills que dependem de filesystem local vai falhar silenciosamente em Lambda; uma extension que faz chamadas de rede sem permissões IAM vai travar o turno.

Este capítulo vive aqui — após os dois fundamentos de modelo — porque as decisões de IAM, networking e container do capítulo 4 em diante dependem de saber quais tools o agente vai precisar invocar. O inventário de skills e extensions não é curiosidade técnica; é o input que determina quais permissões o Lambda role precisa e quais recursos externos a POC deve ou não expor.

## Estrutura

O capítulo cobre: (1) **skills embutidas** — lista das skills nativas do pi.dev (file read/write, shell exec, web fetch, image analysis), como cada uma é invocada pelo LLM, e quais delas funcionam sem modificação em ambiente Lambda/container; (2) **sistema de extensions** — o protocolo de extensão, como uma extension é registrada, o ciclo de vida de uma tool call de extension (LLM decide, pi.dev chama a extension, aguarda resultado); (3) **MCP e integrações externas** — como o pi.dev se relaciona com Model Context Protocol, o que isso significa para tools de terceiros; (4) **filtro para a POC** — skill por skill e extension por extension, quais entram, quais ficam de fora, e o critério usado (precisa funcionar headless em Lambda/Fargate sem estado em disco local e sem dependências de rede não gerenciadas); (5) **implicações de IAM** — quais permissões o execution role precisa para cada skill que vai entrar na POC.

## Objetivo

Ao terminar este capítulo, o leitor terá um inventário claro do que o agente vai poder fazer dentro da POC — nem mais nem menos — e saberá mapear cada tool para suas dependências de runtime (filesystem, rede, IAM). Esse inventário é o input direto para as decisões de IAM e networking que aparecem nos capítulos 4, 6 e 7.

## Subcapítulos

1. [As Sete Tools Nativas](01-as-sete-tools-nativas/CONTENT.md) — read, write, edit, bash, grep, find, ls: o que cada uma faz, como o LLM as invoca, e as flags que controlam o conjunto ativo
2. [O Sistema de Extensions — Protocolo e Ciclo de Vida](02-o-sistema-de-extensions-protocolo-e-ciclo-de-vida/CONTENT.md) — carregamento de módulos TypeScript, a sequência tool_execution_start → tool_call → execute → tool_result → tool_execution_end, e o contrato de ExtensionAPI
3. [Custom Tools via SDK — registerTool e customTools](03-custom-tools-via-sdk-registertool-e-customtools/CONTENT.md) — diferença entre extensions em disco e customTools passados programaticamente ao criar uma sessão SDK, e implicações para agente embedded em Lambda
4. [MCP: Por Que Pi.dev Não Adota e o Que Fazer Quando Você Precisa](04-mcp-por-que-pidev-nao-adota-e-o-que-fazer/CONTENT.md) — a decisão de design (overhead de contexto), o pi-mcp-adapter como válvula de escape, e implicações práticas para a POC
5. [Filtro para a POC — O Que Entra e O Que Fica Fora](05-filtro-para-a-poc-o-que-entra-e-o-que-fica-fora/CONTENT.md) — skill por skill: bash sem shell persistente, read/write sobre EFS ou /tmp, find/grep aceitáveis, web tools problemáticas; critério de corte headless-Lambda
6. [Mapa de IAM — Permissões por Tool que Entra na POC](06-mapa-de-iam-permissoes-por-tool-que-entra-na-poc/CONTENT.md) — o que cada tool aprovada exige do execution role e como esse mapa alimenta os capítulos 4, 6 e 7

## Fontes utilizadas

- [Pi Coding Agent — README oficial, seção de skills e extensions](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [Pi Documentation — pi.dev/docs/latest](https://pi.dev/docs/latest)
- [How to Build a Custom Agent Framework with PI — Nader Dabit](https://gist.github.com/dabit3/e97dbfe71298b1df4d36542aceb5f158)
- [From Local MCP Server to AWS Deployment in Two Commands — DEV Community](https://dev.to/aws/from-local-mcp-server-to-aws-deployment-in-two-commands-ag4)
- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
