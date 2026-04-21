# O conceito de MVP jogável em gamedev

![capa](cover.png)

## O que é?

Projetos pessoais de jogo tendem a morrer por excesso de ambição: o desenvolvedor acumula features sem nunca fechar nada jogável de ponta a ponta, e três meses depois abandona um repositório cheio de sistemas órfãos. O **MVP jogável** (Minimum Viable Product) é a resposta a esse fracasso — a menor versão do jogo que ainda contém o **core loop** rodando do início ao fim, e que serve para provar "isto é um jogo" muito antes de "isto está pronto para lançar".

## Explicação técnica

No vocabulário de gamedev, um MVP é a versão mais enxuta de um jogo que ainda exercita integralmente seu **core loop** — o ciclo repetível de ações que define a experiência ("andar → encontrar inimigo → lutar → voltar a andar", por exemplo). É uma **fronteira** definida por três critérios simultâneos:

1. **Jogabilidade fechada**: o jogador consegue iniciar uma sessão, executar o loop central ao menos uma vez e terminar sem encontrar paredes técnicas (crash, tela vazia, estado impossível).
2. **Escopo mínimo honesto**: contém o **menor subconjunto** de mecânicas que ainda preservam a identidade do jogo. Para um Pokémon-like, um ambiente explorável e um combate por turnos bastam; captura, evolução, árvore completa de tipos e dezenas de mapas ficam de fora.
3. **Qualidade de produção deliberadamente baixa**: arte de placeholder, um único mapa, balanceamento aproximado, zero polimento de UI. O objetivo é **fechar o loop**, não encantar.

O MVP jogável é distinto de três conceitos frequentemente confundidos:

- **Prototype** (protótipo) — valida **uma única pergunta de design** (ex.: "movimento tile-a-tile com interpolação é satisfatório?"). Não precisa ser um jogo; pode ser um cubo numa grade.
- **Vertical slice** — uma fatia de alta fidelidade, com assets finais e polimento, pensada para **vender a visão** (a investidores, publishers, comunidade). Vem **depois** do MVP.
- **First playable / alpha** — marcos de produção industrial, com checklists de features contratuais. Não se aplicam bem a projetos pessoais.

Um MVP é construído ao redor de um **core loop explícito**. A disciplina é: listar tudo que o jogo final deveria ter, identificar as mecânicas **não-negociáveis** desse loop, e cortar implacavelmente tudo o mais. O que fica de fora **não é esquecido** — é parqueado num backlog pós-MVP, que só é tocado depois que o loop central está rodando.

O custo de errar o recorte é concreto e mensurável: pesquisas com desenvolvedores indie indicam que escopo excessivo é o fator citado em mais de 70% dos abandonos. MVP jogável é, antes de ser uma técnica de produto, uma **técnica de sobrevivência de projeto**.

## Exemplo concreto

Imagine dois desenvolvedores começando um RPG 2D online estilo Pokémon no mesmo dia.

**Desenvolvedor A** (sem MVP): planeja um mundo com cinco mapas interligados, sistema de captura, evolução, dezoito tipos elementares, trocas entre jogadores, chat, leaderboard. Passa semana 1 desenhando o sistema de tipos numa planilha; semana 2 implementando inventário; semana 3 mexendo em shaders de água num dos mapas. No fim do mês, **nada está jogável**: o jogo não abre numa sessão completa, porque as peças não se encontram. Três meses depois, abandona.

**Desenvolvedor B** (com MVP jogável fixado): define o core loop como "explorar um mapa top-down → topar com um NPC ou inimigo → entrar em combate por turnos → voltar ao mapa". O MVP é `um mapa simples + movimento em grid + um NPC que abre diálogo + um encontro de combate com cálculo básico de dano + dois clientes vendo o mesmo jogador no mapa`. Tudo o mais — captura, evolução, tipos, múltiplos mapas, balanceamento fino, arte final — entra no backlog pós-MVP.

Semana 1 ele entrega movimento tile-a-tile com um quadrado colorido num tilemap de placeholder. Semana 2, um NPC parado que responde a um botão de interação. Semana 3, uma tela de combate que roda até o inimigo ou o jogador zerarem HP. Semana 4, um segundo cliente conectado vendo o primeiro andar. No fim do mês, **o loop inteiro roda** — feio, simplificado, mas inteiro. A partir daí, cada semana adicional **melhora** algo que já funciona, em vez de tentar finalmente ligar peças soltas.

A diferença não é disciplina pessoal; é **topologia do projeto**. O desenvolvedor B tem, em qualquer momento, um artefato jogável que responde "isto é o jogo?". O desenvolvedor A só teria um jogo no dia mítico em que tudo ficasse pronto ao mesmo tempo — um dia que quase nunca chega.

## Síntese

Um MVP jogável é a menor versão do jogo que ainda fecha o **core loop** de ponta a ponta, ignorando deliberadamente polimento, variedade e features secundárias para proteger o projeto contra a morte por escopo. Ele se diferencia de protótipo (que valida uma pergunta isolada) e de vertical slice (que vende a visão em alta fidelidade); vem **antes** dos dois. No contexto deste livro, o MVP é a régua que permite, nos próximos conceitos, traçar a **fronteira concreta** do que entra e do que fica de fora do protótipo Pokémon-like online, transformando uma referência cultural ("estilo Pokémon Fire Red") em uma especificação curta o suficiente para caber num livro.

## Fontes utilizadas

- [Game Dev Glossary: Prototype, Vertical Slice, First Playable, MVP, Demo — @askagamedev](https://www.tumblr.com/askagamedev/746300998961741824/game-dev-glossary-prototype-vertical-slice)
- [How to USE a Minimum Viable Product to Build a Better Game — Game Designing](https://gamedesigning.org/career/mvp/)
- [What is an MVP? Starting Game Production — Tiny Colony](https://medium.com/@TinyColonyGame/what-is-an-mvp-starting-game-production-40f5a552856d)
- [Vertical Slice vs MVP: What's the Difference? — Tiny Hydra](https://tinyhydra.com/vertical-slice-vs-mvp/)
- [Prototypes & Vertical Slice — Rami Ismail](https://ltpf.ramiismail.com/prototypes-and-vertical-slice/)
- [How to Build an MVP Game: A Step-by-Step Guide — The Mind Studios](https://games.themindstudios.com/post/how-to-build-an-mvp-game/)
- [Scope Creep in Indie Games: How to Avoid Development Hell — Wayline](https://www.wayline.io/blog/scope-creep-indie-games-avoiding-development-hell)
- [Designing The Core Gameplay Loop: A Beginner's Guide — Game Design Skills](https://gamedesignskills.com/game-design/core-loops-in-gameplay/)

---

**Próximo conceito** → [A fronteira concreta do MVP deste projeto](../04-a-fronteira-concreta-do-mvp-deste-projeto/CONTENT.md)
