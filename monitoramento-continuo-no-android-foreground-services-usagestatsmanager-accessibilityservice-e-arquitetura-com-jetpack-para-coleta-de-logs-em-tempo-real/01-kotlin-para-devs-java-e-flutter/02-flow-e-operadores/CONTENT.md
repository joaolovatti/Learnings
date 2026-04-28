# `Flow` e Operadores

![capa](cover.png)

## Sobre este subcapítulo

Este subcapítulo cobre o mecanismo de canal de dados reativo que conecta a camada de coleta de eventos à camada de apresentação no livro todo. `Flow` é o sucessor idiomático do RxJava para devs Java e do `Stream` do Dart para devs Flutter — mas integrado nativamente ao modelo de coroutines, sem dependências externas além do `kotlinx.coroutines`. Aparece nesta posição imediatamente após coroutines porque `Flow` é construído sobre `suspend fun` e `CoroutineScope`: entender coroutines primeiro torna a semântica de `collect` natural em vez de mágica.

O recorte é restrito ao conjunto de operadores que aparecem nos capítulos de coleta e de pipeline reativo: criadores com `flow {}`, operadores de transformação (`map`, `filter`, `onEach`), controle de backpressure com `conflate`, e a distinção fundamental entre `Flow` frio (começa a produzir só quando há coletor) e `StateFlow`/`SharedFlow` quentes (produzem independente de coletor e são a forma de compartilhar estado entre serviço e ViewModel).

## Estrutura

Os grandes blocos são: (1) `flow {}` e o modelo cold — como o builder cria um produtor que só executa quando há coletor, o papel de `emit`, e por que `Flow` não é um `Observable` do RxJava; (2) `collect` e o contexto de coleta — onde e como consumir um `Flow`, `launchIn` como atalho para coletar dentro de um escopo, e o erro clássico de coletar na main thread sem `flowOn`; (3) operadores de transformação — `map` e `filter` para transformar e filtrar valores, `onEach` para side effects sem quebrar a cadeia, `take` e `drop` para janelas de dados; (4) `conflate` e backpressure — o que acontece quando o produtor é mais rápido que o coletor, `conflate` vs `buffer`, e quando cada estratégia cabe no contexto de eventos de uso de apps; (5) `StateFlow` e `SharedFlow` — temperatura quente, valor inicial obrigatório no `StateFlow`, `replay` no `SharedFlow`, e como expor estado de um serviço Android para o ViewModel via `StateFlow`.

## Objetivo

Ao terminar este subcapítulo, o leitor conseguirá criar um `Flow` de eventos de sistema dentro de um service, aplicar operadores para filtrar e transformar eventos antes de persistir no Room, e expor o resultado como `StateFlow` que o ViewModel coleta respeitando o ciclo de vida. A distinção entre `Flow` frio e quente estará clara o suficiente para o leitor escolher o tipo certo sem consultar documentação no restante do livro.

## Fontes utilizadas

- [Kotlin flows on Android — Android Developers](https://developer.android.com/kotlin/flow)
- [StateFlow and SharedFlow — Android Developers](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [SharedFlow and StateFlow — kt.academy](https://kt.academy/article/cc-sharedflow-stateflow)
- [Kotlin Coroutines and Flow for Android Development — Udemy](https://www.udemy.com/course/coroutines-on-android/)
- [RxJava to Kotlin Coroutines: The Ultimate Migration Guide — ITNEXT](https://itnext.io/rxjava-to-kotlin-coroutines-the-ultimate-migration-guide-d41d782f9803)
- [Mastering State Management in Android with Kotlin Flow — Medium](https://medium.com/@hhhhghhghu/mastering-state-management-in-android-with-kotlin-flow-74f69b6be7dd)
