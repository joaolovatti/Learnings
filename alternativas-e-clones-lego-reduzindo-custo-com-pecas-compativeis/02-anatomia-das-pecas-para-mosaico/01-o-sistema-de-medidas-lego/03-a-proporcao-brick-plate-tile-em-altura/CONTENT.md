# A Proporção Brick/Plate/Tile em Altura

![capa](cover.png)

O conceito anterior introduziu o stud pitch de 8 mm como a régua do eixo horizontal e deixou três valores como ponto de partida para o eixo vertical: 1 brick = 9,6 mm, 1 plate = 3,2 mm, 1 tile = 3,2 mm. A proporção entre essas três alturas não é arbitrária — ela nasce da mesma lógica interna do LDU que o primeiro conceito estabeleceu, e tem consequências diretas para qualquer decisão de compra de peça para mosaico.

A relação central é esta: **um brick padrão mede exatamente 3 plates de altura**. Em LDU, já estabelecidos como 1/8 de plate: 1 plate = 8 LDU, 1 brick = 24 LDU. A matemática fecha sem frações. Em milímetros: 3 × 3,2 mm = 9,6 mm, que é exatamente a altura de um brick medido fisicamente. Esse 3:1 entre brick e plate é o que a comunidade chama de a proporção mais fundamental do sistema LEGO — ela é tão utilizada que um punhado de referências a chama informalmente de "FLU" (Fundamental LEGO Unit), embora esse termo não seja oficial.

Mas há um detalhe que vai contra a intuição de quem vê as peças pela primeira vez. Quando você mede um brick padrão com paquímetro, o número que aparece é **9,6 mm** — e não 12 mm, que seria o total se somasse também a altura do stud no topo (1,6 mm) ao corpo do brick. Isso porque a convenção de altura no sistema LEGO mede a **altura do corpo** da peça, excluindo o stud projetado. O motivo é estrutural: quando uma segunda peça se encaixa sobre a primeira, o stud da peça de baixo se encaixa dentro da câmara da peça de cima, e a face inferior da peça de cima pousa sobre a face superior do corpo da peça de baixo. O stud desaparece dentro do encaixe — ele não soma à altura empilhada. A altura empilhada de dois bricks é 9,6 + 9,6 = 19,2 mm, não 12 + 12 mm.

```
Brick padrão (1×1):
  ┌─────┐  ← stud: 1,6 mm (4 LDU) — encaixa DENTRO da peça de cima
  │     │
  │     │  ← corpo: 9,6 mm (24 LDU)
  │     │
  └─────┘
  ↑ anti-stud (fundo aberto ou tubo)

Plate (1×1):
  ┌─────┐  ← stud: 1,6 mm (4 LDU)
  └─────┘  ← corpo: 3,2 mm (8 LDU)

Tile (1×1):
  ═════════  ← sem stud; superfície plana
  └─────┘  ← corpo: 3,2 mm (8 LDU) — mesma espessura da plate
```

O tile entra aqui como o terceiro elemento da proporção. Ele tem **exatamente a mesma altura de uma plate** — 3,2 mm, 8 LDU. A diferença não está na espessura, mas na superfície: o tile não tem stud. Isso significa que um tile e uma plate são intercambiáveis em altura ao empilhar peças — uma coluna de 3 tiles tem a mesma altura de uma coluna de 3 plates — mas o tile entrega superfície completamente plana, sem o cilindro projetado de 1,6 mm.

| Peça | Altura do corpo (mm) | Altura do corpo (LDU) | Tem stud? |
|---|---|---|---|
| Brick padrão | 9,6 mm | 24 LDU | Sim |
| Plate | 3,2 mm | 8 LDU | Sim |
| Tile | 3,2 mm | 8 LDU | Não |
| Stud (projetado) | 1,6 mm | 4 LDU | — |

A proporção 3:1 entre brick e plate não é apenas uma curiosidade geométrica — ela tem uma consequência construtiva que importa diretamente para mosaicos. Quando uma construção é montada com plates em vez de bricks, ela é **três vezes mais fina** para a mesma quantidade de pixels. Um mosaico de retrato de 48 × 48 studs montado com 1×1 plates tem espessura de uma única plate: 3,2 mm mais a baseplate embaixo. O mesmo mosaico montado com 1×1 bricks teria 9,6 mm de profundidade de pixels. Para um produto de parede — que o cliente vai pendurar num quadro — a diferença de espessura muda o acabamento visual e o peso total.

Existe ainda uma relação entre a dimensão horizontal (stud pitch) e a vertical (plate height) que revela a coerência interna do sistema: **2 studs horizontais = 5 plates de altura**. Em LDU: 2 studs = 2 × 20 = 40 LDU; 5 plates = 5 × 8 = 40 LDU. Essa equivalência é o que permite a técnica SNOT (*Studs Not On Top*) — rotacionar peças 90° e encaixar lateralmente, porque o sistema sabe que há posições onde as distâncias coincidem perfeitamente. Para mosaicos planares (pixels em cima de uma baseplate), o SNOT não é relevante; mas essa proporção 5:2 aparece quando você calcula dimensões físicas de painéis maiores e serve como verificação da consistência do sistema.

Para quem está comprando peças para mosaico, a conclusão operacional é direta: plate e tile têm a mesma espessura (3,2 mm), o que significa que a escolha entre os dois não afeta a espessura do mosaico acabado — afeta apenas a superfície (com ou sem stud). A escolha entre plate e brick sim afeta a espessura, numa razão de 1:3. O próximo conceito vai traduzir essa proporção em cálculo concreto: dado o tipo de peça e a quantidade de camadas, qual é a espessura real do mosaico pronto.

## Fontes utilizadas

- [LDU and You: The Oldest New LEGO Measurement Unit — BrickNerd](https://bricknerd.com/home/ldu-and-you-the-oldest-new-lego-measurement-unit-2-9-23)
- [LEGO Brick Dimensions and Measurements — Christoph Bartneck](https://www.bartneck.de/2019/04/21/lego-brick-dimensions-and-measurements/)
- [Lego Geometry 101: Studs, Bricks, and Plates — Bricking Ohio](https://www.brickingohio.com/blog/lego-geometry-101)
- [LEGO SNOT Basics: Geometry, Techniques and Pitfalls — BrickNerd](https://bricknerd.com/home/snot-basics-geometry-techniques-and-pitfalls-3-18-2021)
- [Brick Geometry — Bricks by the Bay 2018 (Bill Ward)](https://www.brickpile.com/wp-content/uploads/2018/07/brick-geometry-bbtb2018.pdf)
- [Basic LEGO Parts Guide — Brick Architect](https://brickarchitect.com/parts/category-1)
- [Stud Dimensions Guide — Brick Owl](https://www.brickowl.com/help/stud-dimensions)
- [LEGOmetry — Holger Matthes](https://www.holgermatthes.de/bricks/en/geometry.php)

---

**Próximo conceito** → [Calculando a Espessura Real de um Mosaico](../04-calculando-a-espessura-real-de-um-mosaico/CONTENT.md)
