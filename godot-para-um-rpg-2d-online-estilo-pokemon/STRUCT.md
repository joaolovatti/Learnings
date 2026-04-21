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
│   │   ├── 01-o-criterio-de-avaliacao-antes-da-lista/ — por que engines só se comparam de forma útil contra um alvo concreto; as dimensões de comparação aplicadas ao jogo-alvo.
│   │   ├── 02-unity-a-engine-generalista-de-mercado/ — força em mobile e ecossistema de assets, 2D bolt-on sobre pipeline 3D e modelo de licenciamento pós-controvérsia do Runtime Fee.
│   │   ├── 03-phaser-o-framework-javascript-para-web/ — arquitetura de framework (não engine), deploy direto no browser, ausência de editor visual e de multiplayer nativo robusto.
│   │   ├── 04-gamemaker-defold-e-construct-engines-de-nicho-2d/ — apostas diferentes (GML, Lua, no-code), boas para projetos focados, mas com tetos de complexidade e limitações de multiplayer.
│   │   ├── 05-unreal-overkill-consciente/ — por que uma engine 3D AAA é descartável para um RPG top-down 2D: footprint, curva de aprendizado e ausência de ganho real no alvo.
│   │   └── 06-o-mapa-de-trade-offs-consolidado/ — leitura cruzada de todas as engines pelas dimensões definidas; identifica o buraco que as alternativas deixam e motiva o próximo subcapítulo.
│   ├── 03-por-que-godot-4-vence-para-este-projeto/ — cena-como-árvore, GDScript ergonômico, licença MIT, multiplayer de alto nível nativo e footprint enxuto.
│   │   ├── 01-cena-como-arvore-o-paradigma-central-do-godot/ — por que modelar um RPG 2D como árvore de nodes compostos encaixa naturalmente em mapas, NPCs, UI e o jogo como um todo.
│   │   ├── 02-gdscript-ergonomia-e-integracao-com-a-engine/ — sintaxe Python-like, tipagem dinâmica, hot reload e integração profunda com nodes e signals — custo de aprendizado quase zero para quem já programa.
│   │   ├── 03-licenca-mit-e-modelo-sem-royalties/ — o que a licença permissiva significa na prática para um projeto pessoal de longa duração que pode ou não se tornar produto.
│   │   ├── 04-api-de-multiplayer-de-alto-nivel-nativa/ — `MultiplayerAPI`, `MultiplayerSpawner` e `MultiplayerSynchronizer` como camada pronta, com ENet e WebSocket como transports, em contraste com a montagem manual exigida por outras engines.
│   │   ├── 05-footprint-enxuto-e-ciclos-de-iteracao-rapidos/ — editor de ~120MB, abertura em segundos e hot reload de cenas como acelerador de aprendizado para quem nunca abriu uma engine.
│   │   └── 06-limitacoes-honestas-do-godot-4-no-contexto-multiplayer/ — ausência de client-side prediction/rollback nativo, teto prático de ~40 jogadores simultâneos, ferramentas auxiliares por conta do desenvolvedor — e por que isso não invalida a escolha para este alvo.
│   ├── 04-vocabulario-mental-de-gamedev/ — engine, game loop, scene, node, signal e como se conectam ao mundo de sistemas distribuídos do leitor.
│   │   ├── 01-engine-vs-library-vs-framework/ — o que distingue uma engine de uma biblioteca: quem controla o loop principal e por que a engine é simultaneamente runtime, IDE, build pipeline e asset manager.
│   │   ├── 02-game-loop-e-frame/ — o ciclo contínuo de input → update → render, o que é um frame e FPS, e por que difere radicalmente do modelo de eventos discretos de aplicativos mobile.
│   │   ├── 03-delta-time/ — por que o tempo decorrido entre frames precisa calibrar todo movimento e lógica, garantindo comportamento frame-rate-independent.
│   │   ├── 04-node-e-scene-no-godot/ — node como unidade atômica de comportamento, scene como árvore hierárquica de nodes, e por que "scene" no Godot não é sinônimo de "fase".
│   │   ├── 05-signal/ — o mecanismo desacoplado de comunicação entre nodes, em paralelo com pub/sub e callbacks, e a regra "call down, signal up".
│   │   └── 06-autoridade-tick-rate-e-sincronizacao-primeira-visao/ — vocabulário multiplayer inicial: quem é dono do estado, a que frequência o servidor processa ticks e o que significa sincronizar estado, conectado ao modelo mental de sistemas distribuídos.
│   ├── 05-o-mapa-do-livro/ — como os quatro blocos (fundamentos, sistemas Pokémon-like, online, pipeline com AI) se encadeiam até o entregável final.
│   │   ├── 01-bloco-1-fundamentos-da-engine/ — o que cobre e por que é o investimento conceitual sem o qual nenhuma mecânica de jogo faz sentido.
│   │   ├── 02-bloco-2-sistemas-pokemon-like-single-player/ — tilemaps, movimento em grid, câmeras, NPCs, combate, party e persistência local; o jogo single-player completo como pré-requisito honesto do online.
│   │   ├── 03-bloco-3-a-camada-online/ — arquitetura cliente-servidor, sincronização autoritativa e persistência server-side.
│   │   ├── 04-bloco-4-pipeline-de-assets-com-ai/ — integração do fluxo generativo (sprites, tilesets, trilha sonora) ao projeto Godot, fechando a ponte com os demais livros do método.
│   │   └── 05-a-logica-das-dependencias-entre-blocos/ — por que essa ordem específica reduz retrabalho e o que acontece quando se tenta inverter a sequência.
│   └── 06-setup-minimo-instalando-o-godot-4/ — instalação, criação do primeiro projeto vazio e o ritual de abrir o editor pela primeira vez.
│       ├── 01-download-e-portabilidade-do-binario-godot-4/ — por que o editor é um único executável portátil de ~120MB, sem instalador, e como baixar a versão estável correta no site oficial.
│       ├── 02-project-manager-criando-e-organizando-projetos/ — o que é o Project Manager, como criar um novo projeto com nome e diretório adequados, e o que a estrutura de diretórios gerada significa.
│       ├── 03-escolha-do-renderer-forward-mobile-ou-compatibility/ — o que cada renderer oferece, por que o Forward+ (Vulkan) é recomendado para um RPG 2D neste contexto, e quando Compatibility é a alternativa correta.
│       ├── 04-anatomia-do-editor-godot-4/ — as quatro regiões principais (Scene/FileSystem dock, viewport central, Inspector, Output/Debugger), o que cada uma faz e quando o leitor vai interagir com cada uma.
│       ├── 05-o-primeiro-ciclo-cena-save-e-run/ — adicionar um Node2D vazio, salvar a cena como `main.tscn`, rodar com F5, entender a janela preta como vitória, e o que o ciclo abrir-editar-salvar-rodar significa na prática.
│       └── 06-atalhos-e-rituais-de-produtividade-do-editor/ — F5 vs. F6, como reabrir o projeto, e o que esperar (e não esperar) na primeira execução de um projeto vazio.
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
