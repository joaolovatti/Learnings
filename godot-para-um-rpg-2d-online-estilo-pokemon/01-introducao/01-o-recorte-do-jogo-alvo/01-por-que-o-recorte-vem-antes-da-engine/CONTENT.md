# Por que o recorte do jogo-alvo vem antes de qualquer decisão de engine

![capa](cover.png)

A maioria dos projetos pessoais de gamedev não morre por falta de talento nem por escolha errada de engine. Eles morrem porque o autor começou a escolher ferramenta antes de saber exatamente o que estava construindo. Esse é o argumento central deste conceito: a especificação compacta do jogo-alvo — suas mecânicas não-negociáveis, sua fronteira de MVP, o que explicitamente fica de fora — precisa existir **antes** de qualquer comparação de engine, linguagem ou arquitetura. Não é ordem de preferência; é dependência causal.

A razão é direta. Cada engine é boa em algumas coisas e ruim em outras por projeto, não por acaso. Phaser brilha em 2D para web, mas não tem multiplayer de alto nível nativo. Unity cobre quase tudo ao preço de curva de aprendizado e modelo de licença. Godot acerta o ponto ótimo para 2D com multiplayer nativo sob licença MIT — **se** o recorte exige 2D mais multiplayer. Sem recorte, você está escolhendo ferramenta sem conhecer a tarefa: qualquer comparação que você fizer vai ter viés de confirmação disfarçado de análise técnica.

A analogia mais próxima da sua bagagem de engenheiro de dados é a de escolha de banco de dados. Ninguém com experiência em dados adota Cassandra antes de entender se os reads são point-lookups ou scans amplos. Ninguém escolhe DynamoDB sem conhecer o access pattern de leitura e escrita. A engine é o banco; o recorte é o access pattern. A diferença relevante entre os dois mundos é que em engenharia de dados o padrão de acesso, uma vez mapeado, muda pouco — enquanto em gamedev pessoal o recorte é pressionado o tempo todo pela própria vontade do desenvolvedor de adicionar features. Por isso o recorte precisa ser **escrito**: oral, ele cede ao primeiro entusiasmo; no papel, ele resiste.

Considere dois engenheiros decididos a construir "um jogo tipo Pokémon online". O primeiro pula o recorte, instala Unity porque tem mais tutoriais e começa pelo que acha interessante: modela uma criatura em 3D, tenta um sistema de captura, adia a parte online porque configurar Mirror dá trabalho. Três meses depois tem assets desconexos e nenhum loop de gameplay funcionando. Desiste. O segundo escreve uma página antes de abrir qualquer editor:

| Dimensão | Decisão registrada |
|---|---|
| Mecânicas não-negociáveis | Top-down em grid, combate por turnos sem sistema de tipos, NPCs com diálogo, dois clientes vendo o mesmo mundo |
| Fronteira do MVP | Um mapa navegável, uma batalha funcional, dois clientes sincronizados |
| Fora do escopo | Captura, evolução, sistema de tipos — explicitamente |

Com isso na mão, a comparação de engine vira prática: "preciso de 2D com tilemap, multiplayer de alto nível nativo, rodar solo sem royalty, hot reload decente." A resposta cai para Godot 4 em minutos, não em semanas. Quando a tentação de adicionar sistema de tipos aparece no mês dois, ela bate no recorte em vez de entrar no backlog silenciosamente. A diferença entre os dois não é talento nem stack — é ordem de operações.

O problema que essa ordem previne tem nome na literatura: **scope creep** (inchaço de escopo). Post-mortems de jogos indie falhados apontam scope creep como a principal causa de abandono — a expansão gradual do projeto à medida que novas ideias surgem e a ambição cresce, até o ponto em que um desenvolvedor solo não consegue mais sustentar o ritmo. A característica insidiosa do scope creep é que cada adição parece pequena individualmente. "Vou adicionar sistema de tipos também" é uma frase de trinta segundos que representa semanas de trabalho. Um recorte escrito com "o que fica de fora" é a defesa concreta: quando a tentação aparece, você confere o documento em vez de decidir no impulso.

Este é o conceito que abre o subcapítulo porque todos os outros dependem dele. As mecânicas não-negociáveis, a definição de MVP jogável, a fronteira concreta do protótipo, o que fica de fora, o twist do online e a trilha incremental — nenhum desses conceitos faz sentido antes de você aceitar que o recorte vem primeiro. Eles são o conteúdo do recorte; este conceito é o argumento de por que ele precisa existir antes de qualquer linha de comparação técnica.

## Fontes utilizadas

- [Scope Creep in Indie Games: How to Avoid Development Hell (Wayline)](https://www.wayline.io/blog/scope-creep-indie-games-avoiding-development-hell)
- [Scope Creep: The Silent Killer of Solo Indie Game Development (Wayline)](https://www.wayline.io/blog/scope-creep-solo-indie-game-development)
- [Essential Scope Rules for Successful Solo Game Dev (Wayline)](https://www.wayline.io/blog/essential-scope-rules-solo-game-dev)
- [Why Scope Is the Most Dangerous Enemy of Indie Games (All That's Epic)](https://allthatsepic.com/blog/why-scope-is-the-most-dangerous-enemy-of-indie-games)
- [Game Design Document Explained: Choosing the Right Game Engine (Algoryte)](https://www.algoryte.com/news/game-design-document-explained-choosing-the-right-game-engine/)
- [What is an MVP? Starting Game Production (Tiny Colony / Medium)](https://medium.com/@TinyColonyGame/what-is-an-mvp-starting-game-production-40f5a552856d)
- [How to USE a Minimum Viable Product to Build a Better Game (Game Designing)](https://gamedesigning.org/career/mvp/)
- [Scope: Choose A Target! Focus! Shoot! (Game Developer)](https://www.gamedeveloper.com/design/scope-choose-a-target-focus-shoot-)
- [Managing the Scope of Your Video Game Project (IndieGameDev)](https://indiegamedev.net/2020/01/13/managing-scope/)
- [Game design document — Wikipedia](https://en.wikipedia.org/wiki/Game_design_document)

---

**Próximo conceito** → [As mecânicas não-negociáveis de um Pokémon Fire Red-like](../02-mecanicas-nao-negociaveis-de-um-pokemon-fire-red-like/CONTENT.md)
