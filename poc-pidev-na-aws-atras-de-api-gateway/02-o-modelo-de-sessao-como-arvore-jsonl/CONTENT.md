# O Modelo de Sessão Como Árvore JSONL

![capa](cover.png)

## Sobre este capítulo

Pi.dev persiste sessões como arquivos JSONL onde cada linha é um nó com `id` e `parentId` — o que torna a estrutura uma árvore, não uma lista linear. Isso é deliberado: permite fork (criar uma nova branch a partir de qualquer ponto da conversa) e branch navigation sem duplicar dados. Para o engenheiro que vai resolver persistência fora do disco local, esse modelo é a informação mais crítica: saber o que está no arquivo determina o que precisa ser salvo, como serializar para S3 ou replicar via EFS, e o que acontece quando um fork é perdido.

Este capítulo existe aqui, logo após a anatomia dos modos, porque toda decisão de persistência nos capítulos 8 e 9 — EFS com access points, SessionManager sobre S3 — depende de saber exatamente o que está sendo persistido. Quem pula esta leitura tende a tratar a sessão como um log linear e só descobre o problema quando o cliente tenta retomar um fork que sumiu.

## Estrutura

O capítulo cobre: (1) **formato JSONL linha a linha** — anatomia de uma entrada de sessão (`id`, `parentId`, `role`, `content`, metadados), como o pi.dev lê e escreve o arquivo em append-only; (2) **a semântica de árvore** — por que parentId transforma o arquivo num grafo dirigido acíclico, o que distingue o trunk do fork, como branches coexistem no mesmo arquivo; (3) **fork e branch na prática** — como o usuário cria um fork via TUI ou via SDK, o que acontece no arquivo JSONL quando isso ocorre, e como pi.dev navega para retomar um branch específico; (4) **implicações diretas para persistência** — o que "continuar uma sessão" significa em termos de leitura de arquivo, por que append-only importa para EFS mas cria tensão com S3, e por que a ordem das linhas no arquivo não pode ser ignorada ao serializar; (5) **operações proibidas** — o que não fazer com o arquivo (editar linhas no meio, truncar, reordenar) e o que isso causa no harness.

## Objetivo

Ao terminar este capítulo, o leitor saberá ler e interpretar um arquivo de sessão JSONL do pi.dev, entenderá a diferença entre um trunk e um branch, saberá o que acontece no arquivo durante um fork, e conseguirá avaliar com precisão as restrições que essa estrutura impõe sobre qualquer mecanismo de persistência externo (EFS ou S3). Esse entendimento é pré-requisito direto para os capítulos 8 e 9.

## Subcapítulos

1. [Anatomia de uma Entrada JSONL](01-anatomia-de-uma-entrada-jsonl/CONTENT.md) — campos do SessionHeader e SessionMessageEntry, roles possíveis e o comportamento append-only de escrita
2. [A Árvore de Sessão — DAG, Trunk e Branches](02-a-arvore-de-sessao-dag-trunk-e-branches/CONTENT.md) — como parentId transforma o arquivo num grafo dirigido acíclico, o conceito de leaf ativa, e a coexistência de branches no mesmo arquivo físico
3. [Entradas Especiais — Compaction, BranchSummary e Labels](03-entradas-especiais-compaction-branchsummary-e-labels/CONTENT.md) — CompactionEntry com firstKeptEntryId, BranchSummaryEntry gerada ao trocar de branch, labels como bookmarks, e a distinção entre custom e custom_message
4. [Fork e Branch na Prática — Criar e Navegar](04-fork-e-branch-na-pratica-criar-e-navegar/CONTENT.md) — o que acontece no arquivo JSONL durante um branch (mesmo arquivo) e durante um fork (novo arquivo com parentSession), e como invocar as operações via TUI e SDK
5. [Append-Only Como Contrato de Persistência — EFS vs S3](05-append-only-como-contrato-de-persistencia-efs-vs-s3/CONTENT.md) — restrições que o contrato append-only impõe sobre EFS (append nativo, atômico) e S3 (sem append nativo, tensão com consistência eventual) e implicações de read-after-write
6. [Operações Proibidas e Restrições de Integridade](06-operacoes-proibidas-e-restricoes-de-integridade/CONTENT.md) — editar no meio, truncar, reordenar, colisão de id em forks concorrentes, e o sistema de migração de versão v1→v2→v3

## Fontes utilizadas

- [Pi session format — docs/session.md (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [Pi Coding Agent — README oficial](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [How to Build a Custom Agent Framework with PI — Nader Dabit](https://gist.github.com/dabit3/e97dbfe71298b1df4d36542aceb5f158)
- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
- [pi.dev.details.md — community gist](https://gist.github.com/rajeshpv/eccc1dc8d70e8cdcf948de3312ca111f)
