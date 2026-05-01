# Conceitos: O Sistema de Extensions — Protocolo e Ciclo de Vida

> _Aula contínua dos conceitos atômicos deste subcapítulo. Cada conceito vira uma seção `## N.` preenchida em sequência pela skill `estudo-explicar-conceito`. Cada nova iteração lê o que já foi escrito e dá continuidade — sem repetir vocabulário, sem reapresentar exemplos, sem saltos de tom._

## Roteiro

1. O que é uma extension no pi.dev — módulo TypeScript com factory default export que recebe ExtensionAPI
2. Descoberta automática de extensions — os dois caminhos em disco (~/.pi/agent/extensions/ e .pi/extensions/) e a flag -e para teste direto
3. O papel do jiti — execução de TypeScript sem compilação, o ambiente virtualizado e o que está disponível no escopo
4. O contrato de ExtensionAPI — o que o factory recebe: registerTool, registerCommand, registerShortcut, e on/off para eventos
5. A sequência completa de eventos de uma tool call — tool_execution_start → tool_call → execute → tool_execution_update → tool_result → tool_execution_end
6. Interceptar e bloquear em tool_call — como o handler pode cancelar a execução de uma tool e o que acontece com o turno do LLM quando isso ocorre
7. Modificar o resultado em tool_result — encadeamento middleware de handlers, como cada um recebe e pode transformar o resultado antes do LLM ver
8. Por que a descoberta em disco falha em Lambda — ausência de home directory, filesystem efêmero, e o que ctx.hasUI === false significa para handlers que tentam abrir UI dialogs

<!-- ROTEIRO-END -->

<!-- PENDENTE-START -->
> _Pendente: 8 / 8 conceitos preenchidos._
<!-- PENDENTE-END -->

<!-- AULAS-START -->
## 1. O que é uma extension no pi.dev — módulo TypeScript com factory default export que recebe ExtensionAPI

Uma extension no pi.dev é um arquivo TypeScript com um único requisito estrutural: exportar uma função `default` — o factory — que recebe um objeto `ExtensionAPI` e opcionalmente retorna uma `Promise<void>`. O pi.dev carrega o arquivo, executa o factory, e a extension passa a estar ativa para a sessão. Não há interface base para implementar, não há classe para herdar, não há decorator para declarar — é uma função que recebe uma API e registra o que quiser nela.

```typescript
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default async function(pi: ExtensionAPI): Promise<void> {
  pi.registerTool({
    name: "my_tool",
    description: "...",
    parameters: { /* TypeBox schema */ },
    execute: async (_id, params) => { /* ... */ },
  });

  pi.on("tool_call", async (event, ctx) => {
    // interceptar antes da execução
  });
}
```

A extensão pode chamar qualquer método de `ExtensionAPI` — registrar tools, comandos, shortcuts, e handlers de eventos — e o faz sinchronamente ou de forma assíncrona no corpo do factory. Depois que o factory retorna, o pi.dev considera a extension inicializada e inclui suas tools no catálogo que o LLM vai receber no próximo turno.

**Fontes utilizadas:**

- [pi-mono extensions.md](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)
- [Pi Documentation — docs/latest/extensions](https://pi.dev/docs/latest/extensions)
- [Extension System — agentic-dev-io/pi-agent DeepWiki](https://deepwiki.com/agentic-dev-io/pi-agent/5-extension-system)

## 2. Descoberta automática de extensions — os dois caminhos em disco (~/.pi/agent/extensions/ e .pi/extensions/) e a flag -e para teste direto

O pi.dev procura extensions em dois caminhos no momento em que a sessão é iniciada. O primeiro é global: `~/.pi/agent/extensions/` — qualquer `.ts` ali é carregado em toda sessão iniciada pelo usuário, independente do projeto. O segundo é local ao projeto: `.pi/extensions/` no diretório de trabalho corrente — carregado apenas quando a sessão é iniciada com aquele diretório como cwd.

A precedência é aditiva: extensions globais e locais são carregadas em conjunto, não em substituição. Se uma tool com o mesmo nome é registrada por duas extensions, a segunda sobrescreve a primeira (ou o pi.dev lança erro de colisão de nome, dependendo da versão).

Para desenvolvimento e teste, a flag `-e ./caminho/da/extension.ts` carrega um arquivo específico sem que ele precise estar nos diretórios padrão:

```bash
pi -e ./tools/my-restricted-bash.ts
```

Essa flag é útil para iterar numa extension antes de "instalá-la" nos diretórios padrão, ou para testar o comportamento do agente com um conjunto específico de tools antes de embarcar no Lambda.

O ponto de atenção para a POC: **nenhum desses caminhos existe num container Lambda**. `~` numa função Lambda não é um home directory de usuário — é `/root` ou `/home/sbx_user1051` dependendo da imagem base, e não tem persistência entre invocações nem entre builds. A flag `-e` também não se aplica porque o agente é invocado via SDK, não via CLI. O mecanismo relevante para Lambda é o `customTools` do SDK — coberto no subcapítulo 03.

**Fontes utilizadas:**

- [pi-mono extensions.md — discovery paths](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)
- [Extension System — agentic-dev-io/pi-agent DeepWiki](https://deepwiki.com/agentic-dev-io/pi-agent/5-extension-system)

## 3. O papel do jiti — execução de TypeScript sem compilação, o ambiente virtualizado e o que está disponível no escopo

O pi.dev usa o [jiti](https://github.com/unjs/jiti) para executar os arquivos `.ts` de extension sem passar por um passo de compilação explícito. O jiti intercepta o `require`/`import` do Node.js, transpila o TypeScript em memória (via esbuild ou SWC, dependendo da versão), e executa o resultado. Para o desenvolvedor da extension, o arquivo `.ts` roda "como está" — sem `tsc`, sem `tsup`, sem bundler no meio.

O ambiente virtualizado que o jiti cria dentro de uma extension tem acesso a:

- `@mariozechner/pi-coding-agent` — o pacote do pi.dev em si, de onde vêm os tipos como `ExtensionAPI`, `AgentTool` etc.
- `@sinclair/typebox` — a biblioteca de schema usado para definir parâmetros de tools.
- Qualquer pacote já instalado no `node_modules` do projeto (ou globalmente no sistema).

O que **não** está disponível: módulos nativos do Node.js que dependem de paths absolutos do sistema de arquivos, binários compilados sem caminho correto, ou APIs de browser (óbvio, mas relevante se a extension for copiada de um projeto web).

Para a POC, a ausência do jiti é irrelevante porque a abordagem Lambda usa `customTools` no SDK — que não passa por jiti, e sim pelo bundle normal do handler Lambda. O jiti importa no desenvolvimento local para iterar em extensions `.ts` sem build step.

**Fontes utilizadas:**

- [jiti — GitHub](https://github.com/unjs/jiti)
- [Extension System — agentic-dev-io/pi-agent DeepWiki](https://deepwiki.com/agentic-dev-io/pi-agent/5-extension-system)
- [pi-mono extensions.md — jiti loading](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)

## 4. O contrato de ExtensionAPI — o que o factory recebe: registerTool, registerCommand, registerShortcut, e on/off para eventos

`ExtensionAPI` é o objeto que o factory da extension recebe como primeiro argumento. Ele expõe quatro categorias de métodos:

| Método | O que faz |
|---|---|
| `registerTool(tool)` | Adiciona uma tool ao catálogo do agente; o LLM passa a ver essa tool no próximo turno |
| `registerCommand(cmd)` | Adiciona um comando de barra (`/cmd`) invocável na TUI pelo usuário |
| `registerShortcut(key, handler)` | Registra atalho de teclado para a TUI |
| `on(event, handler)` | Subscreve a um evento do ciclo de vida (tool_call, tool_result, etc.) |
| `off(event, handler)` | Cancela a subscrição |

Para a POC, `registerCommand` e `registerShortcut` são irrelevantes — não há TUI num handler Lambda. O que importa é `registerTool` (para tools customizadas) e `on`/`off` (para interceptar ciclos de vida de tools, como logar chamadas ou bloquear operações perigosas).

O `on`/`off` aceita uma lista específica de event types: `tool_execution_start`, `tool_call`, `tool_execution_update`, `tool_result`, `tool_execution_end`, além de eventos de sessão como `turn_start` e `turn_end`. A assinatura do handler é sempre `async (event, ctx) => void | boolean` — o retorno `false` em `tool_call` bloqueia a execução (coberto no conceito 6).

**Fontes utilizadas:**

- [Pi Documentation — docs/latest/extensions, ExtensionAPI](https://pi.dev/docs/latest/extensions)
- [pi-mono extensions.md](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)
- [Extending Pi Coding Agent with Custom Tools and Widgets — JoelClaw](https://joelclaw.com/extending-pi-with-custom-tools)

## 5. A sequência completa de eventos de uma tool call — tool_execution_start → tool_call → execute → tool_execution_update → tool_result → tool_execution_end

Quando o LLM decide invocar uma tool, o pi.dev dispara uma sequência determinística de eventos que as extensions podem observar e modificar:

```
LLM emite tool call
      ↓
tool_execution_start    — notificação: uma tool call começou (toolCallId, toolName, args)
      ↓
tool_call               — interceptação: handlers podem bloquear (retornar false)
      ↓
execute()               — a função execute da tool é chamada de fato
      ↓
tool_execution_update*  — zero ou mais atualizações de progresso durante a execução
      ↓
tool_result             — interceptação: handlers podem modificar o resultado
      ↓
tool_execution_end      — notificação: a tool call terminou (com resultado ou erro)
      ↓
resultado entregue ao LLM
```

Os eventos `*_start` e `*_end` são puramente notificativos — chamar `return false` neles não tem efeito documentado. Os eventos `tool_call` e `tool_result` são os pontos de intervenção. `tool_execution_update` é usado para streaming de saída parcial (útil para `bash` com output longo) e não aceita modificação.

Em modo paralelo de tool calls (quando o LLM emite múltiplas tool calls no mesmo turno), os eventos são disparados concorrentemente. O handler de `tool_call` de uma tool não tem garantia de ver os resultados das tool calls irmãs do mesmo turno no `ctx.sessionManager` — isso é documentado explicitamente no código do pi.dev. Para a POC, isso significa que interceptores de segurança não podem depender de "o que outras tools já fizeram neste turno".

**Fontes utilizadas:**

- [pi-mono extensions.md — event lifecycle](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)
- [Extension System — agentic-dev-io/pi-agent DeepWiki](https://deepwiki.com/agentic-dev-io/pi-agent/5-extension-system)
- [Pi Documentation — docs/latest/extensions](https://pi.dev/docs/latest/extensions)

## 6. Interceptar e bloquear em tool_call — como o handler pode cancelar a execução de uma tool e o que acontece com o turno do LLM quando isso ocorre

O handler de `tool_call` tem a capacidade de bloquear a execução de uma tool antes que a função `execute` seja chamada. O mecanismo é simples: retornar `false` (ou uma Promise que resolve para `false`) no handler registrado via `pi.on("tool_call", ...)`.

```typescript
pi.on("tool_call", async (event, ctx) => {
  if (event.toolName === "bash" && containsDangerousPattern(event.args.command)) {
    return false; // bloqueia a execução
  }
  // retorno implícito undefined = deixa passar
});
```

Quando um handler retorna `false`, a cadeia de handlers subsequentes não é executada (short-circuit), o `execute()` da tool não é chamado, e o pi.dev entrega ao LLM um resultado de erro indicando que a execução foi bloqueada. O LLM recebe isso como `tool_result` com `isError: true` e um texto explicando que a operação foi negada.

O comportamento do LLM após um bloqueio depende do modelo: em geral, ele vai tentar outra abordagem, perguntar ao usuário, ou encerrar a tarefa. Não há garantia de que ele vai "entender" a razão do bloqueio a menos que o resultado de erro inclua uma mensagem explicativa — o que o handler pode customizar ao retornar um objeto de erro em vez de apenas `false`.

Para a POC, o `tool_call` interceptor é a última linha de defesa contra comandos `bash` perigosos que passaram pelo filtro de tool selection do LLM mas que o handler quer bloquear em runtime (ex: comandos que tentam acessar `/etc/passwd`, deletar arquivos fora do diretório de sessão, ou fazer chamadas de rede não esperadas).

**Fontes utilizadas:**

- [pi-mono extensions.md — tool_call blocking](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)
- [Extension System — agentic-dev-io/pi-agent DeepWiki](https://deepwiki.com/agentic-dev-io/pi-agent/5-extension-system)

## 7. Modificar o resultado em tool_result — encadeamento middleware de handlers, como cada um recebe e pode transformar o resultado antes do LLM ver

O evento `tool_result` é disparado depois que o `execute()` termina, antes que o resultado seja entregue ao LLM. Handlers registrados para esse evento recebem o resultado e podem retornar um resultado modificado. Múltiplos handlers são encadeados em ordem de registro, e cada um recebe o resultado do handler anterior — padrão middleware.

```typescript
pi.on("tool_result", async (event, ctx) => {
  // event.result contém o resultado atual (pode ter sido modificado por handlers anteriores)
  const filtered = redactSecrets(event.result);
  return { ...event, result: filtered }; // modifica e passa adiante
  // ou: return undefined para passar sem modificação
});
```

Os casos de uso mais comuns para a POC:

- **Redação de secrets**: o output de `bash` pode conter tokens de autenticação ou credenciais temporárias que não devem entrar no contexto do LLM. Um handler de `tool_result` pode filtrar esses valores antes de chegar ao modelo.
- **Truncagem de output longo**: outputs de `bash` muito longos (ex: `npm install` com centenas de linhas) consomem tokens desnecessariamente. O handler pode truncar para as últimas N linhas ou sumarizar.
- **Logging de auditoria**: registrar no CloudWatch o que cada tool call retornou — útil para diagnóstico quando a POC se comportar de forma inesperada.

O encadeamento garante que cada handler vê o resultado já processado pelos anteriores, não o resultado bruto original. Se qualquer handler retornar `undefined`, o resultado corrente passa inalterado para o próximo handler da cadeia.

**Fontes utilizadas:**

- [pi-mono extensions.md — tool_result middleware](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)
- [Pi Documentation — docs/latest/extensions](https://pi.dev/docs/latest/extensions)

## 8. Por que a descoberta em disco falha em Lambda — ausência de home directory, filesystem efêmero, e o que ctx.hasUI === false significa para handlers que tentam abrir UI dialogs

As extensões em disco dependem de três condições que não existem num container Lambda: (1) um home directory de usuário persistente onde `~/.pi/agent/extensions/` possa residir; (2) um filesystem de projeto persistente com `.pi/extensions/`; (3) a presença de Node.js com acesso a esses caminhos no momento do boot da sessão.

Em Lambda, `~` resolve para `/root` ou `/home/sbx_user1051` dependendo da imagem base, mas esse diretório não tem arquivos persistidos entre builds do container — ele nasce vazio a cada cold start. Mesmo que se tentasse copiar extensions para o diretório `/root/.pi/agent/extensions/` como parte do build da imagem Docker, o jiti ainda precisaria resolver os imports de `@mariozechner/pi-coding-agent` e `@sinclair/typebox` naquele contexto — o que pode funcionar ou não dependendo de como o bundle do Lambda foi empacotado.

O segundo problema é o `ctx.hasUI`. Handlers de eventos que usam `ctx.ui.confirm(...)`, `ctx.ui.notify(...)` ou qualquer método interativo do objeto `ctx` dependem de haver uma TUI ativa. Em headless, `ctx.hasUI` é `false`, e chamadas a esses métodos se tornam no-ops ou retornam valores default. Uma extension escrita para uso interativo que chama `ctx.ui.confirm("Tem certeza?")` em modo Lambda sempre recebe `false` (ou `undefined`) como resposta — o que pode significar bloqueio silencioso de toda e qualquer tool call que o handler interceptar.

Esses dois problemas convergem para a mesma conclusão que o conceito 2 já apontou: extensions em disco não são o mecanismo certo para Lambda. O `customTools` do SDK resolve ambos — não depende de disco e não usa a UI.

**Fontes utilizadas:**

- [pi-mono extensions.md — ctx.hasUI](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)
- [Pi Documentation — docs/latest/extensions](https://pi.dev/docs/latest/extensions)
- [AWS Lambda execution environment — filesystem constraints](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html)
<!-- AULAS-END -->

---

**Próximo subcapítulo** → [Custom Tools via SDK — registerTool e customTools](../03-custom-tools-via-sdk-registertool-e-customtools/CONTENT.md)
