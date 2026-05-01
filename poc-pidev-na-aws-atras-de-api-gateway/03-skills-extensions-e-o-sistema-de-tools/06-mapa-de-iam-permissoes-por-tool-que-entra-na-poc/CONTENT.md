# Mapa de IAM — Permissões por Tool que Entra na POC

![capa](cover.png)

## Sobre este subcapítulo

Com o conjunto de tools aprovadas definido no subcapítulo anterior, o passo final deste capítulo é traduzir cada tool em permissões concretas de IAM que o execution role do Lambda (ou task role do Fargate) precisa ter. Esse mapa não é burocracia: é o que garante que o handler não falhe com `AccessDeniedException` na primeira invocação real, e é o documento que você leva para revisar com o time de segurança antes de subir a POC.

Este subcapítulo fecha o capítulo 3 entregando exatamente o que o `## Objetivo` promete: o inventário de tools mapeado para dependências de runtime. Ele também é o input explícito para as decisões de IAM nos capítulos 4 (Lambda vs. Fargate), 6 (API Gateway routes) e 7 (autenticação).

## Estrutura

O subcapítulo cobre: (1) **metodologia de derivação** — como ir de "esta tool faz X" para "este role precisa da action Y no resource Z", e a diferença entre permissões de plano de dados (ler/escrever arquivos, executar comandos) e permissões de plano de controle (criar recursos, alterar configuração); (2) **mapa por tool** — `read`/`write`/`edit` sobre EFS (permissão de rede via VPC + security group, não IAM direta; nenhuma action IAM extra além do execution role padrão) vs. sobre S3 (`s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` no bucket de sessões); `bash` (sem permissão IAM própria, mas os comandos que ele executa podem precisar de permissões — listagem explícita dos comandos que a POC deixa entrar e o que cada um exige); `grep`, `find`, `ls` (sem permissão IAM específica além do acesso ao filesystem já coberto); (3) **permissões transversais do handler** — além das tools, o execution role precisa de `logs:CreateLogGroup`, `logs:CreateLogDelivery`, `logs:PutLogEvents` para CloudWatch, e as permissões específicas do serviço de modelo LLM (Anthropic via Bedrock ou diretamente via API key em Secrets Manager); (4) **o template de policy mínima** — um esqueleto de IAM policy em JSON com as permissões aprovadas, comentado por tool, pronto para ser adaptado nos capítulos seguintes.

## Objetivo

Ao terminar este subcapítulo, o leitor terá um documento de referência com todas as permissões IAM que a POC precisa, derivadas rigorosamente das tools aprovadas no subcapítulo anterior. Com esse mapa em mãos, o leitor pode entrar nos capítulos de infraestrutura (4, 6, 7) sem precisar renegociar permissões a cada decisão de runtime.

## Conceitos

A explicação completa destes conceitos vive em [`CONCEPTS.md`](CONCEPTS.md), construída sequencialmente pela skill `estudo-explicar-conceito`.

1. Por que o mapa de IAM deriva das tools, não do runtime — o princípio de least privilege aplicado: permissão existe se e somente se uma tool aprovada a exige
2. `AWSLambdaBasicExecutionRole` como baseline obrigatório — logs:CreateLogGroup, logs:CreateLogStream, logs:PutLogEvents, e o que essa policy não cobre
3. Permissões para `read`/`write`/`edit` sobre EFS — a diferença entre acesso de rede via VPC/security group e permissões IAM, e por que o EFS não exige actions IAM adicionais além do baseline
4. Permissões para `read`/`write`/`edit` sobre S3 — s3:GetObject, s3:PutObject, s3:DeleteObject no bucket de sessões, e o princípio de escopo por resource ARN
5. Permissões para `bash` — o que o execution role precisa quando bash executa subprocessos que chamam aws-sdk, e por que isso é um vetor de escalada de privilégio silencioso
6. Permissão para o modelo LLM — Bedrock (bedrock:InvokeModel por ARN) vs. API key em Secrets Manager (secretsmanager:GetSecretValue), e a diferença de superfície de ataque entre os dois
7. O template de policy mínima comentado por tool — o esqueleto JSON pronto para ser adaptado nos capítulos seguintes, e como usar IAM Access Analyzer para validar o que foi realmente usado

## Fontes utilizadas

- [AWS IAM — Lambda execution role documentation](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)
- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
- [Developers guide to using Amazon EFS with Amazon ECS and AWS Fargate — AWS Containers Blog](https://aws.amazon.com/blogs/containers/developers-guide-to-using-amazon-efs-with-amazon-ecs-and-aws-fargate-part-1/)
- [Pi Coding Agent README — flags e controle de tools](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)
- [AWS Security Best Practices — IAM least privilege for Lambda](https://docs.aws.amazon.com/lambda/latest/dg/security-iam.html)
