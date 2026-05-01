# Conceitos: As Sete Tools Nativas

> _Aula contínua dos conceitos atômicos deste subcapítulo. Cada conceito vira uma seção `## N.` preenchida em sequência pela skill `estudo-explicar-conceito`. Cada nova iteração lê o que já foi escrito e dá continuidade — sem repetir vocabulário, sem reapresentar exemplos, sem saltos de tom._

## Roteiro

1. Por que pi.dev parte de apenas 4 tools por padrão — a filosofia de tool budget mínimo e por que grep/find/ls são opcionais
2. `read` — parâmetros, paginação com offset/limit, e o caso especial de imagens (JPG, PNG) como ImageContent
3. `write` — criação automática de diretórios pai e o que acontece em ambiente sem filesystem persistente entre invocações
4. `edit` — o contrato oldText/newText, o fuzzy fallback, e por que a precisão do match importa num agente headless
5. `bash` — execução de shell, streaming de stdout/stderr, e o killProcessTree como garantia de cleanup entre turnos
6. `grep`, `find`, `ls` — as três read-only tools opcionais, o que cada uma retorna, e respeito a .gitignore
7. A flag `--tools` como allowlist explícita — como passar nomes de tools como string[] para controlar exatamente o conjunto ativo
8. `--no-builtin-tools` e `--no-tools` — desabilitar o conjunto padrão para registrar as próprias tools sem conflito de nomes

<!-- ROTEIRO-END -->

<!-- PENDENTE-START -->
> _Pendente: 8 / 8 conceitos preenchidos._
<!-- PENDENTE-END -->

<!-- AULAS-START -->
## 1. Por que pi.dev parte de apenas 4 tools por padrão — a filosofia de tool budget mínimo e por que grep/find/ls são opcionais

Todo tool definition que o LLM recebe ocupa tokens — e esses tokens são consumidos em cada turno, antes que qualquer linha de código ou contexto do projeto apareça. O pi.dev trata isso como problema de projeto, não de conveniência: o sistema prompt mais as definições das quatro tools padrão (`read`, `write`, `edit`, `bash`) caem abaixo de 1.000 tokens totais. Servidores MCP populares como o Playwright MCP (21 tools) ou o Chrome DevTools MCP (26 tools) consomem de 14 mil a 18 mil tokens por sessão, integralmente, em cada requisição ao modelo. Isso é entre 7% e 9% de uma janela de 200k tokens queimados antes de o usuário digitar a primeira instrução.

A decisão de manter exatamente `read`, `write`, `edit` e `bash` como padrão não é arbitrária: elas cobrem o ciclo completo de qualquer tarefa de engenharia de software — ler código, criar ou sobrescrever arquivo, fazer edição cirúrgica e executar comando de shell. Qualquer coisa além disso é opt-in deliberado. A filosofia é a do Unix: primitivos composíveis, não features embutidas.

`grep`, `find` e `ls` ficam fora do conjunto padrão porque são redundantes quando `bash` está disponível — o shell pode executar `grep`, `find` e `ls` nativamente. Elas existem como tools explícitas para o caso de uso em que o operador quer um agente restrito: modo read-only, onde `bash` fica desabilitado para impedir qualquer mutação de filesystem ou execução arbitrária de comando. Nesse cenário, `grep`, `find` e `ls` oferecem capacidade de inspeção sem superfície de ataque de execução. Para a POC, esse trade-off vai entrar no filtro do subcapítulo 05.

A consequência prática para quem embarca pi.dev em Lambda: cada tool a menos no conjunto ativo é menos tokens gastos por turno, o que se traduz em menor custo, menor latência e melhor qualidade de decisão do LLM — modelos maiores degradam em seleção de tool quando o catálogo fica denso. Começar pelo conjunto mínimo e adicionar só o que a POC precisa é o padrão correto.

**Fontes utilizadas:**

- [What I learned building an opinionated and minimal coding agent — Mario Zechner](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)
- [Pi: The Minimal Agent Within OpenClaw — Armin Ronacher](https://lucumr.pocoo.org/2026/1/31/pi/)
- [Effective context engineering for AI agents — Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [pi-mono README — default tools](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)

## 2. `read` — parâmetros, paginação com offset/limit, e o caso especial de imagens (JPG, PNG) como ImageContent

`read` recebe um `filepath` obrigatório e dois parâmetros opcionais: `offset` (linha a partir da qual começar) e `limit` (número de linhas a ler). O comportamento padrão, sem `offset` nem `limit`, lê o arquivo a partir do início com um hard cap de 2.000 linhas ou 50 KB — o que vier primeiro. Para um arquivo de 10.000 linhas o modelo precisa paginar explicitamente: primeira chamada sem `offset`, segunda com `offset: 2000`, e assim por diante.

Essa paginação importa para a POC em dois contextos. Primeiro, quando `read` acessa arquivos de sessão JSONL grandes (cobertos no capítulo 2) — uma árvore de sessão longa pode facilmente ultrapassar 2.000 linhas, e o agente precisa saber que precisa paginar, não que o arquivo foi truncado silenciosamente. Segundo, quando o agente lê logs ou outputs de `bash` armazenados em arquivo temporário.

O caso especial de imagens é o mais técnico: quando `read` é chamado com um path para um arquivo cujo MIME type é `image/jpeg`, `image/png`, `image/gif` ou `image/webp`, o retorno não é string de texto — é um objeto `ImageContent` com os campos `type: "image"`, `data` (base64 da imagem) e `mimeType`. O LLM recebe isso como conteúdo visual, não textual. Para modelos multimodais, o mecanismo funciona. Para modelos que não suportam visão, a chamada falha ou retorna erro. Na POC, que não tem expectativa de análise visual, isso se traduz em uma regra simples: nunca apontar `read` para arquivos binários de imagem em caminhos que o agente possa confundir com texto.

**Fontes utilizadas:**

- [Built-in Tools — agentic-dev-io/pi-agent DeepWiki](https://deepwiki.com/agentic-dev-io/pi-agent/2.3-built-in-tools)
- [pi.dev session format — ImageContent definition](https://pi.dev/docs/latest/session-format)
- [pi-mono README](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)

## 3. `write` — criação automática de diretórios pai e o que acontece em ambiente sem filesystem persistente entre invocações

`write` recebe `filepath` e `content` e sobrescreve o arquivo inteiramente se ele existir, ou o cria do zero se não existir. O comportamento não-óbvio é que ele **cria automaticamente os diretórios pai** que ainda não existem na rota do `filepath`. Uma chamada para `/efs/sessions/abc123/output.json` numa instância Lambda onde `/efs/sessions/abc123/` ainda não foi criado não falha — o `write` cria o caminho completo.

Isso é relevante para a POC porque o agente pode produzir arquivos intermediários durante um turno (outputs de `bash`, rascunhos, arquivos de contexto) sem que o handler precise pré-criar a estrutura de diretórios. O EFS montado num ponto de acesso por tenant (coberto no capítulo 8) fica acessível como caminho normal de filesystem — do ponto de vista do `write`, é indistinguível de um disco local.

O problema é o `/tmp`. Em Lambda, `/tmp` tem até 10 GB e é persistente **dentro do mesmo container** — chamadas subsequentes que caem no mesmo container (warm start) encontram os arquivos que foram escritos antes. Chamadas que caem em container novo (cold start) não encontram nada. Um agente que escreve em `/tmp/session_state.json` no primeiro turno e tenta `read` no segundo turno pode falhar silenciosamente se o container foi reciclado entre invocações. A regra para a POC: `/tmp` serve para arquivos efêmeros dentro de um único turno; qualquer coisa que precisa sobreviver entre turnos vai para EFS ou S3.

**Fontes utilizadas:**

- [Built-in Tools — agentic-dev-io/pi-agent DeepWiki](https://deepwiki.com/agentic-dev-io/pi-agent/2.3-built-in-tools)
- [AWS Lambda — /tmp ephemeral storage](https://docs.aws.amazon.com/lambda/latest/dg/configuration-ephemeral-storage.html)
- [pi-mono README](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)

## 4. `edit` — o contrato oldText/newText, o fuzzy fallback, e por que a precisão do match importa num agente headless

`edit` recebe `filepath`, `oldText` e `newText`. A operação é uma substituição do primeiro match exato de `oldText` no arquivo pelo `newText`. Se o arquivo tiver múltiplas ocorrências do mesmo `oldText`, apenas a primeira é substituída — o LLM precisa fornecer contexto suficiente para tornar `oldText` único dentro do arquivo, ou usar múltiplas chamadas de `edit` em sequência.

O mecanismo de fallback é o `fuzzyFindText`: quando o match exato falha — por diferença de trailing whitespace, aspas normalizadas (e.g., aspas tipográficas `"` → `"`) ou dashes Unicode (`—` → `—`) — o pi.dev tenta um match normalizado. O retorno para o LLM é um diff unificado mostrando exatamente o que foi alterado, útil no modo interativo para revisão humana. Em modo headless, esse diff vai para o stream de eventos, mas nenhum humano o revisa — a responsabilidade de `oldText` ser preciso é inteiramente do LLM.

Para a POC, isso cria um risco específico: quando o agente edita arquivos de configuração (ex: ajustar um campo num arquivo de sessão JSONL ou num JSON de estado), um `oldText` levemente errado não vai causar erro explícito se o fuzzy fallback encontrar algo próximo. O resultado pode ser uma edição no lugar errado sem mensagem de erro. A mitigação é direta: na configuração da POC, para arquivos críticos que não devem ser editados pelo agente, o handler deve excluir `edit` do conjunto de tools ativas via `--tools` (coberto no conceito 7).

**Fontes utilizadas:**

- [Built-in Tools — agentic-dev-io/pi-agent DeepWiki](https://deepwiki.com/agentic-dev-io/pi-agent/2.3-built-in-tools)
- [pi-mono README — edit tool](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)

## 5. `bash` — execução de shell, streaming de stdout/stderr, e o killProcessTree como garantia de cleanup entre turnos

`bash` recebe uma string `command` e a executa num subprocesso shell. O retorno chega como stream de `stdout` e `stderr` intercalados — em modo interativo, o usuário vê a saída em tempo real; em modo headless (que é o que importa para a POC), a saída inteira é capturada como string e entregue ao LLM no evento `tool_result` ao fim da execução.

O detalhe crítico de runtime é o `killProcessTree`: quando uma tool call de `bash` é abortada — por timeout do Lambda, por request cancel, ou por um handler de `tool_call` que bloqueou a execução — o pi.dev não manda apenas um SIGTERM para o processo filho imediato. Ele mata toda a árvore de processos descendentes que o comando pode ter spawned. Sem isso, um `bash` que chama um subcomando que chama outro deixaria processos zumbi no container, consumindo CPU e memória até o Lambda reciclar o container — o que pode ser muito tempo num ambiente warm.

Para a POC, `bash` é a ferramenta mais poderosa e mais perigosa do conjunto. Poderosa porque permite que o agente execute qualquer lógica que caiba num comando shell — consultar a AWS CLI, processar arquivos, encadear utilitários. Perigosa porque sem restrições o agente pode executar comandos que o execution role do Lambda não tem permissão, causando falhas opacas, ou comandos que escrevem em paths locais sem EFS, perdendo estado entre invocações. O filtro do subcapítulo 05 vai especificar exatamente o que o agente da POC pode ou não fazer com `bash`.

Não há shell persistente entre turnos. Cada chamada a `bash` spaw um processo shell novo. Variáveis de ambiente setadas num turno anterior com `export VAR=valor` não sobrevivem ao próximo turno. Isso descarta uma classe inteira de usos de `bash` que funcionariam num shell interativo mas quebram em headless multi-turno.

**Fontes utilizadas:**

- [Built-in Tools — agentic-dev-io/pi-agent DeepWiki](https://deepwiki.com/agentic-dev-io/pi-agent/2.3-built-in-tools)
- [pi-mono extensions.md — tool lifecycle](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md)
- [pi-mono README](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)

## 6. `grep`, `find`, `ls` — as três read-only tools opcionais, o que cada uma retorna, e respeito a .gitignore

As três tools opcionais têm contratos simples e sem efeito colateral: nenhuma delas modifica o filesystem.

`grep` recebe um padrão (regex ou literal) e um caminho de busca, e retorna as linhas que fazem match com o caminho de arquivo e o número de linha de cada uma. Respeita `.gitignore` por padrão — arquivos e diretórios ignorados pelo Git não entram nos resultados. Para a POC, isso significa que arquivos de sessão JSONL em paths não rastreados pelo Git ainda aparecem nos resultados de `grep` se o path de busca for passado diretamente.

`find` recebe um padrão glob e um diretório de busca, e retorna os paths que fazem match, relativos ao diretório de busca. Também respeita `.gitignore`. A distinção em relação ao `bash find` nativo é que `find` como tool nativa do pi.dev não expõe as opções avançadas do `find(1)` do Unix — é uma interface simplificada que cobre os casos mais comuns sem deixar o LLM formular comandos `find` complexos que poderiam falhar por sintaxe.

`ls` recebe um `filepath` (que pode ser diretório ou arquivo) e retorna o conteúdo em ordem alfabética, com `/` sufixo para diretórios. Inclui dotfiles. Para a POC, `ls` é útil para que o agente inspecione a estrutura de diretórios de sessão no EFS antes de tentar `read` ou `write` — descoberta sem mutação.

A razão pela qual essas três tools existem separadas de `bash` é permitir um conjunto read-only seguro: `--tools read,grep,find,ls` dá ao agente capacidade de inspeção completa do filesystem sem nenhuma superfície de execução arbitrária. Para a POC, se o agente não precisar executar comandos shell, esse subset é preferível a habilitar `bash`.

**Fontes utilizadas:**

- [Built-in Tools — agentic-dev-io/pi-agent DeepWiki](https://deepwiki.com/agentic-dev-io/pi-agent/2.3-built-in-tools)
- [pi-mono README — optional tools](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)

## 7. A flag `--tools` como allowlist explícita — como passar nomes de tools como string[] para controlar exatamente o conjunto ativo

`--tools` é uma allowlist: quando presente, o agente tem acesso **apenas** às tools cujos nomes estão na lista, independente do que estiver habilitado por padrão ou registrado por extensions. O formato é uma lista de nomes separados por vírgula:

```bash
pi --tools read,grep,find,ls
```

Esse comando levanta um agente read-only, sem `write`, `edit` ou `bash`. A allowlist aplica ao conjunto total: tools nativas, tools de extensions carregadas e `customTools` passados via SDK — tudo que não estiver no `--tools` fica invisível para o LLM.

No SDK, a mesma lógica se aplica ao parâmetro `tools` de `createAgentSession`. A interface espera um `string[]` com os nomes, não instâncias de tool:

```typescript
const session = await createAgentSession({
  tools: ["read", "bash", "grep"],
  customTools: [myCustomTool],
  // ...
});
```

Aqui, o LLM vê `read`, `bash`, `grep` e `myCustomTool` (porque ela está em `customTools` e seu nome não está sendo bloqueado por uma allowlist que a excluiria). A `write` e `edit` nativas ficam fora.

Para a POC, o padrão de uso é definir a allowlist no handler antes de criar a sessão, com base no inventário aprovado no subcapítulo 05. Isso torna o conjunto de tools do agente explícito e auditável no código do handler — não depende de configuração externa, não muda entre invocações, não sofre de "tools extras carregadas por extensions não esperadas".

**Fontes utilizadas:**

- [pi-mono README — --tools flag](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [pi-mono/packages/coding-agent/docs/sdk.md](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md)

## 8. `--no-builtin-tools` e `--no-tools` — desabilitar o conjunto padrão para registrar as próprias tools sem conflito de nomes

`--no-builtin-tools` remove do agente as quatro tools nativas padrão (`read`, `write`, `edit`, `bash`). As tools opcionais (`grep`, `find`, `ls`) não são afetadas — elas já são opt-in e não fazem parte do conjunto padrão. O caso de uso principal é registrar custom tools com os mesmos nomes das tools nativas sem conflito: se você quer uma `read` customizada que adiciona logging de auditoria ou restringe o conjunto de paths permitidos, precisar remover a nativa primeiro.

`--no-tools` vai mais longe: desabilita **tudo** — nativas, opcionais, e tools registradas por extensions carregadas pelo agente. O efeito é um agente que começa com catálogo vazio, e você popula esse catálogo inteiramente via `customTools` no SDK. Para a POC, esse é o padrão mais controlado: nenhuma tool entra sem passar pelo código do handler.

A combinação que a POC provavelmente vai usar:

```typescript
const session = await createAgentSession({
  // sem tools nativas
  // customTools define o conjunto completo
  customTools: [readWithAudit, bashRestricted, grepPassthrough],
  // --no-tools via SDK equivale a passar tools: [] sem customTools sobrepostos
});
```

O equivalente via CLI para teste:

```bash
pi --no-tools -e ./my-tools.ts
```

Onde `my-tools.ts` é uma extension que registra o conjunto customizado. Isso é útil para validar o comportamento do agente com o conjunto aprovado antes de embarcar no Lambda.

A distinção entre `--no-builtin-tools` e `--no-tools` tem efeito prático quando o agente carrega extensions do disco (algo que não acontece no Lambda, mas acontece no desenvolvimento local). Com `--no-builtin-tools` as tools das extensions ainda entram; com `--no-tools` elas também ficam fora até que o `customTools` as re-registre explicitamente.

**Fontes utilizadas:**

- [feat(coding-agent): boot without built-in tools — Issue #555 pi-mono](https://github.com/badlogic/pi-mono/issues/555)
- [pi-mono CHANGELOG — --tools e --no-tools flags](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/CHANGELOG.md)
- [pi-mono README](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
<!-- AULAS-END -->

---

**Próximo subcapítulo** → [O Sistema de Extensions — Protocolo e Ciclo de Vida](../02-o-sistema-de-extensions-protocolo-e-ciclo-de-vida/CONTENT.md)
