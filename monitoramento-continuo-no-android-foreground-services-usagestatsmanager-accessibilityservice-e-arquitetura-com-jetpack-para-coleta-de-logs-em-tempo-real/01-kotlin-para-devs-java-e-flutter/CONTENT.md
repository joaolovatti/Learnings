# Kotlin para Devs Java e Flutter

![capa](cover.png)

## Sobre este capítulo

Este capítulo fecha a lacuna específica do leitor em Kotlin aplicado a contextos de serviços Android. O perfil declarado é de um dev com domínio do ecossistema JVM via Java e do paradigma reativo via Flutter/Dart — o que significa que conceitos como null safety e programação assíncrona não são novidades conceituais, mas a sintaxe e os idioms de Kotlin em serviços Android são. O recorte cobre exatamente o Kotlin necessário para o restante do livro: não é um curso completo da linguagem, mas um mapeamento cirúrgico das construções que aparecem na implementação de Foreground Services, coleta de eventos e arquitetura com Jetpack. Aparece na posição um porque qualquer capítulo seguinte pressupõe esse vocabulário.

Os temas são selecionados pela frequência de aparição nos capítulos posteriores: coroutines e `suspend fun` são o mecanismo central de execução assíncrona nos serviços; `Flow` e `StateFlow` são o canal de dados do pipeline de coleta; `sealed class` e `when` expressivo estruturam os estados do serviço; extension functions aparecem nos helpers de contexto e de permissão; null safety idiomático (`?.`, `?:`, `let`, `also`, `run`) elimina NullPointerExceptions nos retornos das APIs de sistema.

## Estrutura

Os grandes blocos são: (1) coroutines e `suspend` — `CoroutineScope`, `launch`, `async`, `withContext`, `Dispatchers.IO` vs `Dispatchers.Main`, cancelamento cooperativo e `SupervisorJob` como protetor de escopo; (2) `Flow` e operadores — `flow {}`, `collect`, `map`, `filter`, `onEach`, `conflate`, diferença entre `Flow` frio e `StateFlow`/`SharedFlow` quentes; (3) sealed classes e when — modelagem de estados do serviço, hierarquias de eventos e substituição do enum Java por sealed hierarchy com dados acoplados; (4) extension functions e scope functions — `let`, `also`, `apply`, `run`, `with` em contextos reais de setup de notificações e verificação de permissões; (5) null safety na prática — interoperabilidade com APIs Android que retornam `null` em Java, uso de `?:` como fallback e `requireNotNull` como asserção de contrato.

## Objetivo

Ao terminar este capítulo, o leitor conseguirá ler e escrever Kotlin idiomático nos contextos que aparecem nos serviços Android: lançar coroutines dentro de um `LifecycleScope`, coletar um `StateFlow` reagindo a mudanças de estado, modelar o estado de um serviço com sealed classes e navegar a interoperabilidade de null safety com as APIs de sistema Android. Esse vocabulário é o pressuposto silencioso de todos os capítulos seguintes — o leitor não precisará pausar a leitura para consultar referências básicas de Kotlin.

## Subcapítulos

1. [Coroutines e `suspend fun`](01-coroutines-e-suspend-fun/CONTENT.md) — `CoroutineScope`, `launch`, `async`, `withContext`, `Dispatchers`, cancelamento cooperativo e `SupervisorJob`
2. [`Flow` e Operadores](02-flow-e-operadores/CONTENT.md) — `flow {}`, `collect`, `map`, `filter`, `onEach`, `conflate`, e a distinção entre `Flow` frio e `StateFlow`/`SharedFlow` quentes
3. [Sealed Classes e `when` Expressivo](03-sealed-classes-e-when-expressivo/CONTENT.md) — modelagem de estados do serviço e tipos de evento com sealed hierarchies e `when` exaustivo sem `else`
4. [Extension Functions e Scope Functions](04-extension-functions-e-scope-functions/CONTENT.md) — `let`, `also`, `apply`, `run`, `with` em contextos reais de setup de notificações e verificação de permissões
5. [Null Safety na Prática](05-null-safety-na-pratica/CONTENT.md) — interoperabilidade com APIs Android que retornam `null` em Java, `?.`, `?:`, `requireNotNull` e platform types
6. [Kotlin Idiomático em Serviços Android](06-kotlin-idiomatico-em-servicos-android/CONTENT.md) — integração dos quatro blocos num esqueleto completo de `LifecycleService` com `StateFlow` de estado e extension functions de arranque

## Fontes utilizadas

- [Kotlin coroutines on Android — Android Developers](https://developer.android.com/kotlin/coroutines)
- [Kotlin flows on Android — Android Developers](https://developer.android.com/kotlin/flow)
- [Kotlin for Java developers — JetBrains / Kotlin Docs](https://kotlinlang.org/docs/comparison-to-java.html)
- [Idioms — Kotlin Docs](https://kotlinlang.org/docs/idioms.html)
- [Sealed classes and interfaces — Kotlin Docs](https://kotlinlang.org/docs/sealed-classes.html)
- [Background vs Foreground Services in Android (Kotlin + Jetpack Compose) — Medium](https://medium.com/@YodgorbekKomilo/background-vs-foreground-services-in-android-kotlin-jetpack-compose-726b94983469)
