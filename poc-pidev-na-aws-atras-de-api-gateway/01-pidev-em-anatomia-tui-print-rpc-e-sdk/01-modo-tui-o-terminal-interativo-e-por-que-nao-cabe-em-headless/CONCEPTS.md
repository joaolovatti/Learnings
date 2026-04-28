# Conceitos: Modo TUI — o Terminal Interativo e Por Que Ele Não Cabe em Headless

> _Aula contínua dos conceitos atômicos deste subcapítulo. Cada conceito vira uma seção `## N.` (ou `## 0N.` quando o roteiro tem 10+ conceitos) preenchida em sequência pela skill `estudo-explicar-conceito`. Cada nova iteração lê o que já foi escrito e dá continuidade — sem repetir vocabulário, sem reapresentar exemplos, sem saltos de tom._

## Roteiro

1. Flag de invocação e detecção de TTY — como o harness decide entrar em modo TUI (ausência de flag ou `--mode interactive`) e o papel da detecção de TTY nessa decisão
2. O que o modo TUI entrega — rendering diferencial via ANSI, backbuffer, editor multi-linha com syntax highlighting e feedback em tempo real de tool execution
3. Dependências de ambiente do modo TUI — o que o processo exige do OS para funcionar: TTY real, raw mode, controle ANSI e stdin não redirecionado
4. O que acontece sem TTY — crash, hang ou fallback silencioso: por que piped I/O e stdin redirecionado quebram o modo interativo
5. Por que Lambda e Fargate não têm TTY por design — como esses serviços inicializam processos sem terminal anexado e o que isso significa para o harness
6. Quando o TUI ainda vale no contexto desta POC — desenvolvimento local, debugging de prompts e tools antes do deploy, e o limite dessa utilidade

<!-- ROTEIRO-END -->

<!-- PENDENTE-START -->
> _Pendente: 6 / 6 conceitos preenchidos._
<!-- PENDENTE-END -->

<!-- AULAS-START -->
## 1. Flag de invocação e detecção de TTY

Para quem chega ao pi.dev vindo de ferramentas com interfaces rígidas — um `aws` CLI que sempre imprime JSON, um `node script.js` que sempre termina em segundos — o primeiro estranhamento é que `pi` não exige flag nenhuma para entrar em modo TUI. Você digita `pi` num terminal e o harness decide sozinho o que fazer. Essa decisão, que parece trivial, é o núcleo do conceito 1: entender *como* o harness decide e *por que* a ausência de flag funciona como padrão.

A lógica de resolução de modo do pi.dev examina dois fatores em sequência. Primeiro, ela verifica se há uma flag explícita que force um modo alternativo: `-p` (ou `--print`) para saída batch, `--mode json` para event stream em JSON, `--mode rpc` para protocolo JSONL sobre stdin/stdout. Se nenhuma dessas flags está presente, o harness passa para o segundo fator: verifica se `stdin` é um TTY real. Só depois dessas duas checagens o modo interativo é confirmado ou descartado.

O que é um TTY no sentido que importa aqui? O nome vem de *teletypewriter* — os terminais físicos dos anos 60 e 70. Hoje, na prática, um TTY é a interface entre um processo e um terminal emulado. Quando você abre um terminal no macOS ou no Linux, o emulador de terminal (iTerm, GNOME Terminal, Windows Terminal) cria um par de dispositivos pseudoterminais (PTY): um lado master, controlado pelo emulador, e um lado slave, exposto ao processo filho (o shell, ou o `pi`). O processo filho — `pi`, neste caso — vê o lado slave como um arquivo de dispositivo em `/dev/pts/N`. Ele pode perguntar ao kernel se esse descritor é um TTY real usando a chamada de sistema `isatty(fd)`.

Em Node.js, o wrapper dessa chamada de sistema aparece como a propriedade `isTTY` nas streams do processo. `process.stdin.isTTY` é `true` quando o descritor 0 (stdin) está conectado a um PTY real; é `undefined` (ou falsy) quando stdin veio de um pipe, de um redirecionamento de arquivo, ou de qualquer fonte que não seja um terminal. O pi.dev usa essa propriedade — internamente via a função `resolveAppMode` — para distinguir "está num terminal real" de "está sendo chamado por outro processo". A combinação das duas checagens (ausência de flag + `stdin.isTTY === true`) é o que dispara o modo TUI.

```
Execução                         stdin.isTTY    Flag explícita    Modo resultante
───────────────────────────────  ─────────────  ───────────────   ───────────────
$ pi                             true           nenhuma           TUI (interativo)
$ pi --mode rpc                  true           --mode rpc        RPC
$ echo "prompt" | pi             false          nenhuma           falha / fallback
$ pi -p "prompt"                 true           -p                Print
$ node handler.js (Lambda)       false          nenhuma           falha / fallback
```

A armadilha mais documentada nessa categoria de ferramentas — e que afeta diretamente o pi.dev — é tentar rodar o harness em modo TUI sem TTY e receber o erro `Raw mode is not supported`. Quando o harness confirma o modo interativo e tenta colocar o stdin em raw mode (necessário para capturar teclas individuais, setas, combinações como Ctrl+C sem interpretação do kernel), o runtime Node.js exige que o stream seja de fato um `tty.ReadStream`. Se `stdin` for um pipe ou um arquivo, a tentativa de chamar `setRawMode(true)` resulta em exceção imediata — não em degradação silenciosa. Isso é exatamente o comportamento que os capítulos seguintes do livro vão explorar: quando Lambda inicializa o processo `pi` sem terminal anexado, esse erro aparece no primeiro turno e derruba o handler antes de qualquer resposta ser gerada.

Um detalhe que confunde quem lê o código pela primeira vez: a detecção de TTY checa `stdin`, mas o raw mode e o rendering ANSI são sobre o *conjunto* stdin + stdout + stderr. Um processo pode ter `stdout` conectado a um pipe (para capturar a saída) e `stdin` ainda num TTY — nesse caso `stdin.isTTY` seria `true` mas o rendering diferencial do TUI não teria onde imprimir os frames ANSI. Na prática, o pi.dev opera sob a premissa de que um TTY real no stdin implica stdin+stdout+stderr todos conectados ao mesmo terminal — o que é verdade no uso interativo normal, e é falso em todos os ambientes headless que aparecem nos capítulos 4 e 5.

**Fontes utilizadas:**

- [Getting Started & CLI Reference — badlogic/pi-mono DeepWiki](https://deepwiki.com/badlogic/pi-mono/4.1-getting-started-and-cli-reference)
- [Pi Coding Agent README — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [TTY — Node.js v25.9.0 Documentation](https://nodejs.org/api/tty.html)
- [Pseudoterminal — Wikipedia](https://en.wikipedia.org/wiki/Pseudoterminal)
- [Linux terminals, tty, pty and shell — DEV Community](https://dev.to/napicella/linux-terminals-tty-pty-and-shell-192e)
- [CLI crashes with "Raw mode is not supported" error when piping input — anthropics/claude-code Issue #5925](https://github.com/anthropics/claude-code/issues/5925)
- [Error Raw mode is not supported in non-interactive (non-TTY) environments — ruvnet/claude-flow Issue #213](https://github.com/ruvnet/claude-flow/issues/213)

## 2. O que o modo TUI entrega

O conceito 1 estabeleceu o mecanismo de decisão: como o harness detecta o TTY e confirma o modo interativo. O que acontece depois dessa confirmação é o que este conceito cobre — a superfície concreta que o leitor encontra ao rodar `pi` num terminal real e que, como veremos nos conceitos 3 e 4, está inteiramente ausente em qualquer ambiente headless.

O modo TUI é construído sobre a biblioteca `@mariozechner/pi-tui`, extraída do próprio pi.dev como pacote independente. O primeiro elemento visível ao usuário é um editor multi-linha com suporte a syntax highlighting, baseado no Kitty keyboard protocol para captura confiável de modificadores e combinações como Alt+Enter, Ctrl+K ou teclas de seta. "Kitty keyboard protocol" aqui não tem relação com o terminal Kitty — é um protocolo de evento de teclado que qualquer emulador moderno pode implementar e que substitui o encoding xterm-legacy, notoriamente ambíguo para diferenciar, por exemplo, `Esc` de `Alt+[`. O editor aceita entrada multi-linha (quebra de linha via Enter), suporta undo/redo com kill-ring, e exibe syntax highlighting em tempo real sobre o texto digitado — o highlighting é aplicado por um renderer de markdown interno com colorização baseada em tema, o mesmo renderer que processa as respostas do modelo.

A resposta do agente não aparece como um bloco de texto de uma vez. Ela é renderizada de forma progressiva, diretamente no terminal, à medida que o modelo emite tokens — e aqui entra o mecanismo central do TUI: **rendering diferencial com backbuffer**. O engine da pi-tui mantém um array interno chamado `previousLines`, que registra exatamente o que foi escrito no terminal no último frame. A cada novo frame, o engine compara linha a linha o estado atual com esse backbuffer. Quando localiza a primeira linha que diverge, move o cursor do terminal para aquela posição usando sequências ANSI de movimento de cursor (`ESC[<linha>;<coluna>H`) e redesenha a partir daí até o final — descartando qualquer linha da renderização anterior que não exista mais no frame atual. O resultado é que só o delta vai para stdout, não a tela inteira. Em sessões longas com múltiplos blocos de código e markdown já renderizados e estabilizados, os tokens novos chegando causam atualizações de apenas algumas linhas no final da tela, não um flush completo.

A estratégia de rendering tem três casos distintos. O primeiro é a renderização inicial (first render), em que o engine simplesmente imprime todas as linhas porque não há `previousLines` — é um flush completo, mas só acontece uma vez por sessão. O segundo é o redraw forçado: quando o usuário redimensiona a janela do terminal, o número de colunas muda e o soft-wrapping de linhas longas precisa ser recalculado — qualquer linha que antes cabia em uma linha visual agora pode ocupar duas, e vice-versa; nesse caso o engine limpa a tela inteira e re-renderiza do zero, porque o backbuffer inteiro ficou obsoleto. O terceiro é o differential update, que é o caminho normal: backbuffer comparado, cursor movido para o primeiro ponto divergente, redesenho a partir daí. Uma limitação real aqui: se a primeira linha que mudou estiver acima do viewport atual (o usuário rolou o terminal para cima), o engine não consegue escrever no scrollback buffer acima do cursor — o terminal não permite isso. Nesse caso, ele desce para o final e faz um redraw completo.

Para evitar que o usuário veja frames intermediários durante o differential update — o que causaria flickering perceptível —, a pi-tui envolve cada ciclo de renderização com as sequências de synchronized output: `ESC[?2026h` antes de emitir qualquer dado, `ESC[?2026l` ao final. Esses dois marcadores instruem o emulador de terminal a bufferizar toda a saída recebida entre eles e só exibir atomicamente quando o marcador de fechamento chegar. Em emuladores modernos como Ghostty ou iTerm2, isso resulta em atualizações completamente sem flicker. No terminal embutido do VS Code, o suporte ao protocolo CSI 2026 é parcial e o resultado é flicker ocasional — o próprio autor da pi-tui documenta essa limitação como aceitável dentro do escopo da ferramenta.

O outro pilar do TUI é o feedback em tempo real da execução de tools. Enquanto o agente executa uma chamada de ferramenta — rodar um bash command, ler um arquivo, fazer uma requisição HTTP — os componentes `ToolExecutionComponent` e `BashExecutionComponent` atualizam o terminal progressivamente, mostrando o status corrente da execução (iniciando, executando, saída parcial, concluído). Um caso especialmente visível: quando o agente reescreve um arquivo com a tool de edição, o diff é exibido à medida que o modelo still streams os argumentos da chamada — a pi-ai, a camada de comunicação com o modelo, faz parsing incremental do JSON parcial recebido e alimenta o componente de display antes de o JSON da chamada de ferramenta estar completo. Isso significa que o usuário vê a diff sendo construída linha a linha, não como dump atômico ao final. Esse comportamento é produzido pela combinação de streaming de tokens do modelo com parsing progressivo de JSON — e é, por design, impossível de replicar em nenhum dos modos headless: Print espera o turno inteiro terminar antes de emitir qualquer saída, e RPC emite eventos discretos (text chunk, tool call, tool result) em vez de uma superfície visual contínua.

A armadilha real documentada em projetos derivados do pi-tui é a dependência implícita no suporte terminal ao Kitty keyboard protocol para algumas funcionalidades do editor. Terminais que não implementam o protocolo (versões antigas de xterm, PuTTY, terminais de IDE desatualizados) degradam o editor — algumas combinações de teclas não chegam como esperado, o que produz comportamentos erráticos no editor multi-linha. A pi-tui tenta detectar o suporte e fazer fallback gracioso, mas alguns edge cases escapam. Para o contexto desta POC, isso é irrelevante — o TUI só serve em desenvolvimento local, e qualquer terminal moderno (macOS Terminal, iTerm2, Windows Terminal, GNOME Terminal recente) implementa o protocolo. O ponto importante é que essas dependências em protocolos específicos de emulador de terminal são mais um motivo pelo qual o TUI é descartado para execução headless: Lambda e Fargate não apenas não têm TTY, como também não têm emulador de terminal nenhum — os conceitos de "protocolo de teclado" e "synchronized output" simplesmente não existem nesses contextos, como vamos detalhar nos conceitos 4 e 5.

**Fontes utilizadas:**

- [pi-tui: Terminal UI Library — DeepWiki badlogic/pi-mono](https://deepwiki.com/badlogic/pi-mono/5-pi-tui:-terminal-ui-library)
- [Terminal User Interface (pi-tui) — DeepWiki agentic-dev-io/pi-agent](https://deepwiki.com/agentic-dev-io/pi-agent/4-terminal-user-interface-(pi-tui))
- [What I learned building an opinionated and minimal coding agent — Mario Zechner](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)
- [@mariozechner/pi-tui — npm](https://www.npmjs.com/package/@mariozechner/pi-tui)
- [TUI Components — pi hochej.github.io](https://hochej.github.io/pi-mono/coding-agent/tui/)
- [ANSI escape code — Wikipedia](https://en.wikipedia.org/wiki/ANSI_escape_code)
- [Kitty keyboard protocol — sw.kovidgoyal.net](https://sw.kovidgoyal.net/kitty/keyboard-protocol/)

## 3. Dependências de ambiente do modo TUI

Os conceitos anteriores estabeleceram o mecanismo de decisão (como o harness confirma o modo interativo via `stdin.isTTY` e ausência de flag) e a superfície que o TUI entrega (rendering diferencial, backbuffer, editor multi-linha, Kitty keyboard protocol, synchronized output). O que ainda não ficou explícito é a lista de contratos que o sistema operacional precisa honrar para que tudo aquilo funcione. Esta seção cataloga essas dependências na ordem em que o harness as consome — da mais fundamental à mais específica — porque é exatamente essa lista que vai aparecer, uma a uma, faltando, nos ambientes headless dos conceitos 4 e 5.

A primeira dependência, e a mais fundamental, é a **presença de um TTY real anexado ao processo**. Quando Node.js inicializa um processo, ele examina o descritor de arquivo 0 (stdin) e verifica se ele aponta para um dispositivo do tipo terminal. Se sim, instancia `process.stdin` como um `tty.ReadStream` — uma subclasse de `stream.Readable` com métodos adicionais específicos de terminal, incluindo `setRawMode()`. Se stdin apontar para qualquer outra coisa (um pipe, um arquivo, `/dev/null`, um socket), `process.stdin` é instanciado como `stream.Readable` comum — sem `setRawMode`, sem `isTTY`, sem a infraestrutura de terminal. A verificação de `process.stdin.isTTY` que o conceito 1 descreveu é, na prática, a pergunta "o meu descritor 0 é um `tty.ReadStream`?" — e a resposta negativa descarta imediatamente o modo TUI antes mesmo de tentar qualquer operação de terminal.

A segunda dependência é o **raw mode sobre stdin**. O modo "cooked" (ou canônico) é o padrão do kernel para terminais: caracteres digitados são acumulados numa linha, e o processo só os recebe quando o usuário pressiona Enter. O kernel processa Backspace, Ctrl+C (gerando SIGINT), Ctrl+Z (SIGTSTP) e eco de caracteres — tudo antes do dado chegar ao processo. Esse comportamento é exatamente o oposto do que um TUI precisa: o editor multi-linha da pi-tui precisa capturar cada tecla individualmente no momento em que é pressionada, incluindo setas, Home, End, Alt+Enter, e Ctrl+combinações que o modo canônico interceptaria antes de entregar. A solução é colocar stdin em **raw mode**: `process.stdin.setRawMode(true)` chama internamente `tcsetattr()` no POSIX (a chamada de sistema que reconfigura os atributos do terminal), desabilitando echo, buffering por linha, e processamento de sinais. O kernel passa a entregar cada byte assim que chega, sem interpretação. A armadilha concreta, já referenciada no conceito 1 como o erro `Raw mode is not supported`, é que `setRawMode()` só existe em instâncias de `tty.ReadStream` — em qualquer `stream.Readable` comum, o método simplesmente não está no protótipo, e a tentativa de invocá-lo lança `TypeError` ou, em versões antigas do Node.js, `Cannot read property 'setRawMode' of null`. O pi.dev não protege essa chamada com uma verificação antecipada de `isTTY` no caminho TUI (porque é desnecessário — se chegou no modo TUI, a checagem do conceito 1 já garantiu que stdin é TTY); mas o crash ao tentar `setRawMode` em ambiente sem TTY é exatamente o que um desenvolvedor encontra ao tentar rodar o harness em modo errado.

```
Modo canônico (cooked)         Raw mode
────────────────────────────   ────────────────────────────────
Entrada bufferizada por linha  Entrada byte a byte, imediata
Backspace tratado pelo kernel  Backspace entregue como byte ao processo
Ctrl+C → SIGINT                Ctrl+C → byte 0x03 entregue ao processo
Echo automático pelo kernel    Processo decide se e o que exibir
Enter entrega a linha          Qualquer tecla entrega imediatamente
```

A terceira dependência é o **controle ANSI sobre stdout**. O conceito 2 descreveu o rendering diferencial: o engine compara backbuffer com frame atual, move o cursor para a primeira linha divergente via `ESC[<linha>;<coluna>H`, redesenha, e usa `ESC[?2026h`/`ESC[?2026l` para synchronized output. Todas essas sequências são enviadas para stdout. Se stdout não estiver conectado a um emulador de terminal que interprete ANSI, o que chega do outro lado é lixo binário — os bytes `0x1B[H` impressos literalmente em vez de mover o cursor. Quando stdout está redirecionado para um arquivo ou para um pipe, o processo não recebe erro nenhum — `write(1, ...)` retorna sucesso, porque o kernel não sabe (nem se importa) se o destinatário interpreta ANSI. A saída simplesmente fica poluída com escape sequences ilegíveis. Isso significa que a terceira dependência é implícita: o harness não valida se stdout é um terminal; assume que sim, porque a checagem de `stdin.isTTY` filtrou os casos óbvios. Se alguém forçar stdin como TTY mas redirecionar stdout para um arquivo — cenário artificial, mas possível — o TUI vai rodar e produzir saída corrompida silenciosamente.

A quarta dependência é o **stdin não redirecionado e exclusivo do processo**. O TUI precisa de stdin como canal exclusivo de captura de eventos de teclado, em raw mode, lido continuamente por um event listener. Dois cenários comuns quebram isso: (1) outro processo enviando dados para o stdin via pipe — o editor recebe os bytes do pipe misturados com eventos de teclado, produzindo comportamento indefinido; (2) o processo sendo iniciado com stdin apontando para `/dev/null` — o stream fecha imediatamente e o event loop do TUI para de receber eventos. A detecção de TTY via `isTTY` cobre o caso (1) parcialmente (pipe torna `isTTY` falsy) e o caso (2) inteiramente (stdin de `/dev/null` não é TTY). Mas existe um quinto cenário documentado como armadilha real em issues do Node.js: quando o usuário tem um terminal real mas `process.stdin` foi pausado por outro módulo antes de o TUI ser inicializado. A pi-tui assume que pode chamar `stdin.resume()` e adicionar seu próprio listener `on('data')` — se outro módulo chamou `stdin.destroy()` ou removeu o stream do event loop, o TUI não recebe eventos de teclado mas também não lança exceção, resultando num editor silenciosamente travado.

Em síntese, as quatro dependências — TTY real no stdin, raw mode possível e disponível, ANSI interpretado no stdout, stdin exclusivo e não redirecionado — formam um conjunto que só existe intacto num contexto de terminal interativo genuíno. Remove qualquer uma e o TUI quebra, silenciosamente ou com exceção, dependendo de qual foi removida. Esse é o mapa que os conceitos 4 e 5 vão usar para explicar o que, especificamente, falta em Lambda e Fargate — não é um argumento vago de "headless não funciona", é a lista exata de contratos que cada serviço viola por design.

**Fontes utilizadas:**

- [TTY — Node.js v25.9.0 Documentation](https://nodejs.org/api/tty.html)
- [TTY — Node.js v22.15.1 Documentation](https://nodejs.org/docs/latest-v22.x/api/tty.html)
- [Entering raw mode — Build Your Own Text Editor (viewsourcecode.org)](https://viewsourcecode.org/snaptoken/kilo/02.enteringRawMode.html)
- [Terminal mode — Wikipedia](https://en.wikipedia.org/wiki/Terminal_mode)
- [setRawMode fails when running with non-TTY stdin — vadimdemedes/ink Issue #166](https://github.com/vadimdemedes/ink/issues/166)
- [Error Raw mode is not supported in non-interactive environments — ruvnet/claude-flow Issue #213](https://github.com/ruvnet/claude-flow/issues/213)
- [Color and TTYs — eklitzke.org](https://eklitzke.org/ansi-color-codes)
- [Raw Mode and Input Processing — DeepWiki vadimdemedes/ink](https://deepwiki.com/vadimdemedes/ink/7.3-raw-mode-and-input-processing)

## 4. O que acontece sem TTY

O conceito 3 catalogou as quatro dependências de ambiente que o modo TUI exige — TTY real, raw mode, ANSI sobre stdout, stdin exclusivo. Este conceito descreve o que acontece quando essas dependências estão ausentes: não existe uma resposta única. O comportamento sem TTY divide-se em três padrões distintos — crash imediato, hang silencioso e fallback automático — e qual deles ocorre depende da combinação entre como o processo foi invocado, qual dependência está faltando, e em que ponto da inicialização do harness a ausência é detectada.

O caminho mais frequentemente documentado é o **crash por raw mode**. Ele ocorre quando o harness já confirmou o modo TUI (porque nenhuma flag alternativa foi passada) e o processo chegou até o ponto em que precisa colocar stdin em raw mode para inicializar o editor multi-linha. Se `process.stdin` não é uma instância de `tty.ReadStream` — o que acontece sempre que stdin é um pipe, um arquivo, ou qualquer descritor diferente de um PTY real — a chamada `setRawMode(true)` falha. Em versões modernas do Node.js, o método `setRawMode` simplesmente não existe no protótipo de `stream.Readable` comum; a tentativa de invocá-lo lança `TypeError: process.stdin.setRawMode is not a function`. Em algumas versões mais antigas do Node.js ou em contextos específicos de integração (como o wrapper de terminal do VS Code), a mensagem é diferente mas igualmente fatal: `Error: Raw mode is not supported on the current process.stdin`. Esse é o erro mais documentado em issues de CLIs baseados em Ink — a família inclui claude-code, ruvnet/claude-flow, e qualquer outro harness que use react-ink como camada de TUI — e é exatamente o que o pi.dev produziria se o guard de `isTTY` do conceito 1 não estivesse em frente ao caminho TUI. O crash é imediato, não há retry nem degradação: o processo encerra com código de saída não-zero antes de processar qualquer prompt.

O segundo padrão é o **hang silencioso por stdin de `/dev/null`**. Esse cenário é menos intuitivo do que o crash porque o processo *parece* funcionar: não lança exceção, não imprime erro, simplesmente não avança. O que acontece internamente é o seguinte. Quando stdin aponta para `/dev/null`, Node.js instancia `process.stdin` como um `stream.Readable` comum (não é TTY), então `isTTY` é falsy e o guard do conceito 1 deveria interceptar o modo TUI antes de chegar no raw mode. O harness entra então em algum modo alternativo ou simplesmente não tem o que processar — mas o event loop do Node.js permanece ativo. `stream.Readable` não fecha automaticamente quando a fonte subjacente é `/dev/null`; o stream pode continuar registrado no event loop esperando dados. Se o harness adicionou um listener `on('data')` ou `on('end')` antes de verificar TTY, ou se algum módulo de terceiro (como uma extensão) registrou um listener no stdin, o event loop não drena e o processo fica vivo sem produzir nada. Do ponto de vista de quem invocou o processo — um orquestrador Lambda, um shell script — o processo simplesmente trava sem output e sem saída, até que um timeout externo o kill. Em sistemas de integração contínua, esse padrão é a origem da classe de bugs de "job que nunca termina" — distinto do crash, que ao menos falha rápido e deixa logs.

O terceiro padrão — e o mais relevante para o design desta POC — é o **fallback automático para print mode**. Quando nenhuma flag explícita foi passada e `stdin.isTTY` é falsy, a função `resolveAppMode` do pi.dev não tenta forçar o TUI: ela reconhece a ausência de TTY como sinal de contexto não-interativo e resolve o modo como print. Isso significa que uma invocação do tipo `echo "meu prompt" | pi` ou `pi < prompt.txt` não crasheia — ela entrega uma resposta em batch (uma única geração, sem sessão persistida) e termina. O fallback é gracioso *desde que o prompt venha junto com o stdin pipe* — o harness tem algo para processar. Se o stdin piped for vazio (como em `cat /dev/null | pi`) ou se o prompt só existir como argumento (como em `pi -p "prompt"` com stdin de um pipe vazio), o comportamento depende de como o harness trata a ausência de conteúdo; na prática, o modo print encerra sem geração nenhuma ou com erro de validação de input.

A distinção entre crash, hang e fallback pode ser resumida pelo que está presente ou ausente em cada situação:

```
Cenário de invocação              stdin.isTTY   Modo resolvido   Comportamento
────────────────────────────────  ────────────  ───────────────  ─────────────────────────────
$ pi                              true          TUI              OK — sessão interativa
$ echo "..." | pi                 false         Print (fallback) Gera resposta e termina
$ cat /dev/null | pi              false         Print (fallback) Sem input → termina vazio
$ pi < /dev/null                  false         Print (fallback) Sem input → termina vazio
stdin=/dev/null sem pipe          false         Print (fallback) Event loop pode travar (*)
Forçar TUI com stdin não-TTY (**)  false        TUI (forçado)    Crash: Raw mode not supported
```

`(*) O hang por event loop ocorre quando stdin de /dev/null não fecha o stream antes que listeners sejam registrados por algum módulo de inicialização.`
`(**) Cenário artificial: nenhuma flag do pi.dev força TUI explicitamente; o harness descobre isso via resolveAppMode antes de chegar no raw mode.`

Uma armadilha real documentada em projetos que usam CLIs baseados em Ink (a mesma família de rendering que o pi-tui) é o crash por raw mode ocorrer **mesmo com a flag `-p` passada**. O mecanismo é o seguinte: alguns módulos de extensão ou plugins inicializam o TUI durante o bootstrap do processo — antes que a resolução de modo tenha ocorrido — e registram listeners de raw mode no stdin de forma incondicional. Quando a flag `-p` chega depois, o modo print é resolvido corretamente, mas o listener de raw mode já tentou `setRawMode(true)` no stdin não-TTY durante a inicialização e já crashou. Esse padrão é exatamente o que foi reportado no issue claude-mem/claude-code #1482: o plugin `claude-mem` força a inicialização do Ink mesmo em `--print` mode, fazendo com que qualquer invocação com stdin piped retorne o erro de raw mode, mesmo quando a flag de modo não-interativo foi explicitamente passada. No pi.dev, o sistema de extensões carrega extensões após a resolução de modo — o que evita esse race de inicialização — mas é um ponto de atenção para quem escrever extensões customizadas para a POC.

O que torna esses três padrões relevantes para os capítulos 4 e 5 é que Lambda e Fargate não entram no cenário de crash ou de hang — eles caem no fallback, mas de um jeito que não serve para uma POC multi-turno. Lambda inicializa o processo handler sem terminal anexado, com stdin configurado pela runtime como um pipe (o event payload chega via variáveis de ambiente e canais internos da runtime, não via stdin do processo filho). O harness detecta ausência de TTY, resolve print mode, e termina após a primeira resposta — exatamente o comportamento correto para o conceito 2 deste capítulo (Print mode) mas incompatível com sessões persistidas e múltiplos turnos, que é o objetivo da POC. Essa é a ponte para o conceito 5: não é que Lambda crasheia ao tentar rodar o TUI, é que o TUI simplesmente nunca é tentado — e o modo que surge no lugar (print) não suporta o que a POC precisa.

**Fontes utilizadas:**

- [CLI crashes with "Raw mode is not supported" error when piping input — anthropics/claude-code Issue #5925](https://github.com/anthropics/claude-code/issues/5925)
- [Raw mode is not supported on current process.stdin — anthropics/claude-code Issue #1072](https://github.com/anthropics/claude-code/issues/1072)
- [Error Raw mode is not supported in non-interactive environments — ruvnet/claude-flow Issue #213](https://github.com/ruvnet/claude-flow/issues/213)
- [claude-mem plugin breaks claude --print (pipe mode) on Windows — thedotmack/claude-mem Issue #1482](https://github.com/thedotmack/claude-mem/issues/1482)
- [setRawMode fails when running with non-TTY stdin — vadimdemedes/ink Issue #166](https://github.com/vadimdemedes/ink/issues/166)
- [TTY — Node.js v25.9.0 Documentation](https://nodejs.org/api/tty.html)
- [Getting Started — DeepWiki agentic-dev-io/pi-agent](https://deepwiki.com/agentic-dev-io/pi-agent/1.1-getting-started)
- [Node process hangs when stdin is piped — nodejs/node Issue #56537](https://github.com/nodejs/node/issues/56537)

## 5. Por que Lambda e Fargate não têm TTY por design

O conceito 4 descreveu o que acontece quando o harness encontra ausência de TTY — crash, hang ou fallback — e concluiu que Lambda e Fargate caem no fallback silencioso para print mode. O que falta explicar é por que esses serviços chegam nessa situação: não é negligência de configuração nem limitação acidental — é uma consequência direta do modelo de execução que cada um deles adota por razões de arquitetura, isolamento e custo.

O ponto de partida para entender Lambda é entender que uma função Lambda não é um processo que você invoca passando uma conexão de terminal. O fluxo começa no serviço de invocação da AWS — via console, via chamada de API, via evento de outro serviço — e chega ao processo handler por um canal completamente diferente de um PTY. O ambiente de execução Lambda é um microVM baseado no Firecracker, um hipervisor KVM open source desenvolvido pela AWS. Dentro desse microVM roda uma instância mínima de Amazon Linux com um processo init customizado escrito em Go chamado Rapid, que assume o PID 1. Rapid orquestra o ciclo de vida completo: carrega o runtime (o bootstrap Node.js, para funções Node.js), gerencia extensões, e comunica com os serviços de controle da AWS via sockets internos cujos file descriptors são marcados com `FD_CLOEXEC` para não vazar para o código do usuário. O payload de invocação — o evento JSON — chega ao runtime via uma API HTTP local (`http://127.0.0.1:9001`) que o runtime polling: o processo Node.js faz um `GET /runtime/invocation/next`, bloqueia até receber o próximo evento, processa, e faz `POST /runtime/invocation/{id}/response`. Em nenhum ponto dessa cadeia um PTY é alocado. Não existe um emulador de terminal, não existe um par master/slave de PTY, e `/dev/pts/` não tem entradas disponíveis para o código do usuário — como o erro `OSError: out of pty devices` documenta quando pexpect (que depende de `pty.fork()`) tenta alocar um PTY dentro de Lambda. O stdin do processo Node.js, nesse contexto, não aponta para um `tty.ReadStream` — ele aponta para nada útil, ou simplesmente não é fonte de entrada de nenhum dado relevante para a função, já que toda entrada real chega via o polling da Lambda Runtime API.

```
Invocação Lambda (Node.js handler)

  AWS Service Event
       │
       ▼
  Lambda Runtime API (HTTP :9001)
       │  GET /runtime/invocation/next  ← bootstrap Node.js polling
       │  POST /runtime/invocation/{id}/response
       ▼
  handler(event, context) → retorna response
       │
  Sem PTY, sem emulador de terminal
  process.stdin.isTTY === undefined
  process.stdin não é tty.ReadStream
```

Fargate tem uma história ligeiramente diferente — e o detalhe importa porque Fargate é uma alternativa real para hospedar o pi.dev com processo de longa duração, como vamos explorar no capítulo 4. No Fargate, o modelo é Docker: você define uma task definition com um container definition, e o ECS provisiona o container usando o Docker daemon gerenciado pela infraestrutura Fargate. O entrypoint do container — o processo que vira PID 1 ou que é iniciado via `CMD` — sobe sem TTY alocado por padrão. O padrão do Docker é rodar containers sem flag `-t` (pseudoTerminal), o que significa que o container recebe stdin conectado a `/dev/null` (ou fechado) e stdout/stderr conectados a pipes de log. O parâmetro `pseudoTerminal: true` na container definition do ECS é o equivalente de `docker run --tty` — ele instrui o daemon Docker a criar um par PTY e conectar o processo ao lado slave. Esse parâmetro existe na API do ECS, mas sua ausência é o estado padrão de qualquer workload de produção no Fargate: não faz sentido alocar um PTY para um servidor HTTP, um worker de fila ou um handler de agente que recebe eventos via chamada HTTP — nenhum desses processos lê stdin como terminal. A consequência para o pi.dev rodando em Fargate é exatamente a mesma que em Lambda: `process.stdin.isTTY` é falsy, `setRawMode` não está disponível, e o harness detecta contexto não-interativo no primeiro `resolveAppMode`.

Há uma distinção importante entre os dois serviços que o `STRUCT.md` reserva para o capítulo 4 (Lambda ou Fargate Para Hospedar Pi.dev): Lambda é mais radical na ausência de PTY (não há dispositivos `/dev/pts/` disponíveis de forma alguma no microVM do código do usuário — o próprio `openpty()` do OS falha), enquanto Fargate permite que você aloque um PTY explicitamente via `pseudoTerminal: true` se realmente precisar. Isso não significa que o modo TUI do pi.dev se tornaria utilizável com `pseudoTerminal: true` — o TUI foi projetado para presença humana real na outra ponta, com teclado, emulador de terminal com suporte a Kitty keyboard protocol e synchronized output, redimensionamento de janela e interação contínua. Mesmo que o container Fargate fosse inicializado com um PTY alocado, não haveria nenhum humano conectado a esse PTY durante a execução de um request HTTP — o PTY seria um canal vazio sem emulador de terminal real na outra ponta. O conceito aqui não é técnico-impossível (o PTY pode ser criado); é arquiteturalmente sem sentido: um cliente enviando um prompt via HTTP não é um usuário num terminal.

O que esses dois serviços têm em comum — e que os distingue de um terminal local — é a ausência de um **canal de teclado interativo em tempo real**. Lambda processa um evento e retorna uma resposta dentro de uma janela de tempo; Fargate roda um processo que serve requisições via protocolo de rede. Em nenhum dos dois modelos existe um humano na outra ponta de um `stdin` aguardando emitir bytes à medida que pensa. O modo TUI do pi.dev — com seu editor multi-linha, rendering diferencial de backbuffer e feedback progressivo de tool execution — é uma superfície inteiramente construída para esse canal interativo. Sem ele, o TUI não apenas não funciona tecnicamente: ele não tem propósito. A detecção de TTY do conceito 1 resolve corretamente nesses ambientes: ausência de `stdin.isTTY` não é um falso negativo, é um diagnóstico preciso de que não existe sessão interativa para servir.

**Fontes utilizadas:**

- [Understanding the Lambda execution environment lifecycle — AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html)
- [Lambda internals (Part one) — ClearVector](https://www.clearvector.com/blog/lambda-internals/)
- [out of pty devices on AWS Lambda — pexpect/pexpect Issue #654](https://github.com/pexpect/pexpect/issues/654)
- [ContainerDefinition: pseudoTerminal — Amazon ECS API Reference](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_ContainerDefinition.html)
- [Amazon ECS task definition parameters for Fargate — AWS ECS Developer Guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html)
- [ECS vs EKS: how to use stdin and tty with ECS tasks — AWS re:Post](https://repost.aws/questions/QUY2PpSbJQQaCWs7r4J14mgg/ecs-vs-eks-how-to-use-stdin-and-tty-with-ecs-tasks)
- [The Interactive and TTY Options in docker run — Baeldung](https://www.baeldung.com/linux/docker-run-interactive-tty-options)

## 6. Quando o TUI ainda vale no contexto desta POC

O conceito 5 encerrou com uma frase que merece ser retomada: a detecção de TTY do harness não é um falso negativo em Lambda e Fargate — é um diagnóstico preciso de que não existe sessão interativa para servir. Isso poderia levar à conclusão de que o modo TUI é irrelevante para quem está construindo esta POC. Seria uma conclusão errada, e entender por que é errada delimita com precisão o papel que o TUI vai ocupar no seu fluxo de trabalho.

O TUI é descartado na execução em produção. Na construção da POC — no ciclo de desenvolvimento local antes de qualquer deploy — ele é a ferramenta mais eficiente disponível para uma categoria específica de problema: observar o comportamento do agente com uma combinação nova de prompt, model, skill, extension ou conjunto de tools, de forma interativa e iterativa. Nenhum dos modos headless oferece o mesmo ciclo de feedback para esse propósito.

O caso de uso central é a iteração de prompts e system prompts. Quando você está escrevendo o prompt do agente que vai viver no handler da POC — definindo persona, restrições, formato de resposta, instruções de uso das tools — você precisa ver o agente respondendo em tempo real, com feedback progressivo de cada token. O modo TUI entrega exatamente isso: o rendering diferencial descrito no conceito 2 atualiza o terminal a cada token recebido do modelo. Você vê onde o agente hesita, onde quebra o formato esperado, onde aluça sobre a disponibilidade de uma tool que não foi declarada — e você itera o prompt imediatamente, sem esperar o turno completo, sem reempacotar um payload HTTP e sem aguardar cold start de Lambda. O ciclo de feedback é a ordem de grandeza mais rápido do que qualquer loop de deploy.

O segundo caso de uso é o debugging de tools antes da integração. As tools que vão entrar na POC — `bash`, `read`, `write`, `edit`, e as extensões customizadas que você vier a construir — podem ser testadas localmente em TUI com `pi` puro, antes de qualquer embedding no handler. O feedback em tempo real do `ToolExecutionComponent` (que o conceito 2 descreveu) exibe o status da execução de cada ferramenta à medida que ocorre: você vê a tool sendo chamada, os argumentos parseados incrementalmente, o resultado chegando. Se uma tool retorna um resultado que o agente interpreta de forma inesperada — causando uma segunda chamada desnecessária, por exemplo —, você identifica o problema no TUI antes de ter que instrumentar o handler em Lambda e cavar nos CloudWatch Logs. Uma prática documentada no próprio pi.dev para debugging multi-sessão é ativar `PI_TUI_WRITE_LOG` — uma variável de ambiente que instrui o harness a escrever um log file por instância de TUI, permitindo inspecionar o que foi enviado e recebido sem depender de instrumentação externa.

O terceiro caso de uso é a exploração da árvore de sessão. O conceito central do capítulo 2 deste livro — o modelo de sessão como árvore JSONL com `id` e `parentId` — tem representação visual direta no TUI via o comando `/tree`. O comando abre um navegador inline na sessão JSONL armazenada em `~/.pi/agent/sessions/`, permite ver o grafo de turnos, fazer fork de qualquer ponto anterior via `/fork`, e continuar a conversa a partir de um branch alternativo, tudo preservado no mesmo arquivo. Para quem está construindo um `SessionManager` customizado para a POC (que o capítulo 9 vai cobrir), explorar sessões reais geradas pelo TUI é o caminho mais direto para entender a estrutura dos dados que o `SessionManager` vai precisar ler, escrever e indexar — sem precisar escrever código de parsers provisórios.

O limite da utilidade do TUI para esta POC tem três bordas claras. Primeira: **o TUI não emula o contexto de produção**. O harness rodando localmente em TUI usa o filesystem local para armazenar sessões, carrega variáveis de ambiente da sua shell, tem acesso direto ao workspace. O handler em Lambda ou Fargate vai rodar numa instância isolada, com variáveis de ambiente injetadas via task definition ou Lambda configuration, com sessões armazenadas em EFS ou S3. Comportamentos que funcionam em TUI mas quebram em produção — por exemplo, uma tool que lê um arquivo local que não existe no container — não aparecem nos testes de TUI. Segunda: **o TUI não testa o caminho RPC ou SDK**. A integração do harness no handler — seja via `pi --mode rpc` wrappado em processo, seja via embedding do SDK com `createAgentSession` — tem seus próprios pontos de falha: framing de mensagens, correlation de eventos, serialização de results de tools. Esses pontos só aparecem quando o caminho headless é exercitado diretamente, não no TUI. Terceira: **o TUI não testa o fluxo HTTP da POC**. O comportamento do agente ao receber um payload via API Gateway, ser hidratado com o `sessionId` correto, executar um turno, e serializar a resposta de volta ao gateway são comportamentos que pertencem ao handler, não ao harness em modo interativo. O TUI ajuda a refinar o que o agente faz; ele não valida como o agente é servido.

A forma pragmática de posicionar o TUI no ciclo de desenvolvimento da POC é: TUI é o ambiente de rascunho. Você usa o TUI para encontrar o prompt certo, confirmar que as tools se comportam como esperado com o modelo escolhido, e entender a estrutura das sessões que o `SessionManager` vai persistir. Quando esses três insumos estão calibrados, você os traslada para o handler e executa o ciclo de integração em headless. O TUI não é o destino — é a bancada de instrumentos antes do laboratório.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/README.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [What I learned building an opinionated and minimal coding agent — Mario Zechner](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)
- [Getting Started & CLI Reference — DeepWiki badlogic/pi-mono](https://deepwiki.com/badlogic/pi-mono/4.1-getting-started-and-cli-reference)
- [@mariozechner/pi-coding-agent — npm](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)
- [Pi: The Minimal Agent Within OpenClaw — Armin Ronacher](https://lucumr.pocoo.org/2026/1/31/pi/)
- [pi-mono/packages/coding-agent/CHANGELOG.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/CHANGELOG.md)

<!-- AULAS-END -->

---

**Próximo subcapítulo** → [Modo Print/JSON — Saída Determinística Para Scripts](../02-modo-print-json-saida-deterministica-para-scripts/CONTENT.md)
