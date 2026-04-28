# Null Safety na Prática

![capa](cover.png)

## Sobre este subcapítulo

Este subcapítulo fecha o vocabulário de Kotlin aplicado ao ponto de maior fricção para devs Java migrando para o ecossistema: a interoperabilidade de null safety com as APIs de sistema Android que foram escritas em Java e retornam `null` em situações variadas. Para o leitor Java, `NullPointerException` em runtime é o inimigo histórico — Kotlin elimina essa classe de bug movendo a responsabilidade para o compilador, mas apenas quando as chamadas cruzam a fronteira Kotlin-Java com os operadores certos. Para o leitor Flutter/Dart, o sistema de null safety (introduzido no Dart 2.12) é análogo, mas a interoperabilidade com bibliotecas Java do Android adiciona uma camada que Dart não tem.

O recorte cobre especificamente os padrões que aparecem nas chamadas às APIs de sistema do livro: `getSystemService()` que retorna `Any?` (Java `Object`), `queryUsageStats()` que pode retornar `null` ou lista vazia, campos de `UsageEvents.Event` opcionais, e `packageName` que pode ser `null` em eventos de acessibilidade. O subcapítulo é propositalmente aplicado — não é uma enumeração completa de null safety em Kotlin, mas a cobertura dos casos que o leitor vai enfrentar nos próximos capítulos.

## Estrutura

Os grandes blocos são: (1) o type system nullable vs non-nullable — `String` vs `String?`, como o compilador impede dereferência unsafe, e a plataforma type (`String!`) de código Java que abre a brecha de runtime; (2) `?.` e `?:` — safe call como substituto do null-check explícito em Java, Elvis operator como fallback compacto, encadeamento de safe calls e o ponto em que a cadeia retorna `null` silenciosamente; (3) `!!` e quando não usar — o non-null assertion como conversão explícita que relança `NullPointerException` se `null`, o único caso justificável (você tem certeza semântica que o compilador não consegue inferir) e a regra de não usar em código de produção de serviço; (4) `requireNotNull` e `checkNotNull` — asserções de contrato que lançam `IllegalArgumentException` / `IllegalStateException` com mensagem descritiva, diferença de `!!` em semântica e em stack trace legível; (5) interoperabilidade com APIs Java — casting seguro com `as?`, tratamento de platform types dos retornos de `getSystemService`, `queryUsageStats` e campos de eventos de acessibilidade, e a estratégia de wrapping em extension functions que encapsulam o tratamento de null.

## Objetivo

Ao terminar este subcapítulo, o leitor conseguirá consumir retornos nullable das APIs `UsageStatsManager` e `AccessibilityService` sem `NullPointerException` em runtime, escrever extension functions em `Context` que encapsulam safe calls para `getSystemService` e retornam tipos não-nullable quando possível, e usar `requireNotNull` como asserção de contrato legível em vez de `!!` em código de inicialização de serviço.

## Fontes utilizadas

- [Null safety — Kotlin Docs](https://kotlinlang.org/docs/null-safety.html)
- [Calling Java code from Kotlin — Kotlin Docs](https://kotlinlang.org/docs/java-interop.html)
- [Kotlin – Using ?. and ?.let {} for Null Safety — Java Code Geeks](https://www.javacodegeeks.com/kotlin-using-and-let-for-null-safety.html)
- [Kotlin Fundamentals: Null Safety — albertlatacz.com](https://www.albertlatacz.com/blog/kotlin-fundamentals-null-safety/)
- [UsageStatsManager — Android Developers](https://developer.android.com/reference/android/app/usage/UsageStatsManager)
- [Idioms — Kotlin Docs](https://kotlinlang.org/docs/idioms.html)
