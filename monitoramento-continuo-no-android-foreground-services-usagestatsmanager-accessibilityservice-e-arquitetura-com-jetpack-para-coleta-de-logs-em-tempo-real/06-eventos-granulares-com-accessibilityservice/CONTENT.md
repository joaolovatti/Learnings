# Eventos Granulares com AccessibilityService

![capa](cover.png)

## Sobre este capítulo

`UsageStatsManager` fornece dados de nível de app — qual app está em foreground e por quanto tempo. `AccessibilityService` desce um nível: entrega eventos de UI dentro do app em foreground, como qual Activity foi exibida, qual notificação chegou e qual texto apareceu em um campo. Para o app de controle parental, essa granularidade é o que permite saber não apenas que o filho abriu o YouTube, mas que assistiu vídeos de um determinado tipo — via conteúdo de notificações ou via título de Activity. Este capítulo cobre a implementação de um AccessibilityService para esse fim, com atenção explícita aos limites impostos pelo Google Play para essa API sensível.

O capítulo aparece depois de `UsageStatsManager` porque a arquitetura de coleta deve tentar sempre o canal menos invasivo primeiro: se `UsageStatsManager` já entrega o dado necessário, `AccessibilityService` é desnecessário e mais difícil de aprovar no Play Store. Quando o dado mais granular é justificável (como em controle parental), o capítulo mostra como implementar de forma que resista ao review do Google Play.

## Estrutura

Os grandes blocos são: (1) o que é um AccessibilityService — diferença de um Service normal, o processo de ativação pelo usuário em Configurações de Acessibilidade, e por que o sistema não permite ativação programática; (2) configuração do serviço — `<accessibility-service>` no manifest com `android:accessibilityEventTypes`, `accessibilityFeedbackType`, `android:canRetrieveWindowContent`, e o XML de configuração separado; (3) `onAccessibilityEvent` — tipos de evento relevantes (`TYPE_WINDOW_STATE_CHANGED`, `TYPE_NOTIFICATION_STATE_CHANGED`, `TYPE_WINDOW_CONTENT_CHANGED`), extração de `packageName`, `className` e texto de `AccessibilityEvent`; (4) captura de conteúdo de notificações — parsing de `Notification.extras` via `Parcelable` nos eventos de notificação, limitações de conteúdo e casos onde o texto não está disponível; (5) política do Google Play — o que a Use of Accessibility API policy permite e proíbe, como declarar o propósito no manifest e na ficha do Play Console, e riscos de remoção do app se a declaração não for precisa.

## Objetivo

Ao terminar este capítulo, o leitor terá implementado um `AccessibilityService` que captura eventos de mudança de janela e de notificação, extraindo package name, class name e texto disponível, e integrando esses eventos ao pipeline de coleta do Foreground Service. O leitor entenderá os limites da política do Google Play para essa API e saberá como declarar o uso de forma que resista ao review de publicação.

## Fontes utilizadas

- [AccessibilityService — Android Developers](https://developer.android.com/reference/android/accessibilityservice/AccessibilityService)
- [Use of the AccessibilityService API — Play Console Help](https://support.google.com/googleplay/android-developer/answer/10964491?hl=en)
- [Updates to Android accessibility features and APIs — Google I/O 2024](https://io.google/2024/explore/c469c529-be54-4013-8ddf-4c1dfbe347fc/)
- [Guidelines for Accessibility in Android — BrowserStack](https://www.browserstack.com/guide/android-accessibility-guidelines)
- [Get foreground activity using UsageStatsManager or AccessibilityService — GitHub/ngdathd](https://github.com/ngdathd/ForegroundActivity)
- [Understanding Google Play's Spyware policy — Play Console Help](https://support.google.com/googleplay/android-developer/answer/14745000?hl=en)
