# Conceitos: MCP: Por Que Pi.dev Não Adota e o Que Fazer Quando Você Precisa

> _Aula contínua dos conceitos atômicos deste subcapítulo. Cada conceito vira uma seção `## N.` preenchida em sequência pela skill `estudo-explicar-conceito`. Cada nova iteração lê o que já foi escrito e dá continuidade — sem repetir vocabulário, sem reapresentar exemplos, sem saltos de tom._

## Roteiro

1. O que é MCP (Model Context Protocol) — o padrão de tool servers, separação host/server, e por que ganhou tração no ecossistema
2. O overhead de contexto como argumento central do pi.dev — custo fixo por request das tool definitions, o problema com muitos servidores conectados, e por que a decisão do pi.dev é "não e não vai mudar"
3. Como o pi.dev resolve o que MCP promete — extensions TypeScript e custom tools como alternativa mais eficiente e portável
4. O `pi-mcp-adapter` — o que ele faz (proxy de tool calls MCP para o formato de custom tools), como é configurado, e o que ele não resolve (o overhead de contexto continua)
5. AWS e o ecossistema MCP — quais AWS tools estão disponíveis como MCP servers, o awslabs/agent-plugins como referência, e quando usar o adaptador vs implementar diretamente
6. Critério de decisão para a POC — superfície de tool por turno × custo de contexto × manutenibilidade, e por que a POC preferirá custom tools diretas

<!-- ROTEIRO-END -->

<!-- PENDENTE-START -->
> _Pendente: 6 / 6 conceitos preenchidos._
<!-- PENDENTE-END -->

<!-- AULAS-START -->
## 1. O que é MCP (Model Context Protocol) — o padrão de tool servers, separação host/server, e por que ganhou tração no ecossistema

MCP é um protocolo aberto criado pela Anthropic que define como um LLM (via host — o agente ou IDE) se comunica com servidores externos que expõem tools, recursos e prompts. A separação é arquitetural: o **host** (ex: Claude Code, Cursor, qualquer agente) faz as chamadas ao modelo e repassa tool calls; o **server** MCP implementa as tools e responde às chamadas via JSON-RPC sobre stdio, SSE ou WebSocket.

O protocolo ganhou tração porque resolve um problema real de ecossistema: tools populares (GitHub, Slack, Postgres, Figma, AWS) passaram a publicar MCP servers oficiais, e qualquer host compatível passa a ter acesso a essas tools sem que o desenvolvedor do host precise implementar cada integração. Para o usuário final, conectar um MCP server ao agente favorito é questão de configuração, não de código.

A estrutura de uma tool call via MCP do ponto de vista do LLM é idêntica à de uma tool nativa: nome, parâmetros, resultado. A diferença está no transporte: em vez do `execute()` local rodando no mesmo processo, a chamada vai via JSON-RPC para o servidor MCP (que pode ser local ou remoto), o resultado volta pelo mesmo canal, e o host repassa ao LLM.

**Fontes utilizadas:**

- [Architecture overview — Model Context Protocol docs](https://modelcontextprotocol.io/docs/learn/architecture)
- [MCP Token Counter: Why Your Tools Are Silently Eating Your Context Window — MCP Playground](https://mcpplaygroundonline.com/blog/mcp-token-counter-optimize-context-window)
- [pi-mono README — "does not and will not support MCP"](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)

## 2. O overhead de contexto como argumento central do pi.dev — custo fixo por request das tool definitions, o problema com muitos servidores conectados, e por que a decisão do pi.dev é "não e não vai mudar"

Quando um host conecta um MCP server, ele recebe o catálogo de tools daquele servidor e injeta as definições no prompt que vai para o modelo em cada turno. Isso é um custo fixo por request — diferente do histórico de conversa, que cresce ao longo da sessão, as definições de tools não crescem mas também nunca desaparecem. Um servidor MCP com 21 tools pode custar 14 mil tokens de overhead em toda requisição, independente de o agente usar alguma delas naquele turno.

O README oficial do pi.dev afirma explicitamente: "pi does not and will not support MCP. MCP servers are overkill for most use cases, and they come with significant context overhead." A decisão não é técnica no sentido de "não conseguimos implementar" — é uma posição de design deliberada sobre o que o pi.dev quer ser: um harness mínimo onde cada token é justificado, não um broker de ecossistema.

O argumento se fortalece com os números reais: um time de engenharia que conecta 3 MCP servers com 81 tools no total queimava 20.000 tokens por sessão antes de qualquer instrução — 16% de uma janela de 128k tokens. Para modelos que degradam em seleção de tool quando o catálogo fica grande (documentado na literatura de context engineering), isso não é só custo monetário, é degradação de qualidade.

**Fontes utilizadas:**

- [What I learned building an opinionated and minimal coding agent — Mario Zechner](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)
- [pi-mono README — MCP statement](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [MCP Context Window Explained: Where Tokens Actually Go — DeployStack](https://deploystack.io/blog/how-mcp-servers-use-your-context-window)

## 3. Como o pi.dev resolve o que MCP promete — extensions TypeScript e custom tools como alternativa mais eficiente e portável

A promessa do MCP é desacoplamento: você não precisa reescrever cada integração para cada agente. O pi.dev oferece o mesmo resultado por um caminho diferente: o sistema de extensions e `customTools` (cobertos nos subcapítulos 02 e 03) permite integrar qualquer serviço externo escrevendo um `AgentTool` em TypeScript — sem protocolo de transporte intermediário, sem servidor separado, sem overhead de definições não utilizadas.

A diferença de eficiência é direta: um `AgentTool` que chama a AWS SDK tem apenas a sua própria definição no prompt (tipicamente 50–200 tokens), não o catálogo inteiro de um MCP server. Se o agente da POC precisa de 3 integrações AWS, são 3 tools com seus próprios tokens — não um servidor MCP com 30 tools das quais 27 nunca serão chamadas.

A portabilidade também é melhor para Lambda: uma custom tool é código JavaScript que roda no mesmo processo do handler, sem servidor externo para gerenciar, sem porta aberta, sem processo filho. Para ambientes serverless onde cada recurso extra tem custo (memória, tempo de inicialização, configuração de rede), isso é relevante.

**Fontes utilizadas:**

- [Pi: The Minimal Agent Within OpenClaw — Armin Ronacher](https://lucumr.pocoo.org/2026/1/31/pi/)
- [Effective context engineering for AI agents — Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [pi-mono README](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)

## 4. O `pi-mcp-adapter` — o que ele faz (proxy de tool calls MCP para o formato de custom tools), como é configurado, e o que ele não resolve (o overhead de contexto continua)

O `pi-mcp-adapter` é um pacote de terceiros (não oficial do pi.dev) que faz o bridge entre um MCP server e o formato de `customTools` do pi.dev. Ele conecta a um ou mais MCP servers, busca o catálogo de tools deles, e os transforma em instâncias de `AgentTool` que podem ser passadas via `customTools` a `createAgentSession`.

```typescript
import { createMcpAdapter } from "pi-mcp-adapter";

const mcpTools = await createMcpAdapter({
  servers: [
    { command: "npx", args: ["-y", "@modelcontextprotocol/server-github"] }
  ]
});

const session = await createAgentSession({
  customTools: mcpTools,
  // ...
});
```

O que o adaptador **resolve**: permite usar MCP servers existentes com pi.dev sem modificar o pi.dev. Especialmente útil se o MCP server em questão já está sendo usado por outros agentes no mesmo projeto e não vale duplicar a implementação.

O que o adaptador **não resolve**: o overhead de contexto. Todas as tools do servidor MCP ainda entram no catálogo do agente e consomem tokens em cada turno. O adaptador apenas muda o formato, não a quantidade de definições injetadas no prompt. Para a POC com Lambda, adicionar um MCP server de 20+ tools via adaptador continua sendo o mesmo anti-padrão de custo de contexto.

**Fontes utilizadas:**

- [pi-mcp-adapter — GitHub](https://github.com/nicobailon/pi-mcp-adapter)
- [MCP Token Counter — MCP Playground](https://mcpplaygroundonline.com/blog/mcp-token-counter-optimize-context-window)

## 5. AWS e o ecossistema MCP — quais AWS tools estão disponíveis como MCP servers, o awslabs/agent-plugins como referência, e quando usar o adaptador vs implementar diretamente

A AWS mantém o repositório `awslabs/agent-plugins` com plugins para agentes de codificação que incluem skills e MCP servers para operações AWS comuns: SAM deploy, CDK Lambda constructs, serverless CI/CD pipeline, e outros. Esses plugins são projetados para agentes como GitHub Copilot e Claude Code — hosts que suportam MCP nativamente.

Para a POC, esses plugins representam um atalho tentador mas incorreto: usar o `pi-mcp-adapter` para conectar o MCP server AWS seria carregar um catálogo de 15–30 tools de infraestrutura (deploy, criar stack, listar funções) no agente que vai atender turnos de conversação do cliente. O agente da POC não precisa fazer deploy da própria infraestrutura — precisa ler e escrever no EFS, eventualmente chamar um serviço específico. Essas 2–3 operações não justificam o overhead de um server AWS completo.

Quando usar o adaptador vs implementar diretamente:

| Usar `pi-mcp-adapter` | Implementar como `AgentTool` diretamente |
|---|---|
| Server MCP já existe e é mantido por terceiro | Precisa de 2–5 operações específicas |
| Catálogo é pequeno (< 5 tools) | Catálogo do servidor é grande (10+ tools) |
| Ambiente não é serverless crítico em custo | Lambda/Fargate onde cada token tem custo |
| Agente genuinamente precisa de toda a breadth do server | Só um subset pequeno do server é relevante |

Para a POC: implementar diretamente.

**Fontes utilizadas:**

- [awslabs/agent-plugins — GitHub](https://github.com/awslabs/agent-plugins)
- [From Local MCP Server to AWS Deployment in Two Commands — DEV Community](https://dev.to/aws/from-local-mcp-server-to-aws-deployment-in-two-commands-ag4)
- [pi-mcp-adapter — GitHub](https://github.com/nicobailon/pi-mcp-adapter)

## 6. Critério de decisão para a POC — superfície de tool por turno × custo de contexto × manutenibilidade, e por que a POC preferirá custom tools diretas

Três variáveis determinam a escolha entre MCP (via adaptador) e `customTools` diretas para qualquer integração na POC:

**Superfície de tool por turno**: quantas das tools do servidor MCP o agente da POC vai usar num turno típico? Se a resposta é 1–2 de 20+, o overhead de carregar as outras 18 no prompt não se justifica. Custom tools diretas expõem exatamente o que é necessário.

**Custo de contexto**: cada token desperdiçado em definição de tool não usada é custo monetário (Lambda cobra por GB·s, e o modelo cobra por token de input) e custo de qualidade (mais tools no catálogo → maior probabilidade de hallucination de tool call). Para a POC que pretende demonstrar ao cliente viabilidade da solução, custo e qualidade são métricas que precisam ser defensáveis.

**Manutenibilidade**: uma custom tool escrita pelo mesmo time que escreve o handler é código que o time entende, testa unitariamente e refatora junto com o resto da POC. Um MCP server de terceiro é uma dependência externa — versões, breaking changes, disponibilidade são fora do controle.

A conclusão para a POC é direta: custom tools diretas para todas as integrações que ela precisa. O `pi-mcp-adapter` fica como opção de escape se, em iteração futura, um MCP server com catálogo pequeno e bem mantido oferecer funcionalidade que o time não quer reimplementar — mas não como padrão de arquitetura da POC inicial.

**Fontes utilizadas:**

- [Effective context engineering for AI agents — Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [How to Optimize MCP Server Token Usage — MindStudio](https://www.mindstudio.ai/blog/optimize-mcp-server-token-usage)
- [pi-mono README — MCP statement](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
<!-- AULAS-END -->

---

**Próximo subcapítulo** → [Filtro para a POC — O Que Entra e O Que Fica Fora](../05-filtro-para-a-poc-o-que-entra-e-o-que-fica-fora/CONTENT.md)
