# Element ID

![capa](cover.png)

Os dois conceitos anteriores — Design ID e Color ID — operam em dimensões separadas: um identifica o molde, o outro identifica a cor. O Element ID é a combinação dessas duas dimensões num único número atribuído pela LEGO Group. Ele representa não "a forma da peça" nem "a cor", mas sim **"esta peça nesta cor"** — um exemplar concreto e inequívoco dentro do catálogo oficial.

A estrutura é simples: o Element ID tem de 6 a 7 dígitos e é gerado e atribuído internamente pela LEGO para cada combinação válida de Design ID + coloração de ABS. Quando a LEGO fabrica um 1×1 plate preto, esse par (Design ID `3024` + cor preta) recebe um Element ID próprio — por exemplo `302426`. Quando o mesmo molde é injetado em vermelho, o Element ID muda — mesmo que o Design ID `3024` permaneça idêntico. Isso significa que peças visualmente diferentes mas do mesmo molde são distinguidas pelo Element ID, enquanto peças iguais em aparência mas provenientes de lotes históricos com colorações ligeiramente diferentes podem, em teoria, ter Element IDs distintos se a LEGO registrou a mudança de formulação de cor como uma variante.

O lugar natural onde você encontra o Element ID é **no final dos livretos de instruções dos sets oficiais LEGO**. Cada instrução lista o inventário de peças do set com imagem e ao lado a sequência de 6 ou 7 dígitos — esse número é o Element ID. Não é o Design ID (4-5 dígitos sem hífen) nem o código de lote (formato com hífen): é exclusivamente o identificador da combinação forma+cor. O site de atendimento da LEGO (`lego.com/service`) e a ferramenta de reposição de peças perdidas também operam com Element IDs — você informa o número da instrução e o Element ID da peça perdida, e o sistema identifica exatamente o que enviar.

No BrickLink, o Element ID ocupa um papel secundário em relação ao par Design ID + Color ID, mas não é ignorado. A plataforma mantém uma tabela de correspondência entre Element IDs oficiais da LEGO e suas próprias combinações de Part Number + Color ID. Ao digitar um Element ID de 7 dígitos diretamente na caixa de busca do BrickLink, o sistema redireciona para a ficha da peça na cor correta — o que é conveniente quando você está partindo das instruções de um set para completar peças faltantes. Essa funcionalidade é documentada na própria Central de Ajuda do BrickLink e é, na prática, um atalho para quem tem o número em mãos mas não conhece o Design ID ou o Color ID correspondente.

A distinção entre os três identificadores pode ser resumida assim:

| Identificador | Dimensão | Dígitos | Onde aparece |
|---|---|---|---|
| Design ID | Forma (molde) | 4–5 | Gravado fisicamente na peça |
| Color ID | Cor | 1–3 | Tabela do BrickLink / catálogos |
| Element ID | Forma + Cor | 6–7 | Livretos de instrução LEGO, site de peças perdidas |

O ponto de confusão mais frequente — documentado em fóruns e em threads do Eurobricks — é usar o Element ID das instruções como se fosse o Design ID ao pesquisar no BrickLink. Os números têm comprimentos diferentes (6–7 dígitos vs 4–5 dígitos), mas quem não conhece o sistema interpreta qualquer sequência numérica de uma instrução como "o número da peça" e tenta buscá-la nos catálogos de peças avulsas. O resultado é uma busca sem correspondência ou, pior, um falso positivo se por coincidência o número tiver o comprimento certo para ser interpretado como Design ID de outra peça.

Para o fluxo de trabalho deste livro — montar pedidos de mosaico usando peças compatíveis — o Element ID raramente é o ponto de entrada. Você vai trabalhar quase sempre com o par Design ID + Color ID porque é essa a linguagem dos catálogos de fornecedores como Gobricks. No entanto, saber que o Element ID existe e entender de onde ele vem resolve imediatamente a confusão ao abrir um livreto de instruções LEGO para conferir uma peça: os números de 7 dígitos que aparecem ao lado das imagens de peça não são "o número para buscar no BrickLink" — são Element IDs que combinam forma e cor. Para usá-los no BrickLink, basta digitá-los na busca; a plataforma faz a tradução internamente para o par Design ID + Color ID que sua Wanted List precisa.

## Fontes utilizadas

- [Element ID — BrickWiki](http://www.brickwiki.info/wiki/element_id/)
- [Part and Color Combination Code (PCC Code) — BrickLink Help](https://www.bricklink.com/help.asp?helpID=1916)
- [Understanding LEGO part numbers — Brickset](https://brickset.com/article/54327/understanding-lego-part-numbers)
- [Rebrickable Help Guide: Part Numbering](https://rebrickable.com/help/part-numbering/)
- [Identifying LEGO set and piece numbers — LEGO.com](https://www.lego.com/en-mx/service/help-topics/article/identifying-lego-set-and-piece-numbers)
- [Lego Element ID — What's the logic? — Eurobricks Forums](https://www.eurobricks.com/forum/forums/topic/105451-lego-element-id-whats-the-logic/)

---

**Próximo conceito** → [Como Pesquisar no Catálogo BrickLink](../04-como-pesquisar-no-catalogo-bricklink/CONTENT.md)
