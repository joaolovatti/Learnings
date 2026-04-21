# Setup Mínimo — Instalando o Godot 4 e Abrindo o Primeiro Projeto

![capa](cover.png)

## Sobre este subcapítulo

Este subcapítulo é o aterrissar do capítulo: depois de toda a fundamentação estratégica, é o momento em que o leitor sai do plano conceitual e abre, fisicamente, a engine. O recorte é deliberadamente mínimo — instalar, criar projeto vazio, identificar as quatro regiões principais do editor, salvar — sem entrar em nodes, scenes ou scripts (esses são o capítulo 2). A motivação é eliminar a fricção de "primeira execução" antes que o leitor encare o primeiro conceito teórico real, garantindo que o capítulo 2 comece com o editor já familiar e funcional.

Ele aparece como último subcapítulo porque, em ordem pedagógica, faz mais sentido instalar a ferramenta sabendo o que se vai fazer com ela. Também é o subcapítulo onde o leitor cruza pela primeira vez do papel para a prática — o ritual de "abri o editor pela primeira vez", que muitos projetos pessoais nunca executam, é tratado aqui como rito explícito e celebrado.

## Estrutura

Os blocos deste subcapítulo são: (1) **download e instalação** — como pegar a versão estável do Godot 4 no site oficial, por que o binário é portátil (~120MB, sem instalador necessário), onde colocá-lo no sistema, e como confirmar que ele abre; (2) **Project Manager e criação do projeto** — abrir o Project Manager, criar um novo projeto chamado por exemplo `pokemon-clone-godot`, escolher o renderer correto (Forward+ ou Mobile, com a recomendação justificada para 2D), entender a estrutura de diretórios criada; (3) **anatomia do editor** — as quatro regiões principais (Scene/FileSystem dock à esquerda, viewport central, Inspector à direita, output/debugger na base), com o que cada uma faz e quando se usa; (4) **o primeiro save** — adicionar um Node2D vazio só para experimentar o gesto, salvar a cena como `main.tscn`, fechar e reabrir o projeto para validar o ciclo; (5) **rituais e atalhos úteis** — `F5` para rodar o projeto, `F6` para rodar a cena atual, e o que esperar quando o jogo "vazio" abre pela primeira vez (uma janela preta — e por que isso é uma vitória).

## Objetivo

Ao terminar, o leitor terá o Godot 4 instalado e funcional, um projeto vazio criado no disco, terá experimentado o ciclo abrir-editar-salvar-rodar pelo menos uma vez, e estará familiarizado com a anatomia básica do editor. A barreira de entrada para os capítulos seguintes — onde o livro entra de fato em nodes, scenes e scripts — fica reduzida a zero: o capítulo 2 começa com o editor já aberto.

## Fontes utilizadas

- [Godot Engine — site oficial (download)](https://godotengine.org/download/)
- [Godot Engine — Introduction to the editor (documentação oficial)](https://docs.godotengine.org/en/stable/getting_started/introduction/first_look_at_the_editor.html)
- [Godot 4: Getting Started (Kodeco)](https://www.kodeco.com/37604834-godot-4-getting-started)
- [Learn GODOT 4 In 90 Minutes (GameDev Academy)](https://gamedevacademy.org/godot-beginner-tutorial/)
- [How to Start Learning Godot in 2026: A Beginner's Guide](https://eathealthy365.com/a-step-by-step-guide-to-learning-the-godot-engine/)
- [Godot Beginner Guide 2026: What I Wish I Knew Before Starting (YouTube)](https://www.youtube.com/watch?v=VwbD5_c7Bq0)
