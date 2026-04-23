# O Efeito do Stud na Luz e na Textura

![capa](cover.png)

A diferença entre um mosaico montado com 1×1 plates e um montado com 1×1 tiles não é só uma questão de "ter ou não ter stud". É uma questão de como a geometria de cada peça interage com a luz ambiente — e como essa interação altera a percepção de cor e contraste na peça acabada pendurada na parede. Antes de comparar plate contra tile (o que o próximo conceito faz), é necessário entender o mecanismo em si: o que o stud faz, fisicamente, quando a luz o atinge.

O stud de um 1×1 plate é um cilindro com aproximadamente 4,8 mm de diâmetro e 1,7 mm de altura, posicionado no centro superior da peça. Esses 1,7 mm são discretos quando vistos de perto, mas suficientes para transformar a superfície do plate de uma face plana em uma superfície com relevo tridimensional. Quando luz difusa de ambiente — a iluminação típica de uma sala ou escritório — incide sobre um mosaico, ela raramente é perfeitamente ortogonal ao plano do painel. Há sempre um componente angular, por menor que seja: luz de janela, luminárias de teto deslocadas do eixo ou simplesmente o observador se movendo. É aí que o stud começa a trabalhar.

Um cilindro iluminado por luz não perfeitamente frontal acumula dois efeitos simultâneos. No lado voltado para a fonte de luz, a superfície curva do stud captura um highlight especular — uma faixa brilhante que pode ter tom levemente mais claro ou mais saturado do que a cor base da peça. No lado oposto, o cilindro projeta uma micro-sombra sobre a superfície plana da peça imediatamente abaixo e ao redor de sua base. Essa sombra não é um ponto negro forte; é uma penumbra discreta, com gradação de intensidade que começa mais escura logo ao pé do stud e se dissolve conforme se afasta. Para uma única peça, esses efeitos são minúsculos. Para um mosaico de 1.024 peças (um painel 32×32), eles se repetem em cada pixel e criam um campo visual de micro-texturas que não existe nos dados de cor originais.

```
Perfil lateral de um plate com stud:

        ┌──┐           ← stud (cilindro Ø4.8mm × 1.7mm alt.)
  ──────┘  └──────     ← superfície superior do plate

Iluminação com ângulo leve vindo da esquerda:

    ☀→        ✦ highlight no lado esquerdo do cilindro
        ┌──┐  
        │  │░           ← micro-sombra projetada à direita da base
  ──────┘  └░░────  
```

O efeito óptico resultante depende da direção e qualidade da iluminação ambiente. Com luz lateral — o caso mais comum quando o painel está em parede e a janela está à esquerda ou à direita — os highlights e sombras ficam alinhados horizontalmente e criam uma textura direcional perceptível mesmo a distâncias médias (1,5 m a 2 m). Com luz difusa centralizada, os highlights aparecem no topo do cilindro e as sombras se acumulam ao redor da base, criando uma textura que parece granulada ou pontilhada quando o painel é observado a ângulo levemente rasante.

O impacto mais relevante para um mosaico de retrato não é o highlight em si, mas a micro-sombra. Ela modifica localmente a luminosidade percebida de cada peça. Uma peça de cor `Medium Blue` (BrickLink Color ID 102) montada com plate terá, em certas condições de iluminação, a região ao redor do stud sutilmente mais escura do que a mesma peça renderia se fosse tile liso. Isso não é defeito na cor do ABS — é geometria. A cor do plástico não mudou; o que mudou foi a quantidade de luz que alcança cada ponto da superfície.

Para um mosaico de retrato, isso tem duas consequências práticas. Primeiro, a paleta de cores percebida pelo observador não é idêntica à paleta dos color IDs especificados no algoritmo — ela sofre uma variação local dependente da geometria do stud e do ângulo de luz. Algoritmos de mosaico que calculam a correspondência de cores baseando-se em valores RGB absolutos não levam esse efeito em conta; o ajuste é um fator humano, incorporado à experiência de quem produz e aprecia esses painéis regularmente. Segundo, essa textura de micro-sombras cria uma sensação de profundidade na superfície que pode ser percebida como "mais LEGO" — reconhecível como produto brick — mesmo a distâncias onde os studs individuais não são distinguíveis.

| Característica | Superfície com stud (plate) | Superfície sem stud (tile) |
|---|---|---|
| Relevo por peça | +1,7 mm (cilindro) | Zero |
| Highlight especular | Presente, posição varia com a luz | Ausente (superfície plana uniforme) |
| Micro-sombra na base | Presente, cresce com ângulo de luz | Ausente |
| Percepção de cor | Ligeiramente modulada pela geometria | Fiel ao color ID base |
| Textura visual | Pontilhada ou direcional | Lisa, quase especular ao toque |
| Profundidade percebida | Maior (sensação 3D) | Menor (mais próximo de uma impressão gráfica) |

Uma armadilha real que aparece em fóruns de MOCs e discussões sobre LEGO Art é confundir o efeito do stud com "cores erradas". Quem monta seu primeiro mosaico com plates e compara ao render digital gerado pelo software fica surpreso porque as áreas escuras do retrato parecem ainda mais escuras no físico do que no digital — especialmente com iluminação lateral. Isso não é erro de calibração de cor das peças; é o stud fazendo o que faz. A correção, quando desejada, não está em trocar fornecedor ou lote de cor: está em escolher tile (assunto do próximo conceito) ou em ajustar o algoritmo de mosaico para prever esse efeito durante a etapa de design.

O ponto de partida para qualquer decisão informada sobre tipo de peça — para um pedido específico de retrato, com um cliente específico — é compreender que o stud não é apenas um mecanismo de encaixe. Ele é geometria que participa ativamente da aparência do produto acabado. Nos conceitos seguintes deste subcapítulo, cada decisão de peça (plate vs tile, round vs square) vai se apoiar nessa compreensão de base.

## Fontes utilizadas

- [Everything You Want to Know About LEGO Mosaics — BrickNerd](https://bricknerd.com/home/everything-you-want-to-know-about-lego-mosaics-11-12-24)
- [LEGO® Art: the new mosaic theme — New Elementary](https://www.newelementary.com/2020/07/lego-art-new-mosaic-theme.html)
- [Stud Dimensions and Other Standards — BrickLink Help](https://www.bricklink.com/help.asp?helpID=261)
- [LEGO Brick Dimensions and Measurements — Christoph Bartneck, Ph.D.](https://www.bartneck.de/2019/04/21/lego-brick-dimensions-and-measurements/)
- [Brick Geometry — Bricks by the Bay 2018 (Bill Ward)](https://www.brickpile.com/wp-content/uploads/2018/07/brick-geometry-bbtb2018.pdf)
- [Lego – Studs — Simon Schreibt](https://simonschreibt.de/gat/lego-studs/)

---

**Próximo conceito** → [Plate vs Tile no Mosaico Acabado](../02-plate-vs-tile-no-mosaico-acabado/CONTENT.md)
