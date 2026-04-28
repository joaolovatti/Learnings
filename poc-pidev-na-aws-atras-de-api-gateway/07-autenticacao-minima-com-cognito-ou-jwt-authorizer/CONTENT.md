# Autenticação Mínima Com Cognito ou JWT Authorizer

![capa](cover.png)

## Sobre este capítulo

Entregar uma URL pública sem autenticação é entregar uma conta AWS aberta para qualquer crawler. A POC precisa de uma barreira de acesso mínima — suficiente para que o cliente consiga usar e para que o desenvolvedor consiga controlar quem tem acesso, sem construir um sistema de auth completo que atrasaria a entrega. O API Gateway oferece dois caminhos para isso: um User Pool do Cognito como identity provider embutido, ou um Lambda Authorizer que valida um JWT emitido por qualquer provedor compatível.

Este capítulo é propositalmente pragmático: o objetivo não é segurança de produção multi-tenant, é uma barreira funcional que o cliente consegue atravessar com um token de teste e o desenvolvedor consegue revogar. As decisões de hardening ficam para um livro posterior; aqui o critério é "mínimo que funciona para a demo".

## Estrutura

O capítulo cobre: (1) **Cognito User Pool como authorizer nativo** — criação de um User Pool mínimo, criação de App Client sem secret, integração direta no API Gateway como Cognito Authorizer, geração de token de teste para o cliente via `aws cognito-idp initiate-auth`; (2) **JWT Authorizer nativo do API Gateway (HTTP API)** — configuração de issuer e audience, validação stateless sem Lambda extra, casos de uso quando o token vem de um provedor externo (Auth0, Supabase Auth, Clerk); (3) **comparação de complexidade operacional** — Cognito gerencia o lifecycle do usuário mas tem setup mais pesado; JWT Authorizer é mais simples mas assume provedor externo já configurado; (4) **propagação do `userId` para os handlers** — como extrair o sub/claim do JWT dentro do handler Lambda e usar como chave de isolamento de sessões (pré-requisito dos capítulos 8 e 9); (5) **roteiro de entrega de credencial ao cliente** — como gerar um usuário de teste no Cognito, como emitir um token JWT temporário, como documentar o fluxo para o cliente testar sozinho sem suporte.

## Objetivo

Ao terminar este capítulo, o leitor terá o API Gateway protegido por um authorizer funcional, saberá extrair o `userId` do token dentro do handler, e terá um roteiro concreto para entregar credencial de teste ao cliente. O `userId` propagado aqui é o que os capítulos 8 e 9 usam para isolar sessões por tenant.

## Fontes utilizadas

- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)
- [Streamlined multi-tenant application development with tenant isolation mode in AWS Lambda — AWS Blog](https://aws.amazon.com/blogs/aws/streamlined-multi-tenant-application-development-with-tenant-isolation-mode-in-aws-lambda/)
- [Tenant isolation — AWS Lambda docs](https://docs.aws.amazon.com/lambda/latest/dg/tenant-isolation.html)
- [Building multi-tenant SaaS applications with AWS Lambda's new tenant isolation mode — AWS Compute Blog](https://aws.amazon.com/blogs/compute/building-multi-tenant-saas-applications-with-aws-lambdas-new-tenant-isolation-mode/)
- [GitHub — serithemage/serverless-openclaw](https://github.com/serithemage/serverless-openclaw)
