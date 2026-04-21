# O twist do online sobre um Pokémon single-player

![capa](cover.png)

## O que é?

Um Pokémon single-player roda inteiro dentro de uma máquina: o cartucho é a fonte da verdade, o save é um arquivo local, ninguém mais precisa concordar com o que aconteceu. Assim que o mesmo jogo passa a ter dois ou mais clientes compartilhando mundo, essa simplicidade desaba: surge a necessidade de um **servidor autoritativo** (single source of truth), de **sincronização de estado** entre clientes e de **persistência remota** em banco. O "twist online" é exatamente essa inversão de arquitetura — sair de "o cliente *é* o jogo" para "o cliente é um terminal que renderiza decisões tomadas em outro lugar".

## Explicação técnica

Num Pokémon single-player, o código que lê o input, aplica a regra do jogo, altera o estado (HP, posição, inventário) e grava o save vive num único processo. O cartucho confia no jogador; não há adversário modelado, não há ninguém para enganar.

Quando o mesmo jogo vira online, três pilares precisam ser instalados:

**1. Autoridade do servidor (server authority).** O servidor torna-se o único lugar que pode dizer "isto aconteceu". O cliente deixa de executar regras de jogo de forma definitiva — ele envia **intenções** (`input: mover para cima`, `ação: atacar com habilidade X`) e espera que o servidor valide, aplique e responda. Se um cliente hackeado tenta dizer "meu Pokémon tem 99999 HP", o servidor simplesmente ignora: ele guarda o HP real em sua própria memória. Esse modelo é chamado de *authoritative server* e é o padrão para qualquer jogo com estado competitivo ou persistente.

**2. Sincronização de estado (state synchronization).** Com vários clientes olhando para o mesmo mundo, o servidor precisa empurrar, periodicamente, o estado que cada cliente deve enxergar. A frequência dessa empurrada chama-se **tick rate** — para um jogo tile-a-tile por turnos, algo como 10-20 ticks por segundo já é generoso (FPSs competitivos rodam em 60-128 Hz, mas aqui a exigência é muito menor). Em Godot 4, o nó `MultiplayerSynchronizer` materializa isso: você marca quais propriedades de quais nós são replicadas, e a engine cuida de propagar as mudanças do peer autoritativo para os demais. A complicação secundária é que a rede atrasa (50-200 ms é comum): o cliente que pressiona "cima" vê o personagem travado até o servidor confirmar o movimento, o que exige técnicas como **client-side prediction** (o cliente aplica o input otimisticamente e corrige se o servidor discordar) para que a experiência não pareça borrachuda.

**3. Persistência remota (server-side persistence).** O save deixa de ser um arquivo no dispositivo do jogador e passa a ser uma linha num banco no servidor — tipicamente Postgres ou equivalente para dados de jogador (conta, party, inventário, posição), e Redis ou memória in-process para estado efêmero (quem está online, quem está em batalha). O estado "vivo" continua em RAM no servidor para ser rápido; o banco é o **medium de persistência**, não a fonte da verdade em tempo real. Gravações acontecem em eventos críticos (mudança de mapa, fim de batalha, troca de item, desconexão) e não a cada tick, para proteger o I/O do banco.

Essas três mudanças não são features adicionais que você encaixa depois — elas **reconfiguram a arquitetura do jogo inteiro**. Código de batalha, de inventário, de movimento: tudo precisa ser escrito já assumindo que a decisão final mora do outro lado de um socket.

## Exemplo concreto

Considere uma única cena de gameplay: o jogador pressiona `↑` duas vezes para entrar no gramado alto, encontra um Pokémon selvagem, ataca e ganha a batalha.

**No Pokémon single-player** (GBA, cartucho Fire Red), esse episódio é um `for`-loop glorificado dentro de um processo:

```
frame N:    input = UP           → posicao.y -= 1
frame N+1:  colisao com gramado  → rand() dispara encontro
frame N+2:  entra em cena de batalha → HP local -= dano
frame N+3:  fim da batalha → EXP local += 120, salva save_slot_1.sav
```

Tudo rodando na mesma CPU, sem testemunhas. Se o jogador usar um Action Replay para setar `nivel = 100`, o cartucho acredita — não existe ninguém para conferir.

**No mesmo jogo em versão online**, com dois clientes (jogadores A e B) e um servidor Godot headless, o mesmo episódio vira uma conversa:

```
cliente_A   → servidor:   {input: UP, tick: 1042}
servidor:                 valida (A pode se mover? tile destino é walkable?)
servidor:                 aplica mudança no estado autoritativo
                          mundo.players[A].pos.y -= 1
servidor    → cliente_A:  {state: pos_A=(4,6)}       // confirma
servidor    → cliente_B:  {state: pos_A=(4,6)}       // A entra no FOV de B
servidor:                 roda RNG de encontro (server-side, nao client-side!)
                          cria instancia Pokemon_selvagem em mundo.battles[A]
servidor    → cliente_A:  {event: battle_started, foe: pokemon_id=27}

cliente_A   → servidor:   {action: attack, move: TACKLE}
servidor:                 calcula dano (formula oficial, rodando NO SERVIDOR)
                          mundo.battles[A].foe.hp -= 18
servidor    → cliente_A:  {battle_state: foe_hp=2}
                          cliente_A anima -18 localmente (client prediction)
...
servidor:                 foe.hp == 0 → grava em PG:
                          UPDATE player_party SET exp = exp + 120 WHERE ...
                          INSERT INTO battle_log ...
servidor    → cliente_A:  {event: battle_won, exp_gained: 120}
```

Três efeitos colaterais do twist ficam visíveis no exemplo:

- O **RNG de encontro rodou no servidor**. Se rodasse no cliente, um jogador poderia forçar encontros a vontade; a autoridade migrou.
- O cliente B foi **notificado de uma mudança que não pediu** — ele não pressionou tecla nenhuma, mas precisa ver A se mover. Isso é sincronização de estado em ação.
- Os 120 de EXP não são mais um incremento em um arquivo local: são uma transação num banco compartilhado, que sobrevive ao fechamento de ambos os clientes.

## Síntese

O twist do online é uma realocação de responsabilidades: o cliente vira um **renderizador de decisões**, o servidor vira o **juiz único do mundo** (apoiado em autoridade, tick rate e `MultiplayerSynchronizer` — conteúdo dos capítulos 12 e 13), e o banco vira o **caderno de histórias compartilhado** (capítulo 14). Essa realocação casa com as mecânicas não-negociáveis listadas nos conceitos anteriores (movimento em grid, combate por turnos, party persistente) sem adicionar nada de novo à lista de features — mas redesenha completamente **onde cada uma delas executa**. Por isso este subcapítulo fecha com o twist: ele é a condição que torna a trilha de chegada (próximo conceito) uma sequência em que a camada online não é o último degrau, e sim uma reescrita que precisa ser desenhada desde o primeiro.

## Fontes utilizadas

- [Client-Server Game Architecture — Gabriel Gambetta](https://www.gabrielgambetta.com/client-server-game-architecture.html)
- [Client-Side Prediction and Server Reconciliation — Gabriel Gambetta](https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html)
- [MultiplayerSynchronizer — Godot Engine documentation](https://docs.godotengine.org/en/stable/classes/class_multiplayersynchronizer.html)
- [High-level multiplayer — Godot Engine documentation](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html)
- [Multiplayer in Godot 4.0: Scene Replication](https://godotengine.org/article/multiplayer-in-godot-4-0-scene-replication/)
- [MMO Architecture: Source of truth, Dataflows, I/O bottlenecks and how to solve them — PRDeving](https://prdeving.wordpress.com/2023/09/29/mmo-architecture-source-of-truth-dataflows-i-o-bottlenecks-and-how-to-solve-them/)
- [MMORPG Data Storage (Part 1) — Plant Based Games](https://plantbasedgames.io/blog/posts/01-mmorpg-data-storage-part-one/)
- [Authoritative Multiplayer — Heroic Labs (Nakama) Documentation](https://heroiclabs.com/docs/nakama/concepts/multiplayer/authoritative/)
- [How do multiplayer games sync their state? — Qing Wei Lim (Medium)](https://medium.com/@qingweilim/how-do-multiplayer-games-sync-their-state-part-1-ab72d6a54043)
- [Netcode — Wikipedia](https://en.wikipedia.org/wiki/Netcode)
- [Client-side prediction — Wikipedia](https://en.wikipedia.org/wiki/Client-side_prediction)
- [Temtem — official site (canonical "Pokémon-like online" reference)](https://temtem.com/)

---

**Próximo conceito** → [A trilha incremental até o MVP](../07-a-trilha-incremental-ate-o-mvp/CONTENT.md)
