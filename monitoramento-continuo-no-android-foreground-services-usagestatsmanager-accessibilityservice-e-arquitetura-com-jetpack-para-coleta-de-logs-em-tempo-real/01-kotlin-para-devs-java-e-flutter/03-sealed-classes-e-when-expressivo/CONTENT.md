# Sealed Classes e `when` Expressivo

![capa](cover.png)

## Sobre este subcapítulo

Este subcapítulo cobre o substituto idiomático de Kotlin para o pattern de enums com dados que Java não consegue expressar de forma elegante. Para o leitor vindo de Java, a transição natural é: `enum` modela estado sem dados acoplados; `sealed class` modela estado com dados diferentes por variante. Para o leitor vindo de Flutter/Dart, a analogia é com discriminated unions ou com o pattern `sealed` introduzido no Dart 3. Aparece aqui porque os capítulos seguintes usam sealed hierarchies para modelar o estado de serviços (`ServiceState.Running`, `ServiceState.Stopped`, `ServiceState.Error`) e o tipo de evento coletado — e o leitor precisa reconhecer e escrever esse pattern sem hesitação.

O recorte cobre a anatomia completa da sealed hierarchy: `sealed class`, `data class` vs `object` como subtipos, e o `when` exaustivo sem `else` que o compilador garante. Inclui o padrão de modelar hierarquias de evento (tipo, severidade, payload) e a substituição prática de `enum` + `companion object` de Java por sealed hierarchy com dados acoplados.

## Estrutura

Os grandes blocos são: (1) anatomia da `sealed class` — restrição de subtipos no mesmo package, `sealed class` vs `sealed interface` (Kotlin 1.5+), e por que o compilador consegue exigir exaustividade no `when`; (2) subtipos com e sem dados — `data class` como variante com estado (ex: `Error(val message: String, val code: Int)`), `object` como variante singleton (ex: `Loading`), e `data object` introduzido no Kotlin 1.9; (3) `when` exaustivo como expressão — diferença entre `when` como statement e como expressão que retorna valor, eliminação do `else` e o erro de compilação quando uma variante nova é adicionada à sealed sem atualizar os `when`; (4) modelagem de estados de serviço — sealed hierarchy para os estados do Foreground Service (`Idle`, `Collecting`, `Error`), sealed hierarchy para tipos de evento (`AppForeground`, `AppBackground`, `NotificationPosted`); (5) substituição do enum Java — mapeamento explícito de `enum` com campo adicional em Java para `sealed class` com `data class`, e quando manter `enum` (conjuntos fechados sem dados extras).

## Objetivo

Ao terminar este subcapítulo, o leitor conseguirá definir uma sealed hierarchy para estados de serviço e para tipos de evento, consumir essas hierarquias com `when` exaustivo sem `else`, e reconhecer imediatamente nos capítulos seguintes os padrões de sealed class sem precisar pausar para consultar referência. O compilador passa a ser aliado: qualquer nova variante de estado não tratada vira erro em tempo de compilação.

## Fontes utilizadas

- [Sealed classes and interfaces — Kotlin Docs](https://kotlinlang.org/docs/sealed-classes.html)
- [How to Use Sealed Classes for Type-Safe State in Kotlin — oneuptime](https://oneuptime.com/blog/post/2026-02-02-kotlin-sealed-classes-state/view)
- [Stateful Data on Android with sealed classes and Kotlin Flow — Medium](https://naingaungluu.medium.com/stateful-data-on-android-with-sealed-classes-and-kotlin-flow-33e2537ccf55)
- [Kotlin for Java developers — JetBrains / Kotlin Docs](https://kotlinlang.org/docs/comparison-to-java.html)
- [How to Migrate from Java to Kotlin: Best Practices — codezup](https://codezup.com/migrate-java-to-kotlin-android-best-practices/)
