# Multiplayer em Godot: Arquitetura Cliente-Servidor, ENet e WebSocket

![capa](cover.png)

## Sobre este capítulo

Neste ponto, o leitor tem um jogo single-player completo. O capítulo pivota para o desafio central da trilha: fazer dois ou mais clientes verem o mesmo mundo. Em vez de saltar direto para código, ele começa onde um engenheiro sênior precisa começar — na **arquitetura**. Quais são os modelos de rede (peer-to-peer, lockstep, cliente-servidor autoritativo)? Por que, para um RPG persistente, o único modelo viável é servidor autoritativo? Qual a diferença entre os *transports* disponíveis no Godot (ENet sobre UDP, WebSocket sobre TCP, WebRTC) e quando cada um é a escolha correta?

A partir dessa análise, o capítulo entra na API de alto nível do Godot para multiplayer — `MultiplayerAPI`, `ENetMultiplayerPeer`, `WebSocketMultiplayerPeer`, `@rpc` — e mostra como subir um servidor dedicado rodando em modo *headless* e um cliente conectando nele. Nada de gameplay ainda: o foco é estabelecer o túnel de dados confiável.

## Estrutura

Os blocos são: (1) **modelos de rede em jogos** — peer-to-peer, lockstep, cliente-servidor autoritativo, por que o último vence para RPG persistente; (2) **transports do Godot 4** — ENet (UDP, padrão), WebSocket (TCP, export web), WebRTC (P2P navegador), critérios de escolha; (3) **o servidor dedicado** — export *headless*, como rodar Godot como um processo servidor sem render; (4) **a API de alto nível** — `MultiplayerAPI`, `MultiplayerPeer`, `@rpc`, `multiplayer_authority`; (5) **hello world em rede** — servidor aceita conexão, cliente conecta, troca de ping/pong via RPC; (6) **hands-on** — rodar servidor local + dois clientes, ver logs dos três processos sincronizados.

## Objetivo

Ao fim, o leitor terá um entendimento sólido dos modelos de rede em jogos e da API de multiplayer do Godot, e terá subido um servidor autoritativo rodando em modo headless com dois clientes conectados. A conexão está de pé; o próximo capítulo é o que vai sincronizar mundo e jogadores sobre ela.

## Fontes utilizadas

- [Godot Engine — High-level multiplayer (docs)](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html)
- [Godot Engine — ENetMultiplayerPeer (class reference)](https://docs.godotengine.org/en/stable/classes/class_enetmultiplayerpeer.html)
- [Multiplayer in Godot 4.0: ENet wrappers, WebRTC (Godot blog)](https://godotengine.org/article/multiplayer-changes-godot-4-0-report-3/)
- [Godot Multiplayer in 2026: What Actually Works (Ziva)](https://ziva.sh/blogs/godot-multiplayer)
- [Godot multiplayer networking workbench (GitHub)](https://github.com/goatchurchprime/godot_multiplayer_networking_workbench)
- [Simple Online Multiplayer Networking Authoritative Dedicated Server (Godot Asset Library)](https://godotengine.org/asset-library/asset/755)
