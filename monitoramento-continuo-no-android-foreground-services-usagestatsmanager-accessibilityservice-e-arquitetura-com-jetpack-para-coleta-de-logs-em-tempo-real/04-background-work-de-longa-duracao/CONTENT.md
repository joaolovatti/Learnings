# Background Work de Longa Duração

![capa](cover.png)

## Sobre este capítulo

Um Foreground Service não opera no vácuo: há tarefas periódicas que não precisam estar no serviço principal (sync de logs, limpeza de Room, re-verificação de permissões) e há o problema crítico de sobrevivência a reboot — sem `BOOT_COMPLETED`, o serviço morre quando o usuário reinicia o dispositivo e não volta até abrir o app manualmente. Este capítulo cobre a camada de background work complementar ao Foreground Service: `WorkManager` para tarefas garantidas e periódicas, `BroadcastReceiver` para `BOOT_COMPLETED`, e as restrições progressivas do Android 8 ao 15 que determinam o que pode e o que não pode rodar em background sem estar em foreground.

A distinção central do capítulo é saber quando usar `WorkManager` vs quando usar o Foreground Service diretamente: o serviço cobre trabalho contínuo e perceptível ao usuário; o WorkManager cobre trabalho periódico, deferível e garantido mesmo após reboot. Para o app de controle parental, a divisão prática é: coleta contínua de eventos no serviço; sync periódico de logs com o backend no WorkManager.

## Estrutura

Os grandes blocos são: (1) WorkManager — `OneTimeWorkRequest`, `PeriodicWorkRequest`, `Constraints` (rede, bateria), encadeamento de workers com `then()`, passagem de dados via `Data` e resultado via `Result.success/failure/retry`; (2) `BOOT_COMPLETED` receiver — declaração no manifest com `RECEIVE_BOOT_COMPLETED`, `onReceive` para disparar o serviço, tratamento da permissão no Android 10+; (3) restrições de bateria — Doze Mode e App Standby no Android 6+, background execution limits no Android 8+, background activity launch restrictions no Android 10+, e exact alarms no Android 12+; (4) `ForegroundInfo` no WorkManager — como declarar um Worker como foreground para operações mais longas que não cabe no serviço principal; (5) estratégia combinada — diagrama de decisão: qual componente gerencia qual tarefa no app de controle parental.

## Objetivo

Ao terminar este capítulo, o leitor saberá iniciar o Foreground Service automaticamente no boot do dispositivo via `BOOT_COMPLETED`, configurar um `PeriodicWorkRequest` para sync periódico de logs com o backend, e entender quais restrições do Android 8–15 afetam o app de controle parental e como contorná-las legalmente. O leitor estará apto a construir o pipeline de coleta nos capítulos seguintes sabendo exatamente qual componente gerencia qual responsabilidade em background.

## Fontes utilizadas

- [Task scheduling with WorkManager — Android Developers](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Background work overview — Android Developers](https://developer.android.com/develop/background-work/background-tasks)
- [Optimize for Doze and App Standby — Android Developers](https://developer.android.com/training/monitoring-device-state/doze-standby)
- [Background execution limits (Android 8.0) — Android Developers](https://developer.android.com/about/versions/oreo/background)
- [Run a foreground service via WorkManager — Android Developers](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-work-done/run-in-foreground)
- [Overview of WorkManager in Android Architecture Components — GeeksforGeeks](https://www.geeksforgeeks.org/android/overview-of-workmanager-in-android-architecture-components/)
