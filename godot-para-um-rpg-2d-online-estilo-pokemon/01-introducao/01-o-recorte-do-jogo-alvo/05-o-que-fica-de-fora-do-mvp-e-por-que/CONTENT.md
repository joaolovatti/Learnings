# O que explicitamente fica de fora do MVP e por que

![capa](cover.png)

## O que é?

Projetos pessoais de gamedev morrem muito mais por adicionar features do que por falta delas. "O que fica de fora do MVP" é o **contra-escopo declarado** — a lista explícita, por escrito, das mecânicas que você recusa construir nesta iteração, mesmo que elas façam parte obviamente do jogo final que você sonha. É uma ferramenta de defesa do projeto, não de humildade.

## Explicação técnica

Todo documento sério de escopo tem duas metades: o que **está dentro** (in-scope) e o que **está fora** (out-of-scope, também chamado de *non-goals* ou *exclusions*). A segunda metade existe porque, sem ela, cada reunião consigo mesmo ao longo do projeto vira uma renegociação silenciosa do escopo — o famoso *scope creep*, o "inchaço" por acumulação de features "pequenas" e "rápidas". Em equipes, o inchaço é limitado pela fricção social de convencer os outros; num projeto solo, o único freio é o contra-escopo escrito.

A mecânica é: toda ideia nova que aparece durante o desenvolvimento ("e se eu adicionasse captura? é só uma tela a mais") é confrontada com a lista de exclusão. Se está lá, a regra é: **não constrói, a menos que remova outra coisa de dentro do MVP para abrir espaço**. Trocar, sim; adicionar, não. Isso força o trade-off a ficar visível em vez de se esconder como "só mais uma semana".

Num Pokémon Fire Red-like online, as exclusões típicas de MVP são de quatro famílias:

- **Mecânicas de progressão profunda** — captura de criaturas com cálculo probabilístico (HP atual, status, catch rate, ball modifier), evolução (por nível, item, troca, amizade, horário, gênero), aprendizado de movimentos por level-up, TMs/HMs. Cada uma parece pequena, mas puxa UI, balanceamento, persistência e testes próprios.
- **Sistemas de combate ricos** — tabela completa de tipos (18 tipos, ~324 interações), efeitos de status (paralisia, sono, queimadura, confusão), habilidades, itens de batalha, clima, prioridades de movimento, críticos. O MVP pega **1-2 tipos e dano plano**.
- **Extensão de mundo** — múltiplas cidades e rotas, minigames (pesca, cassino), eventos de história ramificados, NPCs com IA complexa. O MVP pega **um mapa pequeno** que comprove que mapas funcionam.
- **Polimento de produção** — trilha sonora completa, arte final, cutscenes, localização, menus cosméticos, conquistas. No MVP, **placeholder é suficiente**; arte e música sobem em passes posteriores.

O princípio por trás das quatro famílias é o mesmo: cada feature cortada não é "menos jogo"; é **tempo de CPU humano que volta para o core loop jogável**.

## Exemplo concreto

Imagine que, duas semanas depois de o protótipo já mover um personagem em grid e entrar em combate por turnos com uma criatura dummy, aparece a ideia: *"já que estou aqui no combate, vou só implementar captura — é só um botão 'Pokébola' na UI de batalha, uma fórmula e um sprite novo"*.

Sem contra-escopo, essa ideia parece inofensiva. Com o contra-escopo ("captura, evolução, tabela completa de tipos estão FORA do MVP"), a conversa muda. Você se pergunta o que **captura puxa junto**:

1. Um novo estado no combate: pós-tentativa de captura (fuga? captura bem-sucedida? falhou?).
2. Uma fórmula com HP atual, status, catch rate, ball modifier — todos campos que precisam existir no modelo de dados da criatura.
3. Um inventário de pokébolas (logo, sistema de inventário precisa estar pronto, que ainda não está).
4. Uma party com slot aberto para receber a nova criatura (persistência da party precisa existir, o que puxa serialização).
5. No **modo online**, autoridade: quem decide se a captura foi bem-sucedida? Servidor. Então precisa de RPC de captura, validação server-side, replicação da nova criatura na party — três dias, no melhor cenário.

O que parecia "um botão a mais" é **uma semana inteira**. E o core loop (andar no mapa + lutar + ver o outro cliente andar no mesmo mapa) ainda não está fechado ponta-a-ponta. A regra do contra-escopo diz: *se quiser captura, remova duas semanas de algo que já está dentro*. Como não há nada dentro do MVP que valha menos que o core loop, a resposta é **não**. A ideia vira um bilhete em `docs/post-mvp.md` e o foco volta.

Um segundo exemplo, mais sutil: *"mas eu posso pelo menos modelar os 18 tipos no código, para não ter que refatorar depois?"*. Isso é **especulação arquitetural**, uma forma disfarçada de scope creep. O MVP usa dano plano (sem tipos) justamente porque a forma final do sistema de tipos ainda não é conhecida — mexer em `CombatResolver` depois é mais barato do que modelar errado agora. Fica de fora.

## Síntese

O contra-escopo é o mecanismo que transforma "vontade de projeto solo" em "projeto solo que termina". Ele vive lado a lado com a **fronteira concreta do MVP** (o conceito anterior): um define o que está dentro, o outro defende essa fronteira contra a erosão diária. É também o contraponto natural às **mecânicas não-negociáveis** de um Pokémon Fire Red-like — parte do objetivo de listar "não-negociáveis" foi justamente deixar todo o resto cortável. Quando o capítulo sobre o *twist online* entrar, vai ficar ainda mais claro: cada mecânica cortada aqui é uma mecânica que você não precisa sincronizar, validar no servidor e persistir remotamente — triplicando a economia.

## Fontes utilizadas

- [Scope Creep: The Silent Killer of Solo Indie Game Development (Wayline)](https://www.wayline.io/blog/scope-creep-solo-indie-game-development)
- [Solo Game Dev: Avoiding Scope Creep and Staying on Track (Wayline)](https://www.wayline.io/blog/solo-game-dev-scope-creep-stay-on-track)
- [GameDev Protips: How To Kick Scope Creep In The Ass And Ship Your Indie Game (Daniel Doan, Medium)](https://medium.com/@doandaniel/gamedev-protips-how-to-kick-scope-creep-in-the-ass-and-ship-your-indie-game-8fa3051500d1)
- [How to Avoid Scope Creep in Game Development (Codecks)](https://www.codecks.io/blog/2025/how-to-avoid-scope-creep-in-game-development/)
- [Scope — The Level Design Book](https://book.leveldesignbook.com/process/preproduction/scope)
- [How to Build an MVP Game: A Step-by-Step Guide (Mind Studios)](https://games.themindstudios.com/post/how-to-build-an-mvp-game/)
- [Making Your First Game: Minimum Viable Product — Scope Small, Start Right (Extra Credits)](https://www.youtube.com/watch?v=UvCri1tqIxQ)
- [Gen III/IV Capture Mechanics (The Cave of Dragonflies)](https://www.dragonflycave.com/mechanics/gen-iii-iv-capturing/)
- [Pokémon Evolution Charts (Pokémon Database)](https://pokemondb.net/evolution)
- [What is "Out of Scope" and How To Avoid Out of Scope Work (ScopeStack)](https://scopestack.io/blog/what-is-out-of-scope)
- [In Scope vs. Out of Scope Meaning With Examples (Indeed)](https://www.indeed.com/hire/c/info/out-of-scope)

---

**Próximo conceito** → [O twist do online sobre um Pokémon single-player](../06-o-twist-do-online-sobre-um-pokemon-single-player/CONTENT.md)
