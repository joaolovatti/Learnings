# O LDU (LEGO Design Unit)

![capa](cover.png)

Qualquer peça LEGO fabricada hoje encaixa perfeitamente em qualquer peça fabricada em 1970. Essa compatibilidade retroativa de décadas não acontece por acaso — ela é consequência de um sistema de medidas internamente coerente, onde cada dimensão de cada peça é um múltiplo inteiro de uma unidade base. Essa unidade é o LDU.

O LDU (abreviação de *LDraw Unit*) nasceu em 1995 quando James Jessiman criou o LDraw, o primeiro programa CAD open-source para modelagem de peças LEGO no computador. Jessiman enfrentou um problema prático: peças LEGO não têm dimensões exatas em milímetros nem em polegadas. Um stud tem 1,7 mm de diâmetro, uma plate tem 3,194 mm de altura — números que, quando usados em cálculos de posicionamento 3D, geram frações de ponto flutuante e erros de arredondamento que se acumulam ao longo de uma montagem. A solução foi definir uma unidade artificial, de tamanho menor que qualquer dimensão real de uma peça, que tornasse todas as dimensões do sistema inteiros perfeitos. Com isso, o software opera inteiramente com aritmética de inteiros, sem nunca precisar de frações.

A definição do LDU é: **1 LDU ≡ 1/8 da altura de uma plate**. A partir daí, toda a geometria do sistema LEGO se expressa como inteiros:

| Dimensão | Valor em LDU |
|---|---|
| Largura/profundidade de 1 stud (módulo horizontal) | 20 LDU |
| Altura de 1 plate | 8 LDU |
| Altura de 1 brick | 24 LDU |
| Diâmetro de 1 stud (o cilindro projetado) | 12 LDU |
| Altura do stud acima da face superior da peça | 4 LDU |
| Espaçamento entre centros de dois studs adjacentes | 20 LDU |

Nenhum desses valores tem vírgula. Isso é a essência do LDU: uma unidade escolhida cirurgicamente para que a geometria toda viva no domínio inteiro.

A correspondência com o mundo físico é aproximada, não exata: **1 LDU ≈ 0,4 mm**, o que equivale a 1/64 de polegada. O "aproximado" é intencional — as peças LEGO têm pequenas tolerâncias de fabricação, e o LDraw não pretende ser uma especificação de engenharia mecânica. É uma ferramenta de modelagem visual. A precisão que importa é a de posicionamento relativo entre peças, e para isso os inteiros são suficientes.

Para entender por que essa escolha de 1/8 de plate funciona tão bem, olhe para o que ela permite expressar. A altura de um plate (8 LDU) dividida por 8 resulta em 1 LDU. A largura de um stud (20 LDU) é divisível por 4, por 5, por 10. A altura de um brick (24 LDU) é divisível por 3, por 4, por 6, por 8. Técnicas avançadas de construção como SNOT (*Studs Not On Top*) — que rotacionam peças 90° ou as encaixam lateralmente — dependem de calcular offsets precisos entre peças em orientações diferentes. Com LDU, esses offsets são somas e subtrações de inteiros. Sem LDU, seriam cálculos em ponto flutuante sujeitos a imprecisão acumulada.

O LDU saiu da comunidade LDraw e se tornou o padrão de facto de toda a camada técnica do ecossistema. O BrickLink Studio — hoje o software de design de peças mais usado, sucessor do LEGO Digital Designer — usa o mesmo sistema de coordenadas em LDU internamente, herdado diretamente do formato de arquivo `.ldr` criado por Jessiman. Ferramentas de geração de listas de peças, scripts de automação de mosaicos e bibliotecas de renderização 3D como POV-Ray todas operam com LDU porque o formato LDraw é o substrato comum.

Para o contexto prático deste livro — compra e especificação de peças para mosaicos — o LDU raramente aparece explicitamente. Fichas de produto em BrickLink e Gobricks listam dimensões em milímetros, e é isso que você vai usar no dia a dia. O valor do LDU aqui é conceitual: ele explica de onde vêm os números de milímetros que você vai ver, por que eles são o que são, e por que as proporções entre plate, brick e tile são exatamente as que são. O próximo conceito vai mostrar como o espaçamento de 8 mm entre studs — que é 20 LDU × 0,4 mm — se torna a régua prática do sistema horizontal.

## Fontes utilizadas

- [LDU and You: The Oldest New LEGO Measurement Unit — BrickNerd](https://bricknerd.com/home/ldu-and-you-the-oldest-new-lego-measurement-unit-2-9-23)
- [LDU Decoded: The Untold Tale of LEGO Dimensions — Hackaday](https://hackaday.com/2024/12/27/ldu-decoded-the-untold-tale-of-lego-dimensions/)
- [LDraw unit — Brickwiki](https://brickwiki.org/wiki/LDraw_unit)
- [LDraw File Format Specification — LDraw.org](https://www.ldraw.org/article/218)
- [What are LDUs and how do they relate to LEGO bricks? — Bricks Stack Exchange](https://bricks.stackexchange.com/questions/691/what-are-ldus-and-how-do-they-relate-to-lego-bricks)
- [The exact length of 1 LDU — Swooshable](https://swooshable.com/other-resources/the-exact-length-of-1-ldu)

---

**Próximo conceito** → [O Stud como Unidade Prática](../02-o-stud-como-unidade-pratica/CONTENT.md)
