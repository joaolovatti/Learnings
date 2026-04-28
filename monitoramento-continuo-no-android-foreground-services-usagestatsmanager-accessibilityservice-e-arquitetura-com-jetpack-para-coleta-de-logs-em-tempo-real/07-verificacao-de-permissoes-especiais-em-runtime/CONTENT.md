# Verificação de Permissões Especiais em Runtime

![capa](cover.png)

## Sobre este capítulo

`UsageStatsManager` e `AccessibilityService` dependem de permissões especiais que o usuário concede manualmente em telas de Settings do sistema — não via o diálogo padrão de `requestPermissions`. Essa diferença muda completamente o fluxo de onboarding do app: o leitor precisa detectar o estado de cada permissão em runtime, guiar o usuário à tela correta de Settings e implementar fallbacks quando a permissão é negada ou revogada depois. Este capítulo cobre `AppOpsManager` como o mecanismo central de verificação e o fluxo completo de solicitação e verificação dessas permissões especiais.

O capítulo aparece após os dois capítulos de coleta porque só faz sentido falar de verificação de permissão depois de entender o que cada permissão protege. O leitor sai daqui com um componente de gerenciamento de permissões que pode ser chamado pelo Foreground Service a qualquer momento para verificar o estado atual e reagir adequadamente — pausando a coleta, notificando o usuário responsável ou redirecionando para Settings.

## Estrutura

Os grandes blocos são: (1) `AppOpsManager` — `checkOpNoThrow` vs `unsafeCheckOpNoThrow`, `OP_GET_USAGE_STATS`, `MODE_ALLOWED` vs `MODE_DEFAULT` vs `MODE_IGNORED` e como os fabricantes customizam os retornos; (2) verificação de `AccessibilityService` ativo — `AccessibilityManager.getEnabledAccessibilityServiceList` e como determinar se o serviço específico está ativo; (3) fluxo de solicitação — `ACTION_USAGE_ACCESS_SETTINGS` e `ACTION_ACCESSIBILITY_SETTINGS` com deep link para o serviço específico onde possível, e `ActivityResultLauncher` para capturar o retorno; (4) gerenciamento de estado de permissão no Foreground Service — verificação periódica via `lifecycleScope`, `StateFlow` de estado de permissão, pausa seletiva de coleta quando permissão é revogada; (5) fallbacks e degradação graciosa — o que o app ainda consegue fazer sem cada permissão, como comunicar a degradação ao responsável via notificação e como persistir o estado de permissão localmente.

## Objetivo

Ao terminar este capítulo, o leitor terá implementado um gerenciador de permissões especiais que o Foreground Service usa para verificar `PACKAGE_USAGE_STATS` e `AccessibilityService` em runtime, redirecionar o usuário à Settings correta quando necessário, e pausar seletivamente a coleta quando uma permissão é revogada. O pipeline de coleta dos capítulos anteriores terá um guardião de permissões que o torna robusto em produção.

## Fontes utilizadas

- [AppOpsManager — Android Developers](https://developer.android.com/reference/android/app/AppOpsManager)
- [UsageStatsManager — Android Developers](https://developer.android.com/reference/android/app/usage/UsageStatsManager)
- [AccessibilityManager — Android Developers](https://developer.android.com/reference/android/view/accessibility/AccessibilityManager)
- [DevicePolicyManager — Android Developers](https://developer.android.com/reference/android/app/admin/DevicePolicyManager)
- [Use of the AccessibilityService API — Play Console Help](https://support.google.com/googleplay/android-developer/answer/10964491?hl=en)
- [Android UsageStatsManager — Tracking App Usage with Ease — CIIT Training](https://ciit-training.com/en/2024/09/16/android-usagestatsmanager-tracking-app-usage-with-ease/)
