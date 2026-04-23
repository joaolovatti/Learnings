# Critério de Decisão para Pedidos

![capa](cover.png)

Os quatro conceitos anteriores deste subcapítulo construíram o modelo analítico completo: o stud injeta micro-sombras e highlights que modulam a percepção de cor; o tile elimina essa modulação e entrega fidelidade máxima ao color ID; as peças round introduzem espaço negativo sistemático na forma de uma grade de losangos que separa pixels e reforça bordas — mas fragmenta gradações suaves; e a distância de visualização calibra o peso real de cada um desses efeitos, favorecendo a fusão óptica a partir de 1,5 m. O que falta é transformar esse modelo em uma regra operacional: dado um pedido de retrato com características conhecidas — tipo de imagem, expectativa do cliente, orçamento disponível — qual peça você especifica, e como essa especificação chega ao fornecedor sem ambiguidade?

O primeiro eixo de decisão é o **tipo de imagem**. Retratos fotográficos de pessoas reais — face humana iluminada naturalmente, com gradações contínuas de tom, transições suaves de sombra na bochecha e no pescoço — têm exatamente o perfil que mais penaliza qualquer fonte de textura adicional. O objetivo do mosaico é quantizar essa continuidade em células de cor de 8 mm e fazer com que, à distância de apreciação na parede, o observador reconstitua a ilusão de gradação. Square tile é a escolha que mais colabora com esse objetivo: cobertura total da baseplate (sem losangos), ausência de stud (sem micro-sombra), e cores percebidas com fidelidade mais alta ao color ID. Para uma imagem estilizada — silhueta de high-contrast, pop art, ícone com paleta reduzida e bordas bem definidas —, a grade de losangos da round tile deixa de ser ruído e passa a ser recurso: ela cria separação automática entre pixels adjacentes que reforça a leitura de bordas, e o efeito visual a 1,5–2 m evoca o Pop Art dos sets LEGO Art oficiais como Beatles e Andy Warhol. Para um produto que precisa parecer inequivocamente LEGO — em que o cliente quer o "feel" de brick art e não de impressão gráfica —, square plate ou round plate introduzem a textura 3D do stud que permanece lida como profundidade de superfície mesmo a 2 m de distância.

O segundo eixo é a **expectativa do cliente**, que raramente chega articulada em termos de tipo de peça. A maioria dos clientes não sabe a diferença entre plate e tile antes de fazer o pedido. O que eles sabem é o que querem sentir ao ver o produto pronto. Uma forma eficaz de capturar essa expectativa sem entrar em nomenclatura técnica é mostrar duas fotos de referência — um retrato montado em square tile e outro em round tile ou square plate — e perguntar qual deles parece mais com o que a pessoa tem em mente. A resposta situa o cliente em uma das três categorias práticas: "acabamento gráfico limpo" (aponta para square tile), "visual LEGO Art" (aponta para round tile), ou "produto brick com textura" (aponta para plate). Essa conversa de alinhamento antes do pedido evita a situação recorrente em que o cliente recebe um mosaico com round tiles e se surpreende com a grade de losangos que o render digital no BrickLink Studio não mostrava de forma fiel.

O terceiro eixo é o **orçamento**. A diferença de custo entre os tipos de peça é real, mas não dramática. Em compatíveis de qualidade como Gobricks, a hierarquia de preço por unidade é aproximadamente:

| Tipo de peça | Part ID BrickLink | Custo relativo (compatível premium) |
|---|---|---|
| 1×1 square plate | 3024 | Base (mais barato) |
| 1×1 round plate | 4073 | +5% a +10% |
| 1×1 square tile | 3070b | +10% a +20% |
| 1×1 round tile | 98138 | +15% a +25% |

Para um painel 32×32 de 1.024 peças, essa diferença representa entre R$ 10 e R$ 30 no custo de material dependendo do câmbio e do fornecedor. É uma diferença real, mas não é o critério que deveria dominar a escolha para um produto que o cliente vai pendurar na parede. O critério de orçamento torna-se relevante quando o pedido é de múltiplos painéis ou quando o projeto tem um teto de custo de material que não deixa margem para a categoria mais cara. Fora dessas situações, a diferença de custo é absorvível no preço de venda sem impacto perceptível no ticket final.

A regra de decisão pode ser condensada numa árvore de dois níveis:

```
Tipo de imagem:
├── Retrato fotográfico (gradações suaves, tons de pele, iluminação natural)
│   ├── Cliente quer fidelidade máxima → square tile (3070b)
│   └── Cliente quer "feel LEGO Art" reconhecível → round tile (98138)
└── Imagem estilizada (alto contraste, paleta limitada, bordas definidas)
    ├── Quer separação de pixels Pop Art → round tile (98138)
    ├── Quer textura artesanal 3D → round plate (4073)
    └── Quer pixels quadrados limpos → square tile (3070b) ou square plate (3024)
```

A distância de visualização confirmada pelo conceito anterior valida que nenhuma dessas escolhas é "errada" em termos absolutos — os efeitos que parecem problemáticos a 20 cm ficam substancialmente atenuados a 1,5–2 m. O que muda é o caráter do produto: square tile produz o acabamento mais próximo de arte gráfica; round tile produz o padrão visual dos sets LEGO Art modernos; plate (square ou round) produz o produto que mais "parece LEGO". A decisão é de posicionamento, não de qualidade.

Uma vez definido o tipo de peça, a especificação do pedido ao fornecedor precisa ser precisa. A linha de material gerada pelo software de mosaico (BrickLink Studio, Brickmosaicdesigner, ou ferramenta customizada) produz uma lista no formato `Design ID + Color ID + quantidade`. Para que essa lista chegue ao Gobricks ou ao BrickLink sem ambiguidade, o fluxo é:

1. **Confirmar o Design ID correto para o tipo de peça escolhido.** Se o algoritmo de mosaico foi configurado para gerar com round tile mas você quer pedir square tile, a lista precisa ser reprocessada ou as peças precisam ser substituídas manualmente — os Design IDs são diferentes e um fornecedor não vai substituir automaticamente.
2. **Verificar disponibilidade de cor antes de fechar.** No Gobricks, nem todos os Color IDs têm estoque contínuo em todos os tipos de peça. Um Color ID disponível em 1×1 plate pode estar indisponível no mesmo período em 1×1 tile. Conferir isso antes de confirmar o pedido evita atrasos de semanas.
3. **Usar o Design ID e não o nome popular da peça na comunicação com fornecedores.** "Tile liso 1×1" pode ser interpretado como 3070b (tile sem groove) ou como 3070 (versão mais antiga). O número elimina ambiguidade. Para o Gobricks, usar a tabela de correspondência Gobricks ID ↔ BrickLink Design ID — disponível no repositório público no GitHub — garante que a peça recebida é exatamente a que foi calculada no software.

A armadilha mais comum nesse fluxo não é escolher o tipo errado de peça: é especificar um tipo no software e pedir outro no fornecedor por descuido. O resultado é um mosaico montado com a lista de cores calculada para round tile mas as peças físicas sendo square plate — as cores percebidas mudam por causa das micro-sombras do stud e o retrato fica com aparência diferente do que o render digital indicava. Verificar que o Design ID da lista de material corresponde ao tipo de peça efetivamente pedido é o passo de qualidade mais simples e mais frequentemente omitido.

Para um negócio de mosaicos de retrato em escala inicial, a escolha de peça padrão que minimiza variáveis e maximiza qualidade percebida pelo cliente é square tile (3070b) com base preta. Essa escolha alinha com o que os sets LEGO Art de maior apelo fotográfico usam, entrega fidelidade de cor superior para rostos com gradações suaves, e é a categoria que o cliente menos questiona quando vê o produto pronto — porque parece impressão gráfica precisa, não um campo de texturas competindo com o retrato. Quando o cliente pede explicitamente algo que "pareça LEGO Art" referenciando os sets de Beatles ou Warhol — ele quer round tile (98138). Quando o cliente quer o produto mais "artesanal" com profundidade de superfície visível — plate de qualquer variante serve. Esses casos são minoria; a maioria dos pedidos de retrato fotográfico vai para square tile.

## Fontes utilizadas

- [Everything You Want to Know About LEGO Mosaics — BrickNerd](https://bricknerd.com/home/everything-you-want-to-know-about-lego-mosaics-11-12-24)
- [Mosaic — Studio Help Center — BrickLink](https://studiohelp.bricklink.com/hc/en-us/articles/5625025298327-Mosaic)
- [LEGO Art: the new mosaic theme — New Elementary](https://www.newelementary.com/2020/07/lego-art-new-mosaic-theme.html)
- [All About LEGO Mosaics — Brick Builder's Handbook](https://brickbuildershandbook.com/all-about-lego-mosaics/)
- [GoBricksPart-API: conversion table Gobricks vs LEGO part IDs — GitHub](https://github.com/mnemocron/GoBricksPart-API)
- [How to Design a Brick Mosaic — Stewart Lamb Cromar](https://stubot.me/how-to-design-a-brick-mosaic/)
- [Is it really possible to rebrick LEGO Art mosaics at a reasonable price? — Stonewars](https://stonewars.com/features/is-it-really-possible-to-rebrick-lego-art-mosaics-at-a-reasonable-price/)

---

**Próximo subcapítulo** → [Baseplates: O Substrato do Mosaico](../../04-baseplates-o-substrato-do-mosaico/CONTENT.md)
