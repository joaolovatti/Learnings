# Persistência Server-side e Mundo Compartilhado

![capa](cover.png)

## Sobre este capítulo

O capítulo fecha o bloco online respondendo à pergunta: *onde mora o mundo?* Em single-player, o estado do jogador vivia num JSON em `user://`. Agora, ele precisa viver num **armazenamento do servidor**, atado a uma **conta**, e sobreviver a reinícios, deploys e falhas. Este capítulo entra no ponto que engenheiros de backend reconhecem de imediato — mas com os acentos específicos de jogos: latência aceitável do salvamento, consistência eventual vs. forte em inventário, idempotência de ações de combate, e o vetor de ataque que é um cliente tentando enganar o servidor sobre o que já fez.

O capítulo **não** transforma o livro num curso de devops. Ele escolhe um stack pragmático (SQLite embutido no servidor para o protótipo, com notas sobre caminho para PostgreSQL em produção), implementa contas e login mínimos, persiste party e posição do jogador, e deixa hooks claros para o leitor evoluir depois.

## Estrutura

Os blocos são: (1) **modelagem do mundo no servidor** — contas, personagens, party, inventário, flags de mundo, posição; (2) **stack pragmático** — SQLite via plugin nativo ou server-side Python/Node como sidecar, trade-offs para um protótipo de dois jogadores; (3) **contas e autenticação** — login mínimo com token, hashing de senha, ciclo de sessão; (4) **escrita periódica vs. eventual** — salvar a cada combate? a cada N segundos? ao logout?; (5) **consistência e idempotência** — o jogador derrotou um boss: se o pacote de vitória chegar duas vezes, o loot dobra?; (6) **hands-on** — dois clientes logam com contas distintas, a sessão persiste posição e party mesmo após reiniciar o servidor.

## Objetivo

Ao fim, o leitor terá um protótipo online com contas, persistência server-side e mundo compartilhado que sobrevive a restart. Isso cumpre o entregável declarado do livro: protótipo navegável de RPG 2D top-down rodando em rede entre dois ou mais clientes, com combate e base de assets. O último capítulo costura a ponta final: como os assets desse mundo são gerados.

## Fontes utilizadas

- [Godot Engine — High-level multiplayer (docs)](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html)
- [godot-sqlite (GitHub, plugin nativo)](https://github.com/2shady4u/godot-sqlite)
- [Godot Multiplayer in 2026: What Actually Works (Ziva)](https://ziva.sh/blogs/godot-multiplayer)
- [Multi-player (server/client) setup (Godot Forums)](https://godotforums.org/d/36064-multi-player-serverclient-setup)
- [Simple Online Multiplayer Networking Authoritative Dedicated Server (Godot Asset Library)](https://godotengine.org/asset-library/asset/755)
