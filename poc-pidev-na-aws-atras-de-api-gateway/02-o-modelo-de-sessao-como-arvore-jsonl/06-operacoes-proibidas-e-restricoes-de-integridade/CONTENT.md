# Operações Proibidas e Restrições de Integridade

![capa](cover.png)

## Sobre este subcapítulo

Saber como o arquivo de sessão funciona quando tudo corre bem é necessário, mas não suficiente. Quem vai implementar persistência externa precisa saber o que não fazer — e o que acontece quando essas restrições são violadas. Este subcapítulo cataloga as operações proibidas no arquivo JSONL de sessão do pi.dev: editar linhas existentes no meio do arquivo, truncar o arquivo a partir de um ponto, reordenar linhas, e criar colisões de `id` via forks concorrentes sem coordenação. Para cada operação proibida, o subcapítulo descreve o efeito concreto no harness — não como aviso genérico, mas como diagnóstico preciso do que quebra e por quê.

O subcapítulo também cobre o sistema de migração de versão do formato (v1 → v2 → v3), que o harness executa automaticamente ao abrir arquivos legados — e por que qualquer lógica de persistência externa que transforme o arquivo precisa entender essa migração para não produzir arquivos num estado incoerente.

## Estrutura

O subcapítulo cobre: (1) **editar linhas existentes** — por que o harness não valida checksum por linha, o que quebra quando um `id` ou `parentId` é alterado (o índice in-memory fica inconsistente com o arquivo, o caminho leaf-to-root resolve para um nó diferente ou inexistente), e como isso se manifesta em erro de sessão; (2) **truncar o arquivo a partir de um ponto** — truncar remove nós que outros nós referenciam como `parentId`; o harness tenta construir o índice e encontra referências a ids inexistentes; resultado é sessão irrecuperável ou resolvida para raiz incorreta; (3) **reordenar linhas** — o harness não depende da ordem física das linhas para reconstruir o grafo (usa o índice id → entrada), mas a escrita de novas entradas depende do arquivo estar em append; reordenar abre margem para sobrescrita acidental em vez de append; (4) **colisão de id em forks concorrentes** — ids são hex de 8 chars gerados localmente sem coordenação central; em cenários multi-processo, dois processos que estendem a mesma sessão simultaneamente podem gerar ids iguais, corrompendo o índice; estratégia de mitigação: locks ao nível de arquivo ou roteamento de sessão para process único; (5) **migração de versão (v1 → v2 → v3)** — o harness migra automaticamente ao abrir, mas qualquer lógica que leia o arquivo externamente (ex: Lambda lendo de S3) precisa saber que formatos legados existem e que o arquivo pode crescer de versão entre invocações.

## Objetivo

Ao terminar este subcapítulo, o leitor saberá descrever com precisão o que acontece no harness quando cada operação proibida é executada, entenderá por que colisão de id em forks concorrentes é o risco mais silencioso de implementações multi-processo, e estará ciente do sistema de migração de versão e do que isso significa para lógicas de leitura externa. Com isso, o leitor fecha o ciclo de entendimento do modelo de sessão e está pronto para entrar nos capítulos 8 e 9 com o mapa completo do que está sendo persistido e das restrições que o formato impõe.

## Conceitos

A explicação completa destes conceitos vive em [`CONCEPTS.md`](CONCEPTS.md), construída sequencialmente pela skill `estudo-explicar-conceito`.

1. O índice in-memory como único guardião da integridade — por que o harness não valida checksum por linha ao escrever, e por que toda a integridade do arquivo depende do índice reconstruído na leitura
2. Editar linhas existentes — o que muda no índice quando um `id` ou `parentId` é alterado em disco, e como isso se manifesta como erro de sessão ou resolução para nó errado
3. Truncar o arquivo — por que remover linhas físicas cria referências de `parentId` para ids inexistentes, e por que o harness não consegue reconstruir o grafo de forma confiável
4. Reordenar linhas — por que o harness tolera qualquer ordem física para leitura (usa o índice), mas por que reordenar cria risco real de sobrescrita acidental no próximo append
5. Colisão de `id` em forks concorrentes — como dois processos sem coordenação central podem gerar o mesmo hex de 8 chars, por que isso corrompe o índice silenciosamente, e as estratégias de mitigação (lock de arquivo, roteamento de sessão para processo único)
6. Migração de versão v1 → v2 → v3 — como o harness detecta a versão no `SessionHeader` e migra em memória ao abrir, e o que isso significa para lógicas externas que leem o arquivo (Lambda lendo de S3 pode encontrar qualquer versão entre invocações)

## Fontes utilizadas

- [Pi session-format — pi.dev/docs/latest](https://pi.dev/docs/latest/session-format)
- [Session Management and Persistence — DeepWiki (agentic-dev-io/pi-agent)](https://deepwiki.com/agentic-dev-io/pi-agent/2.4-session-management-and-persistence)
- [Pi Coding Agent — README oficial (badlogic/pi-mono)](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [Append-only Log — QuestDB Glossary](https://questdb.com/glossary/append-only-log/)
- [How to Build a Custom Agent Framework with PI — Nader Dabit](https://gist.github.com/dabit3/e97dbfe71298b1df4d36542aceb5f158)
