# As mecânicas não-negociáveis de um Pokémon Fire Red-like

![capa](cover.png)

## O que é?

"Estilo Pokémon Fire Red" só vira especificação útil quando deixa de ser memória afetiva e vira um inventário fechado de mecânicas. As **mecânicas não-negociáveis** são o conjunto mínimo de sistemas sem os quais o jogo não é mais reconhecível como um Pokémon-like — se qualquer um cair, o recorte muda de gênero. É o núcleo duro que depois vai guiar escolhas de engine, arquitetura e MVP.

## Explicação técnica

Cruzando a documentação técnica dos ROMs Gen III com as convenções do sub-gênero Pokémon-like, o núcleo não-negociável se fecha em seis sistemas, cada um com requisitos concretos:

1. **Câmera top-down em projeção ortográfica.** O mundo é visto de cima, em 2D, sem perspectiva. Sprites do jogador e NPCs têm uma animação de caminhada por direção cardinal.

2. **Mundo construído sobre um tilemap discretizado.** No Fire Red o mundo é montado em *blocos* de 16×16 pixels (o tamanho do personagem), compostos por 2×2 *tiles* de 8×8. Tudo que aparece fora de batalha — árvores, casas, água, grama alta, portas, móveis — é tile. Cada tile carrega atributos (caminhável, bloqueante, "grama alta que dispara encontro", porta, etc.).

3. **Movimento em grid, tile-a-tile, nas quatro direções cardinais.** O jogador só caminha em passos discretos para Norte/Sul/Leste/Oeste — nunca diagonal, nunca parado entre tiles. Entre dois tiles a posição é interpolada visualmente para parecer contínua, mas o estado lógico é sempre "estou no tile (x, y)". Isso é o que faz colisão, encontros e scripts de mapa serem resolvíveis por *lookup* na célula atual, e não por física contínua.

4. **NPCs interativos com diálogo scriptado.** Cada NPC é uma entidade posicionada num tile com uma máquina de estados simples (parado, patrulhando, virando, falando) e um script de texto indexado pelo cabeçalho do mapa. Apertar o botão de ação no tile adjacente (olhando para o NPC) dispara o script — que pode abrir uma caixa de diálogo, dar um item, iniciar um combate, ou alterar flags do save.

5. **Combate por turnos contra criaturas, com fórmula determinística.** A batalha é uma cena separada do overworld, entre um Pokémon seu e um inimigo. A ordem do turno é definida pela Speed; o dano segue a fórmula canônica do Gen III `Damage = ((((2·Level/5 + 2) · Atk · Power / Def) / 50) + 2) · STAB · TypeMultiplier · Random/100`. Modificadores de tipo (0×, 0.5×, 2×), críticos e efeitos de status formam a superfície tática.

6. **Party de até seis + mundo persistente entre sessões.** O jogador carrega consigo uma *party* de no máximo 6 criaturas, com PC boxes como armazenamento estendido (no Fire Red original, 14 boxes × 30 = 420 slots). O save serializa party, inventário, posição do jogador no mapa, flags de progressão, estado de NPCs movidos, eventos concluídos — tudo que, quando recarregado, devolve o jogador exatamente ao mundo em que ele parou.

Esses seis sistemas são independentes na implementação (cada um vira um subsistema), mas interdependentes na semântica: tile-a-tile viabiliza grama alta como gatilho; grama alta viabiliza combate; combate pressupõe party; party pressupõe persistência; persistência pressupõe NPCs e flags de mundo. Derrubar um quebra os outros.

## Exemplo concreto

O teste de decisão é curto: **se eu remover esse sistema, o protótipo ainda é reconhecível como Pokémon-like?**

Comece por um caso óbvio: trocar o movimento em grid por movimento analógico livre (como Zelda: A Link to the Past). O mapa continua top-down, os sprites continuam pixel-art, o combate por turnos continua intacto. Mas na hora de perguntar *"o jogador entrou na grama alta?"* não há mais célula: é preciso testar colisão contínua contra polígonos, os encontros passam a depender de tempo gasto sobreposto ao tile, e scripts de mapa que antes eram `on_enter_tile(x, y)` viram `on_overlap(trigger_area)`. O jogo deixa de ser um Pokémon-like e vira um Action RPG — é outro gênero.

Um caso mais sutil: manter tudo exceto a party, permitindo apenas uma criatura por vez. O combate sobrevive, a exploração sobrevive, os NPCs sobrevivem. Mas o loop de progressão desaparece: sem troca em batalha, sem gerenciar quem está ferido vs. quem está descansando, sem vantagens de tipo compostas entre seis slots, a curva tática colapsa para "escolha uma criatura, suba de nível". O jogo passa a lembrar mais um Digimon World do que um Pokémon.

Caso-limite, útil para o MVP deste livro: **é aceitável começar com *uma árvore de diálogo trivial* em vez de um sistema completo de scripting de NPC?** Sim — a mecânica não-negociável é "NPCs interativos com diálogo", não "sistema de scripting com branches e flags". Versão mínima: NPC fixo no tile, ao interagir exibe uma linha de texto. Suficiente para o recorte fechar. Branches, eventos e quests são *elaboração* — entram em capítulos posteriores sem quebrar o recorte.

Esse é o uso prático do inventário: contra cada ideia de feature, perguntar "essencial ou elaboração?". Essencial entra no MVP; elaboração fica na lista de capítulos futuros.

## Síntese

As seis mecânicas não-negociáveis — top-down, tilemap, movimento em grid, NPCs com diálogo, combate por turnos e party + persistência — formam a definição operacional de "Pokémon Fire Red-like" para este livro. Elas convertem uma referência cultural em um checklist técnico, e esse checklist é o que torna concreta a [fronteira do MVP](../04-a-fronteira-concreta-do-mvp-deste-projeto/CONTENT.md) no próximo conceito e o que justifica, mais adiante, a escolha de uma engine com `TileMapLayer`, `Camera2D` e sistema de cenas de primeira classe. É também o filtro que protege o projeto de morrer: tudo que não serve a um desses seis sistemas é [explicitamente excluído](../05-o-que-fica-de-fora-do-mvp-e-por-que/CONTENT.md) do escopo.

## Fontes utilizadas

- [Pokémon FireRed and LeafGreen Versions — Bulbapedia](https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_FireRed_and_LeafGreen_Versions)
- [Pokémon FireRed / LeafGreen Tileset Overview — Pokecommunity](https://www.pokecommunity.com/threads/pok%C3%A9mon-r-s-fr-lg-tileset-overview-in-advancemap.82500/)
- [Damage — Bulbapedia (fórmula canônica de dano Gen III)](https://bulbapedia.bulbagarden.net/wiki/Damage)
- [Damage calculation — GameFAQs (Pokémon Red/Fire Red)](https://gamefaqs.gamespot.com/gameboy/367023-pokemon-red-version/faqs/64175/damage-calculation)
- [Battle Mechanics — The Cave of Dragonflies](https://www.dragonflycave.com/mechanics/battle/)
- [Pokémon Storage System — Bulbapedia](https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Storage_System)
- [PC — Bulbapedia](https://bulbapedia.bulbagarden.net/wiki/PC)
- [Save data structure (Generation III) — Bulbapedia](https://bulbapedia.bulbagarden.net/wiki/Save_data_structure_(Generation_III))
- [How to implement Top-down Grid Movement in Godot — Sandro Maglione](https://www.sandromaglione.com/articles/top-down-grid-movement-in-godot-game-engine)
- [Finite State Machine for Turn-Based Games — GameDev.net](https://gamedev.net/blogs/entry/2274204-finite-state-machine-for-turn-based-games/)
- [Creating a game-size world map of Pokémon Fire Red — Medium](https://medium.com/@mmmulani/creating-a-game-size-world-map-of-pok%C3%A9mon-fire-red-614da729476a)
