# Conceitos: O Subset que Importa Para a POC Headless

> _Aula contínua dos conceitos atômicos deste subcapítulo. Cada conceito vira uma seção `## N.` (ou `## 0N.` quando o roteiro tem 10+ conceitos) preenchida em sequência pela skill `estudo-explicar-conceito`. Cada nova iteração lê o que já foi escrito e dá continuidade — sem repetir vocabulário, sem reapresentar exemplos, sem saltos de tom._

## Roteiro

1. Por que o TUI é descartado tecnicamente — ausência de TTY em Lambda/Fargate, o crash ou hang no harness como consequência direta, e por que não existe workaround viável para POC de produção
2. Por que o Print/JSON é descartado tecnicamente — sessão única por invocação vs exigência de múltiplos turnos com contexto preservado, e por que mesmo `--mode json` não resolve o problema de estado
3. O subset de RPC que entra no handler da POC — a flag `--mode rpc`, os tipos de evento que o handler precisa consumir (`text_delta`, `status`, `tool_call` com aprovação automática), e o que pode ser ignorado neste momento
4. O subset de SDK que entra no handler da POC — as classes mínimas (`createAgentSession`, `SessionManager`, `AuthStorage`, `ModelRegistry`), parâmetros obrigatórios vs opcionais, e os eventos do loop mínimo
5. O gancho para os capítulos 4 e 5 — como esse corte alimenta a decisão Lambda vs Fargate e a comparação SDK vs RPC no handler, com o que cada modo implica para o runtime de hosting

<!-- ROTEIRO-END -->

<!-- PENDENTE-START -->
> _Pendente: 5 / 5 conceitos preenchidos._
<!-- PENDENTE-END -->

<!-- AULAS-START -->

## 1. Por que o TUI é descartado tecnicamente — ausência de TTY em Lambda/Fargate, o crash ou hang no harness como consequência direta, e por que não existe workaround viável para POC de produção

O subcapítulo `01-modo-tui-o-terminal-interativo-e-por-que-nao-cabe-em-headless` estabeleceu os mecanismos: o `InteractiveMode` chama `process.stdin.setRawMode(true)`, que só existe quando stdin é uma instância de `tty.ReadStream`; sem TTY, a chamada lança `TypeError` ou o processo trava no event loop aguardando input que nunca chega. Lambda conecta stdin/stdout/stderr a sockets e pipes capturados pelo runtime — `process.stdout.isTTY` é `undefined` por construção arquitetural, não por configuração. Fargate com `pseudoTerminal: false` (o default para qualquer workload headless) produz o mesmo resultado.

O que este conceito adiciona é o argumento de por que não existe workaround válido para uma POC de produção, além da enumeração dos mecanismos:

**Não há "TUI degradado"**: o harness não detecta ausência de TTY e oferece automaticamente modo texto. A superfície do modo TUI — `setRawMode`, `clearLine`, `moveCursor`, `columns`, `resize` — é uma lista de pré-condições, não de preferências. O design deliberado é: cada modo tem suas pré-condições explícitas, e o invocador escolhe o modo certo para o ambiente. Não há degradação automática porque há modos alternativos corretos.

**Alocar PTY artificialmente não resolve**: Fargate expõe o parâmetro `pseudoTerminal: true` na definição de container, que instrui o daemon Docker a alocar um PTY. Mas alocar um PTY num container headless que não tem usuário na outra ponta apenas cria um TTY fantasma — o `InteractiveMode` inicializaria, mas ninguém digitaria. O modo TUI pressupõe interação humana em tempo real; uma POC servida via API Gateway não tem isso.

**Alternativas de acesso remoto saem do escopo**: tunelar um TTY via ECS Exec + SSH para criar um canal interativo ao container seria mais complexidade de infraestrutura do que simplesmente usar o SDK ou o RPC — que foram projetados exatamente para esse caso. O custo de engenharia de uma "solução TTY em Lambda" não tem relação com o benefício.

A conclusão é operacional: TUI é a ferramenta correta para desenvolvimento local (iterar sobre o comportamento do agente, testar tools, explorar o modelo de sessão com `/fork` e `/tree`), e a ferramenta errada para qualquer invocação programática em produção. O corte é limpo — não há zona cinzenta onde TUI "quase funciona" em Lambda.

**Fontes utilizadas:**

- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [TTY | Node.js v22 Documentation](https://nodejs.org/api/tty.html)
- [ContainerDefinition — Amazon ECS API Reference (pseudoTerminal)](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_ContainerDefinition.html)


## 2. Por que o Print/JSON é descartado tecnicamente — sessão única por invocação vs exigência de múltiplos turnos com contexto preservado, e por que mesmo `--mode json` não resolve o problema de estado

O subcapítulo `02-modo-print-json-saida-deterministica-para-scripts` formulou a limitação estrutural: cada invocação de `pi -p` ou `pi --mode json` cria um `AgentSession` do zero, processa o prompt, e encerra. O contexto existe apenas na memória do processo durante aquela execução. Com `--session <id>` é possível carregar um histórico prévio de arquivo, mas isso exige que o arquivo exista no mesmo filesystem, o que Lambda não garante entre invocações frias.

O problema de estado para a POC é mais específico do que "não persiste": ele é de **multiplexação de clientes**. Uma API multi-turno servindo N clientes simultâneos precisa que cada cliente tenha seu histórico isolado e que qualquer instância de compute — qualquer container Lambda frio, qualquer tarefa Fargate recém-iniciada — possa retomar exatamente aquela conversa sem depender do disco local da instância anterior. O Print/JSON não tem nem a primeira metade (sessão única por invocação) nem a segunda (sem backend de storage configurável).

Por que `--mode json` especificamente não resolve: a flag `--mode json` muda o formato de saída (eventos JSONL em vez de texto final) mas não muda o modelo de execução — o processo ainda inicia, processa um único prompt, e encerra. O stream de eventos mais rico que `--mode json` entrega é útil para debug e para pipes de automação single-shot, mas não cria nenhum canal de persistência. A sessão continua sendo descartada quando o processo fecha.

O critério de descarte é portanto arquitetural, não de configuração: Print/JSON foi projetado para o caso onde a unidade de trabalho é auto-contida. Qualquer tentativa de adaptar Print/JSON para multi-turno exigiria recriar por fora o que o modo RPC e o SDK já fazem por dentro — o processo persistente do RPC ou o `AgentSession` acumulativo do SDK. O descarte não é "Print/JSON é inferior", é "Print/JSON resolve o problema errado para esta POC".

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/json.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/json.md)
- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [Creating and resuming named sessions on launch · Issue #3416 · badlogic/pi-mono](https://github.com/badlogic/pi-mono/issues/3416)


## 3. O subset de RPC que entra no handler da POC — a flag `--mode rpc`, os tipos de evento que o handler precisa consumir (`text_delta`, `status`, `tool_call` com aprovação automática), e o que pode ser ignorado neste momento

Com TUI e Print/JSON descartados pelos conceitos `## 1.` e `## 2.`, o modo RPC entra como um dos dois candidatos reais. O subcapítulo `03-modo-rpc-protocolo-jsonl-sobre-stdin-stdout` cobriu o protocolo inteiro — framing JSONL, todos os tipos de evento, correlação por `id`, aprovação de tool calls. Este conceito recorta o que desse protocolo efetivamente entra no handler da POC.

**Invocação**: `pi --mode rpc`, opcionalmente com `--no-session` se a persistência for gerenciada externamente (EFS ou S3 customizado), ou com `--session-dir <path>` para apontar o diretório de sessões para um volume compartilhado. O handler spawna o processo uma vez por sessão de cliente e o mantém vivo enquanto a conversa está ativa.

**Eventos que o handler precisa consumir**:

| Evento | Para que serve |
|---|---|
| `message_update` com `assistantMessageEvent.type === "text_delta"` | Texto progressivo — cada chunk encaminhado ao cliente via SSE ou acumulado para resposta síncrona |
| `agent_end` | Sinal de que o turno completou — a Promise de turno resolveu, a resposta está completa |
| `auto_retry_end` com `success: false` | Falha definitiva — reportar erro ao cliente |

**Eventos que podem ser ignorados neste momento**:

- `queue_update` — atualiza filas de steering/followUp, irrelevante sem UI de steering
- `compaction_start`/`end` — sinaliza compactação automática de contexto; o handler não precisa reagir, só não pode travar ao receber
- `extension_error` — erro numa extension que não foi carregada; na POC sem extensions, nunca aparece
- `tool_execution_start`/`update`/`end` — detalhes de execução de ferramentas; o handler pode logar para diagnóstico mas não precisa apresentar ao cliente

**Aprovação automática de tool calls**: se o processo RPC for iniciado sem nenhuma extension de aprovação, o agente executa tools sem pedir confirmação — o comportamento default é auto-aprovar. Para a POC sem restrições de tool calls, essa é a configuração correta. Se for necessário bloquear tools específicas, a extension de aprovação responde `extension_ui_request` com `confirmed: false` baseado em regras estáticas — sem interação humana em loop.

O que o subset de RPC implica para o runtime de hosting fica reservado para o conceito `## 5.`; o que importa aqui é o mapa de eventos: 3 tipos a consumir ativamente, os demais a tolerar sem travar o parser.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/rpc.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/rpc.md)
- [RPC Mode — pi (hochej.github.io mirror)](https://hochej.github.io/pi-mono/coding-agent/rpc/)
- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)


## 4. O subset de SDK que entra no handler da POC — as classes mínimas (`createAgentSession`, `SessionManager`, `AuthStorage`, `ModelRegistry`), parâmetros obrigatórios vs opcionais, e os eventos do loop mínimo

O subcapítulo `04-modo-sdk-embedando-pidev-em-nodejs-typescript` cobriu cada classe da API do SDK em detalhe. Este conceito recorta o que desse universo entra no handler mínimo da POC — as escolhas concretas de instanciação, não os mecanismos por trás delas.

**Instanciação para Lambda**:

```typescript
import { createAgentSession, SessionManager, AuthStorage, ModelRegistry } from "@mariozechner/pi-coding-agent";

const authStorage = AuthStorage.create();
authStorage.setRuntimeApiKey("anthropic", process.env.ANTHROPIC_API_KEY!);
const modelRegistry = ModelRegistry.inMemory(authStorage);

// Por turno de cliente:
const { session } = await createAgentSession({
  sessionManager: SessionManager.open(sessionFilePath), // path no EFS ou caminho resolvido do S3
  authStorage,
  modelRegistry,
  // resourceLoader omitido — POC sem extensions customizadas
});
```

As escolhas de parâmetros obrigatórios vs opcionais para a POC:

| Parâmetro | Obrigatório para POC? | Por quê |
|---|---|---|
| `authStorage` com `setRuntimeApiKey` | Sim | Lambda sem `~/.pi/agent/auth.json` |
| `modelRegistry` via `inMemory()` | Sim | Lambda sem `~/.pi/agent/models.json` |
| `sessionManager` via `open()` ou customizado | Sim | Persistência multi-turno entre invocações |
| `resourceLoader` | Não | POC sem extensions — default vazio é suficiente |
| `model` | Não | Default do registry serve para a POC |
| `tools` | Não | Conjunto padrão de tools serve — restrinja se houver motivo de segurança |

**Loop mínimo de eventos**: o conceito `## 6.` do subcapítulo anterior estabeleceu o padrão. Para a POC:

```typescript
const chunks: string[] = [];
const unsubscribe = session.subscribe((event) => {
  if (event.type === "message_update" &&
      event.assistantMessageEvent?.type === "text_delta") {
    chunks.push(event.assistantMessageEvent.delta);
  }
});
await session.prompt(userMessage);
unsubscribe();
const responseText = chunks.join("");
```

Não há framing JSONL, não há parser de linha, não há correlação de `id`. O TypeScript elimina a categoria inteira de bugs de parsing que o modo RPC exige gerenciar manualmente.

O que o subset de SDK implica para o runtime de hosting — Lambda vs Fargate, o custo de cold start por sessão, o modelo de processo vs biblioteca — é o tema do conceito `## 5.`.

**Fontes utilizadas:**

- [pi-mono/packages/coding-agent/docs/sdk.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [pi.dev — SDK documentation](https://pi.dev/docs/latest/sdk)
- [@mariozechner/pi-coding-agent — npm](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)


## 5. O gancho para os capítulos 4 e 5 — como esse corte alimenta a decisão Lambda vs Fargate e a comparação SDK vs RPC no handler, com o que cada modo implica para o runtime de hosting

Os conceitos `## 3.` e `## 4.` definiram os dois candidatos: modo RPC (processo `pi --mode rpc` wrappado pelo handler) e SDK (biblioteca importada diretamente no handler Node.js). Cada um implica restrições diferentes sobre o runtime de hosting — e são exatamente essas implicações que os capítulos 4 e 5 vão explorar.

**O que o modo RPC implica para hosting**: o handler precisa gerenciar o ciclo de vida de um subprocesso por sessão de cliente. O processo `pi --mode rpc` consome memória e mantém o estado da sessão em memória enquanto está vivo. Para Lambda, isso significa que o processo morre junto com o container no fim de cada invocação — a menos que o handler use algum mecanismo de "container quente" para reutilizar o processo entre invocações do mesmo cliente (o que o Lambda não garante). Para Fargate com container de longa vida, o processo pode persistir entre turnos do mesmo cliente no mesmo container, mas isso cria o problema de roteamento: o segundo turno do cliente A precisa chegar ao mesmo container que hospeda o processo RPC da sessão de A. A decisão Lambda vs Fargate para RPC é, em parte, uma decisão sobre se o processo pode ser efêmero ou precisa ser persistente — e Fargate inclina a balança.

**O que o SDK implica para hosting**: não há subprocesso. O `AgentSession` criado pelo handler vive na heap do processo Node.js do Lambda/Fargate enquanto o handler está em execução. No fim da invocação Lambda, o `AgentSession` é garbage-collected — o estado em memória se perde. O que persiste é o que foi salvo no `SessionManager`: o arquivo JSONL da sessão no EFS ou no S3. A próxima invocação cria um novo `AgentSession` com `SessionManager.open(sessionFilePath)` e recarrega o histórico. Não há estado em processo para rotear — qualquer instância Lambda fria pode atender qualquer turno, desde que acesse o mesmo storage. Isso inclina o SDK para Lambda sem estado em processo.

A tabela que os capítulos 4 e 5 vão calibrar com os trade-offs de custo, cold start, streaming e robustez:

| Dimensão | RPC | SDK |
|---|---|---|
| Estado em processo | Sim — o processo RPC mantém o histórico em memória | Não — o histórico vive só no storage |
| Roteamento de sessão | Necessário — turno 2 precisa do mesmo processo do turno 1 | Desnecessário — qualquer instância lê o mesmo arquivo |
| Cold start | Maior — spawn de processo `pi` + carregamento do runtime | Menor — só inicialização do handler Node.js |
| Runtime adequado | Fargate (processo persistente) ou Lambda com warm containers | Lambda stateless (com EFS/S3 para sessão) |

Esse mapa de implicações é o insumo direto para o capítulo `04-lambda-ou-fargate-para-hospedar-pidev` (onde o runtime de hosting é decidido) e para o capítulo `05-sdk-embedado-no-handler-vs-wrapping-de-processo-rpc` (onde a comparação SDK vs RPC é feita em detalhe com código). Este subcapítulo entrega o leitor preparado para avaliar esses trade-offs com base no entendimento técnico dos dois modos — não como receptores de recomendação, mas como engenheiros com o mapa completo em mãos.

**Fontes utilizadas:**

- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [pi-mono/packages/coding-agent/docs/sdk.md — badlogic/pi-mono](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
- [Pi integration architecture — OpenClaw docs](https://docs.openclaw.ai/pi)

<!-- AULAS-END -->

---

**Próximo capítulo** → [O Modelo de Sessão Como Árvore JSONL](../../02-o-modelo-de-sessao-como-arvore-jsonl/CONTENT.md)
