# Estrutura do Livro

> Mapa rapido da organizacao do livro: capitulos, subcapitulos e conceitos. Mantido automaticamente pela skill `estudo-atualizar-struct` — nao edite a mao.

```
poc-pidev-na-aws-atras-de-api-gateway/ — POC End-to-End — Pi.dev Atrás de API Gateway na AWS Para Validação Com Cliente
├── 01-pidev-em-anatomia-tui-print-rpc-e-sdk/ — os quatro modos do harness e o subset que importa para POC headless
│   ├── 01-modo-tui-o-terminal-interativo-e-por-que-nao-cabe-em-headless/ — flags de invocação, rendering diferencial, dependências de TTY, e por que ambiente headless descarta esse modo
│   ├── 02-modo-print-json-saida-deterministica-para-scripts/ — invocação com -p e --mode json, event stream de saída única, limitação de sessão única e o que isso exclui para POC multi-turno
│   ├── 03-modo-rpc-protocolo-jsonl-sobre-stdin-stdout/ — framing LF-delimitado, tipos de eventos emitidos (text chunk, tool call, status), request/response correlation, e ciclo de vida do processo entre turnos
│   ├── 04-modo-sdk-embedando-pidev-em-nodejs-typescript/ — createAgentSession, SessionManager, ModelRegistry, AuthStorage, e o loop de leitura de eventos
│   └── 05-o-subset-que-importa-para-a-poc-headless/ — eliminação técnica de TUI e Print, flags e classes concretas de RPC e SDK que entram no handler, e o gancho para os capítulos 4 e 5
├── 02-o-modelo-de-sessao-como-arvore-jsonl/ — `id`, `parentId`, fork e branch, e por que isso muda o desenho de persistência
│   ├── 01-anatomia-de-uma-entrada-jsonl/ — campos do SessionHeader e SessionMessageEntry, roles possíveis e o comportamento append-only de escrita
│   ├── 02-a-arvore-de-sessao-dag-trunk-e-branches/ — como parentId transforma o arquivo num grafo dirigido acíclico, o conceito de leaf ativa, e a coexistência de branches no mesmo arquivo físico
│   ├── 03-entradas-especiais-compaction-branchsummary-e-labels/ — CompactionEntry com firstKeptEntryId, BranchSummaryEntry gerada ao trocar de branch, labels como bookmarks, e a distinção entre custom e custom_message
│   ├── 04-fork-e-branch-na-pratica-criar-e-navegar/ — o que acontece no arquivo JSONL durante um branch (mesmo arquivo) e durante um fork (novo arquivo com parentSession), e como invocar as operações via TUI e SDK
│   ├── 05-append-only-como-contrato-de-persistencia-efs-vs-s3/ — restrições que o contrato append-only impõe sobre EFS (append nativo, atômico) e S3 (sem append nativo, tensão com consistência eventual) e implicações de read-after-write
│   └── 06-operacoes-proibidas-e-restricoes-de-integridade/ — editar no meio, truncar, reordenar, colisão de id em forks concorrentes, e o sistema de migração de versão v1→v2→v3
├── 03-skills-extensions-e-o-sistema-de-tools/ — o que vem embutido, o que se pluga, e o que não vai entrar na POC
│   ├── 01-as-sete-tools-nativas/ — read, write, edit, bash, grep, find, ls: o que cada uma faz, como o LLM as invoca, e as flags que controlam o conjunto ativo
│   ├── 02-o-sistema-de-extensions-protocolo-e-ciclo-de-vida/ — carregamento de módulos TypeScript, a sequência tool_execution_start → tool_call → execute → tool_result → tool_execution_end, e o contrato de ExtensionAPI
│   ├── 03-custom-tools-via-sdk-registertool-e-customtools/ — diferença entre extensions em disco e customTools passados programaticamente ao criar uma sessão SDK, e implicações para agente embedded em Lambda
│   ├── 04-mcp-por-que-pidev-nao-adota-e-o-que-fazer/ — a decisão de design (overhead de contexto), o pi-mcp-adapter como válvula de escape, e implicações práticas para a POC
│   ├── 05-filtro-para-a-poc-o-que-entra-e-o-que-fica-fora/ — skill por skill: bash sem shell persistente, read/write sobre EFS ou /tmp, find/grep aceitáveis, web tools problemáticas; critério de corte headless-Lambda
│   └── 06-mapa-de-iam-permissoes-por-tool-que-entra-na-poc/ — o que cada tool aprovada exige do execution role e como esse mapa alimenta os capítulos 4, 6 e 7
├── 04-lambda-ou-fargate-para-hospedar-pidev/ — calibragem dos trade-offs específicos (cold start, runtime limit, streaming, custo)
├── 05-sdk-embedado-no-handler-vs-wrapping-de-processo-rpc/ — duas formas de embarcar pi.dev e quando cada uma vence
├── 06-api-gateway-na-frente-rotas-para-criar-sessao-enviar-turno-e-listar-sessoes/ — desenho dos endpoints HTTP da POC
├── 07-autenticacao-minima-com-cognito-ou-jwt-authorizer/ — barreira de acesso suficiente para entregar URL pública ao cliente
├── 08-efs-multi-tenant-por-access-point-sessoes-pidev-sobreviventes/ — redirecionando o diretório de sessões para storage compartilhado
├── 09-sessionmanager-customizado-backed-por-s3/ — alternativa quando EFS não cabe e como preservar fork/branch sobre object storage
├── 10-lambda-response-streaming-para-respostas-progressivas/ — entregando turnos do agente como SSE em vez de bloqueio síncrono
├── 11-logs-metricas-e-tracos-minimos-para-diagnostico/ — instrumentação suficiente para debugar quando a POC der ruim em produção
└── 12-empacotando-a-entrega-para-o-cliente/ — URL, credencial, instruções e roteiro de validação ponta-a-ponta
```
