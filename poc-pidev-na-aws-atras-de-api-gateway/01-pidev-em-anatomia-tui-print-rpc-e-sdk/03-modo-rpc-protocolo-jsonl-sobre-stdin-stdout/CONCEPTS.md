# Conceitos: Modo RPC — Protocolo JSONL Sobre stdin/stdout

> _Aula contínua dos conceitos atômicos deste subcapítulo. Cada conceito vira uma seção `## N.` (ou `## 0N.` quando o roteiro tem 10+ conceitos) preenchida em sequência pela skill `estudo-explicar-conceito`. Cada nova iteração lê o que já foi escrito e dá continuidade — sem repetir vocabulário, sem reapresentar exemplos, sem saltos de tom._

## Roteiro

1. O que é o modo RPC e como invocá-lo — a flag `--mode rpc`, o que muda em relação ao Print/JSON (processo persistente, stdin ativo, stdout como stream de eventos contínuos), e por que esse modelo é adequado para hosting de longa vida
2. Framing JSONL estrito — LF (`\n`) como único delimitador de registro, por que `\r\n` deve ser normalizado antes do parse, e o contrato que o servidor exige do cliente ao escrever comandos no stdin
3. A armadilha do `readline` do Node.js — como U+2028 e U+2029 (Unicode Line/Paragraph Separators) corrompem o framing quando se usa o módulo nativo `readline`, e qual alternativa de parsing é correta para clientes RPC
4. Tipos de eventos emitidos no stdout — agent/turn/message lifecycle events, streaming deltas (`text_delta`, `thinking_delta`, `toolcall_delta`), tool execution events (`tool_execution_start`, `tool_execution_update`, `tool_execution_end`), e eventos de sistema (`queue_update`, `compaction_start`/`end`, `auto_retry_start`/`end`)
5. Request/response correlation com o campo `id` — como o campo `id` opcional em cada comando faz o response espelhar o mesmo identificador, por que a correlação é necessária quando múltiplos comandos podem estar em flight, e o formato do objeto response (`type`, `command`, `success`, `error`, `data`, `id`)
6. Ciclo de vida do processo entre turnos — como o processo RPC persiste entre invocações do agente, como o caller envia o próximo turno via stdin sem reiniciar o processo, e como detectar e tratar a morte inesperada do processo
7. Aprovação de tool calls — o sub-protocolo de `extension_ui_request`/`extension_ui_response` para métodos de diálogo (`select`, `confirm`, `input`), a diferença entre métodos bloqueantes (que esperam response) e fire-and-forget (`notify`, `setStatus`), e a relevância desse mecanismo para ambientes controlados

<!-- ROTEIRO-END -->

<!-- PENDENTE-START -->
> _Pendente: 7 / 7 conceitos preenchidos._
<!-- PENDENTE-END -->

<!-- AULAS-START -->
## 1. O que é o modo RPC e como invocá-lo

Nos subcapítulos anteriores deste capítulo (`01-modo-tui` e `02-modo-print-json`) vimos dois extremos: o modo TUI, que exige TTY e é descartado em headless, e o Print/JSON, que nasce, processa um único prompt e morre. O problema com Print/JSON para uma POC multi-turno é que o processo não sobrevive entre chamadas — a sessão do agente precisa ser reconstruída do zero a cada invocação, o que inviabiliza manter contexto de conversa sem persistência externa. O modo RPC resolve exatamente isso: o processo fica vivo entre turnos.

A invocação mínima é:

```bash
pi --mode rpc
```

As flags mais relevantes para o contexto da POC são:

| Flag | Função |
|---|---|
| `--mode rpc` | Ativa o modo RPC; obrigatória |
| `--provider <name>` | Define o provedor de LLM (`anthropic`, `openai`, `google`, etc.) |
| `--model <pattern>` | Seleciona o modelo pelo identificador ou padrão |
| `--no-session` | Desabilita persistência de sessão em disco |
| `--session-dir <path>` | Diretório customizado para armazenar sessões |

A diferença estrutural em relação ao Print/JSON não está só na flag: é o modelo de execução inteiro que muda. No Print/JSON o processo responde e encerra — stdin é efêmero, stdout entrega a resposta e fecha. No RPC o processo bloqueia em `stdin` aguardando comandos indefinidamente. O stdout passa a ser um stream de eventos contínuos: à medida que o agente processa um prompt, eventos chegam em JSONL (um objeto JSON por linha), cobrindo fragmentos de texto, chamadas a tools, atualizações de status e conclusão de turno — sem fechar o pipe ao terminar.

A direção do fluxo de dados fica assim:

```
caller stdin  ──► [pi --mode rpc]  ──► caller stdout
  comandos JSON        processo             eventos JSON
  (um por linha)      persistente         (stream contínuo)
```

Essa assimetria — um comando entra e N eventos saem — é a consequência direta do fato de o agente ser iterativo por natureza: ele pode invocar múltiplas tools, emitir texto progressivo (streaming), e passar por compactação automática de contexto, tudo dentro de um único turno.

Por que esse modelo é adequado para hosting de longa vida, como um container Fargate que fica ativo aguardando requisições? Porque o custo de cold start do processo `pi` — carregar o runtime, restaurar sessão do disco, autenticar com o provedor de LLM — acontece uma única vez na inicialização do container, não em cada requisição. O handler da POC apenas escreve um comando no stdin do processo já em execução e consome os eventos do stdout. O capítulo 5 (`05-sdk-embedado-no-handler-vs-wrapping-de-processo-rpc`) vai comparar esse modelo com o SDK embedado em detalhe; por ora, o que importa registrar é que o modo RPC é a superfície que torna esse wrapping possível — é o que o capítulo 5 chama de "processo wrappado".

**Fontes utilizadas:**

- [RPC Mode — pi-mono docs (hochej mirror)](https://hochej.github.io/pi-mono/coding-agent/rpc/)
- [pi-mono/packages/coding-agent/docs/rpc.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/rpc.md)
- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)

## 2. Framing JSONL estrito

O stream de eventos que o processo RPC emite no stdout precisa ser parseado de forma confiável pelo caller — e o contrato de framing é o que torna isso possível. O pi.dev adota JSONL (JSON Lines) com uma restrição mais rígida do que a especificação pública do formato permite: o único delimitador de registro válido é `\n` (LF, U+000A). Cada objeto JSON — seja um evento emitido pelo processo ou um comando enviado pelo caller — ocupa exatamente uma linha, terminada por `\n` e sem nenhum caractere de nova linha interno não escapado.

Por que essa restrição é viável sem perder expressividade? Porque a especificação JSON (RFC 8259) proíbe que `\n` e `\r` apareçam literalmente dentro de strings — eles precisam ser escapados como `\n` e `\r`. Isso significa que um objeto JSON serializado em uma única linha nunca pode conter um LF real no meio do payload, tornando o LF um delimitador inequívoco: ao encontrar um byte 0x0A, o leitor sabe que o objeto terminou ali.

O problema com `\r\n` (CRLF) não é que o formato seja inválido em si — a especificação JSON Lines oficial aceita `\r\n` como alternativa, porque o `\r` antes do `\n` é descartado pelo parser JSON ao processar os limites do valor. O problema aparece no caminho entre o gerador e o parser: ambientes Windows, alguns wrappers de processo e pipes em modo texto podem converter `\n` em `\r\n` sem que o caller perceba. Se o parser espera dividir no `\n` mas recebe `\r\n`, o `\r` fica anexado ao fim do JSON antes do parse e pode quebrar o `JSON.parse` dependendo da implementação — `JSON.parse('{"type":"prompt"}\r')` falha em vários runtimes porque `\r` não é whitespace JSON. A correção segura é normalizar antes do parse: sempre que o buffer terminar em `\r\n`, remover o `\r` antes de tentar deserializar a linha.

O contrato que o servidor RPC exige do caller ao escrever comandos no stdin é simétrico: um objeto JSON completo por linha, terminado por `\n`, com flush imediato após a escrita. O "flush imediato" é relevante porque o pipe entre caller e processo pode estar em modo buffered — escrever o JSON e não chamar `flush` (ou `write` de forma que drene o buffer) resulta em o processo RPC nunca receber o comando, ficando bloqueado em leitura enquanto o caller fica bloqueado esperando eventos. Em Node.js, `process.stdin` de um processo filho via `child_process.spawn` usa `Writable` com `write()` que drena automaticamente em pipes, mas em clientes Python com `subprocess.Popen`, `stdin.write()` sem `stdin.flush()` é a armadilha clássica.

```
stdin  (caller → processo)     stdout (processo → caller)
───────────────────────────    ─────────────────────────────────
{"type":"prompt","message":"X"}\n    {"type":"agent_start",...}\n
                                     {"type":"text_delta",...}\n
                                     {"type":"agent_end",...}\n
{"type":"get_state"}\n               {"type":"response","data":{...}}\n
```

O formato é simétrico no sentido de que ambos os lados usam JSONL puro — mas assimétrico no volume: um comando no stdin tipicamente dispara múltiplos eventos no stdout antes do evento final de conclusão do turno. Essa proporção 1:N é o que justifica o modelo de stream contínuo descrito no conceito anterior em vez de um protocolo de pares síncronos (um request → um response bloqueante). O conceito 5 vai detalhar como o campo `id` resolve a correlação quando múltiplos comandos estão em flight simultaneamente.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/rpc.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/rpc.md)
- [RPC Mode — pi-mono docs (hochej mirror)](https://hochej.github.io/pi-mono/coding-agent/rpc/)
- [JSON Lines — especificação oficial](https://jsonlines.org/)
- [RFC 8259 — The JavaScript Object Notation (JSON) Data Interchange Format](https://datatracker.ietf.org/doc/html/rfc8259)
- [JSONL Definition & Specification — JSONL.help](https://jsonl.help/definition/)
## 3. A armadilha do `readline` do Node.js

O conceito anterior estabeleceu que o único delimitador válido no protocolo RPC é U+000A (LF) e que o caller precisa normalizar `\r\n` antes do parse. A consequência prática disso é que a escolha da biblioteca de leitura importa tanto quanto o protocolo em si — e o módulo `readline` do Node.js, que parece o candidato natural para consumir linhas do stdout de um processo filho, é exatamente o que não usar.

O motivo está em ECMA-262 §11.3, que define a lista completa de terminadores de linha do JavaScript. Essa lista inclui `\n` (LF), `\r` (CR), `\r\n` (CRLF) e também dois caracteres que não são separadores ASCII: U+2028 (LINE SEPARATOR) e U+2029 (PARAGRAPH SEPARATOR). O módulo `readline` obedece a esse padrão da especificação — o que é correto do ponto de vista do JavaScript em geral, mas incorreto para o protocolo JSONL do RPC, que define LF como único delimitador válido.

O problema surge porque U+2028 e U+2029 são caracteres perfeitamente válidos dentro de strings JSON (RFC 8259 não os proíbe). `JSON.stringify` não os escapa. Isso significa que se o conteúdo de um campo de texto — a mensagem do usuário, um resultado de tool, um trecho da resposta do agente — contiver qualquer um desses caracteres, o `JSON.stringify` vai emiti-los literalmente na linha JSONL. O `readline` do Node.js vai então partir essa linha no meio, entregar dois fragmentos como se fossem dois registros separados, e o `JSON.parse` vai falhar no primeiro fragmento com `SyntaxError: Unexpected end of JSON input`. O evento que o caller esperava simplesmente desaparece; nenhum alerta chama atenção para o que aconteceu, porque do ponto de vista do `readline` ele estava se comportando corretamente.

Essa categoria de bug tem ocorrências documentadas em ferramentas do ecossistema: o Copilot CLI reportou crash no parser JSONL de sessões, o Anthropic claude-agent-sdk-typescript teve issue aberto sobre `readline`-based transport quebrando mensagens de ferramentas MCP que retornavam U+2028 em texto, e o anthropic-sdk-typescript registrou o mesmo padrão com output de tool results. Em todos os casos, a cadeia de causalidade é a mesma: `JSON.stringify` não escapa → `readline` parte no meio → `JSON.parse` falha.

A alternativa correta é acumular os bytes do stdout num buffer e fazer a busca por `\n` (LF, byte 0x0A) manualmente. A documentação oficial do protocolo RPC do pi.dev documenta exatamente esse padrão:

```javascript
const { StringDecoder } = require("string_decoder");

function attachJsonlReader(stream, onLine) {
    const decoder = new StringDecoder("utf8");
    let buffer = "";

    stream.on("data", (chunk) => {
        buffer += typeof chunk === "string" ? chunk : decoder.write(chunk);

        while (true) {
            const newlineIndex = buffer.indexOf("\n");
            if (newlineIndex === -1) break;

            let line = buffer.slice(0, newlineIndex);
            buffer = buffer.slice(newlineIndex + 1);
            if (line.endsWith("\r")) line = line.slice(0, -1);
            onLine(line);
        }
    });
}
```

Três decisões técnicas nesse padrão merecem atenção. Primeiro, `StringDecoder` garante que chunks de bytes não partam no meio de um codepoint UTF-8 multibyte — sem ele, um chunk que termina no meio de um caractere de 3 bytes geraria JSON inválido. Segundo, `buffer.indexOf("\n")` busca somente o byte 0x0A, sem qualquer lógica para U+2028 ou U+2029 — esses caracteres, quando presentes dentro de uma string JSON, passam transparentemente pelo parser sem causar divisão de linha. Terceiro, a normalização de `\r` é feita após encontrar o LF: se a linha termina em `\r\n`, o `\r` fica no fim do slice antes do LF e é removido com `endsWith("\r")`, preservando o comportamento correto tanto para ambientes Unix quanto Windows.

Para clientes escritos em Python, o risco não existe da mesma forma: o `subprocess.Popen` com `stdout=PIPE` e iteração `for line in proc.stdout` usa o modo texto do Python, cujo separador padrão é `\n` e não os Unicode separators do ECMA — `for line in proc.stdout` é seguro para o protocolo RPC. A armadilha é específica para clientes Node.js que recorrem ao `readline` por conveniência.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/rpc.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/rpc.md)
- [MCP Tool Result containing U+2028/U+2029 breaks JSON parsing · Issue #137 · anthropics/claude-agent-sdk-typescript](https://github.com/anthropics/claude-agent-sdk-typescript/issues/137)
- [U+2028 LINE SEPARATOR in MCP tool results causes JSON parsing failures · Issue #882 · anthropics/anthropic-sdk-typescript](https://github.com/anthropics/anthropic-sdk-typescript/issues/882)
- [Session JSONL parser crashes on U+2028/U+2029 · Issue #2607 · github/copilot-cli](https://github.com/github/copilot-cli/issues/2607)
- [readline: should handle all ECMAScript newline characters · Issue #5988 · nodejs/node-v0.x-archive](https://github.com/nodejs/node-v0.x-archive/issues/5988)
- [Subsume JSON — JSON ⊂ ECMAScript (ES2019 fix history) · V8 Blog](https://v8.dev/features/subsume-json)

## 4. Tipos de eventos emitidos no stdout

O conceito 2 estabeleceu que o stdout é um stream assimétrico: um comando no stdin dispara múltiplos eventos antes do sinal de conclusão. O conceito 3 mostrou como ler esse stream de forma confiável. O que falta é a taxonomia completa dos eventos — sem ela, o cliente RPC não sabe o que esperar nem quando o turno terminou.

O protocolo agrupa os eventos emitidos em quatro famílias.

**Ciclo de vida do agente e do turno.** `agent_start` é emitido quando o processo começa a processar um `prompt` e `agent_end` encerra o ciclo com o campo `messages` contendo toda a conversa acumulada até ali. Dentro de cada rodada do loop do agente há um par `turn_start` / `turn_end` — um turno abrange uma resposta do assistente mais todos os tool calls e resultados gerados antes de o agente pedir ao caller o próximo prompt. `turn_end` carrega `message` (a mensagem do assistente que fechou o turno) e `toolResults` (resultados das ferramentas). O `agent_end` por sua vez envolve os turn events: pode haver múltiplos turnos — cada vez que o agente invoca tools e retoma — antes de o `agent_end` ser emitido.

```
agent_start
  turn_start
    message_start
    message_update (text_delta, ...) × N
    message_end
    tool_execution_start × M
    tool_execution_update × K  (por tool)
    tool_execution_end × M
  turn_end
  [turn_start ... turn_end × ...] — se o agente continuar chamando tools
agent_end
```

**Streaming de mensagem (`message_update`).** `message_start` e `message_end` delimitam o objeto `AgentMessage` completo; os fragmentos chegam via `message_update`, que carrega dois campos: `message` (a mensagem parcial acumulada até o momento) e `assistantMessageEvent` (o delta de streaming). O `assistantMessageEvent.type` é o que o cliente consulta para saber o que está chegando:

| `assistantMessageEvent.type` | Significado |
|---|---|
| `start` | Início do bloco de conteúdo |
| `text_start` / `text_delta` / `text_end` | Fragmento de texto da resposta |
| `thinking_start` / `thinking_delta` / `thinking_end` | Fragmento do raciocínio interno (extended thinking) |
| `toolcall_start` / `toolcall_delta` / `toolcall_end` | Fragmento dos argumentos de uma tool call em construção |
| `done` | Geração encerrada; `stopReason` é `"stop"`, `"length"` ou `"toolUse"` |
| `error` | Geração interrompida; `reason` é `"aborted"` ou `"error"` |

O campo `contentIndex` identifica qual bloco de conteúdo da mensagem o delta pertence — relevante quando a mensagem tem múltiplos blocos intercalados (texto, thinking, tool call). O campo `partial` dentro do `assistantMessageEvent` acumula o estado do bloco até o momento, então o cliente pode optar por reconstruir a mensagem apenas desse campo, sem precisar concatenar deltas manualmente.

**Execução de tools.** `tool_execution_start` anuncia o início da execução com `toolCallId`, `toolName` e `args`. `tool_execution_update` entrega `partialResult` — e aqui há uma distinção importante: `partialResult` não é um delta incremental, é o resultado acumulado até o momento. O cliente deve substituir o estado exibido, não concatenar. `tool_execution_end` entrega o `result` final e o flag `isError`, que indica se a tool retornou um erro ao agente (distinto de uma falha técnica de execução). O `toolCallId` é o elo que correlaciona todos os três eventos — em rodadas com múltiplas tools rodando em paralelo, o cliente usa esse campo para parear cada update com o tool call correto (o conceito 5 vai detalhar como o campo `id` do comando resolve correlação no outro sentido, caller→processo).

**Eventos de sistema.** Três grupos operam fora do ciclo agente/turno/mensagem:

- `queue_update` é emitido sempre que a fila de `steering` ou `followUp` muda — os campos trazem os arrays completos atuais, não deltas. O cliente pode usar isso para atualizar qualquer indicador de "instruções pendentes" na UI.

- `compaction_start` / `compaction_end` sinaliza compactação automática ou manual do contexto. O campo `reason` em `compaction_start` é `"manual"`, `"threshold"` (limite de tokens configurado) ou `"overflow"` (janela de contexto do modelo estourou). Em `compaction_end`, `willRetry: true` indica que o turno que disparou a compactação por overflow será reexecutado automaticamente após a compactação — o caller não precisa reenviar o prompt.

- `auto_retry_start` / `auto_retry_end` sinaliza tentativas automáticas em erros transientes (rate limit, overloaded, 5xx). `auto_retry_start` traz `attempt`, `maxAttempts`, `delayMs` e `errorMessage`. `auto_retry_end` traz `success` e, em caso de falha definitiva, `finalError`.

Há ainda `extension_error`, emitido quando uma extension lança exceção em algum hook — carrega `extensionPath`, `event` (o hook que falhou) e `error`. Para a POC headless, extensions não são relevantes neste estágio, mas o evento aparece no stream e o cliente precisa ignorá-lo sem travar o parser.

Um cliente RPC mínimo só precisa processar três eventos para entregar a resposta ao usuário: `message_update` com `assistantMessageEvent.type === "text_delta"` (texto progressivo), `agent_end` (sinal de conclusão do turno) e `auto_retry_end` com `success: false` (falha definitiva para reportar erro). Os demais eventos são relevantes para UIs ricas, instrumentação e fluxos de aprovação — temas do subcapítulo `05-o-subset-que-importa-para-a-poc-headless` e do capítulo `05-sdk-embedado-no-handler-vs-wrapping-de-processo-rpc`.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/rpc.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/rpc.md)
- [RPC Mode — pi-mono docs (hochej mirror)](https://hochej.github.io/pi-mono/coding-agent/rpc/)
- [RPC Mode | badlogic/pi-mono | DeepWiki](https://deepwiki.com/badlogic/pi-mono/4.5-rpc-mode)
## 5. Request/response correlation com o campo `id`

O conceito 4 mostrou que um único comando `prompt` dispara uma sequência de muitos eventos no stdout — `agent_start`, múltiplos `message_update`, `agent_end` — antes de o processo voltar a aguardar o próximo comando no stdin. Enquanto esses eventos chegam, o caller pode ter necessidade de emitir outros comandos: cancelar o turno, consultar o estado atual da sessão via `get_state`, ou atualizar uma instrução de steering com `steer`. O problema que emerge é de identidade: no stream JSONL, todos os objetos chegam misturados na mesma sequência de linhas. Sem um mecanismo de correlação, o caller não consegue distinguir qual objeto `type: "response"` responde a qual comando que ele enviou.

O protocolo resolve isso com um campo `id` opcional em cada comando. Se o comando enviado pelo caller contém um `id`, o objeto de resposta que o processo RPC emite para aquele comando específico espelhará o mesmo `id` de volta. Sem `id`, a resposta é emitida sem o campo — o caller sabe que é uma resposta, mas não consegue amarrá-la a nenhum comando em particular sem rastrear manualmente a ordem de envio.

O formato do objeto `response` que o processo emite para todo comando é:

```json
{
  "type": "response",
  "command": "<nome-do-comando>",
  "success": true,
  "id": "<mesmo-id-do-comando>",
  "data": { }
}
```

Em caso de falha:

```json
{
  "type": "response",
  "command": "<nome-do-comando>",
  "success": false,
  "id": "<mesmo-id-do-comando>",
  "error": "<mensagem-de-erro>"
}
```

Os campos `id` e `error` são condicionais: `id` só aparece se o comando o incluiu; `error` só aparece quando `success` é `false`. O campo `data` carrega o payload específico do comando — para `get_state`, traz o objeto de estado da sessão; para `prompt`, está vazio porque o resultado do processamento chega via eventos, não via `data`.

Uma distinção crítica que o campo `command` torna visível: a resposta de um `prompt` (que confirma que o processo aceitou e enfileirou o prompt) chega **antes** do `agent_start` e de todos os eventos do turno. O `response` com `success: true` para um `prompt` não significa que o agente já respondeu — significa que o processo recebeu o comando e começou a processá-lo. A resposta do agente em si chega depois, via `agent_end` com o campo `messages`. Isso é importante para o design do caller: o timeout aguardando pelo `response` de um `prompt` deve ser curto (confirmação de enfileiramento); o timeout aguardando pelo `agent_end` deve refletir o tempo de processamento do LLM.

Quando múltiplos comandos podem estar em flight — por exemplo, o caller enviou um `prompt` e, antes de receber o `agent_end`, precisou chamar `get_state` para verificar se a sessão está em um estado esperado — o `id` é o que permite ao caller manter um mapa de promessas pendentes:

```javascript
const pending = new Map();

function sendCommand(proc, command) {
    return new Promise((resolve, reject) => {
        const id = crypto.randomUUID();
        pending.set(id, { resolve, reject });
        proc.stdin.write(JSON.stringify({ ...command, id }) + "\n");
    });
}

// No handler de linhas do stdout (o attachJsonlReader do conceito 3):
function onLine(line) {
    const obj = JSON.parse(line);
    if (obj.type === "response" && obj.id && pending.has(obj.id)) {
        const { resolve, reject } = pending.get(obj.id);
        pending.delete(obj.id);
        obj.success ? resolve(obj.data) : reject(new Error(obj.error));
    } else {
        // evento de ciclo de vida (agent_start, message_update, etc.)
        handleEvent(obj);
    }
}
```

O padrão de `Map` de promessas pendentes keyed por `id` é o mesmo usado em protocolos como Language Server Protocol (LSP) e JSON-RPC 2.0. A especificação JSON-RPC 2.0 exige que o servidor ecoe exatamente o mesmo `id` do request no response, e o protocolo do pi.dev segue a mesma semântica — o campo `id` é um passthrough opaco: o processo RPC não interpreta nem transforma o valor, apenas o copia. Isso significa que o caller pode usar UUIDs, inteiros incrementais ou qualquer string que facilite o debug.

O `id` não se limita à correlação caller→processo. O mecanismo aparece de forma simétricamente invertida no sub-protocolo de `extension_ui_request`, que será coberto no conceito 7: quando o agente precisa de interação do caller durante a execução de uma tool (aprovação, seleção, input de texto), ele emite um `extension_ui_request` com seu próprio `id` gerado pelo processo, e o caller deve responder com `extension_ui_response` incluindo esse mesmo `id`. Nesse caso, é o processo RPC que está aguardando a correlação — o fluxo é invertido, mas o contrato de espelhar o `id` é idêntico.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/rpc.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/rpc.md)
- [RPC Mode — pi-mono docs (hochej mirror)](https://hochej.github.io/pi-mono/coding-agent/rpc/)
- [JSON-RPC 2.0 Specification — jsonrpc.org](https://www.jsonrpc.org/specification)

## 6. Ciclo de vida do processo entre turnos

O conceito 5 tratou de como o caller correlaciona respostas a comandos usando o campo `id`. Para que essa correlação faça sentido em múltiplos turnos, o processo RPC precisa estar vivo durante toda a conversa — e a responsabilidade de mantê-lo assim recai inteiramente no caller.

O modelo é simples: um único `pi --mode rpc` é iniciado na abertura da sessão e permanece rodando enquanto houver conversação. O caller envia `prompt` via stdin, consome todos os eventos do stdout até o `agent_end`, e então envia o próximo `prompt` — sem reiniciar o processo, sem perder o histórico da conversa que o processo acumula em memória. O fluxo fica assim:

```
spawn pi --mode rpc
       │
       ├─► stdin: {"type":"prompt","message":"Olá"}\n
       │   stdout: agent_start ... message_update × N ... agent_end
       │
       ├─► stdin: {"type":"prompt","message":"Pode detalhar?"}\n
       │   stdout: agent_start ... message_update × N ... agent_end
       │
       └─► (caller encerra a sessão: fecha stdin ou mata o processo)
```

O ponto crítico que a issue #1721 do paperclipai/paperclip documenta é que **stdin nunca deve ser fechado entre turnos**. O processo RPC interpreta o fechamento do stdin como sinal de encerramento da sessão — não como pausa entre prompts — e encerra imediatamente, antes de processar qualquer resposta pendente. O padrão correto é escrever o prompt no stdin, manter a stream aberta, aguardar o `agent_end` no stdout, e só então decidir se envia o próximo prompt ou encerra a sessão.

Para encerrar a sessão de forma limpa, o caller fecha o stdin (`child.stdin.end()` em Node.js ou `proc.stdin.close()` em Python) e aguarda o processo sair naturalmente. O processo detecta o EOF no stdin e encerra. Para encerramento forçado, `child.kill()` ou envio de SIGTERM são adequados; a partir de determinadas versões do pi.dev, o SIGTERM dispara o evento `session_shutdown` nas extensions antes de sair, permitindo cleanup.

A detecção de morte inesperada do processo (crash, OOM, SIGKILL pelo container runtime) precisa ser tratada pelo caller de forma ativa. Em Node.js, o evento correto para monitorar não é `close` — que só dispara após todas as stdio streams terem sido drenadas — mas sim `exit`, que dispara assim que o processo termina independentemente do estado do pipe:

```javascript
const child = spawn("pi", ["--mode", "rpc"], { stdio: ["pipe", "pipe", "pipe"] });

child.on("exit", (code, signal) => {
    // processo morreu — code é null se terminou por signal
    handleProcessDeath(code, signal);
});

child.stdout.on("close", () => {
    // stdout fechou — pode ser consequência do exit acima
    // ou EOF do processo; aqui você para de processar eventos
    stopEventProcessing();
});
```

O evento `exit` chega antes de `close` e é o ponto certo para reagir à morte do processo. Em ambientes Lambda, a morte inesperada implica em recriar o processo na próxima invocação; em Fargate, o container é reiniciado pelo ECS scheduler. O capítulo `05-sdk-embedado-no-handler-vs-wrapping-de-processo-rpc` discute as implicações dessa fragilidade — process wrapping exige gerenciamento explícito de ciclo de vida que o SDK embedado abstrai — mas o contrato do protocolo é o que está aqui: um processo, um canal stdin/stdout aberto, N turnos, e fechamento explícito pelo caller quando a sessão termina.

Um ponto operacional relevante para a POC: o processo RPC não emite nenhum sinal de "pronto para receber comandos" ao inicializar. O caller pode começar a escrever o primeiro `prompt` assim que o processo é spawned — o processo lê do stdin de forma assíncrona e o bufferiza internamente enquanto o runtime ainda carrega. Na prática, o handshake informal é: caller escreve o primeiro prompt, o processo emite `agent_start` quando está pronto para processar. Se o processo morrer antes de emitir `agent_start`, o `exit` event detecta a falha.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/rpc.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/rpc.md)
- [RPC Mode — pi-mono docs (hochej mirror)](https://hochej.github.io/pi-mono/coding-agent/rpc/)
- [Pi adapter: RPC mode stdin closes immediately, causing empty agent responses · Issue #1721 · paperclipai/paperclip](https://github.com/paperclipai/paperclip/issues/1721)
- [Child process — Node.js documentation (exit vs close events)](https://nodejs.org/api/child_process.html)

## 7. Aprovação de tool calls

O conceito 5 apontou que o campo `id` aparece de forma invertida num sub-protocolo específico: quando o agente precisa de interação do caller durante a execução de uma tool, o processo RPC emite um `extension_ui_request` com um `id` próprio e aguarda a resposta do caller com o mesmo `id`. É esse sub-protocolo que este conceito detalha.

O mecanismo de aprovação de tool calls não está no núcleo do protocolo RPC — ele vive na camada de extensions. Uma extension se registra no hook `tool_call`, que o protocolo executa **antes** de a tool efetivamente rodar, com possibilidade de bloqueio. Quando a extension decide que aquela chamada precisa de autorização do caller (baseada no nome da tool, nos argumentos, ou em qualquer lógica customizada), ela invoca `ctx.ui.confirm()` ou `ctx.ui.select()`. Em RPC mode, `ctx.hasUI` é `true` — esses métodos de UI são funcionais porque o sub-protocolo `extension_ui_request`/`extension_ui_response` os implementa sobre o canal stdin/stdout existente. O agente pausa a execução da tool e emite um `extension_ui_request` no stdout; o processo RPC fica bloqueado aguardando que o caller escreva um `extension_ui_response` correspondente no stdin.

O contrato de identidade nesse sub-protocolo é simétrico ao descrito no conceito 5, mas com os papéis trocados: agora é o processo quem gera o `id` e o caller quem precisa espelhá-lo de volta. Sem o `id` correto na resposta, o processo não consegue parear a resposta com a chamada de UI que está bloqueada.

Os métodos de diálogo disponíveis, todos bloqueantes, são:

| Método | Campo principal de resposta | Comportamento de timeout |
|---|---|---|
| `select` | `value` (string da opção escolhida) | auto-resolve com `undefined` |
| `confirm` | `confirmed` (boolean) | auto-resolve com `false` |
| `input` | `value` (string livre digitada) | auto-resolve com `undefined` |
| `editor` | `value` (texto multi-linha editado) | auto-resolve com `undefined` |

O campo `timeout` (em milissegundos) é opcional nos requests de diálogo. Quando presente, o processo RPC gerencia o timer internamente e resolve automaticamente com o valor padrão se o caller não responder a tempo — o caller não precisa rastrear timers para esses requests. O cancelamento explícito é sinalizado com `cancelled: true` no response, o que resulta em `undefined` para select/input/editor e `false` para confirm.

O request de aprovação de tool call com `confirm` tem este formato:

```json
{
  "type": "extension_ui_request",
  "id": "uuid-gerado-pelo-processo",
  "method": "confirm",
  "title": "Permitir execução de rm -rf?",
  "message": "O agente está prestes a executar: rm -rf /tmp/build",
  "timeout": 30000
}
```

O caller responde no stdin:

```json
{"type": "extension_ui_response", "id": "uuid-gerado-pelo-processo", "confirmed": true}
```

Se o caller responder com `confirmed: false` ou `cancelled: true`, a extension recebe esse resultado do `ctx.ui.confirm()` e pode retornar `{ block: true, reason: "Usuário rejeitou" }` no hook `tool_call` — o que faz o agente registrar a rejeição e decidir o que fazer a seguir sem executar a tool.

Os métodos fire-and-forget (`notify`, `setStatus`, `setWidget`, `setTitle`, `set_editor_text`) seguem o mesmo formato de envelope — `type: "extension_ui_request"` com `id` e `method` — mas o processo RPC não aguarda nenhum `extension_ui_response`. O caller pode ignorar esses eventos completamente sem que o processo trave. Para a POC headless, todos os fire-and-forget são descartáveis: `setStatus` atualiza um indicador de status de UI inexistente, `setWidget` projeta um widget em terminal que não existe, e `notify` dispara uma notificação que não tem destinatário. O único que pode ter leve utilidade é `notify` com `notifyType: "warning"` ou `"error"`, que pode ser logado para diagnóstico, mas não é obrigatório.

A relevância do mecanismo para ambientes controlados — que o roteiro levanta explicitamente — vale ser pontuada com precisão. Em POC headless rodando em Fargate sem interação humana em tempo real, a aprovação interativa é incompatível com o modelo de resposta: o caller não tem humano disponível para responder um `extension_ui_request` durante o processamento. Há duas saídas. A primeira é não carregar nenhuma extension que invoque diálogos bloqueantes — o processo roda sem hooks de aprovação, e o handler RPC nunca vê um `extension_ui_request` bloqueante. A segunda é que o próprio caller implemente um "aprovador automático" que, ao receber um `extension_ui_request` do tipo `confirm`, responde imediatamente com `confirmed: true` (ou `false` baseado em regras estáticas), sem esperar input humano. Essa segunda abordagem serve quando a POC precisa de controle mínimo de quais tools o agente pode chamar — por exemplo, bloquear automaticamente todo `bash` com `rm -rf` — sem depender de um humano em loop. O subcapítulo `05-o-subset-que-importa-para-a-poc-headless` revisita quais partes do protocolo RPC entram de fato no handler da POC e o que pode ser descartado; a aprovação de tool calls, na maioria dos cenários de POC, cai na segunda categoria.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/rpc.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/rpc.md)
- [RPC Mode — pi-mono docs (hochej mirror)](https://hochej.github.io/pi-mono/coding-agent/rpc/)
- [pi-mono/packages/coding-agent/docs/extensions.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)
- [Extensions — pi-mono docs (hochej mirror)](https://hochej.github.io/pi-mono/coding-agent/extensions/)

<!-- AULAS-END -->

---

**Próximo subcapítulo** → [Modo SDK — Embedando Pi.dev em Node.js/TypeScript](../04-modo-sdk-embedando-pidev-em-nodejs-typescript/CONTENT.md)
