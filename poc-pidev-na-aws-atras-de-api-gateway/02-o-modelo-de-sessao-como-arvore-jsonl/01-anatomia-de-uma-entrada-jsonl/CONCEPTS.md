# Conceitos: Anatomia de uma Entrada JSONL

> O pi.dev persiste sessões como arquivos JSONL — um formato onde cada linha é um objeto JSON completo e autossuficiente. Este subcapítulo desmonta uma entrada de sessão campo a campo: o `SessionHeader` que abre o arquivo, as `SessionMessageEntry`s que registram a conversa (incluindo todos os roles possíveis dentro do objeto `message`), as entradas de metadados que registram mudanças de estado sem alterar o contexto do LLM, e o comportamento append-only que torna cada write atômica ao nível de linha. Sem esse mapa, é impossível raciocinar sobre a estrutura de árvore que o conjunto de entradas forma — que é o ponto de partida do subcapítulo seguinte.

## Roteiro

1. O que é JSONL e por que o pi.dev o usa para sessões — o formato linha-por-objeto, por que ele é adequado para logs append-only, e como o pi.dev organiza um arquivo de sessão como sequência de linhas independentes
2. `SessionHeader` — a linha de abertura obrigatória do arquivo, com campos `type: "session"`, `version`, `id` (UUID), `timestamp`, `cwd`, e o campo opcional `parentSession` que aparece em sessões derivadas de fork
3. `SessionMessageEntry` base — os quatro campos estruturais que toda entrada regular carrega: `type: "message"`, `id` (hex de 8 caracteres), `parentId` (null na primeira entrada do trunk, referência hex nas demais), e `timestamp` ISO 8601
4. O objeto `message` e seus roles — a anatomia interna de uma `SessionMessageEntry`: o que cada role representa (`user`, `assistant`, `toolResult`, `bashExecution`, `custom`, `branchSummary`, `compactionSummary`) e os campos específicos por role
5. Entradas de metadados — `model_change` e `thinking_level_change` como tipos de linha que participam da árvore via `id`/`parentId` mas registram mudanças de estado sem carregar conteúdo de mensagem para o LLM
6. Append-only como contrato de escrita — como o harness abre o arquivo em modo append, escreve uma linha completa e fecha, por que isso torna cada write atômica ao nível de linha, e o que esse contrato proíbe (editar, truncar, reordenar)

## 1. O que é JSONL e por que o pi.dev o usa para sessões

JSONL — JSON Lines, também chamado de NDJSON (Newline Delimited JSON) — é um formato de texto onde cada linha é um objeto JSON completo e autossuficiente, separado do seguinte por um único `\n`. O arquivo como um todo não é um JSON válido: não há colchetes externos, não há vírgulas entre registros. Cada linha pode ser lida, parseada e descartada de memória independentemente das outras, o que torna o formato diretamente compatível com `readline`, pipes Unix e qualquer consumidor que processe um registro por vez.

A razão pela qual esse design resolve o problema de logging fica clara ao compará-lo com alternativas. Um array JSON convencional exige que o escritor mantenha um documento coerente: ao adicionar um elemento, é preciso ler o arquivo, desserializar, inserir, serializar de volta e reescrever — ou ao menos reescrever o sufixo `]`. Com JSONL, adicionar um registro é `file.write(JSON.stringify(entry) + "\n")` em modo append: o escritor não precisa conhecer o estado anterior do arquivo, e o arquivo nunca precisa ser relido para ser estendido. Essa propriedade é o que torna JSONL a escolha padrão para logs, pipelines de streaming e sistemas de auditoria onde a escrita é contínua e a leitura é posterior.

O pi.dev aproveita exatamente essa propriedade. A cada turno de conversa — mensagem do usuário, resposta do assistente, resultado de tool call — o harness abre o arquivo da sessão em modo append, serializa a entrada como uma única linha JSON e fecha. Não há lock de arquivo entre writes, não há necessidade de manter o arquivo em memória entre turnos, e a perda de energia no meio de um write deteriora no máximo a última linha (que estará incompleta e portanto inválida como JSON), deixando todas as anteriores intactas. Em termos de resiliência, um write parcial num array JSON corromperia a estrutura inteira; num JSONL, corromperia apenas um registro.

A estrutura de um arquivo de sessão pi.dev como sequência de linhas independentes reflete essa arquitetura: a primeira linha é sempre o `SessionHeader` (um objeto especial de metadados), e cada linha seguinte é uma entrada da conversa com seu próprio campo `type` declarando o que aquela linha representa. O parser do pi.dev lê o arquivo linha a linha — ele não tenta desserializar o arquivo como um todo. Isso também significa que o arquivo pode crescer indefinidamente sem que o consumo de memória de parse escale com o tamanho: parse é O(N) em leituras sequenciais mas O(1) em memória por linha.

O ponto que conecta diretamente ao restante deste subcapítulo é que cada linha carrega campos `id` e `parentId` que transformam a sequência linear de linhas em uma estrutura de árvore — mas esse mecanismo é detalhado nos conceitos seguintes. Por ora, o essencial é que o JSONL resolve a escrita: atômica ao nível de linha, sem necessidade de reescrita, resiliente a falhas parciais.

**Fontes utilizadas:**

- [JSON Lines — especificação oficial](https://jsonlines.org/)
- [JSONL for Log Processing — JSONL.help](https://jsonl.help/use-cases/log-processing/)
- [NDJSON Definition & Specification — NDJSON.com](https://ndjson.com/definition/)
- [Working with NDJSON: Newline-Delimited JSON for Logs and Streams — JSON Parser](https://jsonparser.com/ndjson-guide)

## 2. `SessionHeader`

O arquivo de sessão JSONL do pi.dev não começa com uma entrada de conversa — começa com uma linha especial cujo único papel é identificar o contêiner. Essa linha é o `SessionHeader`, e sua semântica é distinta de todas as outras: ela é metadados puros sobre a sessão, não participa da árvore de conversa, e não carrega `id` nem `parentId`. O parser a reconhece pelo campo `"type": "session"` e a consome uma vez, na abertura do arquivo.

O schema do `SessionHeader` na versão atual (v3) tem cinco campos obrigatórios e um opcional:

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `type` | `"session"` (literal) | sim | Discriminator que identifica esta linha como cabeçalho |
| `version` | número | sim | Versão do schema de sessão — atualmente `3` |
| `id` | UUID string | sim | Identificador único da sessão |
| `timestamp` | ISO 8601 string | sim | Instante de criação da sessão |
| `cwd` | string (path) | sim | Diretório de trabalho em que o harness foi iniciado |
| `parentSession` | string (path) | não | Caminho absoluto do arquivo JSONL da sessão-pai; presente apenas em sessões derivadas de fork |

Uma sessão nova, criada do zero, produz um `SessionHeader` sem `parentSession`:

```json
{"type":"session","version":3,"id":"a3f8c1d2-4b7e-4a2c-9f61-0e2b3d4c5a6b","timestamp":"2025-04-30T10:22:11.483Z","cwd":"/home/user/projeto"}
```

Uma sessão criada via `/fork` (ou via `newSession({ parentSession })` no SDK) produz um arquivo novo — com seu próprio `id` e seu próprio `timestamp` — mas inclui o `parentSession` apontando para o `.jsonl` de origem:

```json
{"type":"session","version":3,"id":"9b2e7f4a-1c3d-4e5f-8a9b-0c1d2e3f4a5b","timestamp":"2025-04-30T11:05:33.120Z","cwd":"/home/user/projeto","parentSession":"/home/user/.pi/sessions/a3f8c1d2-4b7e-4a2c-9f61-0e2b3d4c5a6b.jsonl"}
```

Três pontos merecem atenção direta de quem vai implementar persistência:

**`version` como sinalização de migração.** O harness evoluiu por três versões de schema — v1 (sem `id`/`parentId`, sequência linear), v2 (introdução de `id`/`parentId`), v3 (padronização dos roles de `custom message`). Ao ler um arquivo, o `SessionManager` checa esse campo e migra automaticamente se necessário. Código que consome sessões diretamente (fora do SDK, como uma lambda custom que lê o JSONL para exibir histórico) precisa estar preparado para encontrar arquivos v1 ou v2 no EFS e lidar com o schema mais antigo — ou forçar migração antes de processar.

**`cwd` como contexto de execução.** O campo não é cosmético: o harness usa o `cwd` registrado ao retomar a sessão para reancorá-la ao diretório correto de trabalho. Quando a sessão muda de host (ex: sessão criada em uma instância Lambda e retomada em outra, com EFS compartilhado), o `cwd` precisa continuar válido no novo host — ou o harness vai resolver caminhos relativos errado. Para a POC, isso raramente causa problema porque o código do projeto está no EFS ou em `/tmp` com paths absolutos, mas é o motivo pelo qual `cwd` não pode ser ignorado na serialização para S3 (voltaremos a isso nos subcapítulos `05-append-only-como-contrato-de-persistencia-efs-vs-s3` e `09-sessionmanager-customizado-backed-por-s3`).

**`parentSession` como elo de grafo entre arquivos.** Dentro de um único arquivo JSONL, a árvore de conversa é formada via `id`/`parentId` nas entradas — conceitos que os próximos itens deste roteiro cobrem. Mas o `parentSession` é um elo de nível superior: conecta arquivos distintos. Uma sessão com `parentSession` é um arquivo separado que começa a partir de um ponto qualquer da sessão-pai (o fork point está registrado na primeira `SessionMessageEntry` via `parentId`). Essa distinção — fork produz arquivo novo, branch fica no mesmo arquivo — é o que determina as implicações de storage: para preservar um fork, não basta persistir o arquivo filho; é preciso persistir também o arquivo pai referenciado por `parentSession`. Essa relação entre arquivos é o tema central do subcapítulo `04-fork-e-branch-na-pratica-criar-e-navegar`.

**Fontes utilizadas:**

- [pi.dev — Session Format (docs oficiais)](https://pi.dev/docs/latest/session-format)
- [Session Management and Persistence — DeepWiki (agentic-dev-io/pi-agent)](https://deepwiki.com/agentic-dev-io/pi-agent/2.4-session-management-and-persistence)
- [pi-mono/packages/coding-agent/README.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [Session tree format — Issue #316 (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/issues/316)

## 3. `SessionMessageEntry` base

Se o `SessionHeader` é o envelope que identifica o contêiner, as `SessionMessageEntry`s são o conteúdo. Toda linha do arquivo JSONL que não é o header — seja uma mensagem do usuário, uma resposta do assistente, um resultado de tool call, ou uma mudança de modelo — é uma entrada que estende o mesmo contrato base de quatro campos: `type`, `id`, `parentId`, e `timestamp`.

O campo `type` na `SessionMessageEntry` é o discriminator literal `"message"`. Outros tipos de entrada (que o conceito 5 deste roteiro cobre — `model_change`, `thinking_level_change`) também usam `id`/`parentId`, mas têm `type` diferente. O parser usa esse campo primeiro para decidir qual schema aplicar ao restante da linha.

O campo `id` é uma string hexadecimal de **8 caracteres** — por exemplo, `"a1b2c3d4"`. Ele é gerado aleatoriamente pelo harness no momento em que a entrada é criada, e sua única garantia é unicidade dentro do arquivo. Não é um UUID (que tem 32 dígitos hexadecimais mais hífens); é um identificador compacto que funciona como chave primária de linha. A escolha de 8 hex foi deliberada: compacto o suficiente para não inflar o tamanho do arquivo, improvável de colidir dentro de uma sessão típica (4 bilhões de valores possíveis para uma sessão que dificilmente excede milhares de entradas).

O campo `parentId` é `string | null`. Ele aponta para o `id` da entrada imediatamente precedente na cadeia de conversa. A primeira entrada de conversa do arquivo tem `parentId: null` — esse é o marcador de raiz da árvore. Cada entrada subsequente no trunk aponta para a anterior. Quando o usuário cria um branch a partir de um ponto anterior (digita uma mensagem nova sem a última entrada como contexto), a nova entrada aponta para a entrada mais antiga onde o branch se formou — e isso é tudo que é necessário para que o parser reconstrua a topologia. O arquivo continua sendo append-only; não há reescrita de nenhuma linha existente.

O campo `timestamp` é uma string ISO 8601 com precisão de milissegundos — por exemplo, `"2025-04-30T10:22:15.347Z"`. Ele registra o instante em que o harness criou a entrada, não em que o LLM finalizou a resposta. Para auditoria e debugging, esse campo é o que permite reconstruir a linha do tempo da sessão.

O schema completo de `SessionMessageEntry` como interface TypeScript expõe a separação entre o envelope estrutural e o conteúdo:

```typescript
interface SessionEntryBase {
  type: string;
  id: string;            // 8-char hex, ex: "a1b2c3d4"
  parentId: string | null;
  timestamp: string;     // ISO 8601, ex: "2025-04-30T10:22:15.347Z"
}

interface SessionMessageEntry extends SessionEntryBase {
  type: "message";
  message: AgentMessage; // UserMessage | AssistantMessage | ToolResultMessage | ...
}
```

O campo `message` com seus roles é o conceito 4 deste roteiro. O que importa aqui é a separação: `id`, `parentId` e `timestamp` são o esqueleto estrutural que o parser usa para montar a árvore — e o faz sem tocar em `message`. Em termos de implementação, ao carregar o arquivo para navegar o histórico, o `SessionManager` pode primeiro indexar todas as entradas pelo `id` e montar o grafo, e só então resolver os `message` para renderizar cada nó. Esse design permite lazy loading por nó e evita parse completo do conteúdo de toda a sessão só para encontrar a leaf atual.

Para ilustrar os três casos de `parentId` numa sequência real:

```jsonl
{"type":"message","id":"a1b2c3d4","parentId":null,"timestamp":"2025-04-30T10:22:15.000Z","message":{"role":"user","content":"Qual a capital do Brasil?"}}
{"type":"message","id":"b2c3d4e5","parentId":"a1b2c3d4","timestamp":"2025-04-30T10:22:16.482Z","message":{"role":"assistant","content":[{"type":"text","text":"Brasília."}]}}
{"type":"message","id":"c3d4e5f6","parentId":"b2c3d4e5","timestamp":"2025-04-30T10:22:20.111Z","message":{"role":"user","content":"E do Argentina?"}}
```

A primeira entrada tem `parentId: null` — raiz do trunk. A segunda aponta para a primeira, a terceira aponta para a segunda. Se o usuário tivesse criado um branch a partir da primeira entrada, a nova mensagem teria `parentId: "a1b2c3d4"` — e no arquivo apareceria como quarta linha, depois das três acima, mesmo que logicamente pertença a um ramo paralelo. O arquivo cresce em append; quem define a topologia é o `parentId`, não a posição da linha.

Um ponto operacional relevante para a POC: ao construir o contexto que vai para o LLM, o harness **não** envia todas as entradas do arquivo — ele caminha da leaf ativa até a raiz via `parentId` (O(profundidade da árvore)), coleta as entradas nesse path, e inverte a ordem para montar a sequência cronológica de mensagens. Entradas em branches não-ativos não entram no contexto. Esse mecanismo é o que permite que forks e branches coexistam no mesmo arquivo sem contaminar o contexto uns dos outros — e é o que o subcapítulo `02-a-arvore-de-sessao-dag-trunk-e-branches` vai detalhar.

**Fontes utilizadas:**

- [pi.dev — Session Format (docs oficiais)](https://pi.dev/docs/latest/session-format)
- [Session Management and Persistence — DeepWiki (agentic-dev-io/pi-agent)](https://deepwiki.com/agentic-dev-io/pi-agent/2.4-session-management-and-persistence)
- [Session tree format — Issue #316 (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/issues/316)
- [pi-coding-agent: Coding Agent CLI — DeepWiki (badlogic/pi-mono)](https://deepwiki.com/badlogic/pi-mono/4-pi-coding-agent:-coding-agent-cli)

## 4. O objeto `message` e seus roles

O campo `message` dentro de uma `SessionMessageEntry` é onde vive o conteúdo real da linha — o texto que o usuário digitou, a resposta do assistente, o resultado de uma tool call. Mas diferente de um log de chat comum, o pi.dev define sete roles distintos para esse objeto, e a distinção importa para a POC porque nem todos eles chegam ao LLM: alguns existem apenas para o harness gerenciar estado local ou renderizar a TUI.

A separação central é entre **roles LLM-level** e **roles agent-level**. Os roles LLM-level — `user`, `assistant` e `toolResult` — mapeiam diretamente para os tipos de mensagem que o LLM espera receber. Quando o harness monta o contexto para a próxima chamada de API, ele percorre o path da árvore (conforme vimos em `## 3.`), coleta as entradas nesse path e chama `convertToLlm()` para converter o array de `AgentMessage`s em um array de mensagens no formato da API do provedor. Entradas com roles agent-level são filtradas nessa conversão — elas não entram no payload enviado ao modelo. O LLM nunca vê `bashExecution`, `branchSummary`, `compactionSummary` ou `custom`.

Os três roles LLM-level têm estruturas diretas:

```typescript
interface UserMessage {
  role: "user";
  content: string | (TextContent | ImageContent)[];
  timestamp: number; // Unix ms
}

interface AssistantMessage {
  role: "assistant";
  content: (TextContent | ThinkingContent | ToolCall)[];
  api: string;
  provider: string;
  model: string;
  usage: Usage;
  stopReason: "stop" | "length" | "toolUse" | "error" | "aborted";
  errorMessage?: string;
  timestamp: number;
}

interface ToolResultMessage {
  role: "toolResult";
  toolCallId: string;
  toolName: string;
  content: (TextContent | ImageContent)[];
  details?: any;
  isError: boolean;
  timestamp: number;
}
```

O `AssistantMessage` merece atenção: além do `content`, ele persiste `api`, `provider` e `model` — os metadados do provedor que gerou a resposta. Isso significa que o arquivo JSONL registra qual modelo respondeu cada turno individualmente, o que é relevante para sessões longas onde o modelo muda (via `/model` na TUI ou via `model_change` entry — que o conceito 5 cobre). O campo `usage` guarda os contadores de tokens e custo; ao ler o arquivo para auditoria, é possível calcular o custo total de uma sessão somando o `usage.cost.total` de cada `AssistantMessage`.

O `ToolResultMessage` tem um campo `toolCallId` que referencia o `id` de um `ToolCall` dentro do `content` do `AssistantMessage` precedente. Esse par (ToolCall no content da resposta do assistente + ToolResultMessage na entrada seguinte) é o contrato que o harness usa para montar o ciclo request/result de tools. O campo `isError: boolean` distingue resultados de sucesso de erros que o harness reportou ao LLM como resultado da tool call.

Os quatro roles agent-level têm propósitos distintos:

| Role | Propósito | Campo diferencial | Vai ao LLM? |
|---|---|---|---|
| `bashExecution` | Registra execução de comando shell pelo harness | `command`, `output`, `exitCode`, `excludeFromContext` | Não |
| `custom` | Dados de estado arbitrários de extensions | `customType`, `display`, `details` | Não |
| `branchSummary` | Resumo textual do branch abandonado ao trocar de branch | `summary`, `fromId` | Não |
| `compactionSummary` | Resumo do contexto compactado (substitui entradas antigas) | `summary`, `tokensBefore` | Indiretamente (como UserMessage sintética) |

O `BashExecutionMessage` tem um campo `excludeFromContext: boolean` que merece destaque. Comandos prefixados com `!!` na TUI — que executam shell diretamente sem passar pelo LLM — produzem um `BashExecutionMessage` com `excludeFromContext: true`. Esses registros ficam no arquivo para auditoria, mas o harness os ignora ao construir o contexto, mesmo estando no path da árvore ativa.

O `CustomMessage` é o mecanismo de persistência de estado das extensions. Quando uma extension precisa registrar algo no arquivo de sessão (um estado de UI, um marcador de progresso, metadados de uma operação custom), ela cria uma entrada com `role: "custom"` e seu próprio `customType` string para namespacing. O campo `display: boolean` instrui a TUI se deve renderizar esse entry ou apenas persisti-lo silenciosamente. Isso é relevante para a POC se você planejar implementar extensions customizadas (reservado para o capítulo `03-skills-extensions-e-o-sistema-de-tools`).

O `BranchSummaryMessage` e o `CompactionSummaryMessage` têm comportamentos distintos mesmo parecendo similares. O `branchSummary` é gerado automaticamente pelo harness quando o usuário troca de branch via TUI — ele resume o branch que está sendo abandonado, do ponto de fork até a leaf, usando o LLM para gerar o texto. O `compactionSummary` é diferente: quando o contexto ativo ultrapassa o limite de tokens, o harness compacta as entradas mais antigas numa única mensagem de resumo. O par (`compactionSummary`, `firstKeptEntryId`) marca o ponto de corte — entradas antes de `firstKeptEntryId` são ignoradas ao montar o contexto, e o `summary` entra como uma `UserMessage` sintética no topo do contexto enviado ao LLM. Esse mecanismo é detalhado no subcapítulo `03-entradas-especiais-compaction-branchsummary-e-labels`.

Para quem vai implementar um leitor de sessão na POC (por exemplo, um endpoint que retorna o histórico formatado de uma sessão), a regra prática é: itere o path da árvore ativa, e para cada entrada filtre pelo role. Renderize `user`, `assistant` e `toolResult` como conteúdo da conversa; renderize `bashExecution` com `excludeFromContext: false` como ação executada; ignore `custom` com `display: false`; renderize `branchSummary` e `compactionSummary` como separadores de seção se quiser manter o histórico fiel ao que o usuário viu.

**Fontes utilizadas:**

- [pi.dev — Session Format (docs oficiais)](https://pi.dev/docs/latest/session-format)
- [Session Management and Persistence — DeepWiki (agentic-dev-io/pi-agent)](https://deepwiki.com/agentic-dev-io/pi-agent/2.4-session-management-and-persistence)
- [Compaction and Context Management — DeepWiki (agentic-dev-io/pi-agent)](https://deepwiki.com/agentic-dev-io/pi-agent/2.5-compaction-and-context-management)
- [pi-coding-agent: Coding Agent CLI — DeepWiki (badlogic/pi-mono)](https://deepwiki.com/badlogic/pi-mono/4-pi-coding-agent:-coding-agent-cli)
- [pi-mono/packages/coding-agent/docs/session.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/HEAD/packages/coding-agent/docs/session.md)

## 5. Entradas de metadados

Nos conceitos anteriores, toda linha do arquivo JSONL além do `SessionHeader` carregava `type: "message"` e um campo `message` com algum rol de conteúdo. Mas uma sessão pi.dev pode registrar acontecimentos que não são mensagens — o usuário trocou de modelo no meio da conversa, ou aumentou o nível de pensamento (thinking) do agente. Esses eventos precisam ser registrados de forma permanente (para que o arquivo seja a fonte de verdade do estado da sessão), mas não devem aparecer na janela de contexto enviada ao LLM. Essa categoria de linhas são as entradas de metadados: `model_change` e `thinking_level_change`.

Ambas as entradas estendem o mesmo `SessionEntryBase` apresentado em `## 3.` — com os campos `type`, `id` (hex de 8 caracteres), `parentId` e `timestamp`. O que muda é o `type` e os campos adicionais específicos:

```typescript
interface ModelChangeEntry {
  type: "model_change";
  id: string;           // 8-char hex
  parentId: string | null;
  timestamp: string;    // ISO 8601
  provider: string;     // ex: "anthropic", "openai"
  modelId: string;      // ex: "claude-opus-4-5", "gpt-4o"
}

interface ThinkingLevelChangeEntry {
  type: "thinking_level_change";
  id: string;
  parentId: string | null;
  timestamp: string;
  thinkingLevel: "off" | "minimal" | "low" | "medium" | "high" | "xhigh";
}
```

Exemplos de linhas reais num arquivo de sessão:

```jsonl
{"type":"model_change","id":"d4e5f6g7","parentId":"c3d4e5f6","timestamp":"2025-04-30T14:05:00.000Z","provider":"openai","modelId":"gpt-4o"}
{"type":"thinking_level_change","id":"e5f6g7h8","parentId":"d4e5f6g7","timestamp":"2025-04-30T14:06:00.000Z","thinkingLevel":"high"}
```

O fato de ambas usarem `id` e `parentId` é o ponto central. Elas participam da árvore exatamente como uma `SessionMessageEntry` participaria — cada uma aponta para o `id` da entrada imediatamente anterior no caminho ativo, e a entrada seguinte (seja ela qual for) aponta para o `id` desta. O arquivo continua sendo append-only; a mudança de modelo ou de thinking level não provoca reescrita de nada. O harness, ao percorrer o path da leaf ativa até a raiz para montar o contexto, encontra essas entradas no caminho e as usa para reconstruir o estado da sessão — sabe que, a partir daquele ponto, a API deve ser chamada com `provider=openai, modelId=gpt-4o`, e com determinado `thinkingLevel`. Entradas anteriores ao `model_change` no mesmo path podem ter sido geradas com um modelo diferente; isso é preservado no histórico via os campos `api`, `provider` e `model` do `AssistantMessage` (vimos em `## 4.` que cada `AssistantMessage` registra individualmente o modelo que gerou aquela resposta).

O que essas entradas **não** fazem é injetar conteúdo no payload enviado ao LLM. Quando o harness chama `convertToLlm()` para transformar as entradas do path ativo em mensagens da API, ele filtra por `type: "message"` (e `type: "compaction_summary"` com tratamento especial). Entradas com `type: "model_change"` ou `type: "thinking_level_change"` são ignoradas nessa conversão — o LLM nunca vê referência a elas. O modelo não "sabe" que foi trocado; o contexto que ele recebe é simplesmente as mensagens da conversa, montadas pelo harness com o novo modelo como destino.

Há uma nuance relevante para a POC: ao trocar de provedor mid-session (por exemplo, de Anthropic para OpenAI), o histórico de mensagens precisa ser convertido para o formato da nova API. O pi.dev faz isso como melhor-esforço — thinking traces do Anthropic, por exemplo, são convertidos para blocos de texto delimitados por `<thinking></thinking>` dentro das `AssistantMessage`s quando enviados para um provedor que não tem tipo nativo para esse conteúdo. O `model_change` no JSONL é o marcador que diz ao harness onde essa conversão precisa começar. Para a POC headless (onde o modelo é fixo via configuração do handler ou da sessão), entradas `model_change` serão raras ou inexistentes — mas uma implementação de leitura de sessão precisa tratá-las graciosamente sem quebrar o parsing.

Para implementadores que vão construir leitores de sessão na POC (endpoint de histórico, debug tool), a regra é direta: ao iterar o path da árvore ativa, se encontrar `type: "model_change"`, registre que a partir dali o modelo mudou para `provider/modelId` — útil para auditoria de custo por modelo. Se encontrar `type: "thinking_level_change"`, registre o nível ativo a partir desse ponto. Nenhuma das duas entra no array de mensagens renderizadas para o usuário como conteúdo de conversa.

**Fontes utilizadas:**

- [pi.dev — Session Format (docs oficiais)](https://pi.dev/docs/latest/session-format)
- [Session Management and Persistence — DeepWiki (agentic-dev-io/pi-agent)](https://deepwiki.com/agentic-dev-io/pi-agent/2.4-session-management-and-persistence)
- [pi-coding-agent: Coding Agent CLI — DeepWiki (badlogic/pi-mono)](https://deepwiki.com/badlogic/pi-mono/4-pi-coding-agent:-coding-agent-cli)
- [pi-mono/packages/coding-agent/README.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)

## 6. Append-only como contrato de escrita

Os conceitos anteriores descreveram o que está dentro de cada linha do arquivo — o `SessionHeader`, as `SessionMessageEntry`s com seus roles, as entradas de metadados. Este conceito descreve como o arquivo cresce: o padrão de I/O que o harness usa para escrever, e o que esse padrão garante e proíbe.

O contrato é simples: ao criar uma entrada, o harness abre o arquivo de sessão com a flag `a` (append), serializa a entrada como uma única linha JSON terminada em `\n`, escreve essa linha e fecha o arquivo. O arquivo nunca é lido durante uma escrita. Não há lock de arquivo entre turnos — cada turno é uma operação isolada de open-write-close. Essa sequência é o que torna cada write atômico **ao nível de linha**: ou a linha completa chega ao disco, ou não chega nada que o parser tratará como válido.

A fonte dessa atomicidade está na semântica de POSIX `O_APPEND`. Quando um arquivo é aberto com append, o kernel garante que o `lseek` para o fim do arquivo e o `write` subsequente acontecem como uma operação indivisível — outro processo que tente escrever no mesmo instante vai ter seu próprio `write` enfileirado, não intercalado no meio de um byte de outra linha. O que isso significa na prática: se o processo pi.dev for interrompido por sinal, falha de energia ou crash no meio de um `write`, o pior cenário é a última linha do arquivo ficar incompleta. Linhas anteriores estão intactas. O parser lê linha a linha — ao encontrar uma linha que não é JSON válido (incompleta por crash), descarta aquela linha específica e continua. O histórico inteiro da sessão antes do crash permanece recuperável.

Compare com um array JSON convencional. Para adicionar um elemento no final, seria preciso: (1) abrir o arquivo, (2) localizar o `]` final, (3) truncar ou reescrever a partir daí, (4) inserir a nova entrada, (5) fechar. Se o processo morrer no passo 3 ou 4, o arquivo inteiro pode ficar inválido como JSON — o `]` sumiu, o objeto novo está incompleto, e o parser vai rejeitar o arquivo inteiro na próxima leitura. Com JSONL e append, a janela de corrupção cai de "o arquivo inteiro" para "a última linha em progresso no momento do crash".

O que esse contrato proíbe é direto:

- **Editar linhas no meio do arquivo**: JSONL append-only não tem operação de "atualizar uma entrada existente". Se uma entrada foi escrita com conteúdo errado, não se edita — cria-se uma nova entrada que supersede (ou corrige) o estado. O pi.dev não expõe nenhuma API de atualização in-place de entradas.
- **Truncar**: remover linhas do final do arquivo quebra a integridade do grafo `id`/`parentId`. Uma entrada pode ser referenciada como `parentId` de outra que vem depois no arquivo — truncar o arquivo para remover a entrada "mais recente" pode produzir entradas órfãs (com `parentId` apontando para um `id` que não existe mais).
- **Reordenar**: o parser assume que a posição de uma linha no arquivo reflete a ordem de inserção. O algoritmo de reconstrução da árvore constrói o índice de `id` → entrada varrendo o arquivo de cima para baixo; uma entrada que aparece depois no arquivo e referencia uma entrada que aparece antes é válida — o caso de branch funciona exatamente assim. Mas se a posição for embaralhada, o índice pode ser construído com entradas ainda não vistas e referenciar `id`s que ainda não apareceram na varredura, quebrando a reconstrução.

Para a POC, esse contrato tem implicação direta no desenho de persistência fora do disco local — tema dos subcapítulos `05-append-only-como-contrato-de-persistencia-efs-vs-s3` e `09-sessionmanager-customizado-backed-por-s3`. EFS expõe semântica POSIX de arquivo: append nativo, atômico ao nível de write, suporte direto ao contrato. S3 não tem operação de append nativa — um objeto S3 só pode ser substituído inteiro (PUT) ou construído em partes (Multipart Upload), e nenhuma das duas opções é append atômico linha a linha. Essa tensão é o que força uma escolha de arquitetura: ou você usa EFS e preserva o contrato nativamente, ou você implementa um `SessionManager` customizado que materializa as entradas pendentes em memória e faz PUT completo no S3 quando conveniente. O segundo caminho requer tradeoffs sobre consistência e risco de perda de entradas não flushed — o subcapítulo 09 cobre isso em detalhe.

**Fontes utilizadas:**

- [pi.dev — Session Format (docs oficiais)](https://pi.dev/docs/latest/session-format)
- [Session Management and Persistence — DeepWiki (agentic-dev-io/pi-agent)](https://deepwiki.com/agentic-dev-io/pi-agent/2.4-session-management-and-persistence)
- [Append-only — Wikipedia](https://en.wikipedia.org/wiki/Append-only)
- [Appending to a log: an introduction to the Linux dark arts — Paul Khuong](https://pvk.ca/Blog/2021/01/22/appending-to-a-log-an-introduction-to-the-linux-dark-arts/)
- [Are Files Appends Really Atomic? — Not The Wizard](https://www.notthewizard.com/2014/06/17/are-files-appends-really-atomic/)
- [Working with NDJSON: Newline-Delimited JSON for Logs and Streams — JSON Parser](https://jsonparser.com/ndjson-guide)

> _Pendente: 6 / 6 conceitos preenchidos._

---

**Próximo subcapítulo** → [A Árvore de Sessão — DAG, Trunk e Branches](../02-a-arvore-de-sessao-dag-trunk-e-branches/CONTENT.md)
