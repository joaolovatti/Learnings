# Sincronização de Estado e Autoridade do Servidor

![capa](cover.png)

## Sobre este capítulo

Com o servidor e os clientes conversando, o desafio seguinte é fazer o que está no servidor chegar aos clientes (e vice-versa) de maneira confiável, rápida e justa. Este capítulo é sobre **replicação** em Godot 4: como nós específicos (o jogador, um NPC compartilhado, um projétil) existem em múltiplos processos, quem tem autoridade sobre eles, e como o estado flui. Introduzimos `MultiplayerSpawner` e `MultiplayerSynchronizer`, `@rpc("authority"/"any_peer")`, e a disciplina crucial: **o servidor é a fonte da verdade**, o cliente só envia *intenções* (inputs) e recebe *resultados*.

O capítulo também encara o problema que todo RPG online enfrenta: **tick rate** e interpolação. Em grid-based Pokémon-like, o tick é lento comparado com FPS — e usar isso a favor simplifica o código enormemente. Também cobrimos um anti-cheat mínimo que desqualifica clientes que enviam movimentos fisicamente impossíveis.

## Estrutura

Os blocos são: (1) **autoridade em Godot** — `set_multiplayer_authority`, quem chama cada método, a separação entre client-authoritative e server-authoritative; (2) **MultiplayerSynchronizer** — replicar propriedades com `replication_config`, frequência, delta compression; (3) **MultiplayerSpawner** — espawnar nós em todos os clientes a partir do servidor; (4) **intenções vs. estado** — cliente envia `move_intent(direction)`, servidor valida e responde com novo estado; (5) **tick rate** — por que o grid Pokémon-like permite tick rates baixos (10–20 Hz) e como isso reduz banda; (6) **hands-on** — dois clientes conectados veem um ao outro se movendo em grid no mesmo mapa, com o servidor autoritativo.

## Objetivo

Ao fim, dois clientes conectados veem um ao outro se movendo no mesmo mapa, com todos os movimentos validados pelo servidor. É o momento de maior catarse do livro: o mundo virou *compartilhado*. A partir daqui, só falta persistir esse mundo para que ele sobreviva ao reinício do servidor.

## Fontes utilizadas

- [Godot Engine — High-level multiplayer: Synchronizing game state (docs)](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html)
- [Godot Engine — MultiplayerSynchronizer (class reference)](https://docs.godotengine.org/en/stable/classes/class_multiplayersynchronizer.html)
- [Godot Engine — MultiplayerSpawner (class reference)](https://docs.godotengine.org/en/stable/classes/class_multiplayerspawner.html)
- [Godot Multiplayer in 2026: What Actually Works (Ziva)](https://ziva.sh/blogs/godot-multiplayer)
- [Multi-player (server/client) setup (Godot Forums)](https://godotforums.org/d/36064-multi-player-serverclient-setup)
