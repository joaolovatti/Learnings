# Conceitos: Filtro para a POC — O Que Entra e O Que Fica Fora

> _Aula contínua dos conceitos atômicos deste subcapítulo. Cada conceito vira uma seção `## N.` preenchida em sequência pela skill `estudo-explicar-conceito`. Cada nova iteração lê o que já foi escrito e dá continuidade — sem repetir vocabulário, sem reapresentar exemplos, sem saltos de tom._

## Roteiro

1. O critério de corte formal — headless-compatível, stateless entre invocações, e dependências de rede declaradas
2. `bash` na POC — o que funciona sem TTY, ausência de shell persistente entre turnos, e o que fica fora por ser stateful
3. `read`, `write` e `edit` na POC — entram com a condição de path apontando para EFS ou /tmp, e o que acontece quando o container drain limpa /tmp
4. `grep`, `find` e `ls` na POC — entram sem restrição adicional e por quê seu comportamento headless é idêntico ao interativo
5. Tools que ficam de fora — web fetch (rede implícita), image analysis (modelo separado), tools interativas que dependem de ctx.hasUI
6. O conjunto final aprovado e como passá-lo — a lista explícita de tools aprovadas e como configurar via --tools na CLI e via customTools no SDK

<!-- ROTEIRO-END -->

<!-- PENDENTE-START -->
> _Pendente: 6 / 6 conceitos preenchidos._
<!-- PENDENTE-END -->

<!-- AULAS-START -->
## 1. O critério de corte formal — headless-compatível, stateless entre invocações, e dependências de rede declaradas

Uma tool entra no conjunto aprovado da POC se e somente se satisfaz três condições simultaneamente:

**Headless-compatível**: a tool não depende de TTY, não usa `ctx.hasUI` para interação humana em runtime, e não tem comportamento diferente entre modo interativo e não-interativo que produza resultados incorretos silenciosamente (ex: uma tool que retorna "OK" em headless mesmo quando a operação falhou porque não pôde confirmar com o usuário).

**Stateless entre invocações**: o estado que a tool usa ou produz não precisa sobreviver além do escopo da invocação Lambda corrente, OU esse estado é escrito em storage externo durável (EFS, S3) de forma explícita e controlada. Uma tool que escreve em memória local ou em `/tmp` com expectativa de leitura no próximo turno (numa invocação diferente) viola essa condição — como visto no conceito 3 do subcapítulo 01.

**Dependências de rede declaradas**: qualquer chamada de rede que a tool fizer precisa ser uma dependência explícita da POC — listada, com permissão IAM correspondente, e com tratamento de erro adequado. Tools que fazem chamadas de rede implícitas (ex: web fetch para qualquer URL sem controle) não passam no critério porque introduzem superfície de ataque e falhas de runtime não-determinísticas.

**Fontes utilizadas:**

- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
- [pi-mono extensions.md — ctx.hasUI](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)

## 2. `bash` na POC — o que funciona sem TTY, ausência de shell persistente entre turnos, e o que fica fora por ser stateful

`bash` entra no conjunto aprovado, com as restrições a seguir. A ausência de TTY num container Lambda significa que comandos que dependem de terminal interativo — editores (`vim`, `nano`), paginadores (`less`, `more`), ferramentas que detectam se stdout é um terminal (e mudam comportamento) — não funcionam corretamente. Para a POC, o `bash` é restrito a comandos de processamento de dados: parsing de JSON com `jq`, transformações com `awk`/`sed`, verificações de existência de arquivo, e chamadas à AWS CLI quando necessário.

A ausência de shell persistente entre turnos (estabelecida no conceito 5 do subcapítulo 01) descarta qualquer uso de `bash` para fluxo de estado via variáveis de ambiente ou arquivos de configuração de shell (`~/.bashrc`, `source ./env`). Cada comando `bash` começa num shell limpo.

O que fica fora de `bash` na POC:
- Comandos que iniciam processos daemon (ex: `nohup server &`)
- Comandos de instalação de pacotes (`apt-get`, `npm install -g`) — as dependências devem estar no bundle da imagem Lambda
- Comandos que modificam configuração de sistema (`/etc/...`) — filesystem efêmero e sem permissão
- Qualquer chamada de rede implícita não prevista no mapa de IAM do subcapítulo 06

**Fontes utilizadas:**

- [Built-in Tools — agentic-dev-io/pi-agent DeepWiki](https://deepwiki.com/agentic-dev-io/pi-agent/2.3-built-in-tools)
- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)

## 3. `read`, `write` e `edit` na POC — entram com a condição de path apontando para EFS ou /tmp, e o que acontece quando o container drain limpa /tmp

As três tools de acesso a arquivo entram no conjunto aprovado condicionalmente: o agente só deve apontar `read`, `write` e `edit` para paths que fazem sentido no contexto da invocação Lambda.

Para estado que precisa sobreviver entre turnos (arquivos de sessão JSONL, contexto do agente), o path correto é o ponto de montagem EFS (ex: `/efs/sessions/tenant-id/session-id/`). Qualquer `read` ou `write` nesses paths funciona como filesystem local e persiste além do ciclo de vida do container.

Para arquivos temporários de processamento dentro de um único turno (ex: um JSON intermediário que `bash` escreve e `read` lê na mesma invocação), `/tmp` é aceitável. O risco é o warm start parcialmente persistente descrito no conceito 3 do subcapítulo 01: se o container não foi reciclado, arquivos de `/tmp` de invocações anteriores podem estar lá. A POC precisa nomear arquivos temporários de forma que inclua o `requestId` da invocação corrente para evitar conflitos:

```bash
# correto — usa requestId para isolar
TMPFILE="/tmp/$AWS_REQUEST_ID/output.json"
mkdir -p $(dirname $TMPFILE)
# ...
```

`edit` sobre arquivos no EFS funciona corretamente, pois o EFS é append/modify por natureza. `edit` sobre arquivos em `/tmp` tem o mesmo comportamento, mas com o caveat de que o arquivo precisa existir — um `edit` num arquivo que `write` deveria ter criado numa invocação anterior (que não existe porque o container foi reciclado) falha com "file not found".

**Fontes utilizadas:**

- [AWS Lambda — /tmp ephemeral storage](https://docs.aws.amazon.com/lambda/latest/dg/configuration-ephemeral-storage.html)
- [Developers guide to using Amazon EFS with Amazon ECS and AWS Fargate — AWS Containers Blog](https://aws.amazon.com/blogs/containers/developers-guide-to-using-amazon-efs-with-amazon-ecs-and-aws-fargate-part-1/)

## 4. `grep`, `find` e `ls` na POC — entram sem restrição adicional e por quê seu comportamento headless é idêntico ao interativo

As três read-only tools opcionais (`grep`, `find`, `ls`) entram no conjunto aprovado sem nenhuma restrição adicional além das que se aplicam a qualquer acesso de filesystem. O motivo é simples: as três são operações de inspeção puras — não modificam nenhum arquivo, não fazem chamadas de rede, não dependem de TTY, e o resultado que retornam num container headless é exatamente o mesmo que num terminal interativo.

O único ponto de atenção é o respeito a `.gitignore` que `grep` e `find` implementam por padrão: se o ponto de montagem EFS não tem um `.gitignore` configurado (o que é provável, já que é um diretório de sessão, não um repositório Git), as três tools se comportam como se `.gitignore` não existisse — o que é o comportamento correto.

Para a POC, as três tools são úteis para que o agente descubra a estrutura de sessões no EFS antes de tentar operações de leitura ou escrita: `ls /efs/sessions/` para ver os tenants, `find /efs/sessions/tenant-abc/` para ver os arquivos de sessão disponíveis, `grep "sessionId" /efs/sessions/tenant-abc/*.jsonl` para localizar uma sessão específica por conteúdo.

**Fontes utilizadas:**

- [Built-in Tools — agentic-dev-io/pi-agent DeepWiki](https://deepwiki.com/agentic-dev-io/pi-agent/2.3-built-in-tools)
- [pi-mono README — read-only tools](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)

## 5. Tools que ficam de fora — web fetch (rede implícita), image analysis (modelo separado), tools interativas que dependem de ctx.hasUI

Três categorias de tools ficam fora do conjunto aprovado:

**Web fetch**: qualquer tool que faz chamadas HTTP para URLs arbitrárias — incluindo capacidades de fetch embutidas em algumas versions do pi.dev ou registráveis via extension — viola o critério de "dependências de rede declaradas". Uma chamada a uma URL externa não prevista no mapa de IAM não pode ser autorizada pelo execution role do Lambda, e mesmo que pudesse, introduz dependência de disponibilidade de serviço externo no caminho crítico de uma demonstração ao cliente. Se a POC precisar de acesso a APIs específicas, elas entram como `customTools` com chamadas de rede explícitas e permissões IAM correspondentes — não como web fetch genérico.

**Image analysis**: capacidade de análise de imagens depende de um modelo de visão separado ou de uma extension específica. Para a POC, o agente não tem use case de análise visual — o conteúdo das sessões é texto (JSONL). Incluir uma tool de imagem aumentaria o catálogo sem benefício.

**Tools interativas que dependem de `ctx.hasUI`**: qualquer tool ou handler de extension que chama `ctx.ui.confirm()`, `ctx.ui.ask()`, ou métodos similares depende de haver uma TUI ativa. Em headless, esses métodos retornam valores default (tipicamente `false` ou `undefined`) sem aviso. Tools construídas em torno desse padrão simplesmente não funcionam em Lambda — e pior, podem parecer funcionar (não lançam exceção) enquanto tomam decisões erradas silenciosamente. Nenhuma tool da POC pode ter `ctx.hasUI` como dependency de caminho crítico.

**Fontes utilizadas:**

- [pi-mono extensions.md — ctx.hasUI headless behavior](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)
- [Pi Coding Agent Sandbox Analysis — Agent Safehouse](https://agent-safehouse.dev/docs/agent-investigations/pi)

## 6. O conjunto final aprovado e como passá-lo — a lista explícita de tools aprovadas e como configurar via --tools na CLI e via customTools no SDK

O conjunto final de tools aprovadas para a POC é:

| Tool | Status | Condição |
|---|---|---|
| `read` | Aprovada | Paths em EFS ou `/tmp` com `$AWS_REQUEST_ID` |
| `write` | Aprovada | Paths em EFS ou `/tmp` com `$AWS_REQUEST_ID` |
| `edit` | Aprovada | Paths em EFS (arquivo deve existir previamente) |
| `bash` | Aprovada | Sem TTY-dependência, sem daemon, sem instalação de pacote |
| `grep` | Aprovada | Sem restrição adicional |
| `find` | Aprovada | Sem restrição adicional |
| `ls` | Aprovada | Sem restrição adicional |
| web fetch | Fora | Rede implícita não declarada |
| image analysis | Fora | Sem use case na POC |
| tools interativas (ctx.hasUI) | Fora | Headless incompatível |

Para configurar no SDK:

```typescript
const session = await createAgentSession({
  // tools nativas ativas (allowlist explícita)
  tools: ["read", "write", "edit", "bash", "grep", "find", "ls"],
  // nenhuma customTool adicional na POC base
  customTools: [],
  // sem agentDir — nenhuma extension carregada em disco
  agentDir: undefined,
  // ...
});
```

Para teste local via CLI:

```bash
pi --tools read,write,edit,bash,grep,find,ls
```

Esse conjunto e essa configuração são o input direto para o mapa de IAM do subcapítulo 06: cada tool aprovada determina exatamente quais ações IAM o execution role precisa ter.

**Fontes utilizadas:**

- [pi-mono README — --tools flag](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [pi-mono/packages/coding-agent/docs/sdk.md](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)
- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
<!-- AULAS-END -->

---

**Próximo subcapítulo** → [Mapa de IAM — Permissões por Tool que Entra na POC](../06-mapa-de-iam-permissoes-por-tool-que-entra-na-poc/CONTENT.md)
