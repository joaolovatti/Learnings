# POC End-to-End — Pi.dev Atrás de API Gateway na AWS Para Validação Com Cliente

![capa](cover.png)

## Sobre este livro

Há duas maneiras de aprender uma tecnologia nova quando o relógio está correndo: ler tudo até dominar, ou cruzar a fronteira específica que separa "nunca abri" de "está rodando em produção pra cliente testar". Este livro é uma travessia do segundo tipo. O ponto de partida é um engenheiro sênior que conhece AWS de cor, já integrou LLMs em produção, e nunca abriu o `pi-coding-agent` na vida; o ponto de chegada é uma POC pública no API Gateway que o cliente consegue chamar via HTTP, criar uma sessão, conversar em múltiplos turnos com um agente, e ter o estado preservado entre chamadas.

A proposta deliberadamente **não é** construir uma arquitetura de sessão do zero (esse recorte já existe num livro irmão deste repositório, focado em substrato persistente, projeção de contexto e state machines genéricas). Aqui pi.dev é tratado como **runtime pronto** — o livro foca em decidir como hospedá-lo na AWS, como expor suas sessões via API Gateway, como mapear seu modelo de árvore JSONL para storage que sobreviva entre invocações, e como entregar tudo isso embalado de forma que um cliente leigo no stack consiga testar e dizer "sim, é isso" ou "não, falta isso aqui".

## Estrutura

Os grandes blocos são: (1) **fundamentos de pi.dev sob a ótica de quem vai produzir** — os quatro modos de execução (TUI, print/JSON, RPC, SDK), o modelo de sessão como árvore JSONL com `id`/`parentId`, o sistema de skills e extensions, e o subset que efetivamente importa para uma POC headless; (2) **escolha do runtime AWS** — calibragem direta entre Lambda (com response streaming e Function URLs) e Fargate (com EFS), focada nos trade-offs específicos do harness pi.dev e não em agentes genéricos; (3) **wiring do API Gateway ao pi.dev** — embedding via SDK em handler Lambda ou wrapping de processo `pi --mode rpc` em container, autenticação mínima com Cognito ou JWT, mapeamento de rotas (criar sessão, enviar turno, listar sessões); (4) **persistência de sessões fora do disco local** — redirecionamento do diretório de sessões pi.dev para EFS multi-tenant por access point ou implementação de um `SessionManager` customizado backed por S3, preservando fork e branch; (5) **UX de demonstração e entrega** — streaming básico de respostas via Lambda response streaming, endpoint de continuação de sessão, instrumentação mínima de logs e métricas suficientes para diagnosticar quando der ruim, e empacotamento da POC (URL pública, credencial de teste, instruções) de forma que o cliente consiga rodar sozinho.

## Objetivo

Ao terminar, o leitor terá uma POC funcional rodando na AWS, com endpoint público autenticado no API Gateway, pi.dev hospedado e gerenciando sessões persistentes, e o cliente conseguindo testar o conceito ponta-a-ponta sem suporte do desenvolvedor. Mais do que isso, o leitor terá entendido **por que** cada decisão técnica foi tomada — Lambda ou Fargate, EFS ou S3, SDK ou RPC, WebSocket ou response streaming — e estará apto a defender cada escolha numa conversa com cliente ou time. O livro não cobre hardening de produção (multi-tenant rigoroso, observabilidade rica, runaway protection, custo finamente otimizado) — esses recortes têm livros próprios na sequência do método; aqui o objetivo é a primeira travessia: do zero ao "está demonstrável".

## Sobre o leitor

O leitor é um engenheiro de software sênior com nível avançado em AWS — domina API Gateway, Lambda, IAM, e já trabalhou com tokens de autenticação em endpoints públicos — e avançado em integração de LLMs em backend, tendo já posto a OpenAI em produção. Conhece infraestrutura serverless, sabe modelar quando faz sentido cada serviço, e tem o reflexo de ler documentação oficial antes de tutorial.

A lacuna específica que justifica este livro é dupla: ele nunca trabalhou com **pi.dev** (não conhece o harness, os modos de execução, o modelo de sessão em árvore, o sistema de extensions), e nunca implementou **gerenciamento de sessão / state management de agentes** — sua experiência prévia foi de chamadas request/response sem memória persistida entre turnos, ou via APIs como a da OpenAI que abstraem essa camada. Os dois conhecimentos vão entrar juntos neste livro, ancorados pelo que ele já domina (AWS) e pelo objetivo claro que ele trouxe (POC entregável pra cliente).

O objetivo declarado é uma POC funcional pronta para validação por cliente externo — não é exercício de aprendizado solto, é entrega de produto em estágio inicial. Isso calibra o livro para ser pragmático: cada conceito existe a serviço da entrega, e tópicos que não impactam diretamente a POC rodando ficam de fora ou são apontados como leitura futura.

## Capítulos

1. [Pi.dev em Anatomia — TUI, Print, RPC e SDK](01-pidev-em-anatomia-tui-print-rpc-e-sdk/CONTENT.md) — os quatro modos do harness e o subset que importa para POC headless
2. [O Modelo de Sessão Como Árvore JSONL](02-o-modelo-de-sessao-como-arvore-jsonl/CONTENT.md) — `id`, `parentId`, fork e branch, e por que isso muda o desenho de persistência
3. [Skills, Extensions e o Sistema de Tools](03-skills-extensions-e-o-sistema-de-tools/CONTENT.md) — o que vem embutido, o que se pluga, e o que não vai entrar na POC
4. [Lambda ou Fargate Para Hospedar Pi.dev](04-lambda-ou-fargate-para-hospedar-pidev/CONTENT.md) — calibragem dos trade-offs específicos (cold start, runtime limit, streaming, custo)
5. [SDK Embedado no Handler vs Wrapping de Processo RPC](05-sdk-embedado-no-handler-vs-wrapping-de-processo-rpc/CONTENT.md) — duas formas de embarcar pi.dev e quando cada uma vence
6. [API Gateway na Frente — Rotas Para Criar Sessão, Enviar Turno e Listar Sessões](06-api-gateway-na-frente-rotas-para-criar-sessao-enviar-turno-e-listar-sessoes/CONTENT.md) — desenho dos endpoints HTTP da POC
7. [Autenticação Mínima Com Cognito ou JWT Authorizer](07-autenticacao-minima-com-cognito-ou-jwt-authorizer/CONTENT.md) — barreira de acesso suficiente para entregar URL pública ao cliente
8. [EFS Multi-Tenant Por Access Point — Sessões Pi.dev Sobreviventes](08-efs-multi-tenant-por-access-point-sessoes-pidev-sobreviventes/CONTENT.md) — redirecionando o diretório de sessões para storage compartilhado
9. [SessionManager Customizado Backed Por S3](09-sessionmanager-customizado-backed-por-s3/CONTENT.md) — alternativa quando EFS não cabe e como preservar fork/branch sobre object storage
10. [Lambda Response Streaming Para Respostas Progressivas](10-lambda-response-streaming-para-respostas-progressivas/CONTENT.md) — entregando turnos do agente como SSE em vez de bloqueio síncrono
11. [Logs, Métricas e Traços Mínimos Para Diagnóstico](11-logs-metricas-e-tracos-minimos-para-diagnostico/CONTENT.md) — instrumentação suficiente para debugar quando a POC der ruim em produção
12. [Empacotando a Entrega Para o Cliente](12-empacotando-a-entrega-para-o-cliente/CONTENT.md) — URL, credencial, instruções e roteiro de validação ponta-a-ponta

## Fontes utilizadas

- [pi.dev — site oficial](https://pi.dev/)
- [Pi Documentation — pi.dev/docs/latest](https://pi.dev/docs/latest)
- [badlogic/pi-mono — repositório monorepo do pi-coding-agent](https://github.com/badlogic/pi-mono)
- [Pi Coding Agent — README oficial](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [@mariozechner/pi-coding-agent — pacote npm](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)
- [How to Build a Custom Agent Framework with PI: The Agent Stack Powering OpenClaw — Nader Dabit](https://gist.github.com/dabit3/e97dbfe71298b1df4d36542aceb5f158)
- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
- [Lambda, Fargate, AgentCore — Which serverless option to choose for your Agentic pattern? — Loïc Labeye](https://medium.com/@loic.labeye/lambda-fargate-agentcore-which-severless-option-to-choose-for-your-agentic-pattern-aaf68cb99700)
- [Developers guide to using Amazon EFS with Amazon ECS and AWS Fargate — AWS Containers Blog](https://aws.amazon.com/blogs/containers/developers-guide-to-using-amazon-efs-with-amazon-ecs-and-aws-fargate-part-1/)
