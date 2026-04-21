# Por que Godot 4 Vence Para Este Projeto

![capa](cover.png)

## Sobre este subcapítulo

Com o alvo fixado e o panorama de engines mapeado, este subcapítulo é a defesa explícita da escolha. Ele cruza as exigências do jogo-alvo — RPG 2D top-down, online, dois ou mais clientes, longa duração como projeto pessoal — com os atributos concretos do Godot 4 e mostra por que, neste cruzamento específico, ele vence. Não é um discurso de "Godot é o melhor"; é um argumento de "para esta combinação de necessidades, o Godot é a opção em que cada propriedade da engine empurra o projeto na direção certa em vez de criar atrito".

Este subcapítulo é o ponto de virada do capítulo: depois dele, a engine deixa de ser uma decisão em aberto e passa a ser premissa silenciosa de todo o resto do livro. Por isso ele precisa ser denso e honesto — incluindo as limitações reais do Godot 4 no contexto multiplayer (ausência de client-side prediction nativa, teto prático de jogadores simultâneos, ferramentas de matchmaking/lobby que precisam ser construídas) — e ainda assim chegar à conclusão de que, para este alvo específico, é a escolha certa.

## Estrutura

Os blocos deste subcapítulo são: (1) **cena-como-árvore** — por que o paradigma de scene tree composta de nodes encaixa naturalmente em RPG 2D (mapas como cenas, NPCs como cenas instanciadas, UI como subárvore independente); (2) **GDScript ergonômico** — sintaxe Python-like, hot reload, integração profunda com nodes e signals, custo de aprendizado quase zero para quem já programa; (3) **licença MIT, zero royalties** — relevância concreta para um projeto pessoal de longa duração que pode ou não virar produto; (4) **API de multiplayer de alto nível nativa** — `MultiplayerAPI`, `MultiplayerSpawner`, `MultiplayerSynchronizer`, ENet/WebSocket como transports prontos, em contraste com a montagem manual exigida por outras engines; (5) **footprint enxuto e iteração rápida** — editor de ~120MB, abre em segundos, hot reload de cenas, permite ciclos de tentativa-erro curtos que importam para quem aprende uma engine pela primeira vez; (6) **as limitações honestas** — ausência de client-side prediction/rollback nativos, teto prático de ~40 jogadores simultâneos por servidor sem trabalho extra, ferramentas auxiliares (lobby, friends list, matchmaking) por conta do desenvolvedor, e por que essas limitações *não* invalidam a escolha para o alvo deste livro.

## Objetivo

Ao terminar, o leitor terá uma decisão técnica fundamentada — não baseada em hype, gosto pessoal ou tendência — sobre adotar Godot 4 para este projeto, conhecerá os principais atributos da engine que sustentam essa decisão e terá visibilidade clara das limitações que precisará contornar nos blocos online do livro. A partir daqui, os capítulos seguintes podem assumir Godot como dado e focar em "como usá-lo" em vez de "se vale a pena usá-lo".

## Fontes utilizadas

- [Godot Multiplayer in 2026: What Actually Works (Ziva)](https://ziva.sh/blogs/godot-multiplayer)
- [Intro to Multiplayer in Godot (GDQuest)](https://www.gdquest.com/tutorial/godot/networking/intro-to-multiplayer/)
- [Godot Engine — documentação oficial (High-level multiplayer)](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html)
- [Godot vs Unreal Engine in 2026 (Ziva)](https://ziva.sh/blogs/godot-vs-unreal)
- [My Experience Creating a 2D RPG Game using Godot Game Engine (Medium — June Han)](https://medium.com/@julialiu08/my-experience-creating-a-2d-rpg-game-using-godot-game-engine-6c1dde370744)
- [Godot 4 Multiplayer: Make Your Own Online Game (GameDev.tv)](https://gamedev.tv/courses/godot-multiplayer)
