# As mecânicas não-negociáveis de um Pokémon Fire Red-like

![capa](cover.png)

"Estilo Pokémon Fire Red" só vira especificação útil quando deixa de ser memória afetiva e vira um inventário técnico fechado. O conceito anterior estabeleceu que o recorte precisa existir antes de qualquer decisão de engine. Este é o conteúdo desse recorte: as **mecânicas não-negociáveis**, o conjunto mínimo de sistemas sem os quais o jogo deixa de ser reconhecível como um Pokémon-like. Se qualquer uma delas cair, o recorte muda de gênero.

Cruzando a documentação técnica dos ROMs Gen III com as convenções estabelecidas do sub-gênero, esse núcleo fecha em seis sistemas. O teste de consistência para cada um é direto: _se eu remover este sistema, o protótipo ainda é reconhecível como Pokémon-like?_ Os seis sistemas que passam nesse filtro são:

| Sistema | Requisito mínimo | Por que é não-negociável |
|---|---|---|
| Câmera top-down ortográfica | Projeção 2D sem perspectiva; sprite com 4 animações de caminhada (N/S/L/O) | Permite colisão por lookup em célula, em vez de física contínua com volumes |
| Tilemap discretizado com atributos | Blocos 16×16 px compostos de tiles 8×8 px, em duas camadas (chão + elevada), cada tile com atributos comportamentais | Toda lógica de script de mapa (encontros, eventos, colisão) se apoia nos atributos do tile |
| Movimento em grid, tile-a-tile, 4 direções | Passos discretos N/S/L/O; posição lógica sempre em (x, y) inteiro; interpolação visual entre tiles | Viabiliza `on_enter_tile(x, y)` como primitiva de gatilho — sem célula, encounters exigem colisão contínua |
| NPCs interativos com diálogo scriptado | Entidade posicionada em tile fixo (ou patrulha); diálogo disparado por ação no tile adjacente | Base do loop de progressão: NPCs são o veículo de quests, eventos e flags de save |
| Combate por turnos determinístico | Cena separada do overworld; ordem por Speed; dano pela fórmula Gen III com truncagem inteira | Garante resultados reproduzíveis e uma máquina de estados finita com transições bem definidas |
| Party de até 6 criaturas + persistência | Save serializa party, inventário, posição, flags de NPCs e estado de eventos | Fundação do multiplayer: a persistência server-side é construída sobre esse modelo |

Cada sistema tem requisitos concretos que precisam ser entendidos antes de qualquer linha de código — e eles são implementáveis de forma independente como subsistemas, mas semanticamente interdependentes na cadeia de gameplay.

**Câmera top-down em projeção ortográfica.** O mundo é visto de cima, em 2D, sem perspectiva. Sprites têm uma animação de caminhada por direção cardinal — quatro direções, quatro ciclos de frames. Não é uma escolha estética: a ortografia é o que permite que colisão, scripts e encontros sejam resolvidos por lookup em célula, em vez de física contínua com volumes de colisão.

**Mundo construído sobre um tilemap discretizado.** No Fire Red, o mundo é montado em blocos de 16×16 pixels (o tamanho exato do personagem), compostos por dois layers de 2×2 tiles de 8×8 — uma camada de chão e uma camada elevada (para objetos como árvores e sinalizações que ficam "à frente" do jogador). Tudo que aparece fora de batalha — árvores, casas, água, grama alta, portas, móveis — é tile. Cada tile carrega atributos comportamentais: caminhável, bloqueante, "grama alta que dispara encontro", porta que transiciona para outro mapa, tile de balcão que permite interação com NPC do outro lado, etc. Sem esse tilemap com atributos, a lógica de encontros e scripts de mapa não tem onde se apoiar.

**Movimento em grid, tile-a-tile, nas quatro direções cardinais.** O jogador só caminha em passos discretos para Norte, Sul, Leste ou Oeste — nunca diagonal, nunca parado entre tiles. A posição do estado lógico é sempre "estou no tile (x, y)"; entre dois tiles, a posição visual é interpolada para parecer contínua, mas o motor decide colisão e gatilhos na célula de destino, antes de a animação terminar. Esse é o sistema que torna viável implementar encontros aleatórios na grama alta como `on_enter_tile(x, y)`: sem célula discreta, a lógica precisaria de colisão contínua contra polígonos — outro paradigma e outro conjunto de problemas.

**NPCs interativos com diálogo scriptado.** Cada NPC é uma entidade posicionada em um tile fixo (ou patrulhando entre tiles), com uma máquina de estados simples — parado, virando, caminhando, falando. Apertar o botão de ação no tile adjacente, com o sprite orientado em direção ao NPC, dispara o script indexado ao cabeçalho do mapa: pode abrir uma caixa de diálogo linear, dar um item, iniciar um combate de treinador, ou setar uma flag de progressão no save. A mecânica não-negociável é "NPCs interativos com diálogo"; a versão mínima é um NPC fixo que exibe uma linha de texto ao ser acionado. Branches, eventos encadeados e quests são elaboração — entram em capítulos posteriores sem quebrar o recorte.

**Combate por turnos contra criaturas, com fórmula determinística.** A batalha é uma cena completamente separada do overworld. A ordem de cada turno é definida pela stat Speed; o dano segue a fórmula canônica do Gen III:

```
Damage = floor( floor( floor(2·Level/5 + 2) · Atk · Power / Def ) / 50 + 2 )
       × STAB × TypeMultiplier × Random(85..100)/100
```

Todos os operandos intermediários são truncagem inteira (`floor`) — não há ponto flutuante no cálculo de dano. Isso tem consequência prática: o combate é completamente determinístico e reproduzível, o que facilita testes unitários e futuro anti-cheat no servidor. Modificadores de tipo (0×, 0.5×, 2×), acertos críticos e efeitos de status formam a superfície tática. O ponto a reter para a implementação: o combate é uma **máquina de estados finita** com transições bem definidas (aguardando input → executando animação → calculando resultado → verificando fim) — não um loop físico contínuo.

**Party de até seis criaturas mais mundo persistente entre sessões.** O jogador carrega consigo uma party de no máximo seis criaturas; o PC boxes funciona como armazenamento estendido. O save serializa party completa, inventário, posição no mapa, flags de progressão, estado de NPCs e eventos concluídos. Quando recarregado, o jogador retorna exatamente ao mundo em que parou — não a um ponto de save manual, mas ao estado preciso do mundo. No contexto deste livro, "mundo persistente" vai além do single-player: é a fundação sobre a qual a persistência server-side do multiplayer será construída.

A interdependência entre os seis é a parte que mais importa entender antes de implementar qualquer subsistema. O movimento tile-a-tile viabiliza a grama alta como gatilho de encounter; a grama alta viabiliza o combate randômico; o combate pressupõe party; a party pressupõe persistência; a persistência pressupõe flags de NPCs e estado de mundo. Derrubar qualquer um enfraquece os outros. O teste de consistência revela isso com clareza: trocar movimento em grid por movimento analógico livre (como em A Link to the Past) mantém sprites, câmera e combate intactos — mas inviabiliza encounters por célula, colisão por lookup e scripts de mapa por posição discreta. O jogo deixa de ser um Pokémon-like e vira um Action RPG. É outro gênero.

É esse inventário — top-down ortográfico, tilemap com atributos, movimento em grid, NPCs com diálogo, combate por turnos determinístico e party com persistência — que converte "estilo Pokémon Fire Red" de referência cultural em checklist técnico. A pergunta "isso é essencial ou elaboração?" respondida contra esse checklist é o filtro que vai determinar o que entra no MVP do próximo conceito e o que fica explicitamente de fora.

## Fontes utilizadas

- [Pokémon FireRed and LeafGreen Versions — Bulbapedia](https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_FireRed_and_LeafGreen_Versions)
- [Damage — Bulbapedia (fórmula canônica de dano Gen III)](https://bulbapedia.bulbagarden.net/wiki/Damage)
- [Save data structure (Generation III) — Bulbapedia](https://bulbapedia.bulbagarden.net/wiki/Save_data_structure_(Generation_III))
- [Pokémon data structure (Generation III) — Bulbapedia](https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_data_structure_(Generation_III))
- [Creating a game-size world map of Pokémon Fire Red — Medium](https://medium.com/@mmmulani/creating-a-game-size-world-map-of-pok%C3%A9mon-fire-red-614da729476a)
- [Pokémon Red and Blue/Notes — Data Crystal (estrutura de tiles e atributos)](https://datacrystal.tcrf.net/wiki/Pok%C3%A9mon_Red_and_Blue/Notes)
- [Pokémon Storage System — Bulbapedia](https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Storage_System)
- [Battle Mechanics — The Cave of Dragonflies](https://www.dragonflycave.com/mechanics/battle/)
- [Top-down Grid Movement in Godot — Sandro Maglione](https://www.sandromaglione.com/articles/top-down-grid-movement-in-godot-game-engine)

---

**Próximo conceito** → [O conceito de MVP jogável em gamedev](../03-o-que-e-um-mvp-jogavel-em-gamedev/CONTENT.md)
