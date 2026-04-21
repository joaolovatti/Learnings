# Vocabulário Mental de Gamedev

![capa](cover.png)

## Sobre este subcapítulo

Este subcapítulo é o ponto onde o leitor recebe os termos-chave do mundo gamedev numa primeira camada — o suficiente para ler o resto do livro sem precisar parar no glossário. Não é uma exploração profunda dos conceitos (essa virá nos capítulos 2 e 3): é uma calibração de vocabulário para alguém que pensa em request/response, ETL e ciclos de release, e precisa começar a pensar em frames, ticks, scenes e signals. A lógica é fazer a tradução cultural antes que a falta dela vire ruído invisível em todo capítulo subsequente.

Ele aparece neste ponto do capítulo porque, depois de defender Godot, faz sentido introduzir os termos próprios da engine antes de mostrar como o livro inteiro vai usá-los. É também o subcapítulo onde o paralelo com o background do leitor (mobile, dados, sistemas distribuídos) é mais explorado — cada termo de gamedev é apresentado em contraste com algo que o leitor já entende, para que o conceito se ancore num modelo mental existente em vez de flutuar.

## Estrutura

Os blocos deste subcapítulo são: (1) **engine** — o que distingue uma engine de uma library, por que ela é simultaneamente runtime, IDE, build pipeline e asset manager, e qual o paralelo (e a diferença) com frameworks mobile como Flutter ou backend como Spring; (2) **game loop e frame** — o coração de qualquer engine, por que ele difere fundamentalmente do modelo de eventos discretos do mobile, o que é frame, FPS, e por que tudo no jogo precisa ser pensado em "o que acontece a cada frame"; (3) **scene e node no Godot** — a abstração central do Godot, por que "scene" no Godot não é o que "scene" significa em Unity, e como uma cena vira tanto um nível quanto um NPC quanto um botão de UI; (4) **signal** — o mecanismo desacoplado de comunicação entre nodes, em paralelo com pub/sub e callbacks que o leitor já usa; (5) **autoridade e tick em multiplayer** — uma primeira menção, sem aprofundar, dos conceitos que dominarão os capítulos finais (autoridade do servidor, tick rate, sincronização), conectando-os ao mundo de sistemas distribuídos.

## Objetivo

Ao terminar, o leitor terá os cinco termos fundadores do livro — engine, game loop, scene, node, signal — calibrados num primeiro nível, com paralelos claros aos modelos mentais que ele já tem de mobile e sistemas distribuídos. A partir daqui, os capítulos seguintes podem usar esses termos sem definição prévia, e o leitor terá um gancho mental para receber o aprofundamento de cada conceito no momento em que ele aparecer (Capítulos 2, 3 e 4 destrinchando nodes/scenes, game loop e signals/GDScript respectivamente).

## Fontes utilizadas

- [Godot Engine — Nodes and Scenes (documentação oficial)](https://docs.godotengine.org/en/stable/getting_started/step_by_step/nodes_and_scenes.html)
- [Godot Engine — Using SceneTree (documentação oficial)](https://docs.godotengine.org/en/stable/tutorials/scripting/scene_tree.html)
- [Godot Engine — Scene organization (documentação oficial)](https://docs.godotengine.org/en/stable/tutorials/best_practices/scene_organization.html)
- [Godot Nodes and the Scene Tree (JetBrains Guide)](https://www.jetbrains.com/guide/gamedev/tutorials/rider-godot-pong/godot-nodes-scene-tree/)
- [Scenes, Nodes and Scripts in Godot 4 (gotut.net)](https://www.gotut.net/scenes-nodes-and-scripts-in-godot-4/)
- [Learn Godot in 15 Minutes — Make Your First Game! (DEV Community)](https://dev.to/rapidsingularity/learn-godot-in-15-minutes-make-your-first-game-61k)
