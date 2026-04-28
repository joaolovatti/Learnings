# Kotlin Idiomático em Serviços Android

![capa](cover.png)

## Sobre este subcapítulo

Este subcapítulo integra os quatro blocos anteriores em um padrão completo de serviço Android escrito em Kotlin idiomático — sem ser um tutorial de `Service` (território do capítulo 2), mas um exercício de leitura e escrita fluida do Kotlin que aparece nessa classe. O leitor que chegou aqui conhece cada peça isolada: coroutines, `Flow`, sealed classes, scope functions e null safety. Este subcapítulo os combina numa estrutura coerente para que o salto para o capítulo 2 seja de vocabulário de Android, não de Kotlin.

O recorte é deliberadamente estreito: um esqueleto de `LifecycleService` com `CoroutineScope` gerenciado por `SupervisorJob`, um `StateFlow` de estado do serviço modelado com sealed class, uma extension function em `Context` para iniciar o serviço com `Intent`, e o tratamento de null safety nos retornos de `getSystemService`. Não tem lógica de coleta real — isso vem nos capítulos 5 e 6. O valor aqui é reconhecer o padrão completo antes de adicionar a complexidade das APIs de sistema.

## Estrutura

Os grandes blocos são: (1) `LifecycleService` como base — por que usar `LifecycleService` em vez de `Service` puro (integração automática com `LifecycleScope`), a diferença de ciclo de vida entre as duas classes e a adição de dependência Jetpack necessária; (2) `CoroutineScope` e `SupervisorJob` no service — declaração do escopo, cancelamento no `onDestroy`, por que `viewModelScope` não está disponível aqui e como `LifecycleScope` preenche esse papel; (3) `StateFlow` de estado do service — declaração com `MutableStateFlow` privado e `StateFlow` público, emissão de variantes sealed com `_state.value = ServiceState.Running`, e coleta no `onStartCommand`; (4) extension functions de arranque — `fun Context.startMonitoringService()` e `fun Context.stopMonitoringService()` que encapsulam a criação de `Intent` e a chamada de `startForegroundService`, eliminando boilerplate nos pontos de invocação; (5) leitura de um serviço real — walkthrough do esqueleto completo integrado, identificando cada idiom no lugar certo e o que cada linha comunica para um leitor experiente em Kotlin.

## Objetivo

Ao terminar este subcapítulo, o leitor conseguirá ler o código de um Foreground Service em Kotlin sem pausar em nenhuma construção de linguagem — coroutines, Flow, sealed class, scope functions e null safety aparecerão como vocabulário familiar. Esse é o estado de leitura silenciosa que os capítulos seguintes pressupõem: o leitor processa a lógica de coleta e de ciclo de vida, não a sintaxe Kotlin.

## Fontes utilizadas

- [Kotlin coroutines on Android — Android Developers](https://developer.android.com/kotlin/coroutines)
- [StateFlow and SharedFlow — Android Developers](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [Background vs Foreground Services in Android (Kotlin + Jetpack Compose) — Medium](https://medium.com/@YodgorbekKomilo/background-vs-foreground-services-in-android-kotlin-jetpack-compose-726b94983469)
- [Launch a foreground service — Android Developers](https://developer.android.com/develop/background-work/services/fgs/launch)
- [Idioms — Kotlin Docs](https://kotlinlang.org/docs/idioms.html)
- [Sealed classes and interfaces — Kotlin Docs](https://kotlinlang.org/docs/sealed-classes.html)
