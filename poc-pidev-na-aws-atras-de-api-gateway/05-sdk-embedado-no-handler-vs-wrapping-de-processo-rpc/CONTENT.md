# SDK Embedado no Handler vs Wrapping de Processo RPC

![capa](cover.png)

## Sobre este capítulo

Dado que o runtime está escolhido (Lambda ou Fargate), a segunda decisão de arquitetura é como o harness pi.dev entra no handler: como biblioteca importada pelo processo Node.js do handler (SDK embed), ou como processo filho independente que o handler controla via JSONL sobre stdin/stdout (process wrapping / RPC). As duas abordagens têm superfícies de API completamente diferentes, implicações distintas para o ciclo de vida do processo, e sensibilidades diferentes ao modelo de execução do runtime escolhido.

Este capítulo existe aqui porque é a ponte entre a escolha de runtime (capítulo 4) e o wiring com o API Gateway (capítulo 6). Sem saber qual das duas formas o handler usa para falar com o pi.dev, não dá para desenhar as rotas, definir o formato de request/response, ou saber que tipo de objeto `session` transitar entre invocações.

## Estrutura

O capítulo cobre: (1) **SDK embed** — como importar `@mariozechner/pi-coding-agent` no handler, inicializar `createAgentSession`, enviar um turno, receber eventos de resposta, e encerrar a sessão; como o SDK gerencia o processo internamente e por que isso é invisível para o handler; (2) **process wrapping via RPC** — como o handler faz spawn do processo `pi --mode rpc`, escreve comandos JSONL no stdin, lê eventos do stdout, e mantém a referência ao processo entre chamadas dentro da mesma invocação Fargate; (3) **comparação direta** — SDK em Lambda (o processo não sobrevive, cada invocação recria a sessão a partir do storage); RPC em Fargate (o processo sobrevive entre turnos do mesmo usuário, estado em memória é seguro); (4) **casos de borda** — o que acontece com o processo RPC durante um cold start tardio, o que fazer quando o processo filho crasha, como detectar e reagir a timeout do harness; (5) **decisão para a POC** — qual abordagem para qual runtime, com o código de inicialização de cada caminho anotado para o próximo capítulo.

## Objetivo

Ao terminar este capítulo, o leitor saberá implementar as duas formas de integração com pi.dev dentro de um handler AWS, entenderá quando cada uma vence dependendo do runtime e do modelo de sessão escolhido, e terá o esqueleto de código de integração pronto para conectar ao wiring do API Gateway no capítulo 6.

## Fontes utilizadas

- [Pi Coding Agent — README oficial, seção SDK e RPC](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [@mariozechner/pi-coding-agent — npm package](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)
- [pi.dev.details.md — community gist com detalhes do protocolo RPC JSONL](https://gist.github.com/rajeshpv/eccc1dc8d70e8cdcf948de3312ca111f)
- [How to Build a Custom Agent Framework with PI — Nader Dabit](https://gist.github.com/dabit3/e97dbfe71298b1df4d36542aceb5f158)
- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
