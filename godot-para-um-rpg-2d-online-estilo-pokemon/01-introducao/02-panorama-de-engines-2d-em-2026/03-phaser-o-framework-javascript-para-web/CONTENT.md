# Phaser — o Framework JavaScript para Web

![capa](cover.png)

Unity falhou nas dimensões eliminatórias 1 e 2 — pipeline 2D bolt-on e multiplayer fragmentado. Phaser entra como segunda candidata natural, especialmente atraente para engenheiros com fluência em JavaScript ou TypeScript: a linguagem é familiar, o deploy é um bundle estático que abre no browser, e o framework é open-source com licença MIT. Mas a primeira distinção que o critério exige fazer é semântica e consequente: Phaser não é uma engine, é um **framework**. Essa diferença não é de nomenclatura — ela determina o que você ganha e o que você precisa construir do zero.

Uma engine empacota um editor visual, um pipeline de assets, sistemas de física, colisão, áudio e rede sob uma interface coesa. Um framework oferece primitivas que você compõe via código; o ambiente de desenvolvimento é o seu editor de texto, não um editor dedicado ao jogo. Para Phaser, isso significa que não existe painel de tilemaps, não existe inspector de cenas, não existe visualizador de hierarquia de objetos — tudo é coordenada e propriedade gerenciada em código.

A arquitetura central de Phaser é o sistema de **Scenes**. Cada cena representa um estado discreto do jogo (menu, nível, inventário, tela de game over) e passa por um ciclo de vida fixo:

```
init() → preload() → create() → update(time, delta) → [destroy()]
```

O `preload()` dispara o loader assíncrono de assets — sprites, tilemaps exportados do Tiled, arquivos de áudio, JSON. O `create()` instancia os objetos e configura física e colisão. O `update()` executa a cada frame, análogo ao `_process()` do Godot ou ao `Update()` do Unity, recebendo `time` em milissegundos desde o início e `delta` em milissegundos desde o último frame — o que permite movimento independente de frame rate multiplicando velocidade por `delta`.

O sistema de física vem em dois sabores independentes:

| Sistema | Modelo de colisão | Casos de uso |
|---------|-------------------|--------------|
| **Arcade Physics** | AABB (retângulos e círculos) | RPGs, plataformers, shooters — maioria dos jogos 2D |
| **Matter.js** | Corpos rígidos, formas complexas, gravidade, restrições | Puzzles físicos, simulações |

Para um RPG top-down em grid, Arcade Physics é suficiente para colisão básica — mas movimento tile-a-tile precisa ser implementado manualmente. Phaser não tem um sistema nativo de snap-to-tile, pathfinding em grid ou interpolação de posição entre tiles. Você implementa a lógica de "o personagem só se move em incrementos de 32px" e garante que o estado do mapa e o estado do sprite estejam sempre sincronizados.

O suporte a tilemaps existe via `Phaser.Tilemaps.Tilemap`, lendo arquivos JSON exportados do Tiled (editor externo separado). O fluxo de integração é:

```js
// preload()
this.load.tilemapTiledJSON('mapa', 'assets/mapa.json');
this.load.image('tileset', 'assets/tiles.png');

// create()
const map = this.make.tilemap({ key: 'mapa' });
const tiles = map.addTilesetImage('nome-no-tiled', 'tileset');
const layer = map.createLayer('Chao', tiles, 0, 0);
layer.setCollisionByProperty({ collides: true });
```

O ciclo de edição para qualquer ajuste no mapa é: editar no Tiled → exportar JSON → recarregar no browser → inspecionar. Sem editor integrado, não existe "ver como ficou sem sair do ambiente de desenvolvimento". Para um RPG com dezenas de tiles, múltiplas camadas, colisão por tipo de terreno e zonas de trigger — tudo isso verificado visualmente a cada iteração — o custo de ciclo de edição se acumula.

A dimensão mais crítica no crivo é a 2 — multiplayer. Phaser não tem nada embutido. A arquitetura assumida pelo framework é cliente-apenas: ele renderiza o estado do jogo no browser, mas não tem primitivas para sincronizar esse estado entre múltiplos clientes. O padrão de mercado para jogos multiplayer com Phaser é integrar um servidor Node.js via **Colyseus** (framework de estado de servidor para jogos em tempo real) ou **Socket.io** (WebSockets de propósito geral):

```
[Phaser (browser)] ←── WebSocket ──→ [Colyseus / Socket.io (Node.js)]
```

O servidor recebe inputs dos clientes, processa a lógica autoritativa e transmite o estado atualizado de volta. Toda a serialização de estado, reconciliação de posição, autoridade de servidor e gerenciamento de sessão é código de aplicação — não existe `MultiplayerSynchronizer`, `NetworkVariable` ou qualquer primitiva de replicação de estado como em Godot ou Unity NGO. Para um RPG com combate por turnos sincronizado, inventário persistente e múltiplas sessões simultâneas, isso significa implementar um protocolo de sincronização completo antes de qualquer mecânica de jogo funcionar.

Aplicando as sete dimensões do critério estabelecido no primeiro conceito:

| Dimensão | Resultado para Phaser |
|----------|-----------------------|
| Pipeline 2D nativo | Boa — nasceu para 2D, sem herança de base 3D |
| **Multiplayer embutido** | **Falha eliminatória** — zero suporte nativo; toda camada de rede é código de aplicação |
| Custo de aprendizado | Baixo para quem domina JS/TS; alto em arquitetura sem editor como guia |
| Licença | MIT — sem restrições |
| Footprint e tempo até primeiro frame | Excelente — bundle estático, abre no browser em segundos |
| **Ergonomia do editor** | **Falha** — sem editor visual; ciclo de edição é totalmente code-only |
| Ecossistema | Bom para jogos casuais no browser; limitado para RPGs complexos online |

Phaser falha na dimensão 2 (eliminatória) e apresenta limitação real na ergonomia do editor para um projeto da complexidade proposta. Para um jogo casual de fim de semana com deploy no browser, Phaser é difícil de bater — o deploy é um `npm run build` que gera um bundle de ~1MB pronto para CDN. Para um RPG online top-down com mapa rico e sincronização de estado entre jogadores, o custo de infraestrutura pré-mecânicas é proibitivo. No próximo conceito, GameMaker, Defold e Construct entram no crivo com um perfil diferente: engines nativas 2D com editores visuais dedicados, mas com trade-offs próprios de licença, ecossistema e multiplayer.

## Fontes utilizadas

- [Phaser — site oficial](https://phaser.io/)
- [Phaser (game framework) — Wikipedia](https://en.wikipedia.org/wiki/Phaser_(game_framework))
- [Phaser vs Godot for 2D Games: Complete Comparison (Generalist Programmer)](https://generalistprogrammer.com/tutorials/phaser-vs-godot-2d-games)
- [My Thoughts on Phaser 3 — Pandaqi Blog](https://pandaqi.com/blog/reviews-and-thoughts/my-thoughts-on-phaser-3-engine/)
- [Phaser: Real Time Multiplayer with Colyseus](https://learn.colyseus.io/phaser/)
- [What is Phaser? — Phaser Docs](https://docs.phaser.io/phaser/getting-started/what-is-phaser)

**Próximo conceito →** [GameMaker, Defold e Construct — Engines de Nicho 2D](../04-gamemaker-defold-e-construct-engines-de-nicho-2d/CONTENT.md)
