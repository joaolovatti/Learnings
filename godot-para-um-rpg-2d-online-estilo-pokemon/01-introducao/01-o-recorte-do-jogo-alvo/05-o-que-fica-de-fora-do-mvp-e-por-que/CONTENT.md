# O que explicitamente fica de fora do MVP e por que

![capa](cover.png)

O conceito anterior terminou com uma cena de teste imaginária — três terminais, dois clientes vendo o mesmo mapa, batalha resolvida localmente, um NPC com diálogo. Tudo que está fora dessa cena é o contra-escopo. E o contra-escopo precisa ser tão explícito quanto a fronteira: não uma lista de coisas esquecidas, mas uma lista de coisas **recusadas** — feature por feature, com o motivo escrito.

Todo documento de escopo sério tem duas metades: o que está dentro (in-scope) e o que está fora (out-of-scope, também chamado de *non-goals* ou *exclusions*). A segunda metade existe porque, sem ela, cada conversa consigo mesmo durante o desenvolvimento vira uma renegociação silenciosa. Em equipes, o inchaço de escopo é freado pela fricção social; num projeto solo, o único freio é o contra-escopo escrito. A mecânica operacional é direta: quando uma ideia nova aparece, ela bate nessa lista. Se está lá, a regra é não construir — a menos que algo de dentro seja removido para abrir espaço. Trocar, sim; acumular, não.

As exclusões deste MVP se organizam em quatro famílias. A lógica por trás de todas é a mesma: parecem pequenas, mas cada uma puxa UI, balanceamento, persistência e testes próprios.

| Família | Features excluídas | Por que parece pequena | Por que não é |
|---|---|---|---|
| Progressão profunda | Captura com cálculo probabilístico, evolução (por nível, item, troca, amizade), aprendizado de movimentos por level-up, TMs | "É só um botão de Pokébola" | Puxa estado novo de combate, campos novos na criatura, inventário de pokébolas, slot na party, autoridade server-side, RPC de captura |
| Combate rico | Tabela completa de 18 tipos (~324 interações), habilidades, itens de batalha, clima, efeitos de status encadeados, prioridades, críticos | "Os tipos são só uma multiplicação" | Decisão arquitetural que não está madura; modelar errado cedo custa mais do que refatorar depois |
| Extensão de mundo | Múltiplas cidades e rotas interconectadas, minigames (pesca, cassino), eventos de história ramificados, NPCs com IA complexa | "É só mais um mapa" | Um segundo mapa não adiciona aprendizagem nova — replica trabalho já validado |
| Polimento de produção | Trilha sonora completa, arte final, cutscenes, localização, menus cosméticos, conquistas | "São detalhes visuais" | Otimizar o que talvez precise ser jogado fora é o anti-padrão clássico de projetos que nunca chegam a ter o loop fechado |

Vale detalhar a captura de criaturas porque ela é o exemplo mais frequentemente subestimado. "É só um botão de Pokébola na UI de batalha" é a frase. A realidade de implementação: a tentativa de captura exige um novo estado no fluxo de combate, a criatura precisa de campos que ainda não existem (HP atual normalizado, status ativo, taxa de captura base da espécie), o inventário de pokébolas precisa estar pronto e validado, a party precisa ter slot aberto com persistência funcionando, e no modo online o servidor precisa ser autoritativo sobre o resultado — RPC de captura, validação server-side, replicação na party do jogador específico. O que parecia uma semana é três semanas no melhor cenário, num projeto em que o core loop ainda não fechou.

O sistema de tipos merece uma nota separada porque a razão para cortá-lo é diferente das outras. Não é incapacidade de implementar — é que a forma final do sistema de tipos ainda não é conhecida com a profundidade necessária para modelar certo. Tentar ao menos "modelar os 18 tipos no código para não ter que refatorar depois" é especulação arquitetural, uma forma disfarçada de scope creep: o MVP usa dano plano exatamente para postergar essa decisão até que haja clareza suficiente. Modelar errado cedo é mais caro do que refatorar depois — uma lição que qualquer engenheiro com experiência em sistemas distribuídos reconhece imediatamente.

O princípio por trás das quatro famílias é o mesmo: cada feature cortada não é "menos jogo". É tempo de desenvolvimento humano que volta para o core loop — para o que realmente precisa funcionar antes de tudo o mais. E neste projeto em particular há um multiplicador que torna o corte ainda mais valioso: cada mecânica que fica de fora é uma mecânica que não precisa ser sincronizada, validada no servidor e persistida remotamente. O twist do online — que o próximo conceito vai explorar — transforma cada decisão de escopo em uma decisão de arquitetura distribuída. Cortar captura no MVP não economiza uma semana; economiza três.

## Fontes utilizadas

- [Scope Creep: The Silent Killer of Solo Indie Game Development (Wayline)](https://www.wayline.io/blog/scope-creep-solo-indie-game-development)
- [Solo Game Dev: Avoiding Scope Creep and Staying on Track (Wayline)](https://www.wayline.io/blog/solo-game-dev-scope-creep-stay-on-track)
- [GameDev Protips: How To Kick Scope Creep In The Ass And Ship Your Indie Game (Daniel Doan, Medium)](https://medium.com/@doandaniel/gamedev-protips-how-to-kick-scope-creep-in-the-ass-and-ship-your-indie-game-8fa3051500d1)
- [How to Avoid Scope Creep in Game Development (Codecks)](https://www.codecks.io/blog/2025/how-to-avoid-scope-creep-in-game-development/)
- [Scope — The Level Design Book](https://book.leveldesignbook.com/process/preproduction/scope)
- [How to Build an MVP Game: A Step-by-Step Guide (Mind Studios)](https://games.themindstudios.com/post/how-to-build-an-mvp-game/)
- [Making Your First Game: Minimum Viable Product — Scope Small, Start Right (Extra Credits)](https://www.youtube.com/watch?v=UvCri1tqIxQ)
- [Gen III/IV Capture Mechanics (The Cave of Dragonflies)](https://www.dragonflycave.com/mechanics/gen-iii-iv-capturing/)
- [What is "Out of Scope" and How To Avoid Out of Scope Work (ScopeStack)](https://scopestack.io/blog/what-is-out-of-scope)
- [In Scope vs. Out of Scope Meaning With Examples (Indeed)](https://www.indeed.com/hire/c/info/out-of-scope)

---

**Próximo conceito** → [O twist do online sobre um Pokémon single-player](../06-o-twist-do-online-sobre-um-pokemon-single-player/CONTENT.md)
