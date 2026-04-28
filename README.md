# learnings

Método de estudo estruturado em livros. Cada livro vive num diretório próprio e se decompõe em capítulos → subcapítulos → conceitos, com `cover.png` (capa didática), `INTRODUCTION.md` (apresentação) e `STRUCT.md` (índice hierárquico completo).

## Livros

### [POC End-to-End — Pi.dev Atrás de API Gateway na AWS Para Validação Com Cliente](poc-pidev-na-aws-atras-de-api-gateway/INTRODUCTION.md)

![capa](poc-pidev-na-aws-atras-de-api-gateway/cover.png)

Travessia de um engenheiro sênior — avançado em AWS e LLMs, zero em pi.dev — até uma POC pública na AWS que o cliente consegue testar via API Gateway sem suporte do dev. Foco deliberadamente prático: pi.dev tratado como runtime pronto, decisões de hospedagem (Lambda vs Fargate, EFS vs S3, SDK vs RPC) calibradas para o caso específico do harness, sessões persistidas fora do disco local, e empacotamento da entrega (URL pública, credencial de teste, instruções) como objetivo final. Não cobre hardening de produção — esse recorte fica para os livros seguintes do método.

### [Monitoramento Contínuo no Android — Foreground Services, UsageStatsManager, AccessibilityService e Arquitetura com Jetpack para Coleta de Logs em Tempo Real](monitoramento-continuo-no-android-foreground-services-usagestatsmanager-accessibilityservice-e-arquitetura-com-jetpack-para-coleta-de-logs-em-tempo-real/INTRODUCTION.md)

![capa](monitoramento-continuo-no-android-foreground-services-usagestatsmanager-accessibilityservice-e-arquitetura-com-jetpack-para-coleta-de-logs-em-tempo-real/cover.png)

Para um desenvolvedor Android com background em Java e Flutter que precisa construir um app de monitoramento contínuo — como controle parental. Cobre a tríade técnica interdependente: manter um Foreground Service vivo sob as restrições do Android 8–15 (com WorkManager e reboot survival), coletar eventos de uso via `UsageStatsManager` e `AccessibilityService`, e estruturar o fluxo completo com Room, StateFlow e Retrofit até o backend.
