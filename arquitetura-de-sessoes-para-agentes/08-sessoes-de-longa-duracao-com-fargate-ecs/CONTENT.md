# Sessões de Longa Duração com Fargate/ECS

![capa](cover.png)

## Sobre este capítulo

Quando Lambda Durable Functions e Step Functions ainda não são suficientes — seja pela latência de cold start na retomada, pela complexidade do estado em memória, ou pela necessidade de manter uma conexão WebSocket ativa pelo tempo de vida da sessão — a solução é hospedar o loop agêntico num container de longa duração. AWS Fargate/ECS oferece exatamente isso: um processo Python que vive enquanto a sessão vive, com acesso direto a estado em memória, sem a penalidade de reconstruir o contexto a cada invocação. Este capítulo cobre a containerização do agente, a comunicação entre API Gateway e o container, e os trade-offs operacionais que vêm com essa escolha.

Este capítulo fecha o bloco de infraestrutura (caps. 6, 7 e 8) e representa o extremo mais stateful do espectro. O leitor chegará aqui com o diagnóstico dos caps. 6 e 7 e usará este capítulo para entender o que ganha e o que paga ao dar esse passo.

## Estrutura

Os grandes blocos são: (1) o agente como processo contínuo — o contraste entre o modelo de invocação do Lambda e o modelo de processo permanente do Fargate; o que muda quando o loop agêntico vive em memória entre turnos do usuário; (2) containerizando o agente existente — adaptação do `executor.py` e `chain_of_thoughts.py` para rodar num servidor HTTP leve (FastAPI ou Flask) dentro do container; gestão do ciclo de vida da sessão em memória com persistência assíncrona no MongoDB; (3) roteamento de requisições — como a API Gateway direciona requisições de um usuário específico sempre para o container da sua sessão (sticky routing com Application Load Balancer); alternativas quando sticky routing não é viável; (4) escalabilidade e isolamento — um container por sessão (máximo isolamento, custo alto) vs. múltiplas sessões por container (mais eficiente, requer gestão interna de concorrência); auto-scaling baseado em número de sessões ativas; (5) operação e custo — comparativo de custo Fargate vs Lambda para diferentes padrões de uso de sessão, monitoramento de containers de agente e estratégias de shutdown gracioso.

## Objetivo

Ao terminar este capítulo, o leitor será capaz de containerizar o seu agente existente e rodá-lo no Fargate com estado em memória, implementar roteamento de sessão via ALB, e tomar uma decisão informada sobre o modelo de isolamento (por sessão vs. compartilhado). O leitor chegará ao capítulo 9 com a infraestrutura de longa duração definida e pronta para receber WebSocket.

## Fontes utilizadas

- [Lambda, Fargate, Bedrock Agent — Which serverless option for your Agentic pattern?](https://medium.com/@loic.labeye/lambda-fargate-agentcore-which-severless-option-to-choose-for-your-agentic-pattern-aaf68cb99700)
- [Architecting the Agent Gateway: Unifying the Agentic Stack — TrueFoundry](https://www.truefoundry.com/blog/agent-gateway-series-part-1-of-7-truefoundry-agent-gateway)
- [AI Agent Deployment: From Prototype to Production — Agentuity](https://agentuity.com/ai-agent-deployment)
- [Strands Agents SDK: A technical deep dive into agent architectures and observability — AWS Blog](https://aws.amazon.com/blogs/machine-learning/strands-agents-sdk-a-technical-deep-dive-into-agent-architectures-and-observability/)
- [Effectively building AI agents on AWS Serverless — AWS Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
