# A trilha incremental até o MVP

![capa](cover.png)

Os seis conceitos anteriores responderam *o quê* construir: as mecânicas inegociáveis, a fronteira exata do MVP, o que fica deliberadamente de fora e como o online realoca a arquitetura inteira. A trilha incremental responde a pergunta que sobra — *em que ordem* — e a ordem importa tanto quanto o conteúdo.

Projetos pessoais de gamedev morrem, com frequência, não por ambição excessiva nem por escolha errada de engine, mas por falta de integração contínua. O padrão tem nome na literatura ágil de gamedev: **component factory**. Arte fabrica sprites num canto, código fabrica sistemas noutro, design escreve documentos de mechanics — e nada é integrado num estado jogável até uma data futura que nunca chega. O resultado é um "pile of parts": peças que individualmente compilam e coletivamente não formam jogo algum. A contramovida é dividir o caminho até o MVP em **blocos sequenciais** onde cada bloco termina em um **entregável testável** — algo que se abre, roda e joga, ainda que feio e incompleto. Rami Ismail, em sua série sobre milestones, chama isso de "first playable": não o jogo pronto, não o demo polido, mas o menor estado possível que ainda é *jogo* e não *peças de jogo*.

Para este projeto, a trilha tem quatro blocos:

```
Bloco 1 — Fundamentos Godot      (caps. 2–6)   → personagem animado sobre tilemap com colisão
Bloco 2 — Sistemas Pokémon-like  (caps. 7–11)  → core loop completo em single-player
Bloco 3 — Camada online          (caps. 12–14) → dois clientes no mesmo mundo, estado persistindo
Bloco 4 — Pipeline de assets AI  (cap. 15)     → MVP do bloco 3 com arte gerada por IA
```

**Bloco 1** cobre os primitivos da engine: `Node`, `Scene`, árvore de cena, `_process` e `_physics_process`, GDScript, `signals`, `Sprite2D`, `AnimatedSprite2D`, `Resource`, `TileMapLayer` e `TileSet`. O entregável é simples ao ponto de parecer insuficiente: um personagem animado andando sobre um mapa de tiles com colisão. Não é um jogo; é a prova de que as peças estruturais estão no lugar. Quadrado branco sobre grid cinza é válido — o objetivo é integração, não polimento.

**Bloco 2** constrói os sistemas Pokémon-like em single-player: movimento em grid tile-a-tile, câmera, transições entre mapas, NPCs com diálogo, combate por turnos, party, inventário e persistência local em `user://`. O entregável é o core loop completo rodando num único cliente — overworld navegável, transição para tela de batalha, combate resolvido até a vitória, retorno ao mapa, save em disco. É exatamente a fronteira concreta do conceito 4: três a quatro mapas, sprites de placeholder, quatro ataques no total, sem captura, sem sistema de tipos. Feio, mas jogável. Se o projeto for abandonado aqui por qualquer razão, o desenvolvedor não tem peças soltas: tem um jogo que roda.

**Bloco 3** adiciona a camada online sobre o single-player que já funciona: `ENetMultiplayerPeer` ou `WebSocketMultiplayerPeer`, servidor dedicado em modo headless, `MultiplayerSynchronizer` para replicação de estado, autoridade do servidor sobre posição e ações, persistência server-side com banco para dados de jogador. O twist que o conceito 6 detalhou entra aqui — e entra *depois* de um loop single-player fechado, nunca em paralelo com ele. O entregável: dois clientes conectados ao mesmo servidor vendo o mesmo mapa, vendo os avatares um do outro se mover em tempo real, com estado persistindo entre sessões. O combate ainda é local neste ponto; sincronizar batalhas é problema pós-MVP deliberado.

**Bloco 4** fecha com o pipeline de assets com IA: geração de sprites, tilesets e trilha sonora via OpenAI/Midjourney e modelos de música, pós-processamento para os formatos do Godot (folhas de sprite, paleta indexada, loops de áudio) e integração ao projeto. O entregável é o MVP do bloco 3 visualmente re-skinnado — o mesmo jogo jogável, agora com arte que não é placeholder.

Três princípios selam o design dessa sequência e valem ser nomeados explicitamente.

**Dependência estritamente ascendente.** O bloco N não assume nada além do bloco N−1. Movimento em grid depende de `TileMapLayer`, não de arquitetura de rede; tentar sincronizar um combate que ainda não existe localmente é o caminho mais curto para a paralisia. O fluxo de dependências no diagrama abaixo é unidirecional — nenhuma seta vai para cima:

```
[TileMap + Node + GDScript] → [grid movement + battle loop + save] → [ENet + MultiplayerSync + DB] → [IA pipeline]
```

**Entregável testável, não polido.** O fim de cada bloco é um "first playable" — algo que *roda*, não algo vendável. Isso elimina o risco de passar meses construindo camadas que nunca são integradas porque "a base ainda não está pronta". A base está pronta quando o entregável do bloco anterior existe e roda.

**Risco técnico isolado por bloco.** Sincronização de estado, autoridade de servidor e desconexão no meio de batalha são problemas difíceis; por isso estão isolados no bloco 3, em cima de um single-player que já fecha o loop. Tentar resolver autoridade de servidor antes de ter um tilemap funcionando produz exatamente o component factory que a trilha existe para evitar.

O contraexemplo que torna o princípio concreto: um desenvolvedor ignora a trilha e decide, no mês 1, estruturar "corretamente" a arquitetura cliente-servidor completa — banco, contas, replicação — antes de ter um `TileMap` funcionando. Três meses depois tem um servidor que autoriza nada, porque não há gameplay para autorizar. A ambição não estava errada; a ordem estava.

A trilha incremental é o fio que converte o recorte definido nos conceitos 1 a 6 nos capítulos concretos que virão a seguir. A decisão de usar Godot 4 — que o próximo subcapítulo vai fundamentar — só faz sentido pleno agora que se sabe quais blocos a engine precisa suportar, em que sequência e com que entregável ao fim de cada um.

## Fontes utilizadas

- [Milestones — Levelling The Playing Field (Rami Ismail)](https://ltpf.ramiismail.com/milestones/)
- [Game Dev Glossary: Prototype, Vertical Slice, First Playable, MVP, Demo (askagamedev)](https://www.tumblr.com/askagamedev/746300998961741824/game-dev-glossary-prototype-vertical-slice)
- [What Is A Vertical Slice? Exploring Key Concepts And Benefits (GIANTY)](https://www.gianty.com/vertical-slice-game-development/)
- [What is an MVP? Starting Game Production (Tiny Colony / Medium)](https://medium.com/@TinyColonyGame/what-is-an-mvp-starting-game-production-40f5a552856d)
- [Continuous Integration in Game Development (Playgama)](https://playgama.com/blog/general/boost-game-development-efficiency-with-continuous-integration-ci/)
- [High-level multiplayer — Godot Engine documentation](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html)
- [Multiplayer in Godot 4.0: Scene Replication (Godot Engine)](https://godotengine.org/article/multiplayer-in-godot-4-0-scene-replication/)
- [ENetMultiplayerPeer — Godot Engine documentation](https://docs.godotengine.org/en/stable/classes/class_enetmultiplayerpeer.html)

---

**Próximo subcapítulo** → [Panorama de Engines 2D em 2026](../../02-panorama-de-engines-2d-em-2026/CONTENT.md)
