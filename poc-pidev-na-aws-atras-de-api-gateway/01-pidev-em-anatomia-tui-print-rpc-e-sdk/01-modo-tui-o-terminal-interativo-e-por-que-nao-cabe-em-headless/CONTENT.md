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

1. O que é e como invocar o modo TUI — a ausência de flag (ou `--mode interactive`) como gatilho, e o que o harness instancia ao detectar presença de TTY
2. Rendering diferencial e editor multi-linha — como o TUI atualiza só regiões modificadas do terminal (sem flicker, sem screen clear) e o que o editor de input oferece (syntax highlighting, slash commands, autocomplete de caminhos)
3. O que é um TTY e por que o modo TUI depende dele — a relação entre `tty.isatty()`/`process.stdout.isTTY`, controle ANSI, e a superfície de terminal que o rendering diferencial e o editor precisam para funcionar
4. O que acontece quando pi roda sem TTY — crash, hang ou saída silenciosa, e por que o harness não tem fallback gracioso para ambientes sem terminal
5. Por que Lambda e Fargate não fornecem TTY — como esses runtimes servem processos sem terminal anexado (I/O redirecionado, sem alocação de pty), tornando o modo TUI impossível de instanciar
6. Quando o TUI ainda é útil no contexto desta POC — o papel do modo TUI em desenvolvimento local (debugging de prompts e tools, exploração de comportamento do agente) antes de subir para AWS, e o limite claro onde ele para de servir

## Fontes utilizadas

- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [Pi Coding Agent CLI — DeepWiki badlogic/pi-mono](https://deepwiki.com/badlogic/pi-mono/4-pi-coding-agent:-coding-agent-cli)
- [Getting Started — DeepWiki agentic-dev-io/pi-agent](https://deepwiki.com/agentic-dev-io/pi-agent/1.1-getting-started)
- [Pi Coding Agent — Complete Guide (Matteo Chieppa)](https://www.matteochieppa.com/en/blog/pi-coding-agent-complete-guide)
- [Pi Coding Agent — Sandbox Analysis Report (Agent Safehouse)](https://agent-safehouse.dev/docs/agent-investigations/pi)
