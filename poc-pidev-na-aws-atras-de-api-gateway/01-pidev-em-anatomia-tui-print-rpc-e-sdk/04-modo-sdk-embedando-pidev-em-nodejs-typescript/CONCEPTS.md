# Conceitos: Modo SDK — Embedando Pi.dev em Node.js/TypeScript

> _Aula contínua dos conceitos atômicos deste subcapítulo. Cada conceito vira uma seção `## N.` (ou `## 0N.` quando o roteiro tem 10+ conceitos) preenchida em sequência pela skill `estudo-explicar-conceito`. Cada nova iteração lê o que já foi escrito e dá continuidade — sem repetir vocabulário, sem reapresentar exemplos, sem saltos de tom._

## Roteiro

1. O SDK como biblioteca embedável — sem spawn de processo — a diferença fundamental entre importar `@mariozechner/pi-coding-agent` e invocar o processo CLI, e o que desaparece quando não há subprocesso
2. `createAgentSession` — a factory central e seus quatro parâmetros — `sessionManager`, `modelRegistry`, `authStorage`, `resourceLoader`: o que cada um faz, quais são obrigatórios, e o que a factory retorna
3. `AgentSession` e o método `prompt()` — enviando turnos e acumulando contexto — o objeto retornado, como `prompt(text)` funciona como `Promise<void>`, e o que significa que o contexto acumula em memória entre chamadas
4. `SessionManager` — os cinco modos de abertura e o que cada um implica para persistência — `inMemory()`, `create()`, `open()`, `continueRecent()`, `forkFrom()`, e onde o SessionManager customizado backed por S3 se encaixa
5. `ModelRegistry` e `AuthStorage` sem home directory — como o SDK resolve credenciais de modelo e autenticação, e o que muda em Lambda (`setRuntimeApiKey`, `inMemory()` para registry, caminho customizado de auth)
6. Loop de eventos via `subscribe()` — o que chega e como consumir — como o SDK emite `AgentSessionEvent` via subscribe/listener (não via readline de stdout), os tipos relevantes para o handler mínimo (`text_delta`, `tool_execution_*`, `agent_end`)
7. `ResourceLoader` — o que pode ser omitido no handler mínimo da POC — como extensions/skills/templates são carregados, o que acontece se `resourceLoader` for omitido em `createAgentSession`, e o que um handler básico pode ignorar sem quebrar

<!-- ROTEIRO-END -->

<!-- PENDENTE-START -->
> _Pendente: 7 / 7 conceitos preenchidos._
<!-- PENDENTE-END -->

<!-- AULAS-START -->

## 1. O SDK como biblioteca embedável — sem spawn de processo — a diferença fundamental entre importar `@mariozechner/pi-coding-agent` e invocar o processo CLI, e o que desaparece quando não há subprocesso

Nos subcapítulos `01` a `03` deste capítulo, o modelo de interação com o pi.dev foi sempre o mesmo: você invoca o binário `pi` como processo externo, e a comunicação acontece por pipes — stdin para comandos, stdout para eventos JSONL. No modo RPC esse modelo alcança sua expressão mais elaborada: o processo persiste entre turnos, o protocolo tem framing explícito, a correlação de resposta usa campo `id`, e o caller precisa lidar com morte de processo e reabertura. Tudo isso é o overhead necessário de qualquer integração baseada em subprocesso.

O SDK elimina esse overhead inteiramente. Ao invés de `child_process.spawn("pi", ["--mode", "rpc"])`, você faz:

```typescript
import { createAgentSession, SessionManager, AuthStorage, ModelRegistry } from "@mariozechner/pi-coding-agent";
```

Não há subprocesso. O harness do pi.dev — o `AgentSession`, o loop de tool calls, o gerenciamento de contexto, a compactação automática — roda **dentro do mesmo processo Node.js** que importou o pacote. A comunicação é chamada de função direta, não troca de bytes por pipe.

A lista do que desaparece é exata e não trivial:

| Presente no RPC | Ausente no SDK |
|---|---|
| Framing JSONL com LF-delimitado | Nenhum — objetos TypeScript diretos |
| Armadilha do `readline` com U+2028/U+2029 | Nenhum — não há stream de texto para parsear |
| Correlação de response com campo `id` | Nenhum — `Promise` já amarra request/response |
| Gerenciamento de ciclo de vida do subprocesso | Nenhum — o processo morre com o caller |
| Detecção de morte do processo (`child.on("exit")`) | Nenhum — a falha vira `rejected Promise` diretamente |
| Latência de IPC (pipes do SO) | Nenhum — chamada em-processo |
| Restrição de linguagem (só funciona de quem pode spawnar) | SDK específico para Node.js/TypeScript |

A documentação oficial coloca a recomendação sem ambiguidade: para quem está construindo em Node.js, use `AgentSession` diretamente via SDK — não spawne subprocesso. O modo RPC existe para callers em outra linguagem (Python, Go, qualquer processo que possa ler/escrever pipes) ou quando isolamento de processo é uma exigência explícita de segurança ou de robustez (uma crash do agente não derruba o caller). Para Node.js sem essas restrições, o SDK é o caminho direto.

O que o SDK **não** muda é o modelo conceitual do agente: o mesmo `AgentSession` que o modo RPC gerencia por dentro — com suas sessões JSONL, tool calls, compactação, events — é exatamente o objeto que o SDK expõe. A diferença é de fronteira de acesso, não de comportamento. O conceito `## 2.` detalha como instanciar esse `AgentSession` via `createAgentSession` e quais parâmetros esse objeto exige.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/sdk.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [RPC Mode — pi (hochej.github.io mirror)](https://hochej.github.io/pi-mono/coding-agent/rpc/)
- [@mariozechner/pi-coding-agent — npm](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)
- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)


## 2. `createAgentSession` — a factory central e seus quatro parâmetros — `sessionManager`, `modelRegistry`, `authStorage`, `resourceLoader`: o que cada um faz, quais são obrigatórios, e o que a factory retorna

`createAgentSession` é a função assíncrona que instancia um `AgentSession` pronto para uso. A chamada mínima funciona sem nenhum argumento — o SDK usa defaults internos para todos os parâmetros — mas na prática uma POC em Lambda precisa controlar explicitamente pelo menos três dos quatro parâmetros do roteiro para não depender do filesystem local do container.

A assinatura resumida:

```typescript
const { session } = await createAgentSession({
  sessionManager?: SessionManager,   // como a sessão é persistida
  authStorage?: AuthStorage,         // onde ficam as credenciais de API
  modelRegistry?: ModelRegistry,     // quais modelos estão disponíveis
  resourceLoader?: ResourceLoader,   // extensions, skills, templates
  model?: string,                    // override do modelo padrão
  tools?: string[],                  // subset de ferramentas a habilitar
  cwd?: string,                      // diretório de trabalho do agente
});
```

Todos os parâmetros são opcionais. Quando omitidos, o SDK usa `DefaultResourceLoader`, que tenta descobrir recursos a partir do `cwd` e do diretório `~/.pi/agent/` — comportamento adequado para desenvolvimento local, problemático em Lambda onde `~` pode não existir ou não estar gravável. Por isso a omissão de parâmetros é uma escolha de desenvolvimento local, não de produção.

O papel de cada parâmetro relevante para a POC:

**`sessionManager`** — determina onde e como o histórico da conversa é gravado. Controla se a sessão sobrevive ao encerramento do handler ou se é descartada. Os cinco modos são o tema do conceito `## 4.`; o que importa aqui é que ele é o único parâmetro diretamente responsável pela persistência multi-turno que a POC precisa honrar.

**`authStorage`** — encapsula o arquivo `auth.json` onde as chaves de API dos provedores de LLM são armazenadas. Por padrão aponta para `~/.pi/agent/auth.json`. Em Lambda, onde `~` é `/root` e pode não existir ou ser somente leitura dependendo da imagem base, o `AuthStorage` precisa ser configurado com caminho explícito ou com chave injetada em runtime via `setRuntimeApiKey()`. O conceito `## 5.` detalha isso.

**`modelRegistry`** — carrega a lista de modelos disponíveis, que por padrão inclui os modelos built-in do pi.dev e pode ser estendida com arquivo customizado. Em ambiente sem disco configurado, `ModelRegistry.inMemory(authStorage)` usa só os modelos built-in sem tentar ler `~/.pi/agent/models.json`. O conceito `## 5.` cobre a configuração específica para Lambda.

**`resourceLoader`** — define onde o harness busca extensions, skills, prompt templates e context files. Quando omitido, o SDK instancia um `DefaultResourceLoader` que descobre recursos a partir do `cwd`. Para a POC sem extensions customizadas, omitir ou passar um loader vazio é o caminho válido. O conceito `## 7.` detalha o que pode ser omitido sem quebrar o comportamento básico do agente.

O retorno de `createAgentSession` é um objeto com pelo menos a propriedade `session` — o `AgentSession` que o conceito `## 3.` descreve. O pattern de desestruturação `const { session } = await createAgentSession(...)` é a forma idiomática na documentação oficial e nos exemplos do OpenClaw. A razão para o wrapper (retornar `{ session }` em vez de retornar o `AgentSession` diretamente) é que a factory pode retornar metadados adicionais de inicialização no mesmo objeto sem quebrar a API existente.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/sdk.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [How to Build a Custom Agent Framework with PI — Nader Dabit (gist)](https://gist.github.com/dabit3/e97dbfe71298b1df4d36542aceb5f158)
- [Pi integration architecture — OpenClaw docs](https://docs.openclaw.ai/pi)
- [@mariozechner/pi-coding-agent — npm](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)


## 3. `AgentSession` e o método `prompt()` — enviando turnos e acumulando contexto — o objeto retornado, como `prompt(text)` funciona como `Promise<void>`, e o que significa que o contexto acumula em memória entre chamadas

`createAgentSession` retorna `{ session }` onde `session` é um `AgentSession` — o objeto com o qual toda interação subsequente acontece. A interface expõe o método central:

```typescript
session.prompt(text: string, options?: PromptOptions): Promise<void>
```

O `Promise<void>` é deliberado: o resultado textual do agente não volta como valor de retorno da Promise. Ele chega via eventos emitidos pelo `subscribe()` durante a execução — conceito `## 6.` cobre isso. `prompt()` resolve quando o agente **completou o turno inteiro** — incluindo todos os tool calls intermediários, retries automáticos e compactação de contexto que possam ter ocorrido. A Promise rejeita se o agente não conseguir completar o turno por erro irrecuperável.

O acúmulo de contexto entre chamadas é a propriedade que distingue o `AgentSession` de uma chamada stateless ao LLM. Cada vez que `session.prompt()` completa, o `AgentSession` registra internamente a mensagem do usuário e a resposta do assistente (incluindo os resultados de tool calls) no histórico da sessão. A próxima chamada a `session.prompt()` entrega esse histórico completo ao modelo como contexto — o modelo "lembra" o que foi dito antes.

O histórico acumulado é acessível via `session.messages: AgentMessage[]` — um array das mensagens trocadas até o momento. Essa propriedade é a mesma que aparece no campo `messages` do evento `agent_end` no modo RPC: o `AgentSession` é a estrutura interna que os modos RPC e TUI usam por baixo, e o SDK simplesmente a expõe diretamente.

Onde esse estado vive fisicamente depende do `SessionManager` passado para `createAgentSession`. Com `SessionManager.inMemory()`, o histórico existe exclusivamente em memória — quando o `AgentSession` é descartado (o handler Lambda termina, o objeto é garbage-collected), o contexto desaparece. Com um `SessionManager` backed por arquivo ou S3, cada chamada a `prompt()` que completa com sucesso persiste o novo estado da sessão no storage configurado, de modo que um `AgentSession` criado numa invocação futura com o mesmo session ID começa com todo o histórico intacto. A escolha entre esses modos é o tema do conceito `## 4.`.

O `AgentSession` também expõe `session.sessionId: string` — o identificador único da sessão que o caller precisa armazenar externamente para associar turnos futuros ao mesmo contexto. Em termos práticos para a POC: quando o cliente HTTP envia um turno, o handler lê o `sessionId` do request (ou cria um novo), reconstrói o `AgentSession` com o `SessionManager` apontando para o storage daquela sessão, chama `session.prompt(texto)`, aguarda a Promise, e devolve os eventos coletados via `subscribe()`.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/sdk.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [pi.dev — SDK documentation](https://pi.dev/docs/latest/sdk)
- [@mariozechner/pi-coding-agent — npm](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)
- [Pi integration architecture — OpenClaw docs](https://docs.openclaw.ai/pi)


## 4. `SessionManager` — os cinco modos de abertura e o que cada um implica para persistência — `inMemory()`, `create()`, `open()`, `continueRecent()`, `forkFrom()`, e onde o SessionManager customizado backed por S3 se encaixa

O `SessionManager` é o objeto que o `AgentSession` usa para gravar e ler o histórico da sessão. Cada vez que `session.prompt()` completa um turno, o `AgentSession` chama o `SessionManager` ativo para persistir o novo estado. O `SessionManager` não conhece S3, EFS ou qualquer storage específico — ele conhece apenas o arquivo JSONL da sessão e as operações de leitura/escrita sobre ele. Isso torna o `SessionManager` o ponto exato onde a POC pode injetar um backend de storage alternativo ao filesystem local.

Os cinco métodos estáticos de construção:

| Método | Persiste em disco? | Caso de uso |
|---|---|---|
| `SessionManager.inMemory(cwd?)` | Não — estado só em RAM | Testes, workers efêmeros, handlers stateless |
| `SessionManager.create(cwd, sessionDir?)` | Sim — cria arquivo novo | Primeira invocação de uma nova conversa |
| `SessionManager.open(path)` | Sim — abre arquivo existente | Retomar sessão por path conhecido |
| `SessionManager.continueRecent(cwd, sessionDir?)` | Sim — abre o mais recente ou cria | Padrão de "continuar de onde parou" |
| `SessionManager.forkFrom(sourcePath, targetCwd, sessionDir?)` | Sim — cria arquivo novo a partir de outro | Ramificação: bifurcar em ponto arbitrário do histórico |

Para a POC multi-turno, `inMemory()` não serve: o estado que ele mantém some quando o handler Lambda termina, e o cliente que envia o segundo turno chega numa nova invocação sem nenhuma memória do primeiro. As opções que preservam estado entre invocações são `create()`, `open()` e `continueRecent()` — todas dependem de um path de arquivo JSONL estável e acessível entre invocações, o que num ambiente Lambda sem EFS não existe por padrão.

O `forkFrom()` merece atenção especial: ele lê um arquivo de sessão existente, extrai o caminho de entradas até uma folha específica (identificada por `sessionId`), e grava esse subconjunto num novo arquivo JSONL no `targetCwd`. O resultado é uma sessão nova que começa com o contexto acumulado até aquele ponto — sem modificar a sessão original. Esse é o mecanismo que o capítulo 2 do livro (`02-o-modelo-de-sessao-como-arvore-jsonl`) explora em profundidade; aqui o que importa registrar é que o `SessionManager` expõe essa operação como método estático, e que ela requer leitura do arquivo-fonte, portanto também depende de storage acessível.

O `SessionManager.list(cwd, sessionDir?)` retorna todas as sessões gravadas para um determinado diretório de trabalho — útil para expor um endpoint `/sessions` na API.

O ponto de extensão para S3 ou outro backend é a implementação de um `SessionManager` customizado que sobrescreve as operações de leitura/escrita do arquivo JSONL para chamar `GetObject`/`PutObject` no S3 em vez de operações de filesystem. O capítulo 9 do livro (`09-sessionmanager-customizado-backed-por-s3`) cobre a implementação desse customizado; o que esta aula estabelece é o contrato: o `SessionManager` que `createAgentSession` recebe precisa implementar a interface de leitura e escrita de sessão JSONL, e o SDK não impõe nada sobre onde o storage físico vive.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/session.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/session.md)
- [Session Management and Persistence — DeepWiki agentic-dev-io/pi-agent](https://deepwiki.com/agentic-dev-io/pi-agent/2.4-session-management-and-persistence)
- [pi.dev — SDK documentation](https://pi.dev/docs/latest/sdk)
- [@mariozechner/pi-coding-agent — npm](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)


## 5. `ModelRegistry` e `AuthStorage` sem home directory — como o SDK resolve credenciais de modelo e autenticação, e o que muda em Lambda (`setRuntimeApiKey`, `inMemory()` para registry, caminho customizado de auth)

`AuthStorage` e `ModelRegistry` são os dois objetos que o `AgentSession` usa para saber *com quem falar* (qual provedor de LLM) e *como se autenticar* (qual chave de API). Em desenvolvimento local, ambos funcionam com defaults que apontam para `~/.pi/agent/` — o diretório que o CLI do pi.dev cria ao fazer login. Em Lambda, esse diretório tipicamente não existe, não foi criado, e não é gravável; a imagem base Node.js usada pela AWS não tem home directory configurado com credenciais de LLM. Contornar isso requer configuração explícita dos dois objetos antes de passá-los para `createAgentSession`.

**`AuthStorage`** encapsula o arquivo `auth.json` — a lista de chaves de API por provedor (`anthropic`, `openai`, `google`, etc.). O padrão `AuthStorage.create()` sem argumentos tenta ler `~/.pi/agent/auth.json`. Para Lambda, há dois caminhos:

1. **Path customizado**: `AuthStorage.create("/tmp/auth.json")` — mas em Lambda `/tmp` é efêmero e vazio em cada cold start, então o arquivo precisaria ser recriado na inicialização, o que é frágil.
2. **Runtime key injection**: `authStorage.setRuntimeApiKey("anthropic", process.env.ANTHROPIC_API_KEY)` — a chave é injetada diretamente em memória, sem leitura de arquivo, sem criação de diretório. A chave runtime tem precedência sobre o `auth.json` mesmo que ele exista. Esse é o padrão correto para Lambda: a chave vem de variável de ambiente (configurada via Secrets Manager ou parameter da função), não de arquivo em disco.

```typescript
const authStorage = AuthStorage.create();
authStorage.setRuntimeApiKey("anthropic", process.env.ANTHROPIC_API_KEY!);
```

**`ModelRegistry`** encapsula a lista de modelos disponíveis e seus parâmetros (contexto máximo, suporte a thinking, etc.). O padrão `ModelRegistry.create(authStorage)` tenta ler um `models.json` customizado do diretório do agente para modelos além dos built-in. Em Lambda sem esse arquivo, a chamada vai tentar acessar um path que não existe. A alternativa segura é `ModelRegistry.inMemory(authStorage)`, que usa apenas os modelos built-in do pacote sem tentar ler nenhum arquivo externo:

```typescript
const authStorage = AuthStorage.create();
authStorage.setRuntimeApiKey("anthropic", process.env.ANTHROPIC_API_KEY!);
const modelRegistry = ModelRegistry.inMemory(authStorage);
```

Essa combinação — `AuthStorage.create()` + `setRuntimeApiKey()` + `ModelRegistry.inMemory()` — é o trio padrão para qualquer deploy serverless do SDK. Não cria arquivos, não lê de `~`, não falha por ausência de diretório. A chave flui de variável de ambiente → `setRuntimeApiKey()` → `authStorage` → `modelRegistry` → `AgentSession` → chamada ao LLM.

O que **não** muda é a interface de `createAgentSession` — os mesmos parâmetros do conceito `## 2.`, agora instanciados com os construtores serverless-safe em vez dos defaults locais.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/sdk.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [@mariozechner/pi-coding-agent — npm](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)
- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)


## 6. Loop de eventos via `subscribe()` — o que chega e como consumir — como o SDK emite `AgentSessionEvent` via subscribe/listener (não via readline de stdout), os tipos relevantes para o handler mínimo (`text_delta`, `tool_execution_*`, `agent_end`)

No modo RPC (subcapítulo `03`), os eventos chegam como linhas JSONL no stdout de um subprocesso: o caller lê com um loop de buffer manual, parseia cada linha, e despacha para o handler correspondente. No SDK, o canal de eventos é um listener registrado via `session.subscribe()` — sem stdout, sem readline, sem risco de U+2028. O método retorna uma função de cancelamento:

```typescript
const unsubscribe = session.subscribe((event: AgentSessionEvent) => {
  // chamado sincronamente para cada evento emitido durante session.prompt()
});

await session.prompt("Qual é o diretório de trabalho atual?");
unsubscribe();
```

O `subscribe()` precisa ser chamado **antes** de `session.prompt()` — o listener é registrado no `AgentSession` e começa a receber eventos assim que `prompt()` inicia o processamento. Chamar `subscribe()` depois que `prompt()` já resolveu não captura nada.

A taxonomia de eventos é a mesma que o modo RPC emite no stdout — o `AgentSession` é a fonte de ambos. Para o handler mínimo da POC, há três famílias relevantes:

**Texto progressivo** — `event.type === "message_update"` com `event.assistantMessageEvent.type === "text_delta"`. Cada delta chega com `event.assistantMessageEvent.delta` contendo o fragmento de texto. Para streaming via SSE (Lambda response streaming, tema do capítulo 10), cada delta é emitido direto para o cliente. Para resposta síncrona, os deltas são concatenados num buffer e enviados quando `agent_end` chegar.

**Execução de ferramentas** — `tool_execution_start`, `tool_execution_update`, `tool_execution_end`. Para uma POC básica sem UI de tool calls, esses eventos podem ser ignorados ou logados para diagnóstico. Se a POC precisar de aprovação automática de tool calls — responder automaticamente a `extension_ui_request` — a lógica entra aqui no listener, não em código separado.

**Conclusão do turno** — `event.type === "agent_end"`. Esse evento sinaliza que `prompt()` está prestes a resolver a Promise. O campo `event.messages` contém todo o histórico acumulado da sessão até o momento. Para o handler, `agent_end` é o ponto onde o texto da resposta está completo e pode ser devolvido ao cliente (se não estiver usando streaming).

Um handler mínimo para coletar a resposta completa:

```typescript
const chunks: string[] = [];
const unsubscribe = session.subscribe((event) => {
  if (
    event.type === "message_update" &&
    event.assistantMessageEvent?.type === "text_delta"
  ) {
    chunks.push(event.assistantMessageEvent.delta);
  }
});

await session.prompt(userMessage);
unsubscribe();

const responseText = chunks.join("");
```

A diferença de ergonomia em relação ao RPC é imediata: não há buffer manual, não há split em `\n`, não há correlação de `id`. O TypeScript garante que `event.assistantMessageEvent` só existe quando `event.type === "message_update"`, tornando o acesso ao delta type-safe. Os outros tipos de evento (`queue_update`, `compaction_start`/`end`, `auto_retry_start`/`end`) chegam no mesmo listener — o handler os ignora simplesmente não tendo um `case` para eles.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/sdk.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [pi.dev — SDK documentation](https://pi.dev/docs/latest/sdk)
- [How to Build a Custom Agent Framework with PI — Nader Dabit (gist)](https://gist.github.com/dabit3/e97dbfe71298b1df4d36542aceb5f158)
- [Pi integration architecture — OpenClaw docs](https://docs.openclaw.ai/pi)


## 7. `ResourceLoader` — o que pode ser omitido no handler mínimo da POC — como extensions/skills/templates são carregados, o que acontece se `resourceLoader` for omitido em `createAgentSession`, e o que um handler básico pode ignorar sem quebrar

O `ResourceLoader` é o objeto que o `AgentSession` consulta para descobrir o que está disponível além das ferramentas built-in: extensions (código que se pluga nos hooks do agente), skills (prompts pré-construídos invocáveis como slash commands), prompt templates (variantes de system prompt selecionáveis) e context files (arquivos que entram automaticamente no contexto da sessão). Para uma POC sem nenhuma dessas customizações, o `ResourceLoader` é o parâmetro mais dispensável dos quatro.

Quando `resourceLoader` é omitido em `createAgentSession`, o SDK instancia internamente um `DefaultResourceLoader` com descoberta automática — ele varre o `cwd`, o diretório `~/.pi/agent/` e qualquer pacote npm instalado localmente buscando arquivos de extensão, arquivos `.md` de skills e templates. Em desenvolvimento local isso funciona e carrega o ambiente configurado pelo desenvolvedor. Em Lambda sem nenhuma dessas pastas ou pacotes, a descoberta automática conclui sem encontrar nada e o agente opera sem extensions — comportamento correto para a POC, mas com o custo de tentativas de leitura de filesystem em caminhos que não existem.

Para eliminar esse overhead e tornar o comportamento explícito, a POC pode passar um `ResourceLoader` mínimo que declara ausência de recursos adicionais:

```typescript
const { session } = await createAgentSession({
  sessionManager: SessionManager.inMemory(),
  authStorage,
  modelRegistry,
  resourceLoader: {
    extensions: [],
    skills: [],
    promptTemplates: [],
    contextFiles: [],
  },
});
```

Ou simplesmente omitir e aceitar que o `DefaultResourceLoader` rodará sem encontrar nada relevante em Lambda — a diferença é de clareza de intenção, não de correção.

O que o `ResourceLoader` **não** controla são as ferramentas built-in do agente (`bash`, `read`, `write`, `search`, etc.) — essas são registradas separadamente via o parâmetro `tools` de `createAgentSession` (que recebe `string[]` com os nomes das ferramentas habilitadas). Extensions podem registrar ferramentas adicionais via `ExtensionAPI.registerTool()`, mas isso só é relevante se alguma extension estiver carregada.

O capítulo 3 do livro (`03-skills-extensions-e-o-sistema-de-tools`) cobre o sistema de extensions e skills em profundidade — o que cada hook faz, como registrar uma tool customizada, como uma skill vira um comando disponível no agente. Para a POC deste livro, o `ResourceLoader` é um parâmetro que existe mas pode ser deixado no default ou explicitamente esvaziado sem impacto no comportamento essencial do agente: criar sessão, enviar turno, receber resposta.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/sdk.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [Skills & Prompt Templates — DeepWiki badlogic/pi-mono](https://deepwiki.com/badlogic/pi-mono/4.8-skills-and-prompt-templates)
- [@mariozechner/pi-coding-agent — npm](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)
- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)

<!-- AULAS-END -->

---

**Próximo subcapítulo** → [O Subset que Importa Para a POC Headless](../05-o-subset-que-importa-para-a-poc-headless/CONTENT.md)
