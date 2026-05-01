# Conceitos: Custom Tools via SDK — registerTool e customTools

> _Aula contínua dos conceitos atômicos deste subcapítulo. Cada conceito vira uma seção `## N.` preenchida em sequência pela skill `estudo-explicar-conceito`. Cada nova iteração lê o que já foi escrito e dá continuidade — sem repetir vocabulário, sem reapresentar exemplos, sem saltos de tom._

## Roteiro

1. `defineTool` vs `registerTool` — as duas formas de criar uma tool no SDK e quando cada uma é a interface correta
2. O tipo `AgentTool<T>` e o padrão TypeBox — `Type.Object`, a inferência `typeof schema`, e o contrato do `execute(toolCallId, params)`
3. O parâmetro `customTools` em `createAgentSession` — como o array se combina com tools de extensions carregadas, e o escopo por sessão
4. O parâmetro `tools` vs `customTools` em `createAgentSession` — distinção entre instâncias de tool pré-construídas e definições dinâmicas via `defineTool`
5. `promptSnippet` e `promptGuidelines` — como o LLM recebe a descrição compacta da tool e bullets de uso, e o impacto no token budget por turno
6. Por que `customTools` é o padrão certo para Lambda — ausência de `agentDir` acessível, inexistência de extensions carregadas em disco, e a inicialização de tools como código JavaScript puro no handler
7. Cold start e o custo de I/O na definição de tools — o que não fazer no corpo do `execute` durante inicialização, e como inicializar conexões com serviços AWS fora do factory de tools

<!-- ROTEIRO-END -->

<!-- PENDENTE-START -->
> _Pendente: 7 / 7 conceitos preenchidos._
<!-- PENDENTE-END -->

<!-- AULAS-START -->
## 1. `defineTool` vs `registerTool` — as duas formas de criar uma tool no SDK e quando cada uma é a interface correta

`defineTool` é uma função utilitária do SDK que recebe um objeto de configuração de tool e retorna uma instância de `AgentTool` tipada. Ela não registra a tool em nenhum lugar — apenas cria e valida o objeto. A tool resultante é passada ao agente via parâmetro `customTools` de `createAgentSession`.

`registerTool` é o método de `ExtensionAPI` visto no subcapítulo 02 — ele recebe o mesmo objeto de configuração e registra a tool diretamente no catálogo da sessão ativa. É chamado dentro de um factory de extension, não de forma programática fora de uma extension.

A distinção prática:

| | `defineTool` | `registerTool` |
|---|---|---|
| Onde usar | Fora de extensions, no código do handler | Dentro de um factory de extension |
| Quando a tool fica disponível | Passada em `customTools` na criação da sessão | No boot da sessão, quando a extension é carregada |
| Depende de disco? | Não | Sim (extension precisa ser carregada do disco ou via `-e`) |
| Ideal para Lambda? | Sim | Não |

Para a POC, `defineTool` é a interface certa. O handler Lambda define as tools como módulos JavaScript puros e as passa a `createAgentSession`. Nenhum disco, nenhum jiti, nenhuma extension.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/sdk.md](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [How to Build a Custom Agent Framework with PI — Nader Dabit](https://nader.substack.com/p/how-to-build-a-custom-agent-framework)
- [@mariozechner/pi-coding-agent — npm](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)

## 2. O tipo `AgentTool<T>` e o padrão TypeBox — `Type.Object`, a inferência `typeof schema`, e o contrato do `execute(toolCallId, params)`

`AgentTool<T>` é um tipo genérico onde `T` é o schema TypeBox dos parâmetros da tool. O TypeBox é uma biblioteca de schema runtime compatível com JSON Schema — você define `T` como um `TObject` e o TypeScript infere automaticamente os tipos dos campos a partir do schema, eliminando cast manual.

O padrão canônico:

```typescript
import { Type, type Static } from "@sinclair/typebox";
import { defineTool } from "@mariozechner/pi-coding-agent";

const schema = Type.Object({
  filePath: Type.String({ description: "Path absoluto do arquivo a ler" }),
  maxLines: Type.Optional(Type.Number({ description: "Máximo de linhas, default 100" })),
});

const readWithAudit = defineTool({
  name: "read_audited",
  description: "Lê um arquivo e registra o acesso em log de auditoria",
  parameters: schema,
  execute: async (toolCallId, params) => {
    // params é inferido como { filePath: string; maxLines?: number }
    await auditLog(toolCallId, params.filePath);
    return readFile(params.filePath, params.maxLines);
  },
});
```

O `execute` recebe dois argumentos: `toolCallId` (o identificador único desta invocação da tool, útil para correlacionar logs) e `params` (os parâmetros inferidos do schema). O retorno é qualquer valor serializável — string, objeto, array — que o pi.dev vai entregar ao LLM como resultado da tool call.

O `Type.Optional` faz um campo opcional tanto no schema JSON quanto no tipo TypeScript inferido. Campos sem `Optional` são obrigatórios — se o LLM tentar invocar a tool sem eles, a chamada falha antes de chegar ao `execute`.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/sdk.md](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [@sinclair/typebox — npm](https://www.npmjs.com/package/@sinclair/typebox)
- [How to Build a Custom Agent Framework with PI — GitHub Gist Nader Dabit](https://gist.github.com/dabit3/e97dbfe71298b1df4d36542aceb5f158)

## 3. O parâmetro `customTools` em `createAgentSession` — como o array se combina com tools de extensions carregadas, e o escopo por sessão

`customTools` é um array de `AgentTool` passado diretamente a `createAgentSession`. As tools nele são combinadas com as tools nativas ativas (conforme o conjunto definido por `--tools` ou padrão) e com quaisquer tools registradas por extensions carregadas — o catálogo final que o LLM vê é a união de todos esses conjuntos.

```typescript
const session = await createAgentSession({
  cwd: "/efs/tenant-abc/session-xyz",
  model: myModel,
  customTools: [readWithAudit, bashRestricted],
  // tools nativas padrão (read, write, edit, bash) também entram, a menos que desabilitadas
});
```

Escopo: as tools em `customTools` existem apenas para esta sessão. Criar uma nova sessão com um `customTools` diferente produz um agente diferente — o catálogo não é global nem compartilhado entre instâncias de sessão. Para a POC, isso significa que cada invocação do handler Lambda cria uma sessão com o conjunto exato de tools aprovadas para aquele tenant ou contexto, sem interferência entre invocações concorrentes.

Se uma tool em `customTools` tem o mesmo nome de uma tool nativa (ex: `name: "read"`), a custom tool sobrescreve a nativa — contanto que `--no-builtin-tools` esteja ativo ou a nativa não esteja no allowlist de `--tools`. Sem isso, o pi.dev pode lançar erro de colisão de nome.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/sdk.md](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [@mariozechner/pi-coding-agent — npm, createAgentSession](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)

## 4. O parâmetro `tools` vs `customTools` em `createAgentSession` — distinção entre instâncias de tool pré-construídas e definições dinâmicas via `defineTool`

`createAgentSession` aceita dois parâmetros relacionados a tools: `tools` e `customTools`. A diferença é sutil mas importante:

- **`tools`**: recebe instâncias pré-construídas de `AgentTool` que já existem (criadas anteriormente, fora do contexto da sessão). Permite reutilizar tools entre sessões sem recriá-las. Tipicamente usado quando a tool é definida uma vez no módulo e reusada em múltiplas chamadas ao handler.
- **`customTools`**: recebe definições de tools criadas via `defineTool` como parte da configuração da sessão. Semanticamente é o mesmo resultado, mas o nome `customTools` indica "ferramentas específicas desta configuração de agente", não ferramentas globais reutilizadas.

Na prática, para a POC a distinção é de organização de código: tools que nunca mudam (ex: uma wrapper de `bash` com regras de segurança fixas) podem ser exportadas de um módulo e passadas via `tools`; tools cujo comportamento varia por tenant ou por configuração de sessão entram em `customTools` construídas no momento da criação.

```typescript
// tool fixa — definida uma vez, reutilizada
import { bashRestricted } from "./tools/bash-restricted";

// no handler:
const session = await createAgentSession({
  tools: [bashRestricted],
  customTools: [buildTenantAwareRead(tenantId)],
});
```

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/sdk.md](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [@mariozechner/pi-coding-agent — npm](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)

## 5. `promptSnippet` e `promptGuidelines` — como o LLM recebe a descrição compacta da tool e bullets de uso, e o impacto no token budget por turno

Além de `name`, `description`, `parameters` e `execute`, a definição de tool aceita dois campos opcionais que controlam como a ferramenta aparece no prompt do LLM:

- **`promptSnippet`**: uma string curta (1 linha) que o pi.dev insere no sistema prompt como representação compacta da tool no catálogo. Quando omitido, o pi.dev usa `name` + `description`. Quando presente, substitui a representação padrão — útil para economizar tokens quando a `description` completa é longa.
- **`promptGuidelines`**: um array de strings, onde cada string é um bullet de orientação de uso que o pi.dev insere junto com a descrição da tool no prompt. Usado para forçar comportamentos específicos do LLM ao usar a tool: "sempre verifique o caminho antes de chamar", "use só para arquivos menores que 1 MB", etc.

O custo: cada bullet em `promptGuidelines` adiciona tokens ao prompt em todo turno da sessão, independente de a tool ser usada naquele turno ou não. Para a POC com conjunto de tools reduzido, esse overhead é tolerável. Para agentes com 15+ tools com `promptGuidelines` longos, o custo se acumula rapidamente — e o conceito 1 do subcapítulo 01 já mostrou o problema de catálogos grandes.

A regra prática: `promptSnippet` é quase sempre uma boa ideia para tools com `description` longa; `promptGuidelines` é útil para restricções de uso que o LLM precisa ver explicitamente, mas cada bullet tem custo real de tokens.

**Fontes utilizadas:**

- [Pi Documentation — docs/latest/extensions, tool fields](https://pi.dev/docs/latest/extensions)
- [pi-mono extensions.md](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)
- [Effective context engineering for AI agents — Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

## 6. Por que `customTools` é o padrão certo para Lambda — ausência de `agentDir` acessível, inexistência de extensions carregadas em disco, e a inicialização de tools como código JavaScript puro no handler

O parâmetro `agentDir` de `createAgentSession` aponta para o diretório global de configuração do agente (`~/.pi/agent/` por padrão) — de onde o pi.dev carrega extensions, settings, e outros recursos. Em Lambda, como visto no conceito 8 do subcapítulo 02, esse diretório não existe de forma útil. Passar `agentDir` apontando para `/tmp` ou para um path dentro do bundle do Lambda requer que os arquivos de extension estejam lá — o que reintroduz a complexidade de bundling que queremos evitar.

`customTools` contorna isso inteiramente: as tools são objetos JavaScript definidos no código do handler, compilados junto com o bundle do Lambda, sem dependência de disco em runtime. O handler Lambda se parece com:

```typescript
import { createAgentSession } from "@mariozechner/pi-coding-agent";
import { readRestricted, bashAudited } from "./tools";

export const handler = async (event: APIGatewayEvent) => {
  const session = await createAgentSession({
    agentDir: undefined, // sem carregamento de extensions em disco
    customTools: [readRestricted, bashAudited],
    model: buildModel(process.env),
    // ...
  });
  // processar turno
};
```

Com `agentDir: undefined` (ou apontando para um diretório vazio), o pi.dev não tenta carregar nada do disco. O conjunto de tools é exatamente o que está em `customTools`, mais as tools nativas ativas. Reproduzível, auditável, sem surpresas de extensões carregadas de lugares inesperados.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/sdk.md](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [How to Build a Custom Agent Framework with PI — Nader Dabit](https://nader.substack.com/p/how-to-build-a-custom-agent-framework)
- [AWS Lambda execution environment](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html)

## 7. Cold start e o custo de I/O na definição de tools — o que não fazer no corpo do `execute` durante inicialização, e como inicializar conexões com serviços AWS fora do factory de tools

O `execute` de uma tool é chamado em runtime, durante uma invocação do handler — não durante a inicialização do módulo. O problema de cold start em Lambda não acontece dentro do `execute`, mas na inicialização do módulo antes que o handler seja invocado pela primeira vez. O anti-padrão a evitar é fazer I/O dentro da definição da tool (no momento do `defineTool`), não no `execute`:

```typescript
// ERRADO — I/O em tempo de definição da tool
const sessionsBucket = await s3.listBuckets(); // chamada de rede no import
const myTool = defineTool({
  name: "read_session",
  execute: async (_, params) => { /* usa sessionsBucket */ },
});

// CORRETO — I/O dentro do execute, ou melhor: conexões inicializadas fora das tools
const s3Client = new S3Client({ region: process.env.AWS_REGION }); // cliente, sem I/O
const myTool = defineTool({
  name: "read_session",
  execute: async (_, params) => {
    const result = await s3Client.send(new GetObjectCommand(/* ... */)); // I/O aqui
    return result;
  },
});
```

O padrão correto em Lambda é inicializar clientes de serviços AWS (S3, DynamoDB, SSM, Secrets Manager) fora do handler, no escopo do módulo — eles são reutilizados em warm invocations sem custo adicional de conexão. A definição das tools apenas captura esses clientes via closure. O cold start paga o custo de inicialização dos clientes uma vez; as invocações seguintes reutilizam.

O que **nunca** fazer no módulo (em tempo de carregamento, não de invocação): chamar `GetSecretValue`, fazer queries ao banco, chamar APIs externas. Esses I/Os fazem o cold start durar segundos a mais e, se falharem, impedem o módulo de carregar — tornando o handler inoperante.

**Fontes utilizadas:**

- [AWS Lambda — best practices for cold start](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [pi-mono/packages/coding-agent/docs/sdk.md](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
<!-- AULAS-END -->

---

**Próximo subcapítulo** → [MCP: Por Que Pi.dev Não Adota e o Que Fazer Quando Você Precisa](../04-mcp-por-que-pidev-nao-adota-e-o-que-fazer/CONTENT.md)
