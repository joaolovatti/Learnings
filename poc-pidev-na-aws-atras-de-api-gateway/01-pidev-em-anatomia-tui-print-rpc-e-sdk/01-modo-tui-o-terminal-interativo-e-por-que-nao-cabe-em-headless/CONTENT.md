# Modo TUI — o Terminal Interativo e Por Que Ele Não Cabe em Headless

![capa](cover.png)

## Sobre este subcapítulo

O modo TUI é o ponto de entrada padrão do pi.dev — o que o usuário encontra ao rodar `pi` sem argumentos num terminal real. Ele oferece a experiência mais rica do harness: rendering diferencial do terminal, editor multi-linha com syntax highlighting, feedback em tempo real da execução de tools, e uma interface que assume presença humana na outra ponta. Entender o que esse modo oferece, e especialmente o que ele exige do ambiente, é o pré-requisito para compreender por que os três modos seguintes existem.

Este subcapítulo constrói a base comparativa do capítulo: cada modo subsequente (Print, RPC, SDK) pode ser lido como uma resposta a uma limitação que o TUI carrega por design. Ao terminar aqui, o leitor terá o modo TUI mapeado com precisão suficiente para nunca confundi-lo com as alternativas headless — e entenderá por que um Lambda sem TTY simplesmente não consegue instanciar essa superfície.

## Estrutura

O subcapítulo cobre: (1) **o que é o modo TUI** — a flag de invocação (ausência de flag ou `--mode interactive`), o que o harness faz ao detectar um TTY, o rendering diferencial e o editor multi-linha; (2) **o que o modo TUI exige do ambiente** — presença de TTY, controle de terminal ANSI, interação humana em tempo real, ausência de I/O redirecionado; (3) **por que headless elimina o TUI** — o que acontece quando `pi` roda sem TTY (crash, fallback, ou hang), como Lambda e Fargate servem processos sem terminal anexado; (4) **quando o TUI ainda é útil no contexto desta POC** — desenvolvimento local, debugging de prompts e tools antes de subir para AWS, exploração do comportamento do agente.

## Objetivo

Ao terminar este subcapítulo, o leitor conseguirá invocar o pi.dev em modo TUI localmente, saberá identificar as dependências de ambiente que o modo requer (TTY, ANSI), e entenderá com precisão técnica por que esse modo é descartado para execução headless na AWS — argumento que reaparece no subcapítulo 5 ao montar o corte final do subset da POC.

## Conceitos

A explicação completa destes conceitos vive em [`CONCEPTS.md`](CONCEPTS.md), construída sequencialmente pela skill `estudo-explicar-conceito`.

1. Flag de invocação e detecção de TTY — como o harness decide entrar em modo TUI (ausência de flag ou `--mode interactive`) e o papel da detecção de TTY nessa decisão
2. O que o modo TUI entrega — rendering diferencial via ANSI, backbuffer, editor multi-linha com syntax highlighting e feedback em tempo real de tool execution
3. Dependências de ambiente do modo TUI — o que o processo exige do OS para funcionar: TTY real, raw mode, controle ANSI e stdin não redirecionado
4. O que acontece sem TTY — crash, hang ou fallback silencioso: por que piped I/O e stdin redirecionado quebram o modo interativo
5. Por que Lambda e Fargate não têm TTY por design — como esses serviços inicializam processos sem terminal anexado e o que isso significa para o harness
6. Quando o TUI ainda vale no contexto desta POC — desenvolvimento local, debugging de prompts e tools antes do deploy, e o limite dessa utilidade

## Fontes utilizadas

- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [Pi Coding Agent CLI — DeepWiki badlogic/pi-mono](https://deepwiki.com/badlogic/pi-mono/4-pi-coding-agent:-coding-agent-cli)
- [Getting Started — DeepWiki agentic-dev-io/pi-agent](https://deepwiki.com/agentic-dev-io/pi-agent/1.1-getting-started)
- [Pi Coding Agent — Complete Guide (Matteo Chieppa)](https://www.matteochieppa.com/en/blog/pi-coding-agent-complete-guide)
- [Pi Coding Agent — Sandbox Analysis Report (Agent Safehouse)](https://agent-safehouse.dev/docs/agent-investigations/pi)
