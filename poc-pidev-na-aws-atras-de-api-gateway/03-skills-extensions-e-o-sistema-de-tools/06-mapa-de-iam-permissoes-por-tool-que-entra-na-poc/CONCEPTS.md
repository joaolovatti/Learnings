# Conceitos: Mapa de IAM — Permissões por Tool que Entra na POC

> _Aula contínua dos conceitos atômicos deste subcapítulo. Cada conceito vira uma seção `## N.` preenchida em sequência pela skill `estudo-explicar-conceito`. Cada nova iteração lê o que já foi escrito e dá continuidade — sem repetir vocabulário, sem reapresentar exemplos, sem saltos de tom._

## Roteiro

1. Por que o mapa de IAM deriva das tools, não do runtime — o princípio de least privilege aplicado: permissão existe se e somente se uma tool aprovada a exige
2. `AWSLambdaBasicExecutionRole` como baseline obrigatório — logs:CreateLogGroup, logs:CreateLogStream, logs:PutLogEvents, e o que essa policy não cobre
3. Permissões para `read`/`write`/`edit` sobre EFS — a diferença entre acesso de rede via VPC/security group e permissões IAM, e por que o EFS não exige actions IAM adicionais além do baseline
4. Permissões para `read`/`write`/`edit` sobre S3 — s3:GetObject, s3:PutObject, s3:DeleteObject no bucket de sessões, e o princípio de escopo por resource ARN
5. Permissões para `bash` — o que o execution role precisa quando bash executa subprocessos que chamam aws-sdk, e por que isso é um vetor de escalada de privilégio silencioso
6. Permissão para o modelo LLM — Bedrock (bedrock:InvokeModel por ARN) vs. API key em Secrets Manager (secretsmanager:GetSecretValue), e a diferença de superfície de ataque entre os dois
7. O template de policy mínima comentado por tool — o esqueleto JSON pronto para ser adaptado nos capítulos seguintes, e como usar IAM Access Analyzer para validar o que foi realmente usado

<!-- ROTEIRO-END -->

<!-- PENDENTE-START -->
> _Pendente: 7 / 7 conceitos preenchidos._
<!-- PENDENTE-END -->

<!-- AULAS-START -->
## 1. Por que o mapa de IAM deriva das tools, não do runtime — o princípio de least privilege aplicado: permissão existe se e somente se uma tool aprovada a exige

O erro comum em configuração de execução role para Lambda é derivar as permissões do que o serviço "pode vir a precisar" — e terminar com políticas como `s3:*` ou `ec2:Describe*` que cobrem casos de uso especulativos. O princípio de least privilege exige o inverso: você começa com zero permissões e adiciona apenas o que é evidentemente necessário.

Para a POC, o ponto de partida é o inventário aprovado no subcapítulo 05: as sete tools (`read`, `write`, `edit`, `bash`, `grep`, `find`, `ls`) e nenhuma custom tool adicional na POC base. Cada permissão IAM no execution role precisa ser rastreável a uma dessas tools — se não há tool que exige a permissão, a permissão não existe. Esse rastreamento é o mapa.

A consequência prática é que o mapa de IAM é um artefato de design que documenta a superfície de ataque do agente: qualquer permissão presente no role é uma operação que o agente pode executar no ambiente AWS. Permissões desnecessárias são vetores de ataque em caso de comprometimento do agente (ex: um prompt injection que faz o agente executar `bash` com `aws s3 rm s3://bucket --recursive` se o role tiver `s3:DeleteObject` em `*`).

**Fontes utilizadas:**

- [Applying the principles of least privilege in AWS Lambda — Orchestra](https://www.getorchestra.io/guides/applying-the-principles-of-least-privilege-in-aws-lambda-developing-least-privilege-iam-roles)
- [Defining Lambda function permissions with an execution role — AWS Lambda docs](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)

## 2. `AWSLambdaBasicExecutionRole` como baseline obrigatório — logs:CreateLogGroup, logs:CreateLogStream, logs:PutLogEvents, e o que essa policy não cobre

Todo execution role de Lambda precisa da `AWSLambdaBasicExecutionRole` como ponto de partida. Ela contém três ações CloudWatch Logs:

```json
{
  "Effect": "Allow",
  "Action": [
    "logs:CreateLogGroup",
    "logs:CreateLogStream",
    "logs:PutLogEvents"
  ],
  "Resource": "arn:aws:logs:*:*:*"
}
```

Essas três ações permitem que o Lambda runtime escreva os logs de execução no CloudWatch — incluindo stdout/stderr do handler, erros não capturados, e timeouts. Sem elas, a função executa mas não produz logs visíveis, tornando diagnóstico impossível.

O que essa policy **não cobre**:
- Acesso a S3 (nenhuma action s3:*)
- Acesso a EFS (não é IAM, é configuração de VPC — ver conceito 3)
- Acesso a Secrets Manager (nenhuma action secretsmanager:*)
- Acesso ao Bedrock (nenhuma action bedrock:*)
- Acesso a DynamoDB, SQS, SNS, ou qualquer outro serviço

Para a POC, `AWSLambdaBasicExecutionRole` é o baseline, e todos os demais acessos são camadas adicionais explícitas derivadas das tools aprovadas.

**Fontes utilizadas:**

- [AWSLambdaBasicExecutionRole — AWS Managed Policy reference](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSLambdaBasicExecutionRole.html)
- [Defining Lambda function permissions — AWS Lambda docs](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)

## 3. Permissões para `read`/`write`/`edit` sobre EFS — a diferença entre acesso de rede via VPC/security group e permissões IAM, e por que o EFS não exige actions IAM adicionais além do baseline

EFS usa um modelo de autorização dual: **nível de rede** (VPC e security groups) e **nível de filesystem** (posix UID/GID do processo). Não há ações IAM separadas para operações de leitura e escrita em arquivos do EFS — diferente do S3, onde cada operação (`GetObject`, `PutObject`) tem uma action IAM específica.

O que determina se um container Lambda consegue ler e escrever no EFS é:
1. **Configuração de VPC**: o Lambda precisa estar na mesma VPC que o EFS (ou conectado via peering/endpoint).
2. **Security group**: o security group do Lambda precisa ter acesso de saída à porta 2049 (NFS) do security group do EFS mount target.
3. **EFS access point**: o Lambda monta o EFS via um access point que define o UID/GID do processo e o path raiz que aquele access point expõe.
4. **IAM policy de recurso no EFS**: o EFS pode ter uma resource policy que restringe quais principals podem montar — se existir, o execution role do Lambda precisa estar autorizado nela. Se não existe resource policy, qualquer principal na VPC com acesso de rede pode montar.

Consequência para o mapa de IAM: as tools `read`, `write` e `edit` sobre EFS **não geram ações IAM adicionais no execution role**. O acesso é controlado na camada de rede e de configuração do access point — documentado nos capítulos 4 e 8. O mapa de IAM para essas tools, em relação ao execution role, fica vazio além do baseline.

**Fontes utilizadas:**

- [Developers guide to using Amazon EFS with Amazon ECS and AWS Fargate — AWS Containers Blog](https://aws.amazon.com/blogs/containers/developers-guide-to-using-amazon-efs-with-amazon-ecs-and-aws-fargate-part-1/)
- [Amazon EFS — security considerations](https://docs.aws.amazon.com/efs/latest/ug/security-considerations.html)

## 4. Permissões para `read`/`write`/`edit` sobre S3 — s3:GetObject, s3:PutObject, s3:DeleteObject no bucket de sessões, e o princípio de escopo por resource ARN

Se a POC usar S3 como storage de sessões (alternativa ao EFS, coberta no capítulo 9), as tools `read`, `write` e `edit` passam a fazer chamadas S3 por baixo — seja via AWS SDK dentro de um `customTool`, seja via `bash` com `aws s3` CLI. Nesse caso, o execution role precisa de ações S3 específicas.

As três ações necessárias para sessões de leitura e escrita:

```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:PutObject",
    "s3:DeleteObject"
  ],
  "Resource": "arn:aws:s3:::poc-pidev-sessions-bucket/*"
}
```

O princípio de escopo por resource ARN é crítico: o `Resource` aponta para o bucket específico da POC com `/*` no final (que concede acesso a todos os objetos dentro dele), não para `arn:aws:s3:::*` (que concederia acesso a todos os buckets da conta). Restrição por ARN de resource é a forma mais eficaz de least privilege em S3.

Se o agente precisar listar objetos (ex: para que o LLM descubra quais sessões existem), a ação `s3:ListBucket` precisa ser adicionada com o ARN do bucket sem o `/*`:

```json
{
  "Effect": "Allow",
  "Action": "s3:ListBucket",
  "Resource": "arn:aws:s3:::poc-pidev-sessions-bucket"
}
```

Nota: `s3:DeleteObject` está no mapa porque `edit` no S3 é implementado como read → modify → write → delete-old-version ou simplesmente como `PutObject` sobre o mesmo key (S3 não tem append nativo — tema do capítulo 9).

**Fontes utilizadas:**

- [Defining Lambda function permissions — AWS Lambda docs](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)
- [SessionManager Customizado Backed Por S3 — capítulo 9 deste livro](../../09-sessionmanager-customizado-backed-por-s3/CONTENT.md)
- [AWS IAM — S3 actions](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3.html)

## 5. Permissões para `bash` — o que o execution role precisa quando bash executa subprocessos que chamam aws-sdk, e por que isso é um vetor de escalada de privilégio silencioso

`bash` em si não exige nenhuma ação IAM adicional — é execução de processo local. O problema é que `bash` pode executar subcomandos que fazem chamadas à API AWS, e esses subcomandos herdam o execution role do Lambda:

```bash
# dentro de uma tool call bash:
aws s3 ls s3://outro-bucket-sensivel/  # usa as credenciais do execution role
aws iam list-users                      # se o role tiver permissão, funciona
```

Isso é um vetor de escalada de privilégio silencioso: se o execution role tiver permissões amplas (ex: para fins de desenvolvimento), e o agente for comprometido via prompt injection, o atacante pode usar `bash` para invocar qualquer operação AWS que o role permitir — mesmo que o agente não tenha nenhuma custom tool para isso.

A mitigação tem duas camadas:
1. **Princípio de least privilege no role**: o execution role só tem as ações listadas neste mapa. `bash` só consegue executar ações AWS que o role permite.
2. **Handler de tool_call para bash**: um interceptor de `tool_call` (coberto no conceito 6 do subcapítulo 02) pode bloquear padrões específicos de `bash` — ex: qualquer comando que contenha `aws iam`, `aws s3 rm`, ou referências a buckets fora do padrão da POC.

O mapa de IAM para `bash` na POC, portanto, não lista ações IAM próprias de `bash` — lista **o máximo que o bash pode alcançar via aws-sdk/cli**, que deve ser idêntico à soma das ações de todas as outras tools aprovadas. Se `bash` consegue fazer mais do que as custom tools permitem, o role está superprovisionado.

**Fontes utilizadas:**

- [AWS Lambda — execution role security](https://docs.aws.amazon.com/lambda/latest/dg/security-iam.html)
- [Applying the principles of least privilege in AWS Lambda — Orchestra](https://www.getorchestra.io/guides/applying-the-principles-of-least-privilege-in-aws-lambda-developing-least-privilege-iam-roles)

## 6. Permissão para o modelo LLM — Bedrock (bedrock:InvokeModel por ARN) vs. API key em Secrets Manager (secretsmanager:GetSecretValue), e a diferença de superfície de ataque entre os dois

O pi.dev precisa de acesso ao modelo LLM que vai processar os turnos. Duas abordagens para a POC:

**Via Amazon Bedrock**: o modelo é chamado via API AWS, e o execution role precisa de:

```json
{
  "Effect": "Allow",
  "Action": "bedrock:InvokeModel",
  "Resource": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-7-sonnet-20250219-v1:0"
}
```

A superfície de ataque é limitada ao ARN do modelo específico: o agente comprometido só consegue chamar aquele modelo, não fazer `bedrock:CreateModelCustomizationJob` ou acessar outros modelos.

**Via API key em Secrets Manager** (ex: API key da Anthropic diretamente): o execution role precisa de:

```json
{
  "Effect": "Allow",
  "Action": "secretsmanager:GetSecretValue",
  "Resource": "arn:aws:secretsmanager:us-east-1:123456789012:secret:poc/anthropic-api-key-XXXXXX"
}
```

A diferença de superfície de ataque: com Bedrock, a credencial de autenticação é o próprio execution role (credenciais temporárias geradas pelo IAM, rotacionadas automaticamente, nunca expostas no código). Com API key em Secrets Manager, a credencial é um segredo estático que, se vazar (ex: via `bash` que imprime o valor da variável de ambiente), permite chamadas diretas à API da Anthropic fora do contexto da POC. Para a POC de demonstração, Bedrock é preferível — mais seguro e sem gestão de segredo.

**Fontes utilizadas:**

- [Amazon Bedrock — IAM permissions](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html)
- [AWS Secrets Manager — GetSecretValue](https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access.html)
- [Effectively building AI agents on AWS Serverless — AWS Compute Blog](https://aws.amazon.com/blogs/compute/effectively-building-ai-agents-on-aws-serverless/)

## 7. O template de policy mínima comentado por tool — o esqueleto JSON pronto para ser adaptado nos capítulos seguintes, e como usar IAM Access Analyzer para validar o que foi realmente usado

O template abaixo consolida todas as permissões dos conceitos anteriores. Cada bloco é comentado pela tool que o justifica:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CloudWatchLogsBaseline",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:REGION:ACCOUNT_ID:*"
    },
    {
      "Sid": "S3SessionStorageForReadWriteEdit",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::poc-pidev-sessions-bucket/*"
    },
    {
      "Sid": "S3SessionListForGrep",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::poc-pidev-sessions-bucket"
    },
    {
      "Sid": "BedrockLLMForAgentTurns",
      "Effect": "Allow",
      "Action": "bedrock:InvokeModel",
      "Resource": "arn:aws:bedrock:REGION::foundation-model/anthropic.claude-3-7-sonnet-20250219-v1:0"
    }
  ]
}
```

**EFS não aparece**: autorizado na camada de rede (VPC + security group + access point), não via IAM action no execution role.

**`bash`, `grep`, `find`, `ls` não aparecem**: operações locais de filesystem e shell — sem ação IAM.

Para validar que o role não está superprovisionado após a POC estar rodando, o **IAM Access Analyzer** analisa os logs do CloudTrail do período de testes e gera uma policy com apenas as ações que foram efetivamente chamadas. Comparar essa policy gerada com o template acima revela permissões presentes no template que nunca foram usadas — candidatas a remoção, ou indicativo de feature não testada.

```bash
# gerar policy de least privilege baseada em CloudTrail (exemplo via CLI)
aws iam generate-service-last-accessed-details --arn arn:aws:iam::ACCOUNT:role/poc-pidev-execution-role
```

Esse template e o processo de validação são os inputs diretos para as decisões de IAM nos capítulos 4 (Lambda vs. Fargate), 6 (API Gateway routes) e 7 (autenticação JWT).

**Fontes utilizadas:**

- [IAM Access Analyzer — generate policy from CloudTrail](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-policy-generation.html)
- [AWS Lambda execution role — best practices](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)
- [Defining Lambda function permissions — AWS Lambda docs](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)
<!-- AULAS-END -->

---

**Próximo capítulo** → [Lambda ou Fargate Para Hospedar Pi.dev](../../04-lambda-ou-fargate-para-hospedar-pidev/CONTENT.md)
