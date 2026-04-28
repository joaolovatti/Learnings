# Foreground Service Estável

![capa](cover.png)

## Sobre este capítulo

Este capítulo é o núcleo operacional do livro: materializa um Foreground Service que sobrevive às condições adversas do Android moderno — restrições de bateria, otimizações de memória, reboots e ANRs. O leitor sai daqui com um serviço que inicia, mantém a notificação persistente, responde a comandos e para corretamente, seguindo os contratos do sistema operacional. O posicionamento no capítulo três é intencional: o modelo mental dos capítulos anteriores (Kotlin idiomático + ciclo de vida de Services) é o pré-requisito direto para cada decisão de implementação que aparece aqui.

O fio condutor é o app de controle parental: o serviço precisa estar vivo enquanto o dispositivo estiver ligado, sobreviver à remoção do app do recentes pelo usuário, e ser reiniciado automaticamente caso o sistema o encerre. Cada detalhe de implementação — da declaração no manifest ao `START_STICKY` em `onStartCommand` — é justificado em termos de comportamento real do sistema, não apenas de API.

## Estrutura

Os grandes blocos são: (1) declaração no manifest — `<service>` com `android:foregroundServiceType`, permissões `FOREGROUND_SERVICE` e `FOREGROUND_SERVICE_DATA_SYNC`, flags de exported e enabled; (2) implementação do serviço — `onStartCommand` com `START_STICKY`, `startForeground` com notificação de canal correto, `stopSelf` com condição, e limpeza de recursos em `onDestroy`; (3) notificação persistente — criação do `NotificationChannel` no Android 8+, builder de notificação com ação de parada, atualização da notificação em runtime com progresso ou status; (4) sobrevivência a condições adversas — `onTaskRemoved` para reagir à remoção do recentes, `PendingIntent` de restart e relação com o `onStartCommand` que o sistema vai chamar novamente; (5) `LifecycleService` do Jetpack — vantagens de estender `LifecycleService` em vez de `Service` puro e integração com `lifecycleScope` para coroutines gerenciadas.

## Objetivo

Ao terminar este capítulo, o leitor terá implementado um Foreground Service completo para o app de controle parental: declarado no manifest com os tipos corretos, com notificação persistente funcionando no Android 8–15, respondendo a `START_STICKY` e sobrevivendo à remoção do app do recentes. O serviço estará pronto para receber as camadas de coleta de eventos dos capítulos seguintes.

## Fontes utilizadas

- [Launch a foreground service — Android Developers](https://developer.android.com/develop/background-work/services/fgs/launch)
- [Foreground service types — Android Developers](https://developer.android.com/develop/background-work/services/fgs/service-types)
- [Understanding foreground service and full-screen intent requirements — Play Console Help](https://support.google.com/googleplay/android-developer/answer/13392821?hl=en)
- [Implementing Foreground Services in Android Apps — Medium](https://medium.com/@khorassani64/implementing-foreground-services-in-android-apps-df2d66535121)
- [ForegroundServiceSamples — GitHub/landomen](https://github.com/landomen/ForegroundServiceSamples)
- [LifecycleService — Android Developers](https://developer.android.com/reference/androidx/lifecycle/LifecycleService)
