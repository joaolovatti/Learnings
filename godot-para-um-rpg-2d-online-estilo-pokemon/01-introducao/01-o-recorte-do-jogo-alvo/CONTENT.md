# O Recorte do Jogo-Alvo

![capa](cover.png)

## Sobre este subcapítulo

Este subcapítulo traduz a frase "RPG 2D online estilo Pokémon" em um recorte técnico fechado, do tipo que um engenheiro de software entende como uma especificação de produto. Antes de qualquer comparação de engine ou setup de ferramenta, é preciso saber exatamente o que se está construindo: a falta dessa precisão é o que faz projetos de gamedev pessoais durarem três meses e morrerem. Aqui o jogo-alvo deixa de ser uma referência cultural ("tipo Pokémon Fire Red") e vira um inventário de mecânicas: top-down em grid, combate por turnos, party, NPCs, mundo persistente, dois ou mais clientes em rede.

Ele aparece como o primeiro subcapítulo porque tudo nos capítulos seguintes — escolha de engine, decisões de arquitetura, fronteiras do MVP, sequência de aprendizado — só faz sentido contra esse alvo. Sem ele fixado, qualquer comparação Godot vs. Unity vira filosófica em vez de prática. Com ele fixado, o resto do livro é apenas uma sequência de "como entregar exatamente isso".

## Estrutura

Os blocos deste subcapítulo são: (1) **a referência cultural** — o que de fato significa "estilo Pokémon Fire Red" em termos de mecânicas (top-down em grid, exploração tile-a-tile, NPCs com diálogo, batalha por turnos contra criaturas, party, mundo persistente entre sessões); (2) **o que é o MVP jogável** — fronteira mínima do protótipo ao fim do livro, com os elementos não-negociáveis (mapa navegável, combate funcional, dois clientes vendo o mesmo mundo) e o que fica de fora (sistema completo de tipos, captura, evolução, dezenas de mapas); (3) **o twist online** — o que muda quando o jogo deixa de ser single-player local e passa a ter dois ou mais clientes compartilhando estado (autoridade do servidor, sincronização, persistência remota); (4) **a trilha de chegada** — como o livro entrega esse alvo de forma incremental, cada bloco viabilizando o próximo, e qual é o entregável testável ao fim de cada bloco.

## Objetivo

Ao terminar, o leitor terá uma especificação mental compacta do jogo-alvo no nível de detalhe que um PRD interno teria — capaz de responder "o que é e o que não é parte deste protótipo?" sem hesitar — e entenderá por que esse recorte específico é o que torna a comparação de engines significativa nos próximos subcapítulos. Ficará claro também por que um Pokémon completo não cabe no escopo do livro, e por que tentar fazê-lo seria a forma mais rápida de o projeto morrer.

## Conceitos

1. [Por que o recorte do jogo-alvo vem antes de qualquer decisão de engine](01-por-que-o-recorte-vem-antes-da-engine/CONTENT.md) — sem alvo fixado, comparações e arquitetura viram discussão filosófica.
2. [As mecânicas não-negociáveis de um Pokémon Fire Red-like](02-mecanicas-nao-negociaveis-de-um-pokemon-fire-red-like/CONTENT.md) — inventário técnico: top-down em grid, tile-a-tile, NPCs com diálogo, combate por turnos, party, mundo persistente.
3. [O conceito de MVP jogável em gamedev](03-o-que-e-um-mvp-jogavel-em-gamedev/CONTENT.md) — fronteira mínima de "isto é um jogo", não "isto está pronto para lançar".
4. [A fronteira concreta do MVP deste projeto](04-a-fronteira-concreta-do-mvp-deste-projeto/CONTENT.md) — mapa navegável + combate funcional + dois clientes vendo o mesmo mundo.
5. [O que explicitamente fica de fora do MVP e por que](05-o-que-fica-de-fora-do-mvp-e-por-que/CONTENT.md) — captura, evolução, sistema completo de tipos e dezenas de mapas ficam fora para proteger o projeto.
6. [O twist do online sobre um Pokémon single-player](06-o-twist-do-online-sobre-um-pokemon-single-player/CONTENT.md) — autoridade do servidor, sincronização de estado e persistência remota como pilares da mudança.
7. [A trilha incremental até o MVP](07-a-trilha-incremental-ate-o-mvp/CONTENT.md) — quatro blocos onde cada um viabiliza o próximo e tem entregável testável ao fim.

## Fontes utilizadas

- [Minimum Viable Product: What Does MVP in Gaming Mean? (Game Designing)](https://gamedesigning.org/career/mvp/)
- [9 Free Fan-Made Pokémon MMOs All Trainers Will Love (MakeUseOf)](https://www.makeuseof.com/tag/free-pokemon-mmos/)
- [Temtem — official site (referência canônica de "Pokémon-like online")](https://temtem.com/)
- [Pokémon Revolution Online — referência de fan-made MMO](https://pokemonrevolution.net/)
- [Game Development Roadmap 2026 (Codelivly)](https://codelivly.com/game-development-roadmap/)
