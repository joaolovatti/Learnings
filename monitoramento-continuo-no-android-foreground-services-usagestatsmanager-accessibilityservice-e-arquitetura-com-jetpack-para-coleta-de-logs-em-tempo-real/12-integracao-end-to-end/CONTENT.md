# Integração End-to-End

![capa](cover.png)

## Sobre este capítulo

Este capítulo conecta todas as peças construídas nos capítulos anteriores em um fluxo coeso e testável. Não introduz APIs novas — o foco é wiring: como o Foreground Service inicializa os coletores de `UsageStats` e `AccessibilityService`, como os eventos fluem para o Room via Repository, como o WorkManager dispara o `SyncWorker` periodicamente, e como o dashboard do responsável reflete o estado atual em tempo real. O resultado ao final deste capítulo é um app de controle parental funcional, do boot do dispositivo à tela do responsável.

O capítulo também cobre o checklist pré-publicação específico para apps de monitoramento: os campos obrigatórios no Play Console para uso de `AccessibilityService`, a Prominent Disclosure exigida pelo Google Play quando o app coleta dados de uso, e os testes manuais que validam o comportamento em cenários críticos (reboot, app em background, permissão revogada em runtime, dispositivo offline por 24h).

## Estrutura

Os grandes blocos são: (1) diagrama de componentes completo — mapa visual de como Foreground Service, Room, Repository, ViewModel, WorkManager, Retrofit e Compose se conectam, com responsabilidade de cada componente explicitada; (2) wiring de inicialização — sequência de boot: `BOOT_COMPLETED` → `startForegroundService` → `onCreate` do serviço → inicialização dos coletores → primeiro ciclo de coleta; (3) injeção de dependências — opções de DI para o projeto (Hilt vs manual), scoping de singletons para Room e Retrofit, injeção no Foreground Service via `@AndroidEntryPoint`; (4) testes manuais dos cenários críticos — reboot do dispositivo, remoção do app dos recentes, revogação de permissão em runtime, offline por período longo, upgrade de versão com migration de Room; (5) checklist pré-publicação — Prominent Disclosure no onboarding, declaração de `AccessibilityService` no Play Console, campos obrigatórios da política de dados de usuário e badges de segurança do Data Safety section.

## Objetivo

Ao terminar este capítulo, o leitor terá um app de controle parental funcionando end-to-end: serviço iniciando no boot, coletando eventos de `UsageStats` e `AccessibilityService`, persistindo no Room, sincronizando periodicamente com o backend via WorkManager + Retrofit, e exibindo o dashboard do responsável em Compose com dados em tempo real. O leitor estará apto a publicar o app no Play Store sabendo que cumpriu os requisitos de política para uso de APIs de acessibilidade e coleta de dados de uso.

## Fontes utilizadas

- [Launch a foreground service — Android Developers](https://developer.android.com/develop/background-work/services/fgs/launch)
- [Use of the AccessibilityService API — Play Console Help](https://support.google.com/googleplay/android-developer/answer/10964491?hl=en)
- [Understanding Google Play's Spyware policy — Play Console Help](https://support.google.com/googleplay/android-developer/answer/14745000?hl=en)
- [Data safety in Google Play — Play Console Help](https://support.google.com/googleplay/android-developer/answer/10787469?hl=en)
- [Dependency injection with Hilt — Android Developers](https://developer.android.com/training/dependency-injection/hilt-android)
- [nowinandroid Architecture Learning Journey — GitHub/android](https://github.com/android/nowinandroid/blob/main/docs/ArchitectureLearningJourney.md)
