# Atalhos e Rituais de Produtividade do Editor

![capa](cover.png)

O ciclo cena → save → run que o conceito anterior colocou em prática é o esqueleto do trabalho no Godot. Mas na velocidade com que vai se repetir ao longo do RPG — centenas de vezes por sessão — cada segundo de atrito se acumula. Atalhos de teclado não são detalhes de conforto: são o mecanismo pelo qual o editor desaparece cognitivamente e você passa a pensar em nodes, cenas e lógica de jogo, não em onde está o botão de duplicar. Para um engenheiro que já tem a musculatura de atalhos de IDEs como IntelliJ, VS Code ou PyCharm, esse aprendizado é rápido — o que muda é o vocabulário específico do Godot, não o hábito mental.

O Godot organiza seus atalhos em domínios: o editor geral (que opera independente do workspace ativo), o viewport 2D, o editor de scripts, e o ciclo de execução. Cada domínio tem um conjunto de teclas que não conflita com os demais porque o editor sabe o contexto ativo. A armadilha mais comum para iniciantes é tentar um atalho do viewport enquanto o foco do teclado está no editor de scripts — os atalhos são consumidos pelo painel focado, e a ação aparentemente "não funciona". Se `F5` não responde, clique uma vez no viewport ou no Scene dock para transferir o foco.

**Execução e depuração** são o domínio mais imediato, e já introduzido no conceito anterior com mais detalhe. Para consolidar em formato referenciável:

| Atalho | Ação | Quando usar |
|---|---|---|
| `F5` | Rodar o projeto completo (main scene) | Teste do fluxo real do jogador |
| `F6` | Rodar apenas a cena atual no editor | Teste isolado da cena sendo editada |
| `F8` | Parar a execução | Encerrar o jogo e retornar ao editor |
| `F9` | Alternar breakpoint na linha atual | Pausar execução para inspecionar estado |
| `F10` | Step over (avançar uma linha no debugger) | Rastrear execução linha a linha |
| `F11` | Step into (entrar em funções chamadas) | Depurar dentro de funções próprias |

A distinção entre `F5` e `F6` vale ser reforçada pelo seu impacto concreto no fluxo de desenvolvimento do RPG. Quando você estiver no capítulo de combate por turnos — por exemplo, iterando sobre o cálculo de dano e a UI de batalha — rodar o projeto com `F5` significaria percorrer a tela inicial, o mapa, chegar a uma área de batalha e triggar o encontro para testar uma mudança pontual. Com `F6`, você abre diretamente a cena `battle_scene.tscn` no editor e a roda em isolamento, chegando ao que importa em segundos. O custo de não conhecer `F6` no começo vai aparecer quando as cenas ficarem mais complexas e interconectadas.

**Gestão de cenas e nodes** é o segundo domínio crítico. O vocabulário muda levemente aqui porque o Godot trata "cena" e "node" como entidades distintas — você cria nodes dentro de uma cena aberta, e gerencia cenas no FileSystem.

| Atalho | Ação |
|---|---|
| `Ctrl+N` | Nova cena vazia |
| `Ctrl+O` | Abrir cena existente pelo seletor de arquivo |
| `Ctrl+S` | Salvar a cena atual |
| `Ctrl+Shift+S` | Salvar a cena atual com outro nome (Save As) |
| `Ctrl+A` | Adicionar node filho ao node selecionado |
| `Ctrl+D` | Duplicar node(s) selecionado(s) |
| `Delete` | Remover node(s) selecionado(s) |
| `F2` | Renomear o node selecionado in-place |
| `Ctrl+Z` / `Ctrl+Y` | Desfazer / Refazer |

O `Ctrl+A` é provavelmente o atalho de edição que você mais vai usar nos primeiros capítulos — ele abre o diálogo "Add Child Node" onde você busca qualquer tipo de node pelo nome, com filtro por substrings. Digitar `spr` já filtra para `Sprite2D`; digitar `char` já filtra para `CharacterBody2D`. Esse diálogo também respeita `class_name` — qualquer script que você criar com `class_name MeuScript` vai aparecer como tipo disponível para adição direta, o que é uma aceleração importante ao construir sistemas custom.

**No viewport 2D**, o conjunto `Q`, `W`, `E`, `R` mapeia para os modos de transformação — e é idêntico ao padrão de softwares de composição como Blender, After Effects e Unity:

| Tecla | Modo | O que faz |
|---|---|---|
| `Q` | Select | Selecionar nodes clicando no canvas |
| `W` | Move | Arrastar para reposicionar |
| `E` | Rotate | Rotacionar em torno do ponto de âncora |
| `S` | Scale | Escalar proporcionalmente ou eixo a eixo |
| `F` | Frame selected | Enquadra o(s) node(s) selecionado(s) no viewport |
| `Scroll` | Zoom | Aproximar/afastar o viewport |
| `Meio do mouse drag` | Pan | Mover a câmera do editor sem selecionar |

Uma nota prática: `F` no viewport 2D é o atalho que você vai usar toda vez que "perder" um node no canvas — quando a posição do node está em algum lugar fora da câmera atual do editor. Selecione o node no Scene dock e pressione `F`: o viewport pula para enquadrar o node selecionado. Para o RPG com tilemaps potencialmente grandes, esse atalho economiza tempo significativo de scroll manual.

**No editor de scripts**, os atalhos refletem os padrões de editores de código convencionais:

| Atalho | Ação |
|---|---|
| `Ctrl+Space` | Autocompletar código (contextual ao nó e tipo) |
| `Ctrl+F` | Buscar no script atual |
| `Ctrl+H` | Buscar e substituir no script atual |
| `Ctrl+Shift+F` | Buscar em todos os scripts do projeto |
| `Ctrl+/` | Comentar/descomentar linha(s) selecionada(s) |
| `Ctrl+D` | Duplicar linha atual |
| `Alt+Up/Down` | Mover linha(s) selecionada(s) para cima/baixo |
| `Ctrl+G` | Ir para linha específica por número |
| `Ctrl+1` a `Ctrl+4` | Trocar para workspace 2D / 3D / Script / AssetLib |

O `Ctrl+Space` no GDScript é particularmente rico: ele oferece completion contextual que conhece os tipos de nodes. Se você está escrevendo dentro de um script anexado a um `CharacterBody2D`, o completion sugere os métodos e propriedades específicos da classe, incluindo métodos herdados. Quando você acessa um node via `$NomeDoNode`, o Godot 4 com tipagem estática (`@onready var player: CharacterBody2D = $Player`) expande o completion para os membros do tipo anotado — uma aceleração expressiva em relação ao completion genérico.

**Customizando atalhos** é uma funcionalidade que costuma ser ignorada nas primeiras semanas e que se torna valiosa quando você tem um conjunto de ações muito repetidas com binding inconveniente. O caminho é `Editor → Editor Settings → Shortcuts` — uma lista completa de todas as ações do editor, cada uma com seu binding atual (ou "None" se sem atalho), editável com double-click. Ações sem atalho padrão que valem considerar vincular: "Move Up in Parent" e "Move Down in Parent" para reorganizar nodes na árvore; "Select All Children" para selecionar a sub-árvore; "Toggle Scene Tree Dock" para liberar espaço horizontal quando você precisa de viewport mais ampla.

Há três **confusões comuns** com atalhos que aparecem cedo no aprendizado. A primeira é a questão de foco já mencionada: o painel que tem foco de teclado consome o atalho, então `Ctrl+A` no Output panel não adiciona um node. Clique no viewport ou no Scene dock antes de usar atalhos de edição de cena. A segunda confusão é `Ctrl+D` ter dois significados dependendo do contexto — no Scene dock duplica nodes; no Script editor duplica a linha atual. O editor resolve a ambiguidade pelo contexto de foco, mas pode surpreender se você pensava estar em um contexto e estava no outro. A terceira é que as alterações feitas **durante a execução** (`F5`/`F6`) — posição de sprites, valores de propriedades no Inspector ao vivo — não são persistidas de volta ao `.tscn` quando você para com `F8`. Essa é uma fonte real de frustração: "juro que ajustei a posição do sprite e salvei", mas o save durante execução apenas registra o estado temporário, que descarta ao parar. A regra é simples: para manter um ajuste, pare, edite no estado não-executando, salve com `Ctrl+S`.

O **ritual de abertura de sessão** que vale construir desde agora é pequeno mas consistente: abrir o Godot, verificar no Project Manager que você vai abrir o projeto correto (o nome e o diretório aparecem listados), clicar em Edit, aguardar o editor carregar a última cena aberta (o Godot lembra a última cena ativa da sessão anterior), e pressionar `F6` uma vez antes de fazer qualquer mudança — para confirmar que o estado atual do projeto está funcional. Esse `F6` inicial é o equivalente de um `git pull` antes de começar a editar: elimina a categoria de erros onde você passa 30 minutos editando e descobre que havia um bug pré-existente no arquivo que nada tinha a ver com sua mudança. Para o RPG, à medida que o projeto cresce em cenas interconectadas, esse hábito vai poupar sessões inteiras de debugging regressivo.

O **ritual de encerramento** é igualmente simples: `Ctrl+S` antes de fechar o editor. O Godot não pergunta se você quer salvar ao fechar — ele fecha e ponto. Se houver mudanças não salvas (asterisco no título da aba), elas desaparecem. Esse comportamento difere de IDEs como VS Code que têm autosave e prompts de confirmação. Até que o autosave se torne hábito mental, `Ctrl+S` como ação reflexiva antes de qualquer pausa é a defesa mais simples.

O subcapítulo de setup mínimo cobre, então, uma trilha completa: de um binário autocontido sem instalador, passando pelo Project Manager e pela escolha de renderer, até a anatomia do editor e o primeiro ciclo funcional de cena → save → run, e agora os atalhos que tornam esse ciclo fluído. O que vem a seguir — nodes, cenas reais, GDScript, signals — pressupõe que o ambiente não é mais um obstáculo. A partir do capítulo 2, cada conceito novo entra sem custo de setup, direto no conteúdo.

## Fontes utilizadas

- [Default editor shortcuts — Godot Engine (stable) documentation](https://docs.godotengine.org/en/stable/tutorials/editor/default_key_mapping.html)
- [Default editor shortcuts — Godot Engine (4.6) documentation](https://docs.godotengine.org/en/4.6/tutorials/editor/default_key_mapping.html)
- [Godot Engine Shortcuts Cheat Sheet — Generalist Programmer](https://generalistprogrammer.com/cheatsheets/godot-shortcuts)
- [Essential Godot Editor Shortcuts to Boost Your Workflow — SightlessDev](https://www.sightlessdev.com/blog/godot/single-posts/editor-shortcuts/)
- [Godot Editor useful shortcuts: General, 2D and Script editor combinations — Game Dev FCups](https://gamedevfcups.com/godot-editor-useful-shortcuts-general-2d-and-script-editor-combinations/)
- [Best practices — Godot Engine (stable) documentation](https://docs.godotengine.org/en/stable/tutorials/best_practices/index.html)

---

**Próximo capítulo** → [Nodes, Scenes e a Árvore de Cena](../../../02-nodes-scenes-e-a-arvore-de-cena/CONTENT.md)
