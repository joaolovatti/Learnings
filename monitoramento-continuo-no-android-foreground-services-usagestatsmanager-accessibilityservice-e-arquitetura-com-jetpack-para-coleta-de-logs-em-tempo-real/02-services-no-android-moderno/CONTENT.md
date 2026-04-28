# Services no Android Moderno

![capa](cover.png)

## Sobre este capítulo

Antes de implementar um Foreground Service resiliente, o leitor precisa ter um modelo mental claro de como o sistema operacional Android enxerga e gerencia serviços — sem isso, os erros de ciclo de vida que aparecem nos capítulos seguintes parecem magia negra. Este capítulo constrói esse modelo: descreve os três tipos de Service (started, bound, foreground), o ciclo de vida completo de cada um, como componentes se comunicam com serviços via `Intent`, `Messenger` e `AIDL`, e por que o Android 8+ exige que qualquer serviço que o usuário perceba seja declarado como foreground com uma notificação obrigatória. Aparece antes da implementação do Foreground Service porque a notificação obrigatória e as restrições de background só fazem sentido no contexto do modelo completo.

O leitor já conhece o modelo de componentes Android via Java — este capítulo não explica o que é um `Service` do zero, mas aprofunda o comportamento em runtime, os callbacks do ciclo de vida (`onCreate`, `onStartCommand`, `onBind`, `onDestroy`), os return values de `onStartCommand` (`START_STICKY`, `START_NOT_STICKY`, `START_REDELIVER_INTENT`) e como o sistema decide matar ou preservar um processo de serviço sob pressão de memória.

## Estrutura

Os grandes blocos são: (1) taxonomia de services — started vs bound vs foreground, quando usar cada um, e como um service pode ser os três ao mesmo tempo; (2) ciclo de vida detalhado — sequência de callbacks, quando o sistema chama `onDestroy` vs quando mata o processo sem aviso, e o papel do `onTaskRemoved`; (3) comunicação com serviços — `startService`, `bindService`, `Intent` com extras, `Messenger` para comunicação bidirecional leve e `AIDL` para IPC cross-process; (4) a notificação obrigatória — `startForeground(id, notification)`, canais de notificação no Android 8+, tipos de serviço (`mediaPlayback`, `dataSync`, `location`, `health`) e as exceções à regra de visibilidade; (5) restrições de background no Android 8–15 — o que mudou em cada API level e como o sistema prioriza ou mata serviços em segundo plano.

## Objetivo

Ao terminar este capítulo, o leitor terá o modelo mental completo para diagnosticar problemas de ciclo de vida em serviços Android, saberá escolher o tipo correto de service para o caso do app de controle parental, entenderá por que a notificação do foreground service não é opcional e estará preparado para implementar um Foreground Service estável no capítulo seguinte sem tropeçar nos comportamentos implícitos do sistema.

## Fontes utilizadas

- [Services overview — Android Developers](https://developer.android.com/develop/background-work/services)
- [Foreground services overview — Android Developers](https://developer.android.com/develop/background-work/services/fgs)
- [Foreground service types — Android Developers](https://developer.android.com/develop/background-work/services/fgs/service-types)
- [Changes to foreground services — Android Developers](https://developer.android.com/develop/background-work/services/fgs/changes)
- [Mastering Android Components: Services — Medium](https://medium.com/@manishkumar_75473/mastering-android-components-services-started-bound-foreground-background-and-intentservice-bca5fd982710)
- [Guide to Foreground Services on Android — Speaker Deck](https://speakerdeck.com/landomen/guide-to-foreground-services-on-android)
