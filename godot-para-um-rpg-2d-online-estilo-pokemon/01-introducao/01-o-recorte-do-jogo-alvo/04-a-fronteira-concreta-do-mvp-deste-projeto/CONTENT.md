# A fronteira concreta do MVP deste projeto

![capa](cover.png)

## O que é?

"Estilo Pokémon Fire Red online" ainda é vago demais para virar backlog. A fronteira concreta do MVP deste projeto é a tradução desse recorte em três entregáveis verificáveis — **mapa navegável em grid**, **combate por turnos funcional** e **dois clientes vendo o mesmo mundo** — com critérios de aceitação explícitos que dizem, sem ambiguidade, quando o protótipo está "pronto o suficiente" para o livro terminar.

## Explicação técnica

Enquanto o conceito genérico de MVP jogável (subcapítulo anterior) define *o formato* — "um loop central funcionando ponta a ponta" —, a fronteira concreta é *a instância específica* desse formato para este projeto. Ela se materializa como um pequeno conjunto de afirmações testáveis, no mesmo espírito de *acceptance criteria* de uma user story, só que aplicadas a um protótipo de jogo. O padrão é o do **walking skeleton**: uma implementação fina que atravessa verticalmente todas as camadas da arquitetura (cliente, rede, servidor, persistência) com funcionalidade mínima em cada uma, de modo que o sistema inteiro já "anda" antes de qualquer camada ficar profunda.

Para este livro, a fronteira é composta por três pilares não-negociáveis:

1. **Mapa navegável em grid.** Um único mapa (uma cidade pequena + uma rota curta, por exemplo) construído com `TileMapLayer`, com camadas de colisão funcionando, personagem do jogador se movendo **tile a tile** com interpolação visual, e pelo menos um NPC com caixa de diálogo disparada por interação. Não é "o mundo de Kanto". É *um* mapa que prova que a engine de mapas, movimento em grid e interação básica fecham o ciclo.

2. **Combate por turnos funcional.** Transição do mundo para uma cena de batalha disparada por um gatilho (NPC ou grama alta simulada), uma *state machine* de combate com pelo menos os estados "selecionar ação → executar → resolver dano → checar vitória", HP decrescendo, e retorno ao mundo quando a batalha termina. Um movimento, um oponente, fórmula de dano simples — o que importa é o loop fechado.

3. **Dois clientes vendo o mesmo mundo.** Um servidor dedicado rodando em modo headless, dois clientes Godot conectando via ENet ou WebSocket, ambos renderizando o mesmo mapa e vendo o avatar do outro jogador mover-se em tempo real. O servidor é autoritativo sobre posição; a persistência pode ser mínima (um JSON no disco do servidor salvando posição do último jogador conectado).

Cada pilar vem com um **critério de aceitação binário** — funciona ou não funciona, sem meio-termo. A fronteira é *inclusiva* nesses três e *exclusiva* em todo o resto: captura, evolução, tabela de tipos completa, múltiplos mapas encadeados, inventário rico, economia, trocas entre jogadores, PvP, anti-cheat sofisticado — tudo isso mora do lado de fora da linha. O subcapítulo seguinte ("O que fica de fora e por que") explicita essas exclusões; aqui, o que importa é a **linha de dentro**.

## Exemplo concreto

Imagine a sessão de teste que valida o MVP ao fim do livro. O engenheiro abre dois terminais:

```
# terminal 1 — servidor
godot4 --headless --path ./server server.tscn

# terminal 2 — cliente A
godot4 --path ./client client.tscn -- --server=localhost --user=alice

# terminal 3 — cliente B
godot4 --path ./client client.tscn -- --server=localhost --user=bob
```

**Pilar 3 — dois clientes no mesmo mundo.** Alice conecta, spawna no centro do mapa. Bob conecta dez segundos depois. No monitor de Alice, aparece um segundo sprite (Bob) se movendo. No monitor de Bob, o mesmo — Alice visível como outro jogador. Alice anda três tiles para o norte; na tela do Bob, Alice desliza tile a tile, com o mesmo timing. Fecha Alice, reabre — ela reaparece na última posição salva pelo servidor. **Critério bate: sim, o servidor é autoritativo e há persistência mínima.**

**Pilar 1 — mapa navegável.** Alice caminha até um NPC na entrada da casa. Pressiona `E`. Abre uma caixa de diálogo: *"Olá, treinador! Cuidado com o mato ali."* Alice fecha o diálogo, tenta atravessar um pedaço de água — o movimento é bloqueado pela camada de colisão. **Critério bate: grid + colisão + NPC + diálogo fecham.**

**Pilar 2 — combate funcional.** Alice entra num tile específico marcado como gatilho. A tela faz fade, entra a cena de batalha: sprite do adversário à direita, HP bar, menu *"Atacar / Fugir"*. Alice ataca; dano é calculado (nível × 2 + aleatório 1–5, digamos), HP do oponente cai de 20 para 14. O oponente ataca de volta. Loop continua até HP zerar. Fade de volta ao mundo, na mesma posição onde Alice estava. Enquanto isso, no cliente do Bob, Alice **não** aparece (ela está em uma cena de batalha local, sem replicação de combate — deliberadamente fora do escopo). **Critério bate: batalha funciona, o escopo da rede não foi inflado desnecessariamente.**

Tudo que o engenheiro observar *além* disso — se a fórmula de dano é balanceada, se o mapa é bonito, se tem música — é bônus. Nada disso é necessário para declarar o MVP entregue. Por outro lado, se qualquer um dos três pilares quebrar (ex: os dois clientes se veem mas os movimentos estão dessincronizados por 2 segundos), o MVP **não está pronto**, por mais polido que o resto esteja.

## Síntese

A fronteira concreta do MVP transforma o recorte cultural ("Pokémon Fire Red online") em três critérios binários — mapa navegável, combate por turnos, dois clientes sincronizados — cuja soma prova que o *walking skeleton* do projeto está de pé. É ela que amarra as mecânicas não-negociáveis do subcapítulo anterior à trilha incremental do seguinte: cada um dos quatro blocos da trilha existe, no fundo, para entregar um pedaço verificável dessa fronteira, e tudo que fica do lado de fora (captura, evolução, tipos completos) está lá justamente para não contaminar o que está do lado de dentro.

## Fontes utilizadas

- [What is an MVP? Starting Game Production (Tiny Colony)](https://medium.com/@TinyColonyGame/what-is-an-mvp-starting-game-production-40f5a552856d)
- [Game Dev Glossary: Prototype, Vertical Slice, First Playable, MVP, Demo (askagamedev)](https://www.tumblr.com/askagamedev/746300998961741824/game-dev-glossary-prototype-vertical-slice)
- [Vertical Slice vs MVP (Tiny Hydra)](https://tinyhydra.com/vertical-slice-vs-mvp/)
- [Walking Skeleton — Smartpedia](https://t2informatik.de/en/smartpedia/walking-skeleton/)
- [Prototypes, proofs of concept, walking skeletons and MVPs (tinnedfruit)](https://tinnedfruit.com/list/20180813)
- [Essential Scope Rules for Successful Solo Game Dev (Wayline)](https://www.wayline.io/blog/essential-scope-rules-solo-game-dev)
- [Multiplayer in Godot 4.0: Scene Replication (Godot blog)](https://godotengine.org/article/multiplayer-in-godot-4-0-scene-replication/)
- [High-level multiplayer — Godot Engine documentation](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html)
- [GameDrivenDesign/godot-multiplayer-template (GitHub)](https://github.com/GameDrivenDesign/godot-multiplayer-template)
- [Minimum Viable Product: What Does MVP in Gaming Mean? (Game Designing)](https://gamedesigning.org/career/mvp/)
