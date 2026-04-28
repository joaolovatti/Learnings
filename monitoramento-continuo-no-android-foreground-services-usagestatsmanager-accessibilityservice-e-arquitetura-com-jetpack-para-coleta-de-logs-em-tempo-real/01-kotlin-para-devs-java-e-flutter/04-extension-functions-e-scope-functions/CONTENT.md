# Extension Functions e Scope Functions

![capa](cover.png)

## Sobre este subcapítulo

Este subcapítulo cobre dois mecanismos de Kotlin que reduzem drasticamente o ruído de código nos contextos de serviços Android: extension functions, que adicionam comportamento a classes existentes sem herança, e scope functions, que agrupam operações sobre um objeto em um bloco delimitado. Para o leitor vindo de Java, extension functions eliminam a proliferação de classes utilitárias estáticas (`ContextUtils.hasPermission(context, ...)`) — em Kotlin, esse helper vira `fun Context.hasPermission(permission: String)`. Para o leitor vindo de Flutter/Dart, a analogia é com extension methods introduzidos no Dart 2.7, mas com o adicional das scope functions que não têm equivalente direto em Dart.

Aparece aqui porque os capítulos de serviços e de verificação de permissões usam esses patterns intensamente: `apply` para construir `NotificationCompat.Builder`, `let` para código condicional sobre resultado nullable de `getSystemService`, `also` para logging de side effect em coleta de eventos. O leitor precisa reconhecer cada scope function pelo seu tipo de retorno e pelo receiver esperado antes de ler esses contextos.

## Estrutura

Os grandes blocos são: (1) extension functions — sintaxe de declaração, o `this` implícito como receiver, extension functions em classes de sistema Android (`Context`, `Intent`, `SharedPreferences`), e a regra de quando preferi-las a um helper estático; (2) `let` — execução condicional sobre não-null, o `it` implícito, encadeamento com `?.let {}` como substituto de null-check em Java, e o caso de uso clássico de `getSystemService()?.let { ... }`; (3) `also` — side effects sem interromper a cadeia (logging, debug, registro em lista), diferença semântica em relação a `let` (retorna o receiver, não o resultado do bloco); (4) `apply` — setup de objetos mutáveis com `this` implícito, uso canônico para configurar `NotificationCompat.Builder` e `Intent`, diferença de `apply` para `with` (receiver explícito vs chamada em objeto já existente); (5) `run` e `with` — `run` como combinação de `let` e `apply` (executa bloco sobre receiver, retorna resultado), `with` para agrupar múltiplas operações sobre um objeto sem encadeamento.

## Objetivo

Ao terminar este subcapítulo, o leitor conseguirá escrever extension functions para encapsular verificações de permissão de `Context`, usar `apply` para montar notificações de Foreground Service sem variáveis intermediárias, e escolher entre `let`, `also`, `apply`, `run` e `with` com base no tipo de retorno esperado e na fonte do receiver. O código de setup de serviços e de permissões no restante do livro vai se tornar imediatamente legível.

## Fontes utilizadas

- [Idioms — Kotlin Docs](https://kotlinlang.org/docs/idioms.html)
- [Scope Functions — Kotlin Docs](https://kotlinlang.org/docs/scope-functions.html)
- [Kotlin Scope Functions in Android Development: Practical Examples — Medium](https://medium.com/@aslam.iit.ju41/kotlin-scope-functions-in-android-development-practical-examples-35ebbb3759a2)
- [Kotlin Apply and other Kotlin Scope Functions — Bugfender](https://bugfender.com/blog/kotlin-apply-and-kotlin-scope-functions/)
- [Kotlin Scope Functions: Guide on When to Use Them — BigKnol](https://bigknol.com/kotlin/kotlin-scope-functions-guide-on-when-to-use-them/)
- [Kotlin for Java developers — JetBrains / Kotlin Docs](https://kotlinlang.org/docs/comparison-to-java.html)
