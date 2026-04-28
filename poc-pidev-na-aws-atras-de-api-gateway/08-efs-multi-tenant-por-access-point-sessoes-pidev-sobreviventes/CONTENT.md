# EFS Multi-Tenant Por Access Point — Sessões Pi.dev Sobreviventes

![capa](cover.png)

## Sobre este capítulo

O problema central da POC serverless com pi.dev é que sessões vivem como arquivos JSONL em disco — e disco local em Lambda não sobrevive entre invocações. A primeira solução canônica é redirecionar o diretório de sessões do pi.dev para um volume EFS montado na Lambda Function, com access points por tenant para garantir isolamento sem criar um filesystem por usuário. Este capítulo resolve a persistência de sessão de ponta a ponta via EFS.

EFS é a solução mais próxima do "plug and play" para o harness pi.dev: o harness não precisa mudar — ele continua escrevendo arquivos JSONL no caminho que espera, e o EFS garante que esses arquivos estejam lá na próxima invocação, independente de qual instância Lambda for acordada. O custo é a latência de filesystem em rede e a dependência de VPC.

## Estrutura

O capítulo cobre: (1) **criação e configuração do EFS** — criação de filesystem, mount targets por AZ, security groups para acesso Lambda, configuração de throughput mode; (2) **access points por tenant** — o que é um EFS Access Point, como ele mapeia um `userId` para um path isolado (`/sessions/<userId>/`) com POSIX uid/gid forçados, como criar um access point por usuário (ou por pool de usuários) via IaC; (3) **montagem do EFS na Lambda Function** — configuração do `FileSystemConfig` na Function, VPC attachment, path de mount dentro da Function (`/mnt/sessions`); (4) **redirecionamento do diretório de sessões do pi.dev** — a variável de ambiente ou flag que instrui o harness a usar `/mnt/sessions/<userId>/` em vez do path padrão; (5) **validação e troubleshooting** — como verificar que a sessão persiste entre invocações, erros comuns (mount timeout, permission denied, POSIX mismatch), e o custo operacional do EFS na escala de uma POC.

## Objetivo

Ao terminar este capítulo, o leitor terá sessões pi.dev sobrevivendo entre invocações Lambda via EFS, com isolamento por usuário via access points, e saberá diagnosticar os erros de mount mais comuns. O capítulo seguinte apresenta a alternativa S3 para casos onde EFS não cabe — quem ficou satisfeito com EFS pode pular o 9 e ir direto para o 10.

## Fontes utilizadas

- [New for Amazon EFS — IAM Authorization and Access Points — AWS Blog](https://aws.amazon.com/blogs/aws/new-for-amazon-efs-iam-authorization-and-access-points/)
- [How to Set Up EFS Access Points for Application-Specific Access — OneUptime Blog](https://oneuptime.com/blog/post/2026-02-12-efs-access-points-application-specific-access/view)
- [Deploy AWS Lambda with Elastic File System using Pulumi — Pulumi Blog](https://www.pulumi.com/blog/aws-lambda-efs/)
- [Developers guide to using Amazon EFS with Amazon ECS and AWS Fargate — AWS Containers Blog](https://aws.amazon.com/blogs/containers/developers-guide-to-using-amazon-efs-with-amazon-ecs-and-aws-fargate-part-1/)
- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
