# O conceito de MVP jogável em gamedev

![capa](cover.png)

O conceito anterior entregou um inventário de seis sistemas sem os quais um Pokémon-like deixa de ser reconhecível. Um inventário completo, porém, não é o mesmo que um plano executável. A tentação natural a partir dele é implementar tudo ao mesmo tempo — e é exatamente aí que a maioria dos projetos pessoais de gamedev morre: não por falta de talento, mas porque o desenvolvedor nunca fecha nada de ponta a ponta antes de perseguir o próximo sistema. A resposta a esse padrão de fracasso tem nome: **MVP jogável** (Minimum Viable Product).

Um MVP jogável é a menor versão do jogo que ainda exercita integralmente o **core loop** — o ciclo repetível de ações que define a experiência central. "Menor" aqui tem precisão técnica: não é "versão inacabada" nem "demo sem polimento". É uma fronteira definida por três critérios simultâneos. Jogabilidade fechada: o jogador consegue iniciar uma sessão, executar o loop central ao menos uma vez e terminar sem encontrar paredes técnicas — crash, tela vazia, estado impossível. Escopo mínimo honesto: contém o menor subconjunto de mecânicas que ainda preserva a identidade do jogo. Qualidade de produção deliberadamente baixa: arte de placeholder, um único mapa, balanceamento aproximado, zero polimento de UI. O objetivo é **fechar o loop**, não encantar.

Três conceitos são frequentemente confundidos com MVP, e vale separar com precisão:

| Conceito | Quando vem | O que valida |
|---|---|---|
| **Protótipo** | Antes do MVP | Uma única pergunta de design ("movimento tile-a-tile com interpolação é satisfatório?") — pode ser um cubo numa grade |
| **MVP jogável** | Primeiro marco de jogo real | O core loop inteiro funciona de ponta a ponta com placeholder |
| **Vertical slice** | Depois do MVP | Uma fatia de alta fidelidade com assets finais, pensada para vender a visão do projeto |
| **First playable / Alpha** | Produção industrial | Checklists de features contratuais — não se aplica bem a projetos pessoais |

O MVP é anterior a todos eles: é a prova de que o core loop funciona antes de qualquer fidelidade ou contrato.

A disciplina operacional do MVP é direta e exige ser executada explicitamente: liste tudo que o jogo final deveria ter, identifique as mecânicas não-negociáveis do core loop, e corte implacavelmente tudo o mais para um backlog pós-MVP. O que fica de fora não é esquecido — é parqueado conscientemente, e só é tocado depois que o loop central está rodando. Pesquisas com projetos indie falhos apontam scope creep como o fator dominante de abandono, com cerca de 40% dos desenvolvedores relatando burnout diretamente ligado a projetos que cresceram além do controlável. Um recorte escrito que especifica o que fica de fora é a defesa concreta contra isso: quando a tentação aparece, você confere o documento em vez de decidir no impulso.

Vale nomear também o perigo oposto: um MVP tão enxuto que nem parece um jogo. Se o core loop não for identificado com precisão, o desenvolvedor pode "fechar" algo que tecnicamente roda mas não captura nenhuma das qualidades que tornam aquele gênero reconhecível. Para um Pokémon-like, o core loop mínimo tem forma específica:

```
explorar tile de mapa
  → topar com entidade (NPC ou inimigo)
    → entrar em combate por turnos
      → resolver o combate
        → retornar ao mapa
```

Um protótipo que só exercita o movimento sem combate, ou só o combate sem o overworld, não fecha o loop — é uma peça isolada. O teste é sempre o mesmo: **o loop inteiro roda de ponta a ponta com placeholder?** Se não, não é MVP; é componente.

A relação entre MVP e o inventário do conceito anterior é direta. Dos seis sistemas listados — top-down ortográfico, tilemap com atributos, movimento tile-a-tile, NPCs com diálogo, combate por turnos e party com persistência — o MVP não precisa implementar todos com profundidade. Precisa que todos estejam presentes o suficiente para o loop fechar: um mapa simples (tilemap), movimento funcional (tile-a-tile), pelo menos um NPC ou inimigo que abre a tela de combate, e um combate que resolve até um lado chegar a zero HP. Party com seis criaturas, múltiplos mapas, branches de diálogo, sistema completo de tipos — isso é pós-MVP. A régua é sempre a mesma: *sem isso, o loop fecha?* Se sim, fica de fora por ora.

Esse conceito é o instrumento que vai converter o inventário de mecânicas já mapeado em uma fronteira concreta — os próximos conceitos aplicam exatamente esse filtro ao Pokémon-like online deste projeto, definindo o que entra, o que fica explicitamente de fora e em que ordem os blocos são construídos.

## Fontes utilizadas

- [Game Dev Glossary: Prototype, Vertical Slice, First Playable, MVP, Demo — @askagamedev](https://www.tumblr.com/askagamedev/746300998961741824/game-dev-glossary-prototype-vertical-slice)
- [How to USE a Minimum Viable Product to Build a Better Game — Game Designing](https://gamedesigning.org/career/mvp/)
- [What is an MVP? Starting Game Production — Tiny Colony](https://medium.com/@TinyColonyGame/what-is-an-mvp-starting-game-production-40f5a552856d)
- [Vertical Slice vs MVP: What's the Difference? — Tiny Hydra](https://tinyhydra.com/vertical-slice-vs-mvp/)
- [Scope Creep in Indie Games: How to Avoid Development Hell — Wayline](https://www.wayline.io/blog/scope-creep-indie-games-avoiding-development-hell)
- [Scope Creep: The Silent Killer of Solo Indie Game Development — Wayline](https://www.wayline.io/blog/scope-creep-solo-indie-game-development)
- [Why MVP is the Kiss of Death for Game Development — Wayline](https://www.wayline.io/blog/mvp-kiss-of-death-game-development)
- [How to Build an MVP Game: A Step-by-Step Guide — The Mind Studios](https://games.themindstudios.com/blog/how-to-build-an-mvp-game/)

---

**Próximo conceito** → [A fronteira concreta do MVP deste projeto](../04-a-fronteira-concreta-do-mvp-deste-projeto/CONTENT.md)
