# O Stud como Unidade Prática

![capa](cover.png)

O LDU nasceu para resolver um problema de software — eliminar frações em cálculos de posicionamento 3D — e, nesse papel, faz sentido perfeito. Mas quando você abre uma ficha de produto no BrickLink, no Gobricks ou em qualquer loja de peças avulsas, o LDU não aparece. O que aparece é milímetros, e a unidade que organiza esses milímetros é o stud.

O stud é o cilindro que projeta do topo de quase toda peça LEGO. Ele é o pino macho do sistema de encaixe: encaixa no anti-stud (buraco) da face inferior da peça de cima, ou no tubo interno de peças com paredes laterais. Funcionalmente, um stud é um ponto de ancoragem. Geometricamente, é a unidade que define a grade horizontal de qualquer construção LEGO.

A medida central do stud como unidade prática é o **espaçamento de 8 mm entre centros de studs adjacentes**. Esse valor — chamado de stud pitch ou simplesmente de "1 stud" — é a régua que governa toda a dimensão horizontal do sistema. Uma peça 1×1 ocupa exatamente 1 stud de largura por 1 stud de profundidade. Uma peça 2×4 ocupa 2 studs por 4 studs. A relação entre essas medidas e o mundo físico é direta e sem fração: 1 stud = 8 mm.

Traduzindo isso em LDU — o que o conceito anterior estabeleceu como linguagem interna do sistema — 1 stud horizontal equivale a 20 LDU. Com 1 LDU ≈ 0,4 mm, temos: 20 × 0,4 = 8 mm. A matemática fecha perfeitamente porque o LDU foi escolhido exatamente para isso: tornar todos os valores inteiros, incluindo esse espaçamento de 8 mm que já existia antes do LDU ser formalizado.

Vale entender a origem desse 8 mm. Uma peça 1×1 não mede exatamente 8 mm de lado — ela mede 7,8 mm. A diferença de 0,2 mm é a folga de tolerância entre peças adjacentes. Quando dois blocos 1×1 são posicionados lado a lado, cada um contribui com 7,8 mm de material mais 0,1 mm de folga de cada lado, somando 8 mm de módulo repetível. O stud em si tem 4,8 mm de diâmetro (3 LDU × 0,4 mm ÷ LDU = 1,2 mm... não; 3 unidades de 1,6 mm = 4,8 mm, onde 1,6 mm = 2 LDU × 0,8 mm — a base dimensional é 1,6 mm, com 5 dessas unidades compondo os 8 mm do módulo). A relação exata:

| Elemento | Dimensão real |
|---|---|
| Lado de uma peça 1×1 (sem folga) | 7,8 mm |
| Folga entre peças adjacentes | 0,2 mm |
| Espaçamento de centro a centro (stud pitch) | 8,0 mm |
| Diâmetro do stud (cilindro) | 4,8 mm |
| Altura do stud acima da face superior da peça | 1,6 mm |

O stud pitch de 8 mm nunca é exposto como tal nas fichas de produto — a ficha de um 1×1 plate no BrickLink mostra "1 × 1" em studs, e qualquer pessoa que saiba que 1 stud = 8 mm converte na hora. Uma baseplate 32×32 tem 32 × 8 mm = 256 mm = 25,6 cm de largura. Um painel de mosaico com 4 baseplates 32×32 montadas em grade 2×2 ocupa 51,2 cm × 51,2 cm. A conversão é direta e repetível porque o módulo de 8 mm é rígido.

Há uma consequência estrutural importante desse módulo que aparece quando você começa a trabalhar com peças de marcas compatíveis. O stud pitch de 8 mm (ou mais precisamente 7,985 mm, medido em detalhes por comunidades como a Lugnet) define o critério mais imediato de qualidade de uma peça compatível: ela precisa manter esse espaçamento dentro de uma tolerância mínima para encaixar com peças originais e para não criar desvio acumulado ao longo de uma baseplate inteira. Uma peça com stud pitch ligeiramente desviante parece encaixar na primeira ou segunda coluna, mas ao longo de 32 studs de comprimento, o desvio acumulado pode tornar o encaixe frouxo ou impossível. Esse é um dos critérios técnicos de avaliação de fornecedores que o capítulo de qualidade técnica vai detalhar — mas ele começa aqui, no stud como unidade de medida.

Para o trabalho prático de especificação e compra de peças para mosaico, o stud funciona como ponto de entrada em qualquer conversa de medida:

```
1 stud  → 8 mm (dimensão horizontal)
1 plate → 3,2 mm (dimensão vertical)
1 brick → 9,6 mm (dimensão vertical)
```

Esses três valores — memorizados uma vez — são suficientes para interpretar qualquer dimensão de produto em qualquer loja de peças. A proporção vertical brick/plate/tile em altura, que o próximo conceito desenvolve, parte exatamente desses números.

## Fontes utilizadas

- [Stud Dimensions and Other Standards — BrickLink Help](https://www.bricklink.com/help.asp?helpID=261)
- [Lego Geometry 101: Studs, Bricks, and Plates — Bricking Ohio](https://www.brickingohio.com/blog/lego-geometry-101)
- [Lego Specifications — Orion Robots](https://orionrobots.co.uk/Lego+Specifications)
- [Stud Dimensions Guide — Brick Owl](https://www.brickowl.com/help/stud-dimensions)
- [LEGO - 01 Basic Dimensions & Bricks Explained — GrabCAD](https://grabcad.com/tutorials/lego-01-basic-dimensions-bricks-explained)
- [LEGO Brick Dimensions and Measurements — Christoph Bartneck](https://www.bartneck.de/2019/04/21/lego-brick-dimensions-and-measurements/)

---

**Próximo conceito** → [A Proporção Brick/Plate/Tile em Altura](../03-a-proporcao-brick-plate-tile-em-altura/CONTENT.md)
