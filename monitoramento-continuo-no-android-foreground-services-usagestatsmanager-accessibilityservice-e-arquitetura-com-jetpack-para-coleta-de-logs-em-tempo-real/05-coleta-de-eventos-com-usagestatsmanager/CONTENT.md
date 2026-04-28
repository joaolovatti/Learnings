# Coleta de Eventos com UsageStatsManager

![capa](cover.png)

## Sobre este capítulo

Com o Foreground Service estável e o background work configurado, o livro entra na segunda grande competência: coletar dados de uso de apps. `UsageStatsManager` é a API de sistema que fornece dois tipos de dados — estatísticas agregadas de uso por app (tempo em foreground por janela de tempo) e o stream de eventos granulares de mudança de estado de apps. Este capítulo cobre os dois modos, a permissão especial `PACKAGE_USAGE_STATS` que os protege, e como integrar a coleta dentro do Foreground Service construído nos capítulos anteriores.

O recorte foca nos dados que o app de controle parental precisa: quanto tempo o filho usou cada app (via `queryUsageStats`) e quais apps foram abertos e quando (via `queryEvents`). A API retorna dados com granularidade mínima de 1 segundo para eventos e de 1 dia para estatísticas agregadas — o capítulo explica as implicações de polling interval, offset de clock e as diferenças de comportamento entre fabricantes (Samsung, Xiaomi, Huawei) que personalizam o Android e às vezes quebram o comportamento padrão da API.

## Estrutura

Os grandes blocos são: (1) permissão `PACKAGE_USAGE_STATS` — por que ela é uma permissão especial (não `dangerous`), como verificar se está concedida via `AppOpsManager.checkOpNoThrow`, e como direcionar o usuário à Settings correto (`ACTION_USAGE_ACCESS_SETTINGS`); (2) `queryUsageStats` — `UsageStatsManager.INTERVAL_DAILY/WEEKLY/MONTHLY/BEST`, parsing do `UsageStats` retornado, tempo total em foreground e last time used; (3) `queryEvents` — `UsageEvents`, `UsageEvents.Event`, `getEventType`, tipos de evento relevantes (`MOVE_TO_FOREGROUND`, `MOVE_TO_BACKGROUND`, `ACTIVITY_RESUMED`, `ACTIVITY_PAUSED`) e janela de tempo segura para polling sem duplicação; (4) integração com o Foreground Service — loop de polling dentro do `lifecycleScope`, intervalo configurável, debounce para evitar flood de eventos, conversão para entidades Room; (5) variações por fabricante — comportamentos documentados no Huawei (EMUI), Xiaomi (MIUI) e Samsung (One UI) e estratégias de detecção e fallback.

## Objetivo

Ao terminar este capítulo, o leitor conseguirá coletar dados de uso de apps via `UsageStatsManager` dentro do Foreground Service: verificar a permissão em runtime, consultar estatísticas agregadas por janela de tempo, receber o stream de eventos de transição de app, e persistir esses dados como entidades Room para sincronização posterior. O leitor entenderá os limites da API e os comportamentos específicos de fabricantes que afetam o app de controle parental em produção.

## Fontes utilizadas

- [UsageStatsManager — Android Developers](https://developer.android.com/reference/android/app/usage/UsageStatsManager)
- [Android AppUsageStatistics sample — GitHub/googlesamples](https://github.com/googlesamples/android-AppUsageStatistics)
- [Show app usage with UsageStatsManager — Medium](https://medium.com/@quiro91/show-app-usage-with-usagestatsmanager-d47294537dab)
- [Android UsageStatsManager — Tracking App Usage with Ease — CIIT Training](https://ciit-training.com/en/2024/09/16/android-usagestatsmanager-tracking-app-usage-with-ease/)
- [Get foreground activity using UsageStatsManager or AccessibilityService — GitHub/ngdathd](https://github.com/ngdathd/ForegroundActivity)
- [A Systematic Survey on Android API Usage for Data-driven Analytics — ACM Computing Surveys](https://dl.acm.org/doi/10.1145/3530814)
