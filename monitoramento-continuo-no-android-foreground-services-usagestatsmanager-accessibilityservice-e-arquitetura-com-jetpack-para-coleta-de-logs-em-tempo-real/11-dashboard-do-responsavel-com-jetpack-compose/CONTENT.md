# Dashboard do Responsável com Jetpack Compose

![capa](cover.png)

## Sobre este capítulo

O responsável precisa de uma interface para consumir os logs coletados: ver o tempo de uso de cada app, navegar pelo histórico de eventos do dia, e entender padrões de uso ao longo da semana. Este capítulo implementa o dashboard do responsável em Jetpack Compose, conectado ao pipeline reativo do capítulo anterior. O recorte foca nos Composables específicos do caso de uso — lista de apps com tempo de uso, timeline de eventos, filtro por data — e em como integrar `StateFlow` do ViewModel de forma segura com o ciclo de vida da Activity.

O leitor tem experiência com Flutter, o que significa que o modelo declarativo do Compose é familiar conceitualmente. O capítulo não ensina Compose do zero — presume que o leitor consegue ler e adaptar código Compose — e foca nos padrões de integração específicos: `collectAsStateWithLifecycle`, recomposição eficiente com `key`, lazy loading de listas de eventos e navegação entre telas de resumo e detalhe.

## Estrutura

Os grandes blocos são: (1) arquitetura de UI — screen Composables vs stateless components, `UiState` sealed class mapeando os estados (Loading, Success, Error), e como o ViewModel expõe o `StateFlow<UiState>`; (2) `collectAsStateWithLifecycle` — integração com o pipeline de `StateFlow` do ViewModel, por que não usar `collectAsState` sem lifecycle awareness, e `rememberUpdatedState` para callbacks; (3) Composables do dashboard — `AppUsageSummaryCard` com tempo de uso formatado, `EventTimelineList` com `LazyColumn` e `key` estável, `UsageBarChart` com `Canvas` API para o gráfico de barras por app; (4) filtro por data e navegação — `DatePickerDialog` para seleção de janela de tempo, passagem de filtro ao ViewModel, e `NavController` para navegar entre a lista de apps e o detalhe de eventos de um app específico; (5) refresh e estados de loading — `SwipeRefresh` ou `PullToRefresh` do Material3 para trigger manual de sync, `CircularProgressIndicator` no estado de loading e `Snackbar` para feedback de sync concluído.

## Objetivo

Ao terminar este capítulo, o leitor terá implementado o dashboard do responsável em Compose: lista de apps com tempo de uso do dia, timeline de eventos com filtro por data, navegação para detalhe por app e feedback de estado de sync. O dashboard estará conectado ao `StateFlow` do ViewModel e recomporá automaticamente quando novos dados chegarem do backend.

## Fontes utilizadas

- [Jetpack Compose — Android Developers](https://developer.android.com/develop/ui/compose)
- [State and Jetpack Compose — Android Developers](https://developer.android.com/develop/ui/compose/state)
- [Collect flows in a lifecycle-aware manner — Android Developers](https://developer.android.com/kotlin/flow/lifecycle-aware)
- [Navigation in Compose — Android Developers](https://developer.android.com/develop/ui/compose/navigation)
- [LazyColumn — Android Developers](https://developer.android.com/develop/ui/compose/lists)
- [Background vs Foreground Services in Android (Kotlin + Jetpack Compose) — Medium](https://medium.com/@YodgorbekKomilo/background-vs-foreground-services-in-android-kotlin-jetpack-compose-726b94983469)
