# Monitoramento Contínuo no Android — Foreground Services, UsageStatsManager, AccessibilityService e Arquitetura com Jetpack para Coleta de Logs em Tempo Real

![capa](cover.png)

## Sobre este livro

Este livro cobre o núcleo técnico de qualquer app de monitoramento contínuo no Android: manter um serviço vivo sob as restrições crescentes do sistema operacional, coletar eventos de uso de apps via APIs de sistema (`UsageStatsManager`, `AccessibilityService`, `AppOpsManager`) e estruturar o fluxo de dados desde a captura até a sincronização com um backend remoto. O recorte foi escolhido porque esse conjunto de três competências — persistência, coleta e arquitetura — é interdependente: sem o serviço rodando de forma estável não há coleta; sem arquitetura adequada, a coleta vira ruído não consumível.

O livro trata o caso de uso de controle parental como fio condutor concreto — um app que monitora as atividades do filho no dispositivo Android —, mas os padrões ensinados se aplicam a qualquer app que precise de monitoramento de longa execução: loggers de produtividade, apps de time-tracking, ferramentas de auditoria corporativa.

## Estrutura

Os grandes blocos são: (1) fundamentos de Kotlin relevantes para quem vem do Java e Flutter — coroutines, extension functions, sealed classes e null safety aplicados a serviços Android; (2) Foreground Services e background work moderno — ciclo de vida de serviços, notificação obrigatória, `WorkManager`, `BOOT_COMPLETED` e as restrições do Android 8–15 para processos de longa execução; (3) APIs de sistema para coleta de eventos — `UsageStatsManager` para tempo de uso por app, `AccessibilityService` para eventos granulares (foco de tela, conteúdo de notificações), `AppOpsManager` para verificar permissões especiais em tempo real; (4) arquitetura com Jetpack — Room para persistência local de eventos, StateFlow com ViewModel, Retrofit/OkHttp para sincronização com backend, e Jetpack Compose para o dashboard dos responsáveis.

## Objetivo

Ao terminar, o leitor conseguirá construir um Foreground Service estável que sobrevive a reboot e às otimizações de bateria do Android moderno, coletar eventos de uso de apps com `UsageStatsManager` e eventos granulares com `AccessibilityService`, persistir esses eventos localmente com Room e sincronizá-los com um backend via Retrofit. O leitor estará apto a integrar essa camada de coleta a qualquer backend que já saiba construir — passando direto para os livros de compliance com o Google Play e de filtragem/bloqueio de apps sem precisar revisitar os fundamentos de serviços Android.

## Sobre o leitor

O leitor é um desenvolvedor com experiência prática em publicação de apps Android — já publicou apps construídos em Java e Flutter na Play Store e tem domínio do Android Studio para ambas as linguagens. Tem background sólido em Flutter e em desenvolvimento backend, o que significa que o modelo de componentes do Android (Activities, Services, BroadcastReceivers) não é conceito novo, mas foi trabalhado principalmente via Java; Kotlin é o ponto de partida mais fraco, embora a transição seja curta dado o background em JVM.

Não tem experiência com segurança mobile nem com testes específicos para Android. O objetivo declarado é publicar um app de controle parental na Play Store — um app instalado no dispositivo do filho que coleta logs de atividade e os disponibiliza para os responsáveis. Esse objetivo exige que o leitor domine exatamente a tríade deste livro antes de atacar as camadas de compliance e bloqueio de conteúdo.

O nível de experiência geral é intermediário-avançado em desenvolvimento de software, com lacuna específica em APIs de sistema Android e no comportamento de processos em background nas versões modernas do SO. O livro não explica o que é uma Activity ou um Intent — assume esse vocabulário como dado — e foca inteiramente nas APIs e padrões que o leitor ainda não tocou.

## Capítulos

1. [Kotlin para Devs Java e Flutter](01-kotlin-para-devs-java-e-flutter/CONTENT.md) — coroutines, sealed classes, extension functions e null safety aplicados a contextos de serviços Android
2. [Services no Android Moderno](02-services-no-android-moderno/CONTENT.md) — tipos de Service, ciclo de vida completo, comunicação com componentes e a notificação obrigatória do foreground
3. [Foreground Service Estável](03-foreground-service-estavel/CONTENT.md) — implementação de um ForegroundService resiliente com tipos declarados, startForeground, stopSelf e sobrevivência a crashes
4. [Background Work de Longa Duração](04-background-work-de-longa-duracao/CONTENT.md) — WorkManager para tarefas garantidas, BOOT_COMPLETED receiver e restrições de bateria do Android 8 ao 15
5. [Coleta de Eventos com UsageStatsManager](05-coleta-de-eventos-com-usagestatsmanager/CONTENT.md) — permissão PACKAGE_USAGE_STATS, QueryUsageStats, UsageEvents e granularidade de dados por janela de tempo
6. [Eventos Granulares com AccessibilityService](06-eventos-granulares-com-accessibilityservice/CONTENT.md) — estrutura de AccessibilityService, eventos TYPE_WINDOW_STATE_CHANGED, captura de notificações e limites do Google Play
7. [Verificação de Permissões Especiais em Runtime](07-verificacao-de-permissoes-especiais-em-runtime/CONTENT.md) — AppOpsManager, OP_GET_USAGE_STATS, direcionamento ao Settings e fallback quando permissões são negadas
8. [Persistência Local com Room](08-persistencia-local-com-room/CONTENT.md) — entidades de eventos, DAOs com Flow, migrations e estratégia de retenção e limpeza de logs antigos
9. [StateFlow, ViewModel e Fluxo Reativo](09-stateflow-viewmodel-e-fluxo-reativo/CONTENT.md) — pipeline de dados do serviço ao ViewModel, backpressure, ciclo de vida e separação entre coleta e apresentação
10. [Sincronização com Backend via Retrofit e OkHttp](10-sincronizacao-com-backend-via-retrofit-e-okhttp/CONTENT.md) — modelagem da API de upload de logs, interceptors de autenticação, retry policy e sync incremental com Room como buffer
11. [Dashboard do Responsável com Jetpack Compose](11-dashboard-do-responsavel-com-jetpack-compose/CONTENT.md) — Composables para tempo de uso e eventos por app, integração com StateFlow e navegação entre telas
12. [Integração End-to-End](12-integracao-end-to-end/CONTENT.md) — ligando Foreground Service, APIs de coleta, Room e Retrofit num fluxo coeso, testes manuais e checklist pré-publicação

## Fontes utilizadas

- [UsageStatsManager — Android Developers](https://developer.android.com/reference/android/app/usage/UsageStatsManager)
- [Launch a foreground service — Android Developers](https://developer.android.com/develop/background-work/services/fgs/launch)
- [Foreground service types — Android Developers](https://developer.android.com/develop/background-work/services/fgs/service-types)
- [Use of the AccessibilityService API — Play Console Help](https://support.google.com/googleplay/android-developer/answer/10964491?hl=en)
- [DevicePolicyManager — Android Developers](https://developer.android.com/reference/android/app/admin/DevicePolicyManager)
- [Understanding Google Play's Spyware policy — Play Console Help](https://support.google.com/googleplay/android-developer/answer/14745000?hl=en)
- [Background vs Foreground Services in Android (Kotlin + Jetpack Compose) — Medium](https://medium.com/@YodgorbekKomilo/background-vs-foreground-services-in-android-kotlin-jetpack-compose-726b94983469)
- [Show app usage with UsageStatsManager — Medium](https://medium.com/@quiro91/show-app-usage-with-usagestatsmanager-d47294537dab)
