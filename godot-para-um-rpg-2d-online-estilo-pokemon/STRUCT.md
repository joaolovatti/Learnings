# Estrutura do Livro

> Mapa rapido da organizacao do livro: capitulos, subcapitulos e conceitos. Mantido automaticamente pela skill `estudo-atualizar-struct` — nao edite a mao.

```
godot-para-um-rpg-2d-online-estilo-pokemon/ — Godot para um RPG 2D Online Estilo Pokémon
├── 01-introducao/ — briefing estratégico da escolha de engine, recorte do jogo-alvo e mapa do livro.
│   ├── 01-o-recorte-do-jogo-alvo/ — MVP Pokémon Fire Red-like, top-down em grid, combate por turnos, dois clientes em rede e a trilha até o protótipo final.
│   │   ├── 01-por-que-o-recorte-vem-antes-da-engine/ — sem alvo fixado, comparações e arquitetura viram discussão filosófica.
│   │   ├── 02-mecanicas-nao-negociaveis-de-um-pokemon-fire-red-like/ — inventário técnico: top-down em grid, tile-a-tile, NPCs com diálogo, combate por turnos, party, mundo persistente.
│   │   ├── 03-o-que-e-um-mvp-jogavel-em-gamedev/ — fronteira mínima de "isto é um jogo", não "isto está pronto para lançar".
│   │   ├── 04-a-fronteira-concreta-do-mvp-deste-projeto/ — mapa navegável + combate funcional + dois clientes vendo o mesmo mundo.
│   │   ├── 05-o-que-fica-de-fora-do-mvp-e-por-que/ — captura, evolução, sistema completo de tipos e dezenas de mapas ficam fora para proteger o projeto.
│   │   ├── 06-o-twist-do-online-sobre-um-pokemon-single-player/ — autoridade do servidor, sincronização de estado e persistência remota como pilares da mudança.
│   │   └── 07-a-trilha-incremental-ate-o-mvp/ — quatro blocos onde cada um viabiliza o próximo e tem entregável testável ao fim.
│   ├── 02-panorama-de-engines-2d-em-2026/ — Unity, Phaser, Defold e nicho avaliados sob a ótica específica de um RPG 2D online.
│   ├── 03-por-que-godot-4-vence-para-este-projeto/ — cena-como-árvore, GDScript ergonômico, licença MIT, multiplayer de alto nível nativo e footprint enxuto.
│   ├── 04-vocabulario-mental-de-gamedev/ — engine, game loop, scene, node, signal e como se conectam ao mundo de sistemas distribuídos do leitor.
│   ├── 05-o-mapa-do-livro/ — como os quatro blocos (fundamentos, sistemas Pokémon-like, online, pipeline com AI) se encadeiam até o entregável final.
│   └── 06-setup-minimo-instalando-o-godot-4/ — instalação, criação do primeiro projeto vazio e o ritual de abrir o editor pela primeira vez.
├── 02-nodes-scenes-e-a-arvore-de-cena/ — a mudança de paradigma central do Godot: jogo como árvore de nós compostos em cenas reutilizáveis.
├── 03-game-loop-delta-time-e-o-editor-em-pratica/ — como a engine executa seu jogo por trás, com `_process`, `_physics_process` e o ciclo de frames.
├── 04-gdscript-e-sinais/ — a linguagem de scripting do Godot e o mecanismo de `signals` como alternativa a callbacks/observers.
├── 05-sprites-animatedsprite2d-e-resources/ — o pipeline visual 2D, `Resource` como recurso reutilizável e animação por frames.
├── 06-tilemaps-e-tilesets/ — como construir os mapas de um RPG top-down com `TileMapLayer`, autotiles e camadas físicas.
├── 07-movimento-em-grid-e-input-handling/ — deslocamento tile-a-tile, interpolação visual e bloqueio por colisão.
├── 08-cameras-transicoes-de-mapa-e-salas/ — `Camera2D`, sistema de salas, troca de cena com preservação de estado do jogador.
├── 09-npcs-dialogos-e-eventos-de-mundo/ — população do mapa, máquinas de estado de NPC, sistema de diálogo e eventos scriptados.
├── 10-combate-por-turnos/ — loop de batalha, state machines, cálculo de dano, UI de batalha e integração com a party.
├── 11-party-inventario-e-persistencia-local/ — sistemas de estado do jogador, `Resource`-based data e save/load em disco local.
├── 12-multiplayer-arquitetura-cliente-servidor/ — modelos de rede, escolha de transport, servidor dedicado em modo headless.
├── 13-sincronizacao-de-estado-e-autoridade/ — replicação de nós, `MultiplayerSynchronizer`, tick rate e anti-cheat mínimo.
├── 14-persistencia-server-side-e-mundo-compartilhado/ — banco no servidor, contas, mundo compartilhado e salvamento remoto.
└── 15-pipeline-de-assets-com-ai/ — integração do fluxo generativo (OpenAI/Midjourney/modelos de música) ao projeto Godot.
```
