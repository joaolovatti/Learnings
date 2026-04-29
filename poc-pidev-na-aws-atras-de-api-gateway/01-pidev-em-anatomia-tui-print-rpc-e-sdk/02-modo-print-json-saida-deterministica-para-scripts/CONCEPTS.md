# Conceitos: Modo Print/JSON — Saída Determinística Para Scripts

> _Aula contínua dos conceitos atômicos deste subcapítulo. Cada conceito vira uma seção `## N.` (ou `## 0N.` quando o roteiro tem 10+ conceitos) preenchida em sequência pela skill `estudo-explicar-conceito`. Cada nova iteração lê o que já foi escrito e dá continuidade — sem repetir vocabulário, sem reapresentar exemplos, sem saltos de tom._

## Roteiro

1. Invocação do modo Print — a flag `-p` e `--mode print`, o ciclo de vida do processo (inicia, processa, imprime, sai), e o que é escrito no stdout versus no stderr
2. O modo JSON como event stream JSONL — `--mode json` como saída única no stdout, o cabeçalho de sessão como primeira linha, e a convenção de framing LF-delimitado
3. Tipos de eventos emitidos em `--mode json` — agent/turn/message lifecycle events, tool execution events, queue_update e compaction: estrutura de cada tipo e sequência de emissão
4. Limitação de sessão única — por que cada invocação começa um contexto do zero, o que isso impede para conversas com memória entre turnos, e o contraste com o contrato que a POC precisa honrar
5. Uso legítimo em pipe e scripts — integração com `jq`, piped stdin (`cat | pi -p`), e os casos concretos onde a limitação de sessão não é obstáculo
6. Print/JSON como rampa de entrada para RPC — como os tipos de evento visíveis em `--mode json` reaparecem no modo RPC e por que entender essa estrutura aqui reduz a curva do subcapítulo seguinte

<!-- ROTEIRO-END -->

<!-- AULAS-START -->

## 1. Invocação do modo Print — a flag `-p` e `--mode print`, o ciclo de vida do processo (inicia, processa, imprime, sai), e o que é escrito no stdout versus no stderr

O modo Print resolve o problema que o TUI deixou em aberto para automação: como usar o pi.dev em um contexto onde não há usuário humano na outra ponta do terminal, mas a interação é de um único prompt. A flag `-p` é o atalho — `pi -p "seu prompt aqui"` — e `--mode print` é a forma longa equivalente. Ambas instruem o harness a não tentar instanciar o `InteractiveMode` nem verificar presença de TTY; o processo entra diretamente no `runPrintMode()`, processa o prompt, escreve a resposta no stdout, e sai.

O ciclo de vida completo tem quatro fases discretas. Na primeira, o processo inicializa o runtime Node.js, carrega o harness e as extensões configuradas, e detecta o modo de execução pela presença da flag. Na segunda, o `AgentSession` é criado e o prompt é enviado ao modelo — o mesmo `AgentSession` que o modo TUI e o SDK usam internamente, o que significa que o mesmo loop de tool calls, steering de prompt, e compaction automática de contexto acontecem aqui. Durante essa fase, o stdout fica em silêncio: não há streaming de tokens à medida que chegam, não há indicadores de progresso, não há output de tool calls intermediários. A terceira fase é a impressão: quando o agente conclui o último turno, o harness escreve o texto final da resposta no stdout e nada mais. A quarta fase é a saída: o processo chama `process.exit(0)` — ou deixa o event loop drenar naturalmente — e encerra com código zero em caso de sucesso, não-zero em caso de erro.

A separação stdout/stderr reflete a mesma convenção de qualquer utilitário Unix bem comportado: stdout carrega o dado que o invocador vai consumir programaticamente (o texto da resposta), enquanto stderr carrega o ruído diagnóstico (avisos de extensão, mensagens de log do harness, erros de inicialização). Versões recentes do harness tomaram o cuidado de redirecionar a saída de package managers e outras mensagens de startup para stderr durante a inicialização de modos não-interativos, para que stdout nunca contenha lixo antes da resposta — o que é um requisito não-negociável quando a saída vai ser consumida por um pipe.

Há uma nuance de processo que tem implicações práticas: o modo Print, quando extensões estão carregadas, pode deixar handles do event loop vivos após a resposta ser emitida — sockets de extensão, listeners de arquivo, timers — impedindo o Node.js de terminar organicamente. O harness corrige isso com uma chamada explícita a `process.exit()` após a resposta. Uma versão anterior desse comportamento gerou o issue #161 do repositório, onde o processo travava após a saída: o processo emitia a resposta mas não encerrava, exigindo Ctrl+C manual. A correção é exatamente um `process.exit()` no fim do `runPrintMode()`. Esse detalhe importa para quem testa o modo Print localmente e espera que o terminal retorne ao prompt: se o processo travar após a saída, a causa quase sempre é uma extensão carregada que mantém um listener ativo.

O contraste com o modo TUI do subcapítulo anterior é imediato: onde o TUI precisa de `setRawMode`, `clearLine`, `moveCursor` e TTY, o modo Print não toca nenhuma dessas primitivas. Ele usa apenas `process.stdout.write()` ou `console.log()` — APIs que funcionam tanto com um TTY conectado quanto com stdout redirecionado para um arquivo ou pipe. Essa indiferença ao tipo de file descriptor é o que torna o modo Print invocável em Lambda, Fargate, CI ou qualquer ambiente sem terminal.

**Fontes utilizadas:**

- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [Make `pi -p` show what it's doing (live output in print mode) · Issue #808 · badlogic/pi-mono](https://github.com/badlogic/pi-mono/issues/808)
- [Print mode (-p) does not exit after output · Issue #161 · badlogic/pi-mono](https://github.com/badlogic/pi-mono/issues/161)
- [pi -p (print mode) hangs when extensions are loaded · Issue #2677 · badlogic/pi-mono](https://github.com/badlogic/pi-mono/issues/2677)
- [pi-coding-agent: Coding Agent CLI — DeepWiki badlogic/pi-mono](https://deepwiki.com/badlogic/pi-mono/4-pi-coding-agent:-coding-agent-cli)

## 2. O modo JSON como event stream JSONL — `--mode json` como saída única no stdout, o cabeçalho de sessão como primeira linha, e a convenção de framing LF-delimitado

Onde o modo Print entrega apenas o texto final da resposta, `--mode json` expõe o processo inteiro: cada evento produzido pelo `AgentSession` durante a execução é serializado como um objeto JSON e escrito no stdout, um por linha, antes de o processo sair. A saída ainda é de uso único — a sessão não persiste entre invocações — mas agora o consumidor vê o fluxo interno completo ao invés de só o resultado.

O stdout começa com uma única linha de cabeçalho de sessão antes de qualquer evento de agente:

```json
{"type":"session","version":3,"id":"<uuid>","timestamp":"<ISO8601>","cwd":"/path/to/workdir"}
```

O campo `version` sinaliza a versão do protocolo — atualmente 3. O `id` é o identificador da sessão (o mesmo conceito de `id` que o modelo de sessão em árvore usará para rastrear ramificações, abordado em profundidade no capítulo 2). O `cwd` indica o diretório de trabalho no qual o processo foi iniciado. Essa linha de cabeçalho não é um evento de agente; ela é metadado estrutural que precede todos os outros eventos e permite a um consumidor identificar de qual sessão os eventos provêm sem depender de metadado externo ao stream.

O framing é JSONL puro: cada objeto JSON ocupa exatamente uma linha, terminada por LF (`\n`, U+000A). Nenhum evento contém literais de newline — qualquer newline dentro de strings é representado como `\n` escape. Isso significa que um consumidor pode delimitar registros com split simples em `\n` sem precisar de parser JSON incremental ou heurísticas de buffer. O parser do lado do consumidor lê até encontrar `\n`, sabe que tem um objeto completo, deserializa, e avança. A nota sobre não usar `readline` do Node.js — que separa também em separadores Unicode — aparece explicitamente na documentação do modo RPC, e vale registrar aqui porque o consumidor que testar com `--mode json` vai naturalmente migrar esse código para RPC depois; o hábito de usar `split('\n')` explícito em vez de `readline` segue para o próximo subcapítulo sem retrabalho.

A distinção entre `--mode print` e `--mode json` se resume ao que chega ao stdout: no print, o stdout recebe uma string de texto — a última `message_end` do agente destilada em prosa. No json, o stdout recebe o stream bruto de eventos que o modo print descartava. Todo o trabalho de renderização que o TUI faz visualmente (animações, tool call boxes, progress indicators) e que o modo Print suprime inteiramente está disponível aqui na forma de dados estruturados: cada `tool_execution_start` entrega nome e argumentos da ferramenta; cada `message_update` entrega o delta de token sendo gerado; cada `compaction_start` sinaliza que o contexto atingiu o limite e está sendo compactado automaticamente.

O contrato de saída resultante é: `2>/dev/null` no stderr suprime todo ruído de inicialização, e o stdout entrega um stream JSONL limpo que pode ser redirecionado para arquivo, pipado para `jq`, ou lido linha a linha por qualquer processo consumidor. Isso resolve o problema que faz com que o modo Print seja pouco útil para integração além do caso de uso mais simples: quando o invocador precisa saber se uma tool foi chamada, qual foi o custo de tokens, ou se houve retry, o modo Print é opaco — tudo isso está no modo JSON.

**Fontes utilizadas:**

- [pi.dev — JSON mode documentation](https://pi.dev/docs/latest/json)
- [pi-mono/packages/coding-agent/docs/json.md — documentação oficial do modo JSON](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/json.md)
- [JSON Lines specification — jsonlines.org](https://jsonlines.org/)
- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)

## 3. Tipos de eventos emitidos em `--mode json` — agent/turn/message lifecycle events, tool execution events, queue_update e compaction: estrutura de cada tipo e sequência de emissão

Ao receber a primeira linha JSONL de cabeçalho de sessão descrita no conceito anterior, o consumidor já sabe que o stream que virá a seguir é um conjunto de eventos tipados — cada um com um campo `type` discriminante e um payload específico. O modelo conceitual de pi.dev organiza esses eventos em quatro camadas aninhadas: o agente como contêiner mais externo, o turno como unidade de interação, a mensagem como unidade de chamada ao modelo, e a execução de ferramenta como operação atômica dentro de uma mensagem. Dois eventos transversais — `queue_update` e compaction — não se encaixam nessa hierarquia linear e aparecem quando o estado interno do harness muda de forma que o consumidor pode querer observar.

**Lifecycle do agente.** O primeiro evento após o cabeçalho de sessão é sempre `agent_start`:

```json
{"type":"agent_start"}
```

O último evento é `agent_end`, que carrega o histórico completo de mensagens processadas no campo `messages`:

```json
{"type":"agent_end","messages":[...]}
```

Entre esses dois, todo o resto do stream acontece. A simetria `agent_start`/`agent_end` delimita o escopo de uma invocação completa — o que não elimina a limitação de sessão única (cada `pi --mode json` é um novo `agent_start`), mas torna essa fronteira explícita no stream.

**Lifecycle do turno.** Dentro de uma invocação, pode haver múltiplos turnos se o agente precisar chamar ferramentas e retornar ao modelo com os resultados. Cada turno é delimitado por `turn_start` e `turn_end`:

```json
{"type":"turn_start"}
{"type":"turn_end","message":{"role":"assistant","content":[...]},"toolResults":[...]}
```

O campo `toolResults` em `turn_end` contém os resultados de todas as ferramentas executadas naquele turno — o que permite a um consumidor reconstruir o par (chamada → resultado) sem precisar correlacionar eventos de ferramenta individualmente.

**Lifecycle da mensagem.** Dentro de cada turno, o modelo produz uma mensagem. O stream de tokens chega como uma sequência `message_start` → N vezes `message_update` → `message_end`:

```json
{"type":"message_start","message":{"role":"assistant","content":[]}}
{"type":"message_update","message":{...},"assistantMessageEvent":{...}}
{"type":"message_end","message":{"role":"assistant","content":[{"type":"text","text":"resposta completa"}]}}
```

`message_update` chega uma vez por delta de token gerado pelo modelo — é o equivalente em stream de dados do que o TUI renderiza progressivamente na tela. O campo `assistantMessageEvent` dentro de `message_update` contém o delta bruto da API do modelo subjacente (Anthropic ou outro), o que significa que sua estrutura varia com o provider. Em `message_end`, o campo `message.content` já contém a resposta completa montada.

**Execução de ferramentas.** Quando o modelo emite uma tool call dentro de uma mensagem, o harness intercala eventos de ferramenta antes de continuar com o próximo `turn_start`:

```json
{"type":"tool_execution_start","toolCallId":"toolu_01...","toolName":"bash","args":{"command":"ls -la"}}
{"type":"tool_execution_update","toolCallId":"toolu_01...","toolName":"bash","args":{...},"partialResult":"..."}
{"type":"tool_execution_end","toolCallId":"toolu_01...","toolName":"bash","result":"total 12\n...","isError":false}
```

O `toolCallId` é o identificador gerado pelo modelo — o mesmo que aparece no objeto de tool call dentro da mensagem — e serve como chave de correlação entre os três eventos de uma mesma execução. `tool_execution_update` é emitido para ferramentas de execução longa que produzem saída progressiva (um shell command com stdout contínuo, por exemplo); ferramentas simples podem ir de `start` direto para `end` sem nenhum `update`. O campo `isError` em `tool_execution_end` sinaliza se o harness considerou a execução um erro — não se o processo que a ferramenta chamou retornou código não-zero, mas se o harness encapsulou o resultado como erro para enviar ao modelo.

**queue_update.** O harness mantém duas filas internas: `steering` (instruções de direcionamento que influenciam o comportamento do agente no próximo turno) e `followUp` (ações pendentes a executar após a resposta atual). `queue_update` é emitido sempre que uma dessas filas muda:

```json
{"type":"queue_update","steering":["foco no arquivo src/main.ts"],"followUp":[]}
```

Para o caso de uso de `--mode json` como ferramenta de inspeção e debug, esse evento é o que expõe a fila de steering em tempo real. Para o caso de uso de automação simples — consumir a resposta final e sair — `queue_update` pode ser ignorado sem perda de informação sobre o resultado.

**Compaction.** Quando o contexto ativo do modelo atinge o limiar configurado (por padrão, `contextTokens > contextWindow - 16384`), o harness dispara compaction automática. O stream sinaliza isso com dois eventos:

```json
{"type":"compaction_start","reason":"threshold"}
{"type":"compaction_end","reason":"threshold","result":{...},"aborted":false,"willRetry":false}
```

O campo `reason` pode ser `"threshold"` (automático por tamanho), `"overflow"` (contexto excedeu o máximo absoluto) ou `"manual"` (invocado via `/compact`). O campo `aborted` indica se a compaction foi interrompida antes de completar; `willRetry` indica se o harness tentará novamente. Para `--mode json` de sessão única com prompts curtos, compaction raramente aparece — mas sua presença no schema significa que um consumidor que processa o stream linha a linha precisa estar preparado para receber esses eventos sem quebrar.

A tabela abaixo consolida todos os tipos e seus campos principais:

| Tipo | Campos relevantes |
|---|---|
| `agent_start` | — |
| `agent_end` | `messages` |
| `turn_start` | — |
| `turn_end` | `message`, `toolResults` |
| `message_start` | `message` |
| `message_update` | `message`, `assistantMessageEvent` |
| `message_end` | `message` |
| `tool_execution_start` | `toolCallId`, `toolName`, `args` |
| `tool_execution_update` | `toolCallId`, `toolName`, `args`, `partialResult` |
| `tool_execution_end` | `toolCallId`, `toolName`, `result`, `isError` |
| `queue_update` | `steering`, `followUp` |
| `compaction_start` | `reason` |
| `compaction_end` | `reason`, `result`, `aborted`, `willRetry` |

Além desses, o harness pode emitir `auto_retry_start` e `auto_retry_end` quando a chamada ao modelo falha e o harness tenta novamente automaticamente — relevante para quem constrói consumidores que precisam distinguir "falha definitiva" de "retry em andamento". Esses dois tipos completam o schema público do stream JSONL de `--mode json`.

A sequência de emissão para um turno sem ferramentas é linear: `agent_start` → `turn_start` → `message_start` → [N × `message_update`] → `message_end` → `turn_end` → `agent_end`. Quando há tool calls, os eventos de ferramenta se intercalam entre `message_end` do turno que emitiu as chamadas e o `turn_start` do turno seguinte que recebe os resultados. Essa estrutura hierárquica e a reutilização do mesmo schema de tipos pelo modo RPC — que veremos em `03-modo-rpc-protocolo-jsonl-sobre-stdin-stdout` — é o motivo pelo qual o subcapítulo atual serve de rampa de entrada: quando o conceito 6 desta aula revisitar essa lista, os tipos já serão velhos conhecidos.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/json.md — documentação oficial do modo JSON](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/json.md)
- [pi.dev — JSON mode documentation](https://pi.dev/docs/latest/json)
- [pi-mono/packages/coding-agent/docs/compaction.md — documentação de compaction](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/compaction.md)

## 4. Limitação de sessão única — por que cada invocação começa um contexto do zero, o que isso impede para conversas com memória entre turnos, e o contraste com o contrato que a POC precisa honrar

O stream de eventos descrito nos três conceitos anteriores já revela o problema pelo que ele não contém: não há nenhum evento de "retomada de contexto anterior", não há referência a turnos de uma sessão prévia, não há mecanismo de handoff entre o processo que acaba de sair e o próximo que será iniciado. Cada invocação de `pi --mode print` ou `pi --mode json` cria um `AgentSession` do zero, envia o prompt, e encerra. O contexto de conversação — o histórico de mensagens que o modelo usa para dar coerência a respostas subsequentes — existe apenas na memória do processo durante aquela única execução.

Tecnicamente, o harness salva a sessão em disco por padrão: o JSONL de sessão é gravado em `~/.pi/agent/sessions/` ao final da execução, e os flags `--session <id>` e `-c` (continue most recent) permitem que uma invocação posterior carregue esse histórico antes de enviar o prompt. Isso funciona quando o mesmo processo ou a mesma máquina gerencia a sequência de chamadas e quando a localização do arquivo de sessão é conhecida e estável. No contexto de desenvolvimento local — um script de shell que encadeia múltiplos `pi -p` com `--session` — essa mecânica é usável. Há até um padrão documentado para agentes periódicos que acumulam contexto entre execuções, como um triage de emails que roda a cada hora no mesmo host.

A quebra acontece quando esse modelo é projetado sobre a arquitetura que a POC exige. Uma API multi-turno servindo N clientes simultâneos precisa que cada cliente tenha seu próprio contexto persistido de forma que qualquer instância de processamento — qualquer Lambda frio, qualquer container recém-iniciado — consiga retomar exatamente aquele contexto sem depender do disco local do processo anterior. Lambda não garante reutilização de container entre invocações; cada invocação fria começa com filesystem efêmero zerado. O `~/.pi/agent/sessions/` do processo que atendeu o turno anterior simplesmente não existe no container que atende o turno seguinte. Mesmo em Fargate com um único container de longa vida, a sessão do cliente A está no disco local de uma instância enquanto o cliente B, roteado para a mesma instância ou para uma diferente, não tem como garantir que seu contexto prévio esteja acessível sem infraestrutura adicional.

Há ainda um segundo problema anterior ao de storage: o mecanismo de retomada via `--session <id>` não compõe bem com automação de múltiplos clientes. O flag espera um UUID de sessão, que precisa ser armazenado externamente por quem gerencia a conversa — a API precisaria salvar o ID da sessão pi.dev e passá-lo de volta a cada nova invocação de processo. Não há endpoint HTTP, não há session handle que o harness exponha como artifact gerenciável por um terceiro. O harness foi projetado para um usuário que está à frente do terminal e sabe que quer `pi -c` (continuar o mais recente) ou `pi -r` (escolher de uma lista interativa). A issue #3416 do repositório documenta exatamente essa lacuna: automatizar sessões nomeadas a partir de contextos não-interativos não tem API pública limpa e força workarounds de scripting manual ou monkey-patching de extensões.

O contraste com o contrato da POC é direto. A POC precisa honrar: (a) N clientes independentes, cada um com seu histórico isolado; (b) estado preservado entre turnos — o cliente que mandou "como criar uma classe Python?" e depois manda "adicione type hints nisso" espera que o agente lembre a resposta anterior; (c) qualquer instância de compute na AWS pode atender qualquer turno de qualquer cliente sem coordenação manual de disco. O modo Print/JSON, mesmo com `--session`, honra no máximo (b) para um único cliente num único host estável. Não honra (a) sem múltiplas trilhas de sessão gerenciadas externamente, e não honra (c) sem redirecionar o storage de sessão para um backend compartilhado — que é exatamente o que os capítulos 8 e 9 abordam para os modos que a POC vai de fato adotar.

A raiz da limitação é arquitetural, não acidental: Print e JSON foram desenhados para o caso de uso de automação simples onde a unidade de trabalho é auto-contida. Um prompt que pede para gerar um relatório a partir de um arquivo, varrer um diretório, rodar testes e retornar o resultado — esses são trabalhos de sessão única sem memória inter-turno. Para esse padrão, Print/JSON é exatamente o modo certo, e a ausência de estado persistido entre invocações é uma característica, não um defeito. O problema surge apenas quando esse modo é avaliado para um endpoint conversacional — e reconhecer essa distinção é o que qualifica o descarte técnico de Print/JSON para a POC que estamos construindo.

**Fontes utilizadas:**

- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [Make `pi -p` show what it's doing (live output in print mode) · Issue #808 · badlogic/pi-mono](https://github.com/badlogic/pi-mono/issues/808)
- [Print mode (-p) does not exit after output · Issue #161 · badlogic/pi-mono](https://github.com/badlogic/pi-mono/issues/161)
- [pi -p (print mode) hangs when extensions are loaded · Issue #2677 · badlogic/pi-mono](https://github.com/badlogic/pi-mono/issues/2677)
- [pi-coding-agent: Coding Agent CLI — DeepWiki badlogic/pi-mono](https://deepwiki.com/badlogic/pi-mono/4-pi-coding-agent:-coding-agent-cli)
- [pi-mono/packages/coding-agent/docs/json.md — documentação oficial do modo JSON](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/json.md)
- [pi.dev — JSON mode documentation](https://pi.dev/docs/latest/json)
- [pi-mono/packages/coding-agent/docs/compaction.md — documentação de compaction](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/compaction.md)
- [Creating and resuming named sessions on launch · Issue #3416 · badlogic/pi-mono](https://github.com/badlogic/pi-mono/issues/3416)
- [Getting Started & CLI Reference — DeepWiki badlogic/pi-mono](https://deepwiki.com/badlogic/pi-mono/4.1-getting-started-and-cli-reference)
- [Pi integration architecture — OpenClaw](https://docs.openclaw.ai/pi)

## 5. Uso legítimo em pipe e scripts — integração com `jq`, piped stdin (`cat | pi -p`), e os casos concretos onde a limitação de sessão não é obstáculo

O conceito anterior terminou num diagnóstico de descarte: Print/JSON não serve para conversas multi-turno na POC. Esse diagnóstico é preciso, mas incompleto — há uma categoria inteira de trabalho real onde a limitação de sessão única não é um defeito, é exatamente o contrato certo. Entender esses casos distingue o descarte técnico fundamentado do preconceito.

O ponto de entrada mais direto é o piped stdin. Em modo Print, o harness detecta se o stdin tem dados disponíveis antes de montar o prompt: se sim, lê o stdin até EOF, concatena o conteúdo ao prompt passado via `-p`, e envia o conjunto ao modelo. O padrão canônico documentado é `cat README.md | pi -p "Summarize this text"` — o leitor de sistema de arquivos local vira trivialmente um pré-processador: `cat error.log | pi -p "Classifique cada linha como ERROR, WARN ou INFO e emita um JSON com contagens"`. O stdin pode ser qualquer coisa que chegue pelo pipe: saída de um `git diff HEAD~1`, stdout de um `kubectl logs`, resultado de um `curl` para uma API externa. O prompt via `-p` age como instrução de processamento, o stdin age como dados. A separação é intuitiva para quem já usa `awk`, `sed`, ou `jq` num pipe.

Há um detalhe de comportamento que importa para scripting: o harness não faz streaming de tokens enquanto processa em modo Print. O stdout fica em silêncio até o agente concluir o último turno, e então a resposta é emitida inteira de uma vez. Para um script que precisa do resultado antes de avançar, isso é exatamente o que se quer — não há necessidade de deserializar um stream incremental, não há race condition de buffer parcial, não há lógica de "esperar o próximo chunk". O próximo comando do pipe recebe uma string limpa que pode ser processada diretamente com `grep`, `awk`, ou passada como argumento para outro comando.

Para casos onde o resultado precisa de estrutura — não só texto livre — `--mode json` combinado com `jq` é a integração natural. O padrão documentado é:

```bash
pi --mode json "Liste os arquivos .ts no diretório src/" 2>/dev/null \
  | jq -c 'select(.type == "message_end") | .message.content[0].text'
```

O `2>/dev/null` silencia o stderr (logs de inicialização, avisos de extensão), deixando o stdout com o JSONL limpo. O `jq -c 'select(.type == "message_end")'` filtra o stream para o único evento que carrega a resposta final — descartando `agent_start`, os `message_update` intermediários, os eventos de ferramenta, e o `agent_end` com histórico completo. O `.message.content[0].text` extrai o texto da resposta. O resultado final é uma string JSON de uma linha, pronta para ser lida pelo próximo estágio do pipe.

Variações úteis do mesmo padrão: `select(.type == "tool_execution_end") | {tool: .toolName, result: .result}` para inspecionar o que cada ferramenta retornou; `select(.type == "agent_end") | .messages | length` para contar quantos turnos o agente precisou; `select(.type | startswith("tool_execution")) | .toolName` para um log sequencial de todas as ferramentas chamadas. A estrutura de eventos coberta no conceito 3 — com `toolCallId` como chave de correlação, `isError` como flag de resultado, `reason` em compaction — existe exatamente para ser consumida dessa forma programática.

Os casos concretos onde a limitação de sessão não é obstáculo compartilham um traço: a unidade de trabalho é **auto-contida por design**. Revisão de código de um diff: `git diff main HEAD | pi -p "Identifique possíveis regressões e emita como JSON com campos file, line, severity, description"`. Análise de log de CI que falhou: `cat test-output.xml | pi -p "Extraia os testes que falharam e agrupe por causa raiz"`. Geração de mensagem de commit: `git diff --cached | pi -p "Escreva uma mensagem de commit concisa no estilo Conventional Commits para esse diff"`. Nesses três casos, o prompt e o dado de entrada compõem o contexto completo — não há "lembrar o que foi dito no turno anterior" porque não há turno anterior. O processo inicia, processa um conjunto fechado de informação, e encerra. A ausência de estado persistido não é uma restrição, é o invariante que torna o trabalho paralelizável: cem diffs podem ser processados em cem invocações paralelas de `pi -p` sem nenhuma coordenação de sessão.

Há ainda um padrão menos óbvio: o pi invocando a si mesmo como sub-agente dentro de uma sessão TUI ou RPC. O harness permite que o agente execute `pi --print` via bash tool para delegar subtarefas auto-contidas — um agente de longa vida que está refatorando um módulo pode invocar `pi -p "Escreva testes unitários para essa função" --tools read` como um processo filho e incorporar o resultado na resposta principal. Aqui a limitação de sessão única do sub-agente é intencional: ele não precisa de contexto da sessão-pai; ele recebe tudo que precisa no prompt e retorna o resultado via stdout. O processo filho entra, processa, sai — exatamente o ciclo de vida do conceito 1.

O critério para decidir se Print/JSON é o modo certo é, portanto, uma pergunta sobre o contexto da tarefa: "o modelo precisa de algo que aconteceu em interações anteriores para executar essa tarefa?" Se a resposta for não — se o prompt mais os dados de entrada forem suficientes para um resultado útil — Print/JSON é o modo correto e a limitação de sessão é irrelevante. Se a resposta for sim — se o usuário espera que o agente se lembre do que disse na última mensagem — Print/JSON falha por design e RPC ou SDK são os candidatos. A POC que estamos construindo cai rigorosamente no segundo caso: a API precisa honrar contexto acumulado entre turnos de um mesmo cliente. Mas entender onde Print/JSON funciona bem é o que torna o descarte técnico inteligível em vez de dogmático.

**Fontes utilizadas:**

- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [pi.dev — Usage documentation](https://pi.dev/docs/latest/usage)
- [pi.dev — JSON mode documentation](https://pi.dev/docs/latest/json)
- [pi-mono/packages/coding-agent/docs/json.md — documentação oficial do modo JSON](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/json.md)
- [pi-coding-agent: Coding Agent CLI — DeepWiki badlogic/pi-mono](https://deepwiki.com/badlogic/pi-mono/4-pi-coding-agent:-coding-agent-cli)
- [What I learned building an opinionated and minimal coding agent — Mario Zechner](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)

<!-- AULAS-END -->

## 6. Print/JSON como rampa de entrada para RPC — como os tipos de evento visíveis em `--mode json` reaparecem no modo RPC e por que entender essa estrutura aqui reduz a curva do subcapítulo seguinte

O conceito anterior fechou com um critério de descarte: Print/JSON não serve para conversas com memória entre turnos porque cada invocação cria um contexto novo e o processo encerra. Essa conclusão abre uma pergunta imediata: o que o modo RPC faz de diferente que o habilita para esse caso de uso? A resposta está em duas mudanças fundamentais — o processo não encerra, e a comunicação passa a ser bidirecional — e essas mudanças são construídas sobre exatamente o mesmo schema de eventos que os conceitos 2 e 3 desta aula já detalharam.

No modo RPC (`pi --mode rpc`), o processo inicia, configura o `AgentSession`, e então entra num loop de escuta no stdin aguardando comandos JSONL. O processo permanece vivo indefinidamente — não há `process.exit()` ao fim de um prompt como existe no `runPrintMode()`. Cada prompt é enviado como um comando JSON pelo stdin: `{"type":"prompt","text":"sua mensagem aqui"}`. O harness processa, emite eventos no stdout durante a execução, e retorna ao estado de escuta aguardando o próximo comando. O contexto de conversação acumula no `AgentSession` que nunca foi destruído — o histórico de mensagens do primeiro turno está em memória quando o segundo turno chega.

O que o stdout emite durante cada turno em modo RPC é o mesmo stream JSONL descrito no conceito 3: `agent_start`, `turn_start`, `message_start`, N × `message_update`, `message_end`, `turn_end`, `agent_end`. Os campos `toolCallId`, `toolName`, `args`, `result`, `isError` nos eventos de ferramenta têm a mesma estrutura. O framing é o mesmo JSONL LF-delimitado do conceito 2, com a mesma ressalva sobre não usar o `readline` do Node.js. A única diferença de schema relevante no modo RPC é o campo `id` opcional nos comandos enviados pelo stdin: qualquer comando pode incluir `{"id":"req-42","type":"prompt",...}` e a resposta correspondente (`{"type":"response","command":"prompt","id":"req-42","success":true}`) ecoa o mesmo `id` — o que permite ao consumidor correlacionar qual resposta pertence a qual comando quando há comandos sendo enviados em rajada ou assincronamente. Esse mecanismo de correlação não existe no modo JSON porque não há stdin nem comandos — só há saída.

A equivalência de schema não é coincidência de implementação: o modo JSON e o modo RPC compartilham o mesmo `AgentSession` e o mesmo código de serialização de eventos. A diferença entre eles é de ciclo de vida do processo e de canal de entrada, não de vocabulário de eventos. Quem aprendeu a filtrar `select(.type == "message_end")` em `jq` para extrair a resposta final já sabe extrair a resposta final num consumidor de modo RPC. Quem entendeu que `tool_execution_end` com `isError: true` sinaliza erro de ferramenta já sabe interpretar esse mesmo sinal quando ele chega pelo stdout de um subprocesso RPC. A tabela de tipos do conceito 3 é o dicionário que serve aos dois modos.

O modo RPC acrescenta ao vocabulário dois grupos de eventos sem equivalente no modo JSON. O primeiro são as respostas de comando: `{"type":"response","command":"<nome>","success":true}` (ou `success: false` com `error`) confirma que o harness recebeu e processou um comando enviado via stdin. O segundo são os eventos de extensão de UI: quando uma extensão precisa de input do usuário — uma confirmação, uma seleção de opção, um texto livre — o harness emite `extension_ui_request` no stdout com um `id` e o consumidor deve responder via stdin com o mesmo `id`. Esse sub-protocolo não existe no modo JSON porque o modo JSON é unidirecional; e não existe no modo Print porque extensões de UI são descartadas ou ignoradas em contextos sem TTY. Para a POC, esse sub-protocolo é relevante apenas se as extensões instaladas fizerem chamadas de UI — no caso mais simples de um agente sem extensões interativas, esses eventos nunca aparecem.

O subcapítulo `03-modo-rpc-protocolo-jsonl-sobre-stdin-stdout` vai entrar no RPC com o vocabulário já estabelecido aqui: framing JSONL, tipos de eventos de lifecycle e ferramenta, correlação por `id`. O que ele precisará adicionar são os comandos do lado do stdin (`prompt`, `steer`, `follow_up`, `abort`, `new_session`, `get_messages`, `fork`), o gerenciamento do ciclo de vida do processo como subprocess de longa vida, e as implicações de processo vivo para persistência de sessão na AWS. A rampa que este subcapítulo entrega é real: não há reaprendizado de schema, só extensão do que já foi visto.

**Fontes utilizadas:**

- [RPC Mode — pi (hochej.github.io mirror)](https://hochej.github.io/pi-mono/coding-agent/rpc/)
- [pi-mono/packages/coding-agent/docs/rpc.md at main · badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/rpc.md)
- [pi-coding-agent: Coding Agent CLI — DeepWiki badlogic/pi-mono](https://deepwiki.com/badlogic/pi-mono/4-pi-coding-agent:-coding-agent-cli)
- [pi-mono/packages/coding-agent/docs/json.md — documentação oficial do modo JSON](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/json.md)

<!-- PENDENTE-START -->
> _Pendente: 6 / 6 conceitos preenchidos._
<!-- PENDENTE-END -->

---

**Próximo subcapítulo** → [Modo RPC — Protocolo JSONL Sobre stdin/stdout](../03-modo-rpc-protocolo-jsonl-sobre-stdin-stdout/CONTENT.md)
