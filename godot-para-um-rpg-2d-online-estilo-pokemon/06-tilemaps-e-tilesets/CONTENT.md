# Tilemaps e Tilesets: a Espinha Dorsal do Mundo

![capa](cover.png)

## Sobre este capítulo

Pokémon é, antes de qualquer combate ou diálogo, um jogo de **mapa**. O Tilemap é o que permite compor centenas de metros de cidade, floresta, rota e caverna a partir de um punhado de sprites quadrados — e é também a estrutura que carrega colisão, Y-sort, camadas e terrenos autotileáveis. Este capítulo explica o modelo de `TileSet` (a paleta) e `TileMapLayer` (a pintura), como configurar camadas físicas e de renderização, como funcionam *terrains* e autotiles (o truque que transforma "um tile de grama" em "20 variações contextualmente certas"), e como estruturar um mapa de forma que amanhã consiga receber transições entre salas sem quebrar.

Este capítulo vem depois dos fundamentos e da parte visual porque o mundo só faz sentido quando você sabe posicionar sprites e ler a árvore — mas vem **antes** do movimento em grid, porque mover o jogador sem saber do mundo em que ele pisa é escrever sobre areia.

## Estrutura

Os blocos são: (1) **TileSet como paleta** — regiões, atlas, físicas por tile, custom data layers; (2) **TileMapLayer** — o substituto moderno do antigo `TileMap`, múltiplas camadas (chão, decoração, overlay), Y-sort; (3) **terrains e autotiling** — *terrain sets*, bits de conectividade, o fluxo de pintar por terreno em vez de por tile; (4) **camadas físicas** — colisão em tile vs. colisão em actor, navegação; (5) **organização de mapas** — um cenário por `.tscn`, nomenclatura, tamanhos padrão de mundo Pokémon-like; (6) **hands-on** — importar um tileset pixel-art, pintar a primeira rota com camadas chão/decoração/colisão e validar que o player não atravessa árvores.

## Objetivo

Ao terminar, o leitor terá um mapa jogável no qual o personagem pode caminhar, colidir com obstáculos e ver decoração estratificada por Y. Saberá organizar novos mapas a partir desse molde e entenderá o papel do Tilemap como fundação do mundo. Assim, o capítulo seguinte — movimento em grid — pode aterrissar num terreno pronto.

## Fontes utilizadas

- [Godot Engine — Using TileMaps (docs)](https://docs.godotengine.org/en/stable/tutorials/2d/using_tilemaps.html)
- [Godot Engine — Using TileSets (docs)](https://docs.godotengine.org/en/stable/tutorials/2d/using_tilesets.html)
- [Catlike Coding's True Top-Down 2D Tutorial Series — Part 1 Tile Map](https://forum.godotengine.org/t/catlike-codings-true-top-down-2d-tutorial-series/84632)
- [Let's Learn Godot 4 by Making an RPG — Part 4: Game TileMap & Camera Setup (DEV)](https://dev.to/christinec_dev/lets-learn-godot-4-by-making-an-rpg-part-4-game-tilemap-camera-setup-1mle)
- [Make a 2D Action & Adventure RPG in Godot 4 — Tilemaps and Tilesets (YouTube)](https://www.youtube.com/playlist?list=PLfcCiyd_V9GH8M9xd_QKlyU8jryGcy3Xa)
