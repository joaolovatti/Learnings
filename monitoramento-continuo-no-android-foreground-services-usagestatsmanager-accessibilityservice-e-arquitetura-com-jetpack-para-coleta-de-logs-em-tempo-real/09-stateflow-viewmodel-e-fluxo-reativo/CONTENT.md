# StateFlow, ViewModel e Fluxo Reativo

![capa](cover.png)

## Sobre este capítulo

Com o Foreground Service coletando eventos e o Room persistindo-os, o próximo problema é conectar essa camada de coleta à UI do responsável de forma reativa: quando um novo evento chega, o dashboard deve atualizar automaticamente sem polling. Este capítulo cobre o pipeline de dados completo do serviço ao ViewModel: como o Room emite `Flow` a cada insert, como o ViewModel transforma e expõe esse `Flow` como `StateFlow`, e como a UI do Compose coleta o `StateFlow` reagindo às mudanças de estado com o ciclo de vida correto.

O desafio central é a fronteira de ciclo de vida: o Foreground Service tem ciclo de vida independente da Activity e do ViewModel. O capítulo define o contrato de comunicação entre o serviço e o ViewModel via Repository — o serviço escreve no Room; o Repository lê o Room como `Flow`; o ViewModel expõe `StateFlow`; o Compose coleta com `collectAsStateWithLifecycle`. Essa separação garante que o serviço nunca dependa da UI e que a UI nunca bloqueie a coleta.

## Estrutura

Os grandes blocos são: (1) Flow frio vs StateFlow quente — diferença de comportamento, quando usar `flow {}` vs `MutableStateFlow`, `stateIn` com `SharingStarted.WhileSubscribed` para converter Flow frio em StateFlow quente com cleanup automático; (2) Repository pattern — `AppUsageRepository` como único ponto de acesso ao Room e ao pipeline de coleta, injeção via Hilt ou construção manual, separação de responsabilidade entre Repository (dados) e ViewModel (estado de UI); (3) ViewModel com StateFlow — `viewModelScope`, `MutableStateFlow` de estado de UI, `combine` de múltiplos Flows, `catch` para erros e exposição de `StateFlow` imutável para a UI; (4) backpressure e conflation — o que acontece quando o produtor (serviço) gera eventos mais rápido que o consumidor (UI) consome, `conflate()` vs `buffer()` e quando usar cada estratégia; (5) `collectAsStateWithLifecycle` — por que `collectAsState` sozinho não é seguro com ciclo de vida, e como `collectAsStateWithLifecycle` do Lifecycle KTX pausa a coleta quando a UI está em background.

## Objetivo

Ao terminar este capítulo, o leitor terá o pipeline reativo completo: Foreground Service → Room → Repository → ViewModel → StateFlow → Compose UI, com ciclo de vida correto em cada fronteira. O dashboard do responsável receberá atualizações em tempo real sem polling, e o serviço de coleta continuará funcionando independentemente do estado da UI.

## Fontes utilizadas

- [Kotlin flows on Android — Android Developers](https://developer.android.com/kotlin/flow)
- [StateFlow and SharedFlow — Android Developers](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [ViewModel overview — Android Developers](https://developer.android.com/topic/libraries/architecture/viewmodel)
- [Collect flows in a lifecycle-aware manner — Android Developers](https://developer.android.com/kotlin/flow/lifecycle-aware)
- [nowinandroid Architecture Learning Journey — GitHub/android](https://github.com/android/nowinandroid/blob/main/docs/ArchitectureLearningJourney.md)
- [Kotlin coroutines on Android — Android Developers](https://developer.android.com/kotlin/coroutines)
