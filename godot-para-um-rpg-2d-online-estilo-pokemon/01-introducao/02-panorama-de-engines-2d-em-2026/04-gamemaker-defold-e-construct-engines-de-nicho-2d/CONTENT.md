# GameMaker, Defold e Construct — Engines de Nicho 2D

![capa](cover.png)

Depois de Unity (falha nas dimensões eliminatórias 1 e 2) e Phaser (falha eliminatória na dimensão 2 e sem editor visual), o espaço que sobra é preenchido por três engines que apostaram em recortes específicos do desenvolvimento 2D: **GameMaker**, com otimização nativa para 2D e linguagem proprietária; **Defold**, com footprint mínimo e arquitetura de mensagens; e **Construct**, sem código, com editor no browser. Cada uma acerta em algo que as anteriores erravam — e cada uma falha de forma diferente no crivo que o projeto impõe.

**GameMaker** existe desde 1999 e passou por várias mãos (YoYo Games, Playtech, Opera). Em 2023 mudou de assinatura para licença única: gratuito para uso não-comercial, $99,99 para comercial com exportação para PC/mobile/web, Enterprise com console export por ~$800/ano. O 2D é genuinamente de primeira classe — o editor tem Room Editor, Sprite Editor, Tile Layer e Image Editor integrados sem nenhuma fricção de base 3D. Dimensão 1: aprovada sem ressalva.

A linguagem é GML (GameMaker Language), criada especificamente para o engine. A sintaxe lembra C superficialmente (`if`, `for`, `while`, ponto e vírgula), mas é uma linguagem proprietária sem tipagem estática, sem orientação a objetos real, sem namespaces e sem package system. Para um engenheiro sênior vindo de Java ou Kotlin, GML parece uma versão amputada do que ele já conhece: você reconhece a forma, mas sente a ausência de generics, interfaces, enums tipados e separação de responsabilidades em módulos. Projetos grandes acumulam colisões de nome de variável global e estruturas ad hoc que não escalam. O modelo de objetos usa **Objects** e **Rooms** — equivalentes aproximados de entities e scenes — sem hierarquia de nós como Godot, composição feita por coordenação manual entre instâncias via variáveis globais ou chamadas diretas.

Na dimensão 2 (multiplayer embutido), GameMaker falha pelo ângulo oposto ao esperado: em 2024/2025 adicionou um sistema de **rollback networking** voltado para jogos de luta e ação local, onde client-side prediction é viável porque ambos os lados executam as mesmas entradas num tick determinístico. Para um RPG servidor-autoritativo com mundo persistente — onde o servidor valida movimento em grid, processa combate por turnos com estado de inventário e gerencia múltiplas sessões simultâneas — rollback não é o paradigma correto. O path seria servidor Node.js com Socket.io, exatamente o que Phaser já demandava, sem ganho nenhum em relação à situação anterior.

---

**Defold** foi criado pela King (Candy Crush) e em 2020 transferido para a Defold Foundation, que mantém o engine como software livre com licença própria permissiva — gratuito para uso comercial, sem royalties, mas não é MIT/Apache. O runtime é C++ compilado nativamente; o scripting é **Lua 5.1**.

A arquitetura é genuinamente incomum: objetos se comunicam via **message passing assíncrono**, sem chamadas diretas entre scripts. Para mover um sprite de outro game object, você envia uma mensagem:

```lua
msg.post("outro_objeto#script", "mover", { dx = 1, dy = 0 })
```

O desacoplamento é extremo — nenhum script referencia diretamente outro — mas o trace de fluxo de programa fica espalhado por mensagens assíncronas. Um engenheiro acostumado a rastrear chamadas síncronas em stack traces vai precisar reaprender a debugar por logs de mensagem, o que tem custo cognitivo real nas primeiras semanas. Lua é uma linguagem real (Redis, Nginx, World of Warcraft a usam para extensão), com closures, metatables, coroutines e FFI para C, mas usa índice `1` como base de arrays e não tem sistema de tipos estático nativo — curva de adaptação existe para quem vem de linguagens tipadas.

O grande diferencial do Defold é o **footprint**: runtime compilado de ~2MB para mobile, builds pequenas sem configuração, hot reload no editor. O editor inclui suporte a TileMaps, Scene editor (chamado de "collection") e funciona bem para 2D. Dimensão 1: aprovada. Na dimensão 2, Defold anunciou em 2025 integração oficial com **Photon Realtime** — um serviço externo de matchmaking para jogos de sessão curta. Para um RPG com mundo persistente e autoridade de servidor, Photon não é o modelo; o servidor custom de lógica de RPG continua inteiramente por conta do desenvolvedor. Dimensão 2: falha. Ecossistema: pequeno — o fórum e o Discord têm resposta rápida da própria equipe, mas a quantidade de tutoriais sobre tópicos específicos (RPG top-down, multiplayer complexo) é uma fração do que existe para Unity ou Godot.

---

**Construct 3** tem o editor no próprio browser — sem instalação — e a proposta central é **desenvolvimento sem código** via **Event Sheets**: cada linha é um par condição → ação:

```
On [Sprite] overlaps [Wall]    →   Set [Player].X to previous X
On [Attack Button] pressed     →   Subtract 10 from [Enemy].HP
```

Para protótipos e jogos simples, Event Sheets funcionam. Para lógica de RPG complexa — máquinas de estado de NPC com múltiplos estados, inventário com filtragem e ordenação, combate por turnos com efeitos em cadeia — as folhas crescem horizontalmente sem hierarquia de chamadas, sem funções reutilizáveis reais, sem separação de responsabilidades. Para um engenheiro sênior que resolve problemas abstraindo em módulos e interfaces, a sensação é a de tentar escrever uma pipeline de dados em Excel — funciona, não escala. Construct suporta JavaScript/TypeScript desde 2019 como alternativa ao Event Sheets, mas nesse ponto você escreve um jogo em JS sem os benefícios de uma arquitetura de engine clara.

Na dimensão 2, Construct tem um plugin de **WebRTC peer-to-peer** embutido: um peer funciona como "host", sem servidor dedicado. Para um RPG servidor-autoritativo, P2P sem autoridade real não resolve; o path é, de novo, servidor externo custom. Na dimensão 4 (licença), Construct usa assinatura mensal (~$9,99/mês ou ~$99/ano para Personal) — exportação bloqueada sem assinatura ativa, o que introduz custo recorrente inexistente em Godot ou Defold.

Aplicando as sete dimensões do critério lado a lado:

| Dimensão | GameMaker | Defold | Construct |
|----------|-----------|--------|-----------|
| Pipeline 2D nativo | Excelente | Bom | Bom |
| **Multiplayer embutido** | **Falha** — rollback, não server-auth | **Falha** — Photon externo | **Falha** — P2P sem servidor |
| Custo de aprendizado | GML proprietário — barreira real | Lua + message passing — curva diferente | Event Sheets até certo ponto; JS depois |
| Licença | Gratuito não-comercial; $99,99 vitalício | Gratuito permissivo | Assinatura mensal obrigatória |
| Footprint | Razoável | Excelente (~2MB runtime) | Excelente (browser, sem instalação) |
| Ergonomia do editor | Bom para 2D | Bom, com hot reload | Bom, mas browser-only |
| Ecossistema | Médio | Pequeno | Pequeno a médio (voltado a iniciantes) |

As três falham na dimensão eliminatória 2, cada uma por um caminho diferente. Somadas às restrições de licença (Construct), ecossistema pequeno (Defold) e linguagem proprietária com teto de complexidade para projetos grandes (GameMaker), as três ficam abaixo da barra para um projeto de longa duração como o deste livro. No próximo conceito, Unreal entra no crivo com um perfil radicalmente oposto: não falha por falta, mas por excesso em todas as dimensões erradas para um RPG top-down 2D.

## Fontes utilizadas

- [GameMaker — site oficial](https://gamemaker.io/)
- [GameMaker November 2023 Pricing/Terms Change FAQ](https://gamemaker.zendesk.com/hc/en-us/articles/14954144182941-November-2023-Pricing-Terms-Change-FAQ)
- [GameMaker Rollback Networking — Create a Multiplayer Game](https://manual.gamemaker.io/beta/en/GameMaker_Language/GML_Reference/Rollback/Creating_Multiplayer.htm)
- [Defold — site oficial](https://defold.com/)
- [Defold in 2025 — A Year in Review](https://defold.com/2026/01/02/Defold-2025-Retrospective/)
- [Why Defold Game Engine is the Secret Weapon for 2D Game Development with Lua](https://game-developers.org/why-defold-game-engine-is-the-secret-weapon-for-2d-game-development-with-lua)
- [Construct (game engine) — Wikipedia](https://en.wikipedia.org/wiki/Construct_(game_engine))
- [Construct 3 Multiplayer — Documentation](https://www.construct.net/en/make-games/manuals/construct-3/plugin-reference/multiplayer)
- [6 Best 2D Game Engines To Use in 2026 — Rocket Brush](https://rocketbrush.com/blog/best-2d-game-engines)

**Próximo conceito →** [Unreal — Overkill Consciente](../05-unreal-overkill-consciente/CONTENT.md)
