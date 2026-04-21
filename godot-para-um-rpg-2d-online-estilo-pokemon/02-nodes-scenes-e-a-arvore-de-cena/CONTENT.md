# Nodes, Scenes e a Árvore de Cena

![capa](cover.png)

## Sobre este capítulo

Antes de escrever uma linha de GDScript, o leitor precisa internalizar a primeira grande mudança de paradigma ao entrar em Godot: o jogo inteiro é uma **árvore de nós** composta por **cenas reutilizáveis**. Para um engenheiro acostumado a pensar em classes, serviços e módulos, a transição não é automática — um `Node` não é exatamente uma classe comum, e uma `Scene` não é um módulo. Este capítulo existe para fazer essa ponte: explica o que é um `Node`, o que é uma `Scene`, por que uma Scene é ao mesmo tempo um arquivo `.tscn` em disco e um nó pronto para ser instanciado em runtime, e como a árvore de cena viva é a verdadeira "forma" do jogo em execução.

O capítulo aparece nesta posição porque todo o conteúdo seguinte — scripts em nós, sinais, tilemaps, multiplayer — pressupõe que o leitor sabe *ler* uma cena Godot e raciocinar em termos dela. Sem essa fluência mental, os próximos capítulos viram fórmulas decoradas; com ela, viram aplicação direta de um modelo coerente.

## Estrutura

Os blocos são: (1) **o nó como unidade mínima** — tipos fundamentais de nós do Godot 4 (`Node`, `Node2D`, `Control`, `CanvasLayer`), hierarquia de classes da engine, como a posição de um nó na árvore afeta transformação, input e rendering; (2) **a cena como composição reutilizável** — o que é um arquivo `.tscn`, como uma Scene encapsula uma árvore, cenas instanciadas vs. cenas herdadas, scene principal do projeto; (3) **a árvore de cena em runtime** — o `SceneTree`, *groups*, *autoload*/singleton e o ciclo `_ready` → `_process`; (4) **boas práticas de estruturação** — quando criar uma Scene nova, quando deixar nós inline, padrões de nomenclatura, organização de pastas; (5) **hands-on** — esboçar a árvore inicial do projeto Pokémon-like (Main, World, Player, UI, GlobalAutoload) a partir de um projeto vazio.

## Objetivo

Ao terminar o capítulo, o leitor será capaz de abrir um projeto Godot, ler a árvore de cena de um jogo existente e entender a função de cada nó, criar cenas compostas e reutilizá-las via instanciação, e esboçar a árvore inicial do seu próprio jogo-alvo sem consultar o editor a cada passo. Isso prepara o terreno para o próximo capítulo, onde o game loop e o delta time passam a operar sobre essa árvore.

## Fontes utilizadas

- [Godot Engine — Step by step (docs oficiais)](https://docs.godotengine.org/en/stable/getting_started/step_by_step/index.html)
- [Godot Engine — Nodes and scenes (docs)](https://docs.godotengine.org/en/stable/getting_started/step_by_step/nodes_and_scenes.html)
- [GDQuest — Godot learning paths](https://www.gdquest.com/tutorial/godot/learning-paths/)
- [Let's Learn Godot 4 by Making an RPG — Part 1: Project Overview & Setup (DEV)](https://dev.to/christinec_dev/lets-learn-godot-4-by-making-an-rpg-part-1-project-overview-setup-bgc)
- [Make a 2D Action & Adventure RPG in Godot 4 — Tutorial Series (YouTube)](https://www.youtube.com/playlist?list=PLfcCiyd_V9GH8M9xd_QKlyU8jryGcy3Xa)
