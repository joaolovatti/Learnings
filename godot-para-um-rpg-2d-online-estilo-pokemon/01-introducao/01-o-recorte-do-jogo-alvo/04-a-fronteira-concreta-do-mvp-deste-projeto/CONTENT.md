# A fronteira concreta do MVP deste projeto

![capa](cover.png)

Os dois conceitos anteriores construíram o instrumento: o inventário dos seis sistemas não-negociáveis de um Pokémon-like e a definição operacional de MVP jogável — a menor versão que fecha o core loop de ponta a ponta. Este conceito aplica esse instrumento. "Estilo Pokémon Fire Red online" é uma referência cultural; a fronteira concreta do MVP é a tradução dessa referência em afirmações testáveis — critérios que dizem, sem ambiguidade, quando o protótipo está pronto o suficiente para o livro terminar.

O MVP deste projeto se sustenta em **três pilares**, cada um com um critério de aceitação binário: funciona ou não funciona, sem meio-termo.

| Pilar | Critério de aceitação |
|---|---|
| Mapa navegável em grid | `TileMapLayer` com colisão, personagem movendo tile a tile com interpolação, pelo menos um NPC com diálogo |
| Combate por turnos funcional | Transição overworld → batalha, state machine com ações/dano/vitória, retorno ao mapa |
| Dois clientes vendo o mesmo mundo | Servidor headless autoritativo, dois clientes conectados via ENet/WebSocket vendo e sincronizando avatares |

O primeiro pilar é um **mapa navegável em grid**: um único mapa — uma cidade pequena com uma rota curta — construído com `TileMapLayer`, com camadas de colisão funcionando, personagem do jogador se movendo tile a tile com interpolação visual, e pelo menos um NPC com caixa de diálogo disparada por interação. Não é "o mundo de Kanto"; é um mapa que prova que a engine de mapas, o movimento em grid e a interação básica fecham o ciclo.

O segundo pilar é o **combate por turnos funcional**: a transição do overworld para uma cena de batalha — disparada por um NPC ou por um tile de grama alta —, uma state machine com pelo menos os estados listados abaixo, HP decrescendo e retorno ao mapa quando a batalha termina.

```
aguardando input
  → executando animação
    → calculando resultado (fórmula de dano, truncagem inteira)
      → verificando fim (HP ≤ 0 → vitória/derrota)
        → retornando ao overworld
```

Um movimento, um oponente, fórmula de dano simples: o que importa é o loop fechado, não o balanceamento.

O terceiro pilar é **dois clientes vendo o mesmo mundo**: um servidor dedicado rodando em modo headless, dois clientes Godot conectando via ENet ou WebSocket, ambos renderizando o mesmo mapa e vendo o avatar do outro se mover em tempo real. O servidor é autoritativo sobre posição; a persistência pode ser mínima — um JSON no disco do servidor salvando a posição do último jogador conectado é suficiente para cumprir o critério.

A estrutura dos três pilares segue o padrão do **walking skeleton**: uma implementação fina que atravessa verticalmente todas as camadas da arquitetura — cliente, rede, servidor, persistência — com funcionalidade mínima em cada uma, de modo que o sistema inteiro "anda" antes de qualquer camada ficar profunda. A diferença do walking skeleton genérico para este projeto é que aqui há três esqueletos — um por pilar — e todos os três precisam estar de pé para o MVP ser declarado completo.

A fronteira é inclusiva nesses três e **exclusiva em tudo o mais**. Captura de criaturas, evolução, tabela de tipos completa, múltiplos mapas encadeados com transições, inventário rico, economia, trocas entre jogadores, PvP, anti-cheat sofisticado — tudo isso mora do lado de fora da linha. Essa exclusão não é postergação descuidada; é o mesmo recorte deliberado que o primeiro conceito deste subcapítulo defendeu. Um recorte escrito com "o que fica de fora" é a defesa concreta contra scope creep: quando a tentação de adicionar o sistema de tipos aparece no mês dois, ela bate na fronteira em vez de entrar silenciosamente no backlog.

Há um detalhe importante no terceiro pilar que vale nomear: o combate por turnos, no MVP, é **local** — ocorre na cena de batalha de um único cliente, sem replicação para o servidor ou para o outro jogador. Isso é uma exclusão intencional, não um descuido. Replicar combate em tempo real exige autoridade de estado compartilhado, sincronização de aleatoriedade e tratamento de desconexão no meio da batalha — problemas não-triviais que pertencem a uma fase posterior. O MVP prova que a rede funciona para o overworld; o combate online é pós-MVP.

Para tornar a fronteira concreta, vale a sessão de teste imaginária que valida o MVP ao fim do livro: três terminais abertos — servidor, cliente A, cliente B. O cliente A (Alice) conecta, spawna no centro do mapa. O cliente B (Bob) conecta dez segundos depois e o sprite de Alice aparece na tela de Bob se movendo. Alice anda três tiles para o norte; na tela de Bob, Alice desliza tile a tile, com o mesmo timing. Alice caminha até um NPC, pressiona `E`, lê o diálogo, tenta atravessar água — o movimento é bloqueado. Alice entra num tile de grama alta, fade, tela de batalha: sprite do adversário, HP bar, menu de ação, dano calculado, HP decresce, retorno ao overworld. Do lado de Bob, Alice simplesmente desapareceu do mapa por um instante e reapareceu — o combate foi local, deliberadamente. Se tudo isso acontece, os três pilares batem. Se qualquer um quebra — por exemplo, os dois clientes se veem mas os movimentos dessincronizam por dois segundos —, o MVP não está pronto, por mais polido que o resto esteja.

Essa fronteira é o ponto de chegada que amarra todo o subcapítulo. O inventário de mecânicas não-negociáveis descreveu os seis sistemas; a definição de MVP jogável forneceu o critério de corte; a fronteira concreta aplica esse corte a este projeto específico. O próximo conceito explicita o lado de fora da linha — o que fica de fora e por que — fechando o mapa completo do recorte antes de o livro entrar em qualquer implementação.

## Fontes utilizadas

- [What is a Walking Skeleton? — Smartpedia (t2informatik)](https://t2informatik.de/en/smartpedia/walking-skeleton/)
- [Walking Skeleton in Software Architecture — Medium](https://medium.com/@jorisvdaalsvoort/walking-skeletons-in-software-architecture-894168276e3f)
- [What is an MVP? Starting Game Production — Tiny Colony](https://medium.com/@TinyColonyGame/what-is-an-mvp-starting-game-production-40f5a552856d)
- [Game Dev Glossary: Prototype, Vertical Slice, First Playable, MVP, Demo — @askagamedev](https://www.tumblr.com/askagamedev/746300998961741824/game-dev-glossary-prototype-vertical-slice)
- [Minimum Viable Product: What Does MVP in Gaming Mean? — Game Designing](https://gamedesigning.org/career/mvp/)
- [High-level multiplayer — Godot Engine documentation](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html)
- [Multiplayer in Godot 4.0: Scene Replication — Godot blog](https://godotengine.org/article/multiplayer-in-godot-4-0-scene-replication/)
- [Essential Scope Rules for Successful Solo Game Dev — Wayline](https://www.wayline.io/blog/essential-scope-rules-solo-game-dev)

---

**Próximo conceito** → [O que explicitamente fica de fora do MVP e por que](../05-o-que-fica-de-fora-do-mvp-e-por-que/CONTENT.md)
