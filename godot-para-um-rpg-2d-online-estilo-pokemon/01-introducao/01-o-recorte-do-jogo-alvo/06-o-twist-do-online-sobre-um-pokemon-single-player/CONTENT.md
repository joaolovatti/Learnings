# O twist do online sobre um Pokémon single-player

![capa](cover.png)

O conceito anterior fechou com uma observação que merece expansão: cortar captura de criaturas do MVP não economiza uma semana, economiza três. A razão disso não é a dificuldade da mecânica em si — é o multiplicador que o online aplica sobre qualquer decisão de estado do jogador. Esse multiplicador é o assunto aqui.

Um Pokémon single-player roda inteiro dentro de uma máquina. O cartucho é a fonte da verdade: o código que lê o input, aplica as regras do jogo, altera o estado — HP, posição, inventário — e grava o save file vive num único processo. O cartucho confia no jogador porque não há adversário modelado, não há ninguém para enganar. Quando um Action Replay seta o nível de uma criatura para 100, o cartucho acredita sem questionar — não existe ninguém para conferir.

Assim que dois ou mais clientes compartilham o mesmo mundo, essa simplicidade desaba em três lugares ao mesmo tempo.

O primeiro é a **autoridade do servidor** (*authoritative server*). O servidor torna-se o único lugar que pode declarar "isto aconteceu". O cliente para de executar regras de jogo de forma definitiva — ele envia *intenções* e espera que o servidor valide, aplique e responda com o novo estado. Se um cliente adulterado tenta declarar "meu Pokémon tem 99999 HP", o servidor ignora: ele guarda o HP real na sua própria memória e nunca aceita estado vindo do cliente, só intenções. Esse modelo resolve o problema de confiança que o cartucho simplesmente não tinha que enfrentar.

O segundo é a **sincronização de estado** (*state synchronization*). Com vários clientes olhando para o mesmo mundo, o servidor precisa empurrar periodicamente o estado que cada cliente deve enxergar. A frequência dessa empurrada chama-se *tick rate* — para um jogo tile-a-tile por turnos, 10 a 20 ticks por segundo já é generoso (FPSs competitivos rodam em 64 a 128 Hz, mas a exigência aqui é incomparavelmente menor). Em Godot 4, o nó `MultiplayerSynchronizer` materializa isso: você declara quais propriedades de quais nós devem ser replicadas, e a engine propaga as mudanças do peer autoritativo para todos os demais. A complicação secundária é que a rede atrasa — 50 a 200 ms é o normal. O cliente que pressiona "cima" vê o personagem travado até o servidor confirmar o movimento; para que a experiência não pareça borrachuda, existe a técnica de *client-side prediction*: o cliente aplica o input otimisticamente e corrige se o servidor discordar. Para um Pokémon-like em grid, onde cada passo é um evento discreto e o ritmo é lento, a janela de atraso é tolerável sem prediction sofisticado — mas o conceito precisa estar no mapa porque vai aparecer ao depurar movimentos que parecem "escorregadios".

O terceiro é a **persistência remota** (*server-side persistence*). O save deixa de ser um arquivo no dispositivo do jogador e passa a ser uma linha num banco no servidor — tipicamente Postgres para dados de jogador (conta, party, inventário, posição, flags de progressão) e Redis ou memória in-process para estado efêmero (quem está online, quem está em batalha). O estado "vivo" continua em RAM no servidor para ser rápido; o banco é o meio de persistência, não a fonte da verdade em tempo real. Gravações acontecem em eventos críticos — mudança de mapa, fim de batalha, troca de item, desconexão — e não a cada tick, para proteger o I/O do banco.

Para tornar concreto o que essa inversão implica, considere um único episódio de gameplay: Alice pressiona `↑` duas vezes, entra na grama alta, encontra um Pokémon selvagem, ataca e vence. No Fire Red, esse episódio é um loop dentro de um processo:

```
frame N:    input = UP           → posicao.y -= 1
frame N+1:  colisao com gramado  → rand() dispara encontro
frame N+2:  entra na tela de batalha → HP local -= dano
frame N+3:  fim da batalha → EXP local += 120, salva save_slot_1.sav
```

Tudo rodando na mesma CPU, sem testemunhas. Na versão online, com Alice (cliente A), Bob (cliente B) e um servidor Godot headless, o mesmo episódio vira uma conversa:

```
cliente_A   → servidor:   {input: UP, tick: 1042}
servidor:                 valida (A pode se mover? tile destino é walkable?)
                          mundo.players[A].pos.y -= 1
servidor    → cliente_A:  {state: pos_A=(4,6)}       // confirma para A
servidor    → cliente_B:  {state: pos_A=(4,6)}       // A entrou no FOV de B

servidor:                 roda RNG de encontro (server-side!)
                          cria instancia Pokemon_selvagem em mundo.battles[A]
servidor    → cliente_A:  {event: battle_started, foe: pokemon_id=27}

cliente_A   → servidor:   {action: attack, move: TACKLE}
servidor:                 calcula dano (formula rodando NO SERVIDOR)
                          mundo.battles[A].foe.hp -= 18
servidor    → cliente_A:  {battle_state: foe_hp=2}

servidor:                 foe.hp == 0 → grava no banco:
                          UPDATE player_party SET exp = exp + 120 WHERE ...
servidor    → cliente_A:  {event: battle_won, exp_gained: 120}
```

Três efeitos da inversão ficam visíveis aqui. O RNG de encontro rodou no servidor — se rodasse no cliente, um cliente adulterado poderia forçar ou suprimir encontros. Bob foi notificado de uma mudança que não pediu: ele não pressionou tecla nenhuma, mas a posição de Alice chegou na tela dele porque o servidor empurrou o estado. Os 120 de EXP não são um incremento em arquivo local — são uma transação num banco compartilhado, visível a qualquer cliente que se conecte depois.

Esse é o twist real do online: não uma feature adicionada sobre um Pokémon single-player pronto, mas uma **realocação de responsabilidades** — o cliente vira um renderizador de decisões, o servidor vira o juiz único do mundo e o banco vira o caderno de histórias compartilhado. Essas três mudanças não são módulos que se encaixam depois; elas reconfiguram a arquitetura do jogo inteiro. Código de batalha, de inventário, de movimento: tudo precisa ser escrito já assumindo que a decisão final mora do outro lado de um socket.

É por isso que o contra-escopo do conceito anterior fechou com o multiplicador. No single-player, captura é um botão na UI de batalha. No online, é um RPC de intenção, uma validação server-side, uma gravação atômica na party do jogador e uma replicação para todos os peers no mesmo mapa. A mecânica é a mesma; a conta é outra. O subcapítulo completo — do recorte ao MVP, do MVP ao contra-escopo — culmina aqui porque o twist é a condição que torna qualquer fronteira de escopo uma decisão de arquitetura distribuída. O próximo conceito vai mostrar, passo a passo, em que ordem esses três pilares são construídos sem afundar o projeto antes de fechar o primeiro loop.

## Fontes utilizadas

- [Client-Server Game Architecture — Gabriel Gambetta](https://www.gabrielgambetta.com/client-server-game-architecture.html)
- [Client-Side Prediction and Server Reconciliation — Gabriel Gambetta](https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html)
- [Client-side prediction — Wikipedia](https://en.wikipedia.org/wiki/Client-side_prediction)
- [Netcode — Wikipedia](https://en.wikipedia.org/wiki/Netcode)
- [MultiplayerSynchronizer — Godot Engine documentation](https://docs.godotengine.org/en/stable/classes/class_multiplayersynchronizer.html)
- [Multiplayer in Godot 4.0: Scene Replication — Godot Engine](https://godotengine.org/article/multiplayer-in-godot-4-0-scene-replication/)
- [High-level multiplayer — Godot Engine documentation](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html)
- [How do multiplayer games sync their state? — Qing Wei Lim (Medium)](https://medium.com/@qingweilim/how-do-multiplayer-games-sync-their-state-part-1-ab72d6a54043)
- [How do you save multiplayer game data, in a database or a file? — DragonFly DB](https://www.dragonflydb.io/faq/save-multiplayer-game-data-database-or-file)
- [Persistence for Ephemeral Game Servers — Hathora](https://blog.hathora.dev/persistence-for-ephemeral-game-servers/)
- [Authoritative Multiplayer — Heroic Labs (Nakama) Documentation](https://heroiclabs.com/docs/nakama/concepts/multiplayer/authoritative/)
- [Tick rate: What is it and how it affects gaming — nbn](https://www.nbnco.com.au/blog/entertainment/what-is-tick-rate-and-what-does-it-do)

---

**Próximo conceito** → [A trilha incremental até o MVP](../07-a-trilha-incremental-ate-o-mvp/CONTENT.md)
