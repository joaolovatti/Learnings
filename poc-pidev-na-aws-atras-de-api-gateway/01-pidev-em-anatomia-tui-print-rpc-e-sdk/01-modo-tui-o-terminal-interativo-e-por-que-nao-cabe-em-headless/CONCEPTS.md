# Conceitos: Modo TUI — o Terminal Interativo e Por Que Ele Não Cabe em Headless

> _Aula contínua dos conceitos atômicos deste subcapítulo. Cada conceito vira uma seção `## N.` (ou `## 0N.` quando o roteiro tem 10+ conceitos) preenchida em sequência pela skill `estudo-explicar-conceito`. Cada nova iteração lê o que já foi escrito e dá continuidade — sem repetir vocabulário, sem reapresentar exemplos, sem saltos de tom._

## Roteiro

1. O que é e como invocar o modo TUI — a ausência de flag (ou `--mode interactive`) como gatilho, e o que o harness instancia ao detectar presença de TTY
2. Rendering diferencial e editor multi-linha — como o TUI atualiza só regiões modificadas do terminal (sem flicker, sem screen clear) e o que o editor de input oferece (syntax highlighting, slash commands, autocomplete de caminhos)
3. O que é um TTY e por que o modo TUI depende dele — a relação entre `tty.isatty()`/`process.stdout.isTTY`, controle ANSI, e a superfície de terminal que o rendering diferencial e o editor precisam para funcionar
4. O que acontece quando pi roda sem TTY — crash, hang ou saída silenciosa, e por que o harness não tem fallback gracioso para ambientes sem terminal
5. Por que Lambda e Fargate não fornecem TTY — como esses runtimes servem processos sem terminal anexado (I/O redirecionado, sem alocação de pty), tornando o modo TUI impossível de instanciar
6. Quando o TUI ainda é útil no contexto desta POC — o papel do modo TUI em desenvolvimento local (debugging de prompts e tools, exploração de comportamento do agente) antes de subir para AWS, e o limite claro onde ele para de servir

<!-- ROTEIRO-END -->

## 4. O que acontece quando pi roda sem TTY — crash, hang ou saída silenciosa, e por que o harness não tem fallback gracioso para ambientes sem terminal

O `## 3.` mostrou que `setRawMode(true)` é o que permite ao `Editor` receber teclas individuais sem o buffer de linha do kernel. O que acontece quando esse método não existe? Em Node.js, `process.stdin.setRawMode` só está disponível quando `process.stdin` é uma instância de `tty.ReadStream` — o que só ocorre quando stdin está conectado a um TTY real. Em qualquer outro caso (stdin redirecionado de arquivo, pipe, ou `/dev/null`), `process.stdin.setRawMode` é `undefined`. Chamar `undefined()` é um `TypeError` imediato — o processo termina com stack trace ou, se houver um handler de erro no event loop, o erro borbulha de forma silenciosa dependendo de onde a chamada está dentro da cadeia de inicialização.

Isso define o primeiro modo de falha: **crash por TypeError**. Quando o `InteractiveMode` tenta inicializar o `Editor` e chama `setRawMode(true)` num stdin não-TTY, o processo lança um erro não recuperável. Não há fallback para modo de texto simples nem mensagem de uso amigável: o harness simplesmente não foi desenhado para degradar graciosamente nesse ponto, porque o modo TUI pressupõe TTY como invariante, não como recurso opcional. Agentes de terminal similares que usam Ink (como o próprio Claude Code) documentam a mesma categoria de erro — "Raw mode is not supported on the stdin provided" — como falha fatal em ambientes sem terminal.

O segundo modo de falha é **hang no event loop**. Se a inicialização do `Editor` for adiada ou protegida por uma guarda de `isTTY`, o processo pode completar a inicialização do `InteractiveMode` e entrar no loop de leitura de stdin aguardando input do usuário — que nunca chega porque stdin está vazio ou fechado imediatamente após a abertura. O `readline` e o event loop do Node.js mantêm o processo vivo enquanto há listeners no stream; sem input e sem timeout, o processo fica suspenso indefinidamente. Esse comportamento foi observado em outros agentes TUI no mesmo ecossistema e corresponde ao que acontece quando um processo interativo é invocado de dentro de um script CI sem alocação de PTY — o script simplesmente trava até o timeout do CI matar o job.

O terceiro modo é menos provável mas possível: **saída silenciosa sem código de erro**. Se alguma guarda mais alta no fluxo de inicialização verificar `process.stdout.isTTY` e retornar cedo sem imprimir nada, o processo termina com exit code 0 e zero output — o que é o pior dos mundos para diagnóstico, porque parece que o comando funcionou. Esse modo só ocorreria se houvesse alguma lógica de detecção adiantada de TTY antes da inicialização do `InteractiveMode`, o que os dados disponíveis sobre o harness não confirmam como caminho atual.

O que não existe no pi.dev é um **fallback gracioso**: o modo TUI não detecta ausência de TTY e oferece automaticamente modo texto, prompt simples, ou encaminha para print/JSON. Essa é uma escolha de design — o harness delega ao invocador a responsabilidade de selecionar o modo certo para o ambiente. Quem quer rodar sem TTY passa `--mode json`, `--mode rpc`, ou usa o SDK; ninguém "descobre" o modo TUI e o harness o rebaixa silenciosamente para algo que funciona. O modelo mental correto é de **superfícies separadas com pré-condições explícitas**, não de degradação progressiva de uma única superfície universal.

Para a POC descrita neste livro, essa ausência de fallback é irrelevante — porque a POC nunca vai invocar o modo TUI no ambiente AWS. O que importa registrar aqui é o mecanismo: cada primitiva que os conceitos anteriores descreveram (`setRawMode`, `clearLine`, `moveCursor`, `columns`, `resize`) termina em falha ou no-op quando o file descriptor não é um TTY, e o conjunto dessas falhas em cascata produz um processo que crash, trava ou sai silenciosamente dependendo de qual primitiva é chamada primeiro e se há guards parciais no caminho.

**Fontes utilizadas:**

- [TTY | Node.js v25.9.0 Documentation](https://nodejs.org/api/tty.html)
- [setRawMode fails when running with non-TTY stdin — Ink Issue #166](https://github.com/vadimdemedes/ink/issues/166)
- [Claude Code CLI hangs without TTY despite using -p flag — Issue #9026](https://github.com/anthropics/claude-code/issues/9026)
- [Understanding and Resolving the Error "The input device is not a TTY" — Medium](https://medium.com/@haroldfinch01/understanding-and-resolving-the-error-the-input-device-is-not-a-tty-75199ab2344d)
- [isTTY can be used to tailor appropriate Node process output — Stefan Judis](https://www.stefanjudis.com/today-i-learned/istty-can-be-used-to-tailor-appropriate-node-process-output/)


<!-- AULAS-START -->

## 1. O que é e como invocar o modo TUI — a ausência de flag (ou `--mode interactive`) como gatilho, e o que o harness instancia ao detectar presença de TTY

O modo TUI é o ponto de entrada padrão do pi.dev: quando você executa `pi` num terminal real sem qualquer flag de modo, o harness inspeciona o stdin via `resolveAppMode` e, ao detectar que está conectado a um TTY, ativa o `InteractiveMode`. Não há nenhuma flag obrigatória — a ausência de `-p`, `--mode json` e `--mode rpc` é ela mesma o gatilho. Se quiser tornar a intenção explícita, o harness aceita `--mode interactive`, mas no dia a dia ninguém escreve isso porque o padrão já é esse.

O que o harness instancia ao entrar em modo TUI é uma árvore de componentes proprietária — o pi não usa Ink, React ou qualquer framework de UI de terminal. A classe `InteractiveMode` inicializa o motor de rendering diferencial, o componente de editor multi-linha, o footer com metadados da sessão (diretório de trabalho, tokens acumulados, custo e modelo ativo), e watchers de arquivo para `.git/HEAD` (detecção de branch) e arquivos de tema. A startup exibe um cabeçalho listando os recursos carregados (extensões, skills, tools habilitadas), e a partir daí a interface fica em modo de leitura contínua de input do usuário.

A interação acontece inteiramente dentro dessa superfície de terminal: o usuário digita no editor multi-linha (Shift+Enter para quebra de linha), usa Tab para completar caminhos, `@` para referenciar arquivos por busca fuzzy, ou cola imagens com Ctrl+V. Slash commands (`/model`, `/resume`, `/fork`, `/tree`, `/settings`) são interpretados pelo próprio harness antes de chegarem ao modelo. A sessão ativa é mantida em memória — ao sair e retomar com `/resume`, o histórico é carregado do disco.

Essa cadeia de dependências — `InteractiveMode` → motor de rendering → ANSI sobre stdout → input de teclado sobre stdin — é o que torna o modo TUI inseparável de um terminal real. Cada um dos conceitos seguintes desta aula desmonta uma peça dessa dependência, chegando ao ponto onde o capítulo 5 (`05-o-subset-que-importa-para-a-poc-headless`) vai declarar formalmente a eliminação desse modo para a POC.

**Fontes utilizadas:**

- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [Getting Started & CLI Reference — DeepWiki badlogic/pi-mono](https://deepwiki.com/badlogic/pi-mono/4.1-getting-started-and-cli-reference)
- [Terminal User Interface (pi-tui) — DeepWiki agentic-dev-io/pi-agent](https://deepwiki.com/agentic-dev-io/pi-agent/4-terminal-user-interface-(pi-tui))
- [Pi Coding Agent — Sandbox Analysis Report (Agent Safehouse)](https://agent-safehouse.dev/docs/agent-investigations/pi)
- [What I learned building an opinionated and minimal coding agent — Mario Zechner](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)

## 2. Rendering diferencial e editor multi-linha — como o TUI atualiza só regiões modificadas do terminal (sem flicker, sem screen clear) e o que o editor de input oferece (syntax highlighting, slash commands, autocomplete de caminhos)

O `InteractiveMode` não escribe para stdout diretamente — cada peça de conteúdo visível (resposta do modelo, spinner de loading, footer com tokens) é uma instância de `Component` na árvore da `TUI`. O ponto que diferencia essa arquitetura de um print simples é o motor de rendering diferencial: a cada ciclo, a `TUI` chama `render(width)` em cada componente, compara as linhas resultantes com o buffer das linhas anteriores (`previousLines`), e emite para o terminal **apenas as linhas que mudaram**. Linhas idênticas não geram nenhum byte de saída. Quando o conteúdo encolhe (ex: um spinner que some ao fim da tool call), as linhas excedentes são explicitamente apagadas via ANSI — sem que o cursor precise voltar ao topo e redesenhar tudo.

Para eliminar o artefato visual de linhas intermediárias aparecendo enquanto o diff é gravado, o pi-tui envolve cada ciclo de atualização nas sequências `CSI ?2026h` / `CSI ?2026l` — o protocolo de "synchronized output" (DEC mode 2026). A ideia é simples: `?2026h` instrui o terminal a acumular todo output sem pintar nada; `?2026l` libera o buffer de uma vez. O resultado é que o usuário enxerga o estado final de cada frame, nunca o estado parcial. Terminais modernos (kitty, ghostty, iTerm2, versões recentes de Terminal.app e Windows Terminal) suportam o DEC 2026; terminais sem suporte ignoram as sequências sem quebrar nada — o rendering apenas perde a garantia de atomicidade, mas não trava.

O componente de editor multi-linha (classe `Editor`) é quem traduz input de teclado em texto estruturado. Ele não usa readline — implementa diretamente: navegação por grafema via `Intl.Segmenter` (o que dá suporte correto a emojis e caracteres wide de CJK), kill ring no estilo Emacs (`Ctrl+K` mata até fim de linha, `Ctrl+Y` cola o último kill), undo stack com coalescing de inserções consecutivas (não empilha um undo por caractere digitado), e "paste markers" para blocos colados grandes (o bloco vira `[paste #1 +12 lines]`, um objeto atômico que o cursor pula inteiro em vez de navegar linha por linha). O Shift+Enter cria nova linha sem submeter; Enter submete o prompt.

Para input de teclado preciso, o editor detecta suporte ao Kitty keyboard protocol (CSI-u sequences) e o ativa quando disponível. Sem ele, Esc e Alt+tecla compartilham a mesma sequência de bytes no terminal; com o protocolo, cada tecla (incluindo modificadores e eventos de key-release distintos de key-press) chega com identificação unívoca. Isso é o que torna possível distinções como Shift+Enter sem ambiguidade.

O autocomplete opera sobre dois namespaces: `/` para slash commands (`/model`, `/resume`, `/fork`, `/settings`, `/tree`) e `@` para caminhos de arquivo. Para os caminhos, o `CombinedAutocompleteProvider` chama `fd` (o binário de busca de arquivos com `.gitignore`-awareness) para listar candidatos, aplica fuzzy matching e apresenta sugestões no terminal em tempo real. Syntax highlighting no editor é rendering por componente — cada linha do `Editor` é renderizada com ANSI colors de acordo com o tipo de conteúdo (código dentro de backticks, paths, etc.).

Toda essa superfície — frame diff, synchronized output, Kitty protocol, kill ring, autocomplete via `fd` — é código que assume que `process.stdout` tem propriedades de terminal: suporta ANSI, tem dimensões acessíveis via `process.stdout.columns`/`rows`, e responde a sequências de controle de cursor. É precisamente esse conjunto de pressupostos que o conceito seguinte vai desmontar ao definir o que é um TTY e o que acontece quando ele não está presente.

**Fontes utilizadas:**

- [Editor and Input Components — DeepWiki agentic-dev-io/pi-agent](https://deepwiki.com/agentic-dev-io/pi-agent/4.2-editor-and-input-components)
- [pi-tui Terminal UI Library — DeepWiki badlogic/pi-mono](https://deepwiki.com/badlogic/pi-mono/5-pi-tui:-terminal-ui-library)
- [Terminal User Interface (pi-tui) — DeepWiki agentic-dev-io/pi-agent](https://deepwiki.com/agentic-dev-io/pi-agent/4-terminal-user-interface-(pi-tui))
- [@mariozechner/pi-tui — npm](https://www.npmjs.com/package/@mariozechner/pi-tui)
- [Build your own Command Line with ANSI escape codes — Li Haoyi](https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html)
- [What I learned building an opinionated and minimal coding agent — Mario Zechner](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)

## 3. O que é um TTY e por que o modo TUI depende dele — a relação entre `tty.isatty()`/`process.stdout.isTTY`, controle ANSI, e a superfície de terminal que o rendering diferencial e o editor precisam para funcionar

TTY é a abreviação de TeleTYpe — os teletipos eletromecânicos do século XX que eventualmente viraram terminais de vídeo e, depois, emuladores de terminal em software. O que persiste do nome é o conceito: um TTY é um arquivo de dispositivo (`/dev/pts/N` num pseudoterminal moderno) que funciona como canal bidirecional entre o processo e um usuário humano, mediado por uma camada de kernel chamada *line discipline*. Essa camada interpreta caracteres especiais (Backspace, Ctrl+C, Ctrl+Z), controla o fluxo de bytes, e expõe as dimensões do terminal (colunas × linhas) via `ioctl`. Quando um processo escreve bytes para esse arquivo e quem está na outra ponta é um terminal emulator, as sequências ANSI são interpretadas como comandos de cursor; quando quem está na outra ponta é um pipe ou um arquivo de log, os mesmos bytes chegam como texto literal — lixo no log, bytes corretos no terminal.

A verificação de presença de TTY é a primeira coisa que qualquer aplicação de linha de comando precisa fazer antes de emitir sequências de controle. No kernel Unix, a syscall `isatty(fd)` chama `ioctl(fd, TCGETS, ...)` internamente: se o file descriptor está associado a um TTY, o `ioctl` responde com os atributos do terminal; se não, retorna `ENOTTY`. Em Node.js isso vira `tty.isatty(fd)` na camada de módulo ou `process.stdout.isTTY` como propriedade de conveniência já calculada pelo runtime — `true` quando stdout está conectado a um TTY, `undefined` quando está redirecionado para pipe, arquivo ou `/dev/null`.

A distinção entre os dois casos não é cosmética. Quando `process.stdout.isTTY` é `true`, o objeto `process.stdout` é uma instância de `tty.WriteStream` — uma classe que herda de `net.Socket` mas expõe métodos adicionais: `clearLine()`, `cursorTo(x, y)`, `moveCursor(dx, dy)`, `getWindowSize()`, e o evento `resize` emitido sempre que o usuário redimensiona a janela do terminal. Esses métodos existem apenas em instâncias de `tty.WriteStream`; num stdout não-TTY, o objeto retorna ao tipo base e nenhum desses métodos opera — chamá-los produz no-op ou erro. Da mesma forma, `process.stdin.isTTY` diz se o stdin é um `tty.ReadStream`, que expõe `setRawMode(true)` — o que desativa o processamento de linha do kernel e entrega cada byte de teclado diretamente ao processo, sem buffer de linha, sem eco automático.

O rendering diferencial do `## 2.` depende exatamente desta superfície. `clearLine()` e `moveCursor()` são as primitivas que permitem ao motor de diff apagar linhas obsoletas e posicionar o cursor para sobrescrever só as linhas modificadas — sem elas, a única saída possível é `console.log`, que avança o scroll e não permite reescrita no lugar. O evento `resize` alimenta o recálculo de `width` que os componentes da TUI usam em cada chamada de `render(width)`. O `setRawMode(true)` no stdin é o que permite ao `Editor` receber teclas individuais (Tab, Shift+Enter, Ctrl+K) sem que o kernel as absorva na linha de edição própria dele. O `process.stdout.columns`/`rows` — acessíveis apenas em TTY — é o que determina o tamanho do viewport para o layout do footer e para o wrapping das respostas do modelo.

Em síntese, o modo TUI do pi.dev não usa TTY como preferência estética — ele requer `process.stdout.isTTY === true` porque cada primitiva que os conceitos `## 1.` e `## 2.` descreveram (`render`, `clearLine`, `moveCursor`, `setRawMode`, `resize`, `columns`) só existe quando esse file descriptor está conectado a um pseudoterminal real. O conceito seguinte mostra o que acontece na prática quando nenhum desses pressupostos se cumpre — o comportamento do harness sem TTY.

**Fontes utilizadas:**

- [TTY | Node.js v22 Documentation](https://nodejs.org/api/tty.html)
- [The TTY demystified — Linus Åkesson](https://www.linusakesson.net/programming/tty/)
- [What do PTY and TTY Mean? — Baeldung on Linux](https://www.baeldung.com/linux/pty-vs-tty)
- [Linux terminals, tty, pty and shell — DEV Community](https://dev.to/napicella/linux-terminals-tty-pty-and-shell-192e)
- [Pseudoterminal — Wikipedia](https://en.wikipedia.org/wiki/Pseudoterminal)

<!-- AULAS-END -->

## 5. Por que Lambda e Fargate não fornecem TTY — como esses runtimes servem processos sem terminal anexado (I/O redirecionado, sem alocação de pty), tornando o modo TUI impossível de instanciar

O `## 4.` descreveu o que acontece quando um processo que depende de TTY roda sem ele — crash por `TypeError`, hang no event loop, ou saída silenciosa. O que falta explicar é por que Lambda e Fargate produzem esse estado estruturalmente, não por acidente de configuração.

No Lambda, o runtime não cria nenhum pseudoterminal. A inspeção de `/proc/1/fd` dentro de um ambiente Lambda ativo revela exatamente:

```
0 -> socket:[...]    # stdin
1 -> pipe:[...]      # stdout
2 -> pipe:[...]      # stderr
```

Stdin é um socket — o canal pelo qual o serviço de controle do Lambda entrega o payload do evento ao processo. Stdout e stderr são pipes capturados pelo wrapper do runtime Node.js, que intercepta as escritas e as encaminha para o `lambda_runtime.log_bytes()` antes de enviá-las ao CloudWatch. Nenhum dos três file descriptors passa pelo teste `isatty(fd)` — todos retornam `ENOTTY` porque nenhum está associado a um dispositivo `/dev/pts`. Consequentemente, `process.stdout.isTTY` é `undefined` e `process.stdin.isTTY` é `undefined` em qualquer função Node.js executada no Lambda. Isso não é comportamento configurável — é a arquitetura de I/O que o serviço usa para capturar saída e entregar eventos.

No Fargate, o mecanismo é diferente mas o resultado é o mesmo. Um task Fargate executa um container Docker cujo processo principal tem stdout e stderr conectados aos pipes do daemon Docker, que os encaminha para o driver de logging configurado (CloudWatch, Firelens, etc.). O parâmetro `pseudoTerminal` na definição de container (`ContainerDefinition.pseudoTerminal` na API do ECS) controla se o daemon Docker executa `docker run --tty` ao criar o container — o que alocaria um PTY e faria `process.stdout.isTTY` retornar `true` dentro do processo. O valor padrão é `false`. Para uma task de workload headless — o que descreve qualquer handler de API Gateway — ninguém define `pseudoTerminal: true` porque o código não interage com usuário nenhum; nenhum humano está na outra ponta. Definir `pseudoTerminal: true` num container de produção sem processo que consuma o TTY seria anomalia de configuração, não solução.

A diferença entre Lambda e Fargate, neste ponto específico, é de grau: Lambda não expõe sequer a opção de alocar PTY (não existe parâmetro equivalente ao `pseudoTerminal` do ECS); Fargate expõe o parâmetro mas nenhuma arquitetura headless sensata o ativa. O resultado prático é idêntico — `process.stdout.isTTY === undefined`, `process.stdin.isTTY === undefined`, e todas as primitivas que os conceitos `## 1.` a `## 3.` descreveram (`setRawMode`, `clearLine`, `moveCursor`, `resize`, `columns`) ficam indisponíveis ou retornam no-op.

Há ainda um fator adicional no Fargate que reforça a impossibilidade: mesmo que alguém ativasse `pseudoTerminal: true` por engano, o container de uma task Fargate não é interativo por definição — não há sessão SSH, não há usuário digitando. O PTY seria alocado mas nunca consumido. O resultado seria um PTY fantasma num processo que nunca espera input humano, o que não resolve nada do ponto de vista do pi.dev (que precisa que o usuário esteja efetivamente presente para o modo TUI fazer sentido).

Para a POC deste livro, Lambda e Fargate são os dois candidatos de runtime discutidos no `04-lambda-ou-fargate-para-hospedar-pidev/`. Em ambos, o modo TUI é descartado pela mesma razão técnica que o `## 4.` formalizou: o harness lança `TypeError` ou trava no event loop sem TTY. O subcapítulo `05-o-subset-que-importa-para-a-poc-headless/` vai usar exatamente esse raciocínio — Lambda sem TTY, Fargate sem TTY por padrão — como argumento de eliminação do modo TUI antes de declarar as superfícies que a POC vai de fato usar.

**Fontes utilizadas:**

- [Reverse engineering AWS Lambda — Denial of Services](https://www.denialof.services/lambda/)
- [ContainerDefinition — Amazon ECS API Reference (pseudoTerminal)](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_ContainerDefinition.html)
- [Amazon ECS task definition parameters for Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html)
- [NEW – Using Amazon ECS Exec to access your containers on AWS Fargate and Amazon EC2](https://aws.amazon.com/blogs/containers/new-using-amazon-ecs-exec-access-your-containers-fargate-ec2/)
- [The Interactive and TTY Options in docker run — Baeldung on Linux](https://www.baeldung.com/linux/docker-run-interactive-tty-options)
- [TTY | Node.js Documentation](https://nodejs.org/api/tty.html)

## 6. Quando o TUI ainda é útil no contexto desta POC — o papel do modo TUI em desenvolvimento local (debugging de prompts e tools, exploração de comportamento do agente) antes de subir para AWS, e o limite claro onde ele para de servir

Os conceitos `## 4.` e `## 5.` fecharam o argumento de eliminação: sem TTY, o modo TUI crash, trava, ou sai silenciosamente — e Lambda e Fargate nunca fornecem TTY por padrão. Dito isso, o modo TUI não desaparece do ciclo de vida desta POC; ele só muda de papel. Antes de qualquer deploy na AWS, há uma fase de desenvolvimento local onde o TUI é a ferramenta certa.

O caso de uso central é **iterar sobre o comportamento do agente antes de comprometer com uma superfície headless**. Quando você está ajustando um system prompt, testando se uma skill responde como esperado, ou verificando se o agente usa corretamente uma tool que você adicionou, o TUI oferece o que nenhum modo headless oferece: feedback visual em tempo real de cada tool call emitido, o texto do modelo chegando token a token, e a possibilidade de mandar uma mensagem de steering ("pare e refaça assim") enquanto o agente ainda está em execução — o harness entrega a mensagem no fim do tool call corrente, antes de iniciar o próximo. Nenhum desses gestos existe no modo Print (que sai após uma resposta) nem no modo RPC/SDK (onde você é o processo controlador e precisa implementar tudo isso você mesmo).

O segundo caso de uso é **explorar o modelo de sessão em árvore antes de implementar a persistência**. O comando `/fork` cria uma nova sessão a partir de qualquer ponto do histórico, copiando o caminho ativo até aquele nó e abrindo o prompt pré-preenchido com a mensagem selecionada — o que permite testar variações de um prompt sem desperdiçar contexto na sessão principal. O `/tree` navega a árvore in-place, permitindo voltar a qualquer bifurcação anterior e retomar de lá. Para um engenheiro que ainda não entende visceralmente como sessões com `id`/`parentId` se comportam ao fazer fork — tema que o subcapítulo `02-o-modelo-de-sessao-como-arvore-jsonl/` aprofunda — brincar com `/fork` e `/tree` no TUI é a forma mais rápida de desenvolver o modelo mental correto antes de implementar a persistência no S3 ou EFS.

O terceiro caso de uso é **debugging de tools específicas que a POC vai usar**. Se você está construindo uma skill que o agente vai invocar como tool no Lambda, você a testa localmente no TUI primeiro: invoca o agente com a skill ativa, pede que ele use a tool, e observa ao vivo se o input/output está correto, se o harness serializa a resposta da forma esperada, e se o agente consegue continuar o raciocínio com o resultado. Só depois que a tool se comporta como esperado localmente é que faz sentido embutir o agente via SDK num handler e testar o fluxo headless.

O limite onde o TUI para de servir é preciso: no momento em que a sessão sai do seu terminal e entra num processo gerenciado pela AWS. Não há modo gradual — ou você tem TTY (desenvolvimento local) ou não tem (Lambda, Fargate). Não existe "TUI com degradação" nem "TUI remoto via SSH" que seja razoável para esta POC; qualquer tentativa de alocar um PTY no container Fargate e tunelar via ECS Exec seria mais complexidade do que simplesmente usar o SDK. A divisão é limpa: TUI para a fase de exploração e validação local, SDK ou RPC para a fase de produção headless.

Para a POC descrita neste livro, o fluxo prático é: (1) use o TUI para entender o comportamento do agente, afinar o system prompt, e validar as tools que vão entrar no handler; (2) descarte o TUI completamente quando começar a construir o handler Lambda ou Fargate — o `05-o-subset-que-importa-para-a-poc-headless/` vai formalizar exatamente quais superfícies (SDK e RPC) substituem o TUI nesse contexto, e por que cada uma delas não depende de TTY.

**Fontes utilizadas:**

- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [What I learned building an opinionated and minimal coding agent — Mario Zechner](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)
- [Session Management and Persistence — DeepWiki agentic-dev-io/pi-agent](https://deepwiki.com/agentic-dev-io/pi-agent/2.4-session-management-and-persistence)
- [pi.dev — site oficial](https://pi.dev/)

> _Pendente: 6 / 6 conceitos preenchidos._

---

**Próximo subcapítulo** → [Modo Print/JSON — Saída Determinística Para Scripts](../02-modo-print-json-saida-deterministica-para-scripts/CONTENT.md)
