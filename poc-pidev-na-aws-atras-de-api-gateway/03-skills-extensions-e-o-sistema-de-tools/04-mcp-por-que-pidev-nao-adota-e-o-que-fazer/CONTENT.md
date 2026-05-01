# MCP: Por Que Pi.dev Não Adota e o Que Fazer Quando Você Precisa

![capa](cover.png)

## Sobre este subcapítulo

Model Context Protocol (MCP) é o padrão que permite a um LLM invocar tools expostas por servidores externos num protocolo uniforme. O pi.dev tomou uma decisão de design explícita: não adotar MCP nativamente. A justificativa é direta — servidores MCP introduzem overhead de contexto significativo (cada servidor expõe seu catálogo de tools no prompt, consumindo tokens em todo turno mesmo quando as tools não são usadas), e para a maioria dos casos de uso o mecanismo de extensions e custom tools do pi.dev é mais eficiente.

Entender essa decisão — e os seus limites — é importante para a POC porque o ecossistema de ferramentas AWS tem adaptadores MCP disponíveis. O subcapítulo esclarece quando essa limitação importa, quando não importa, e qual é a válvula de escape disponível (`pi-mcp-adapter`) caso uma integração via MCP seja de fato necessária.

## Estrutura

O subcapítulo cobre: (1) **o que é MCP e o problema que ele resolve** — o protocolo padronizado de tool servers, a separação entre host (o agente) e server (a implementação da tool), e por que o ecossistema criou momentum em torno dele; (2) **a decisão de design do pi.dev** — o overhead de contexto como argumento central, a alternativa que o pi.dev oferece (extensions TypeScript, custom tools), e o link para a documentação oficial que afirma explicitamente "pi does not and will not support MCP"; (3) **o `pi-mcp-adapter` como válvula de escape** — o que o adaptador faz (proxy de ferramentas MCP para o formato de custom tools do pi.dev), como ele é configurado, e o custo que ele não resolve (o overhead de contexto continua existindo, só fica sob controle do desenvolvedor); (4) **implicações práticas para a POC** — quais integrações AWS disponíveis como MCP servers são relevantes para a POC, se vale usar o adaptador ou implementar as tools diretamente como custom tools, e o critério de decisão (superfície de tool por turno × custo de contexto × manutenibilidade).

## Objetivo

Ao terminar este subcapítulo, o leitor entenderá por que o pi.dev não suporta MCP, saberá avaliar quando o `pi-mcp-adapter` é uma solução razoável e quando é overhead desnecessário, e terá um critério claro para decidir se integrações de terceiros entram na POC via adaptador MCP ou como custom tools diretas.

## Conceitos

A explicação completa destes conceitos vive em [`CONCEPTS.md`](CONCEPTS.md), construída sequencialmente pela skill `estudo-explicar-conceito`.

1. O que é MCP (Model Context Protocol) — o padrão de tool servers, separação host/server, e por que ganhou tração no ecossistema
2. O overhead de contexto como argumento central do pi.dev — custo fixo por request das tool definitions, o problema com muitos servidores conectados, e por que a decisão do pi.dev é "não e não vai mudar"
3. Como o pi.dev resolve o que MCP promete — extensions TypeScript e custom tools como alternativa mais eficiente e portável
4. O `pi-mcp-adapter` — o que ele faz (proxy de tool calls MCP para o formato de custom tools), como é configurado, e o que ele não resolve (o overhead de contexto continua)
5. AWS e o ecossistema MCP — quais AWS tools estão disponíveis como MCP servers, o awslabs/agent-plugins como referência, e quando usar o adaptador vs implementar diretamente
6. Critério de decisão para a POC — superfície de tool por turno × custo de contexto × manutenibilidade, e por que a POC preferirá custom tools diretas

## Fontes utilizadas

- [Pi README — declaração explícita "does not and will not support MCP"](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [pi-mcp-adapter — GitHub, Token-efficient MCP adapter for Pi](https://github.com/nicobailon/pi-mcp-adapter)
- [From Local MCP Server to AWS Deployment in Two Commands — DEV Community](https://dev.to/aws/from-local-mcp-server-to-aws-deployment-in-two-commands-ag4)
- [awslabs/agent-plugins — Agent Plugins for AWS (MCP e skills para coding agents)](https://github.com/awslabs/agent-plugins)
- [What I learned building an opinionated and minimal coding agent — Mario Zechner](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)
