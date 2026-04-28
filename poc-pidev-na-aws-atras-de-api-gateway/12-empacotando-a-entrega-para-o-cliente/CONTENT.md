# Empacotando a Entrega Para o Cliente

![capa](cover.png)

## Sobre este capítulo

Uma POC tecnicamente funcional que o cliente não consegue usar sozinho não cumpriu o objetivo. O ponto de chegada deste livro não é "está rodando na AWS" — é "o cliente consegue chamar via HTTP, criar uma sessão, conversar em múltiplos turnos, e dizer 'sim, é isso' ou 'não, falta isso'". Esse passo final — empacotar a entrega de forma que o cliente seja autônomo — é frequentemente subestimado e frequentemente é onde POCs morrem antes de virar produto.

Este capítulo fecha o livro com a entrega concreta: URL pública, credencial de teste, instruções de uso, e um roteiro de validação ponta-a-ponta que o cliente pode executar sozinho sem suporte do desenvolvedor. É também o momento de documentar explicitamente o que fica fora desta POC — para que o cliente não forme expectativas erradas sobre o que está sendo validado.

## Estrutura

O capítulo cobre: (1) **URL pública e stage de invoke** — como exportar a URL do API Gateway, configurar um stage `poc` ou `demo`, e garantir que a URL é estável (custom domain vs URL gerada); (2) **credencial de teste** — criação de usuário no Cognito User Pool (ou token JWT), validade da credencial, como o cliente a usa para autenticar nas chamadas (`Authorization: Bearer <token>`); (3) **instruções de uso** — documento de 1 página cobrindo: pré-requisitos (curl ou Postman ou Bruno), os 3 fluxos básicos (criar sessão, enviar turno, listar sessões) com exemplos de curl prontos para copiar e colar, o que é esperado em cada resposta; (4) **roteiro de validação ponta-a-ponta** — checklist para o cliente: criar sessão, fazer pergunta simples, fazer pergunta de follow-up (validando multi-turn), verificar que a sessão aparece no `GET /sessions`, reiniciar o cliente e retomar a sessão (validando persistência); (5) **escopo explícito da POC** — o que está validado (harness pi.dev rodando na AWS, sessões persistentes, multi-turn, endpoint público autenticado) e o que não está (custo de produção, multi-tenant rigoroso, observabilidade rica, runaway protection) com ponteiros para os livros seguintes do método.

## Objetivo

Ao terminar este capítulo, o leitor terá entregue ao cliente uma POC completa e autônoma — URL, credencial, instruções e roteiro de validação — e terá documentado explicitamente o escopo validado vs o que fica fora. O livro encerra aqui: do zero ao "está demonstrável", com todos os trade-offs entendidos e defendíveis.

## Fontes utilizadas

- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
- [GitHub — serithemage/serverless-openclaw (empacotamento de POC serverless)](https://github.com/serithemage/serverless-openclaw)
- [How to Build a Custom Agent Framework with PI — Nader Dabit](https://gist.github.com/dabit3/e97dbfe71298b1df4d36542aceb5f158)
- [Pi Coding Agent — README oficial](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [AWS re:Invent 2025 — Serverless and Agentic AI Takeaways — Ran the Builder](https://ranthebuilder.cloud/blog/aws-re-invent-2025-my-serverless-agentic-ai-takeaways/)
