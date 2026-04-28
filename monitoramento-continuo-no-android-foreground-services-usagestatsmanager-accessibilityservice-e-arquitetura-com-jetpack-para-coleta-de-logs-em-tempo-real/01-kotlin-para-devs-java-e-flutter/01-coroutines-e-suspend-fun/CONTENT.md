# Coroutines e `suspend fun`

![capa](cover.png)

## Sobre este subcapítulo

Este subcapítulo instala o vocabulário central de execução assíncrona em Kotlin que permeia todo o restante do livro. Para o leitor vindo de Java, coroutines são o substituto direto de `AsyncTask`, `ExecutorService` e callbacks encadeados — mas com a sintaxe sequencial de código síncrono. Para o leitor vindo de Flutter/Dart, a analogia é com `async`/`await` e `Future`, mas com um modelo de escopo estruturado que evita leaks de tarefas em background quando o componente Android é destruído.

O recorte cobre exatamente o que aparece na implementação de Foreground Services e na coleta de eventos: como criar e delimitar um escopo de coroutine, como lançar tarefas com `launch` e `async`, como mudar de dispatcher para executar I/O sem bloquear a thread principal, como cancelar coroutines cooperativamente e como proteger escopos com `SupervisorJob` para que a falha de uma tarefa não derrube as irmãs.

## Estrutura

Os grandes blocos são: (1) `CoroutineScope` e structured concurrency — o que é um escopo, como ele delimita o tempo de vida das coroutines filhas, e por que `GlobalScope` é perigoso em serviços Android; (2) `launch` vs `async`/`await` — cuándo retornar `Job` vs `Deferred<T>`, composição de resultados e erros em tarefas paralelas; (3) `withContext` e `Dispatchers` — `Dispatchers.IO` para leituras de banco e chamadas de rede, `Dispatchers.Main` para atualizar UI, `Dispatchers.Default` para CPU intensivo, e o custo de troca de contexto; (4) cancelamento cooperativo — `isActive`, `ensureActive()`, uso de `delay()` como ponto de cancelamento e comportamento de `finally` em coroutines canceladas; (5) `SupervisorJob` — diferença entre `Job` e `SupervisorJob` na propagação de exceção, `CoroutineExceptionHandler` e quando cada um cabe num serviço de longa execução.

## Objetivo

Ao terminar este subcapítulo, o leitor conseguirá declarar um `CoroutineScope` com `SupervisorJob` dentro de um service Android, lançar coroutines de I/O em `Dispatchers.IO` sem bloquear a thread principal, cancelar o escopo no `onDestroy` sem vazar tarefas em background e distinguir quando usar `launch` (disparo sem retorno) de `async` (resultado futuro). Esse repertório é o pressuposto direto dos capítulos de Foreground Service e WorkManager.

## Conceitos

A explicação completa destes conceitos vive em [`CONCEPTS.md`](CONCEPTS.md), construída sequencialmente pela skill `estudo-explicar-conceito`.

1. O mecanismo de suspensão — o que `suspend` faz ao compilar (CPS), por que a thread não bloqueia e como isso difere de threads e de `Future`/`async`-`await` do Dart
2. `CoroutineScope` e structured concurrency — escopo como delimitador do tempo de vida das coroutines filhas, a relação pai-filho entre Jobs e por que `GlobalScope` vaza em serviços Android
3. `launch` vs `async`/`await` — quando retornar `Job` vs `Deferred<T>`, como compor resultados de tarefas paralelas e como exceções se propagam em cada builder
4. `Dispatchers` e `withContext` — `Dispatchers.IO`, `Main` e `Default`, a regra de nunca bloquear a thread principal e o custo de troca de contexto
5. Cancelamento cooperativo — como `isActive`, `ensureActive()` e `delay()` viram pontos de cancelamento, o comportamento de `finally` em coroutines canceladas e por que o cancelamento exige cooperação do código
6. `SupervisorJob` e `CoroutineExceptionHandler` — diferença entre `Job` e `SupervisorJob` na propagação de exceção, isolamento de falhas entre coroutines irmãs e como montar o escopo canônico de um service Android com esses dois elementos

## Fontes utilizadas

- [Kotlin coroutines on Android — Android Developers](https://developer.android.com/kotlin/coroutines)
- [Coroutines guide — Kotlin Docs](https://kotlinlang.org/docs/coroutines-guide.html)
- [Introduction to Coroutines in Kotlin Playground — Android Developers](https://developer.android.com/codelabs/basic-android-kotlin-compose-coroutines-kotlin-playground)
- [Kotlin Coroutines Tutorial for Android: Getting Started — Kodeco](https://www.kodeco.com/37885995-kotlin-coroutines-tutorial-for-android-getting-started)
- [Structured Concurrency — kotlinx.coroutines](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-scope/)
- [The Beginner's Guide to Kotlin Coroutine Internals — DoorDash](https://careersatdoordash.com/blog/the-beginners-guide-to-kotlin-coroutine-internals/)
