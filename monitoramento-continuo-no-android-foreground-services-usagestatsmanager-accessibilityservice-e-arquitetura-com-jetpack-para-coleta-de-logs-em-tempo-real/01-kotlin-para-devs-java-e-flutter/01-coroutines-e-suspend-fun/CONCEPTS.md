# Conceitos: Coroutines e `suspend fun`

> _Aula contínua dos conceitos atômicos deste subcapítulo. Cada conceito vira uma seção `## N.` (ou `## 0N.` quando o roteiro tem 10+ conceitos) preenchida em sequência pela skill `estudo-explicar-conceito`. Cada nova iteração lê o que já foi escrito e dá continuidade — sem repetir vocabulário, sem reapresentar exemplos, sem saltos de tom._

## Roteiro

1. O mecanismo de suspensão — o que `suspend` faz ao compilar (CPS), por que a thread não bloqueia e como isso difere de threads e de `Future`/`async`-`await` do Dart
2. `CoroutineScope` e structured concurrency — escopo como delimitador do tempo de vida das coroutines filhas, a relação pai-filho entre Jobs e por que `GlobalScope` vaza em serviços Android
3. `launch` vs `async`/`await` — quando retornar `Job` vs `Deferred<T>`, como compor resultados de tarefas paralelas e como exceções se propagam em cada builder
4. `Dispatchers` e `withContext` — `Dispatchers.IO`, `Main` e `Default`, a regra de nunca bloquear a thread principal e o custo de troca de contexto
5. Cancelamento cooperativo — como `isActive`, `ensureActive()` e `delay()` viram pontos de cancelamento, o comportamento de `finally` em coroutines canceladas e por que o cancelamento exige cooperação do código
6. `SupervisorJob` e `CoroutineExceptionHandler` — diferença entre `Job` e `SupervisorJob` na propagação de exceção, isolamento de falhas entre coroutines irmãs e como montar o escopo canônico de um service Android com esses dois elementos

<!-- ROTEIRO-END -->

<!-- PENDENTE-START -->
> _Pendente: 6 / 6 conceitos preenchidos._
<!-- PENDENTE-END -->

<!-- AULAS-START -->
## 1. O mecanismo de suspensão — o que `suspend` faz ao compilar (CPS), por que a thread não bloqueia e como isso difere de threads e de `Future`/`async`-`await` do Dart

O problema central de qualquer código assíncrono é: como esperar o resultado de uma operação demorada (I/O, rede, timer) sem imobilizar a thread enquanto isso? Java resolve com bloqueio de thread — `Future.get()` congela a thread até o resultado aparecer, ou você encadeia callbacks que viram callback hell. Dart resolve com `async`/`await`, que é açúcar sobre `Future` e suspende a `isolate` sintaticamente mas em essência é uma máquina de estados gerada pelo compilador. Kotlin faz a mesma geração de máquina de estados, mas o mecanismo e os contratos de cancelamento são diferentes — e entender essa diferença é o que separa usar coroutines de entendê-las o suficiente para depurá-las num service Android.

A palavra-chave `suspend` não é uma instrução de runtime: ela é uma anotação ao compilador. Quando o compilador Kotlin encontra uma `suspend fun`, aplica a transformação de **Continuation Passing Style (CPS)**: injeta um parâmetro extra do tipo `Continuation<T>` na assinatura e altera o tipo de retorno para `Any?`. O que era `suspend fun fetchData(): String` vira, no bytecode, algo equivalente a `fun fetchData(continuation: Continuation<String>): Any?`. O retorno `Any?` existe porque a função pode retornar ou o valor real `String`, ou a sentinela especial `COROUTINE_SUSPENDED` — um objeto singleton que sinaliza "ainda não tenho resultado, vou chamar o continuation quando tiver".

O compilador também reescreve o **corpo** da função como uma máquina de estados. Cada chamada a outra `suspend fun` dentro do corpo cria um ponto de suspensão; o compilador numera esses pontos com um campo `label` e converte o fluxo linear em um bloco `when (label)`. Antes de cada ponto de suspensão, as variáveis locais relevantes são salvas no objeto `Continuation` — que funciona como a pilha de chamadas serializada. Quando a função é retomada (alguém chama `continuation.resumeWith(result)`), o `when` despacha para o `label` correto e restaura as variáveis do `Continuation`, continuando do ponto exato onde parou.

```kotlin
// Código fonte (o que você escreve)
suspend fun loadAndProcess(): String {
    val raw = fetchFromNetwork()   // ponto de suspensão 1
    val parsed = parseJson(raw)    // ponto de suspensão 2
    return parsed
}

// Estrutura gerada pelo compilador (pseudocódigo simplificado)
fun loadAndProcess(continuation: Continuation<String>): Any? {
    val state = continuation as? LoadAndProcessState ?: LoadAndProcessState(continuation)
    when (state.label) {
        0 -> {
            state.label = 1
            val result = fetchFromNetwork(state)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            state.raw = result as String
            // cai no case 1 imediatamente se fetchFromNetwork não suspendeu
        }
        1 -> {
            state.raw = state.result as String
            state.label = 2
            val result = parseJson(state.raw, state)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            state.parsed = result as String
        }
        2 -> {
            return state.parsed as String
        }
    }
    error("unreachable")
}
```

O não-bloqueio de thread acontece exatamente aqui: quando `fetchFromNetwork` precisa aguardar I/O, ela devolve `COROUTINE_SUSPENDED` — essa sentinela sobe pela cadeia de chamadas até o loop de eventos do dispatcher, que simplesmente retorna o controle da thread. A thread não fica presa em `wait()` nem em `sleep()`: ela fica disponível para processar outras coroutines. Quando o I/O termina, alguma parte do sistema (o runtime da coroutine, o callback do socket, etc.) chama `continuation.resumeWith(Result.success(data))`, que reenfileira a coroutine no dispatcher. Esse mecanismo permite que milhares de coroutines compartilhem um punhado de threads de `Dispatchers.IO` sem cada uma precisar de uma thread própria.

A diferença em relação a threads nuas é de custo e de modelo de escopo. Uma thread Java ocupa ~2 MB de memória de stack (configurável, mas 512 KB a 2 MB é a faixa real), está sujeita a preempção pelo OS e exige sincronização explícita com locks para memória compartilhada. Uma coroutine suspensa ocupa apenas o seu objeto `Continuation` — algumas dezenas a centenas de bytes — e o agendamento é cooperativo: a coroutine cede o controle nos pontos de suspensão, não quando o OS decide. Não existe lock para trocar contexto entre coroutines no mesmo dispatcher.

Com `Future`/`async`-`await` do Dart, a analogia estrutural é forte: ambos transformam código sequencial em máquina de estados, ambos evitam bloqueio de thread. A diferença principal está no **modelo de cancelamento e escopo**: um `Future` Dart não tem cancelamento nativo — uma vez disparado, roda até o fim ou até uma exceção; não existe conceito equivalente ao `Job` que cancela toda uma árvore de coroutines filhas. Coroutines Kotlin têm cancelamento estruturado como contrato de primeira classe, o que é diretamente relevante para serviços Android: quando o `Service` é destruído, o escopo é cancelado e todas as coroutines filhas são canceladas em cascata, sem que o código de cada tarefa precise conhecer o lifecycle do componente. Esse mecanismo de escopo é o que os conceitos `## 2.` a `## 6.` deste subcapítulo constroem sobre.

Com `ExecutorService` e `Future.get()` de Java, a diferença é ainda mais direta: `Future.get()` bloqueia a thread chamadora até o resultado aparecer, consumindo um thread de pool enquanto espera. Em ambientes com dezenas de operações concorrentes (como um service que coleta eventos de múltiplas fontes ao mesmo tempo), threads bloqueadas equivalem a memória e scheduling overhead que coroutines simplesmente não têm.

**Fontes utilizadas:**

- [Coroutines under the hood — kt.academy](https://kt.academy/article/cc-under-the-hood)
- [Coroutines basics — Kotlin Documentation](https://kotlinlang.org/docs/coroutines-basics.html)
- [Kotlin Coroutine Internals: Suspension, Continuation, CPS — Bluue Whale](https://bluuewhale.github.io/posts/kotlin-coroutine-internals/)
- [Futures, cancellation and coroutines — Roman Elizarov / Medium](https://elizarov.medium.com/futures-cancellation-and-coroutines-b5ce9c3ede3a)
- [Kotlin's suspend functions compared to JavaScript's async/await — Joffrey Bion / Medium](https://medium.com/@joffrey.bion/kotlins-suspend-functions-are-not-javascript-s-async-they-are-javascript-s-await-f95aae4b3fd9)
- [How does suspension work in Kotlin coroutines? — kt.academy](https://kt.academy/article/cc-suspension)
## 2. `CoroutineScope` e structured concurrency — escopo como delimitador do tempo de vida das coroutines filhas, a relação pai-filho entre Jobs e por que `GlobalScope` vaza em serviços Android

O mecanismo de suspensão descrito em `## 1.` resolve como uma coroutine pausa e retoma sem bloquear a thread; o que ele não responde é: quem sabe que a coroutine existe, quando ela precisa terminar e o que acontece se ela lançar uma exceção? Sem uma resposta estruturada a essas perguntas, coroutines viram daemons soltos — tarefas em background que o código que as criou perdeu a referência, não consegue cancelar e não consegue aguardar. Structured concurrency é o contrato que evita isso: toda coroutine tem um escopo, e o escopo define o tempo de vida máximo das coroutines que ele contém.

`CoroutineScope` é um objeto que carrega um `CoroutineContext` — a combinação de dispatcher, `Job` e outras informações opcionais de contexto. O `Job` dentro do escopo é o nó pai na árvore de coroutines. Quando você chama `launch { }` ou `async { }` dentro de um escopo, o builder lê o `Job` do escopo no contexto e estabelece o `Job` recém-criado como filho desse pai — sem que o código de chamada precise fazer nada explícito. A hierarquia é automática: cada `launch` aninhado aprofunda a árvore.

```kotlin
val scope = CoroutineScope(Dispatchers.IO + Job())

scope.launch {                          // Job A — filho direto do Job do scope
    launch {                            // Job B — filho de A
        delay(1_000)
        println("B concluiu")
    }
    launch {                            // Job C — filho de A
        delay(2_000)
        println("C concluiu")
    }
    println("A aguardando filhos")
}                                       // A não termina até B e C terminarem
```

Três regras emergem dessa hierarquia. Primeiro, um pai nunca completa enquanto qualquer filho está ativo — a árvore drena de baixo para cima. Segundo, cancelar o pai cancela todos os filhos recursivamente: quando `scope.cancel()` é chamado, todos os `Job`s descendentes recebem o sinal de cancelamento em cascata. Terceiro, se um filho falha com uma exceção não tratada, ele cancela o pai, que por sua vez cancela todos os irmãos — a falha se propaga para cima e depois desce para os lados (este último ponto muda com `SupervisorJob`, tema do `## 6.`).

A relação pai-filho é estabelecida pelo contexto, não pelo escopo léxico. Um detalhe importante: se você passar um `Job()` novo explicitamente como parâmetro de `launch`, o builder usa esse `Job` como pai em vez do `Job` do escopo corrente — desconectando a nova coroutine da hierarquia. O escopo para de ser seu pai e perde a capacidade de cancelá-la ou aguardá-la. Isso quebra silenciosamente a structured concurrency, e é uma das principais fontes de coroutines órfãs.

```kotlin
// Correto: Job filho herdado do escopo
scope.launch {
    delay(1_000)
}

// Errado: Job explícito desconecta da hierarquia do scope
scope.launch(Job()) {          // Job do scope não é mais o pai — scope.cancel() não alcança esta coroutine
    delay(1_000)
}
```

`GlobalScope` é um `CoroutineScope` cujo `Job` não tem pai. Coroutines lançadas nele vivem enquanto o processo Android existir — independentemente de qualquer componente. Em um service Android, isso significa que se você usa `GlobalScope.launch { coletarEventos() }` no `onCreate()` do service e o service é destruído (`onDestroy()` chamado), a coroutine continua rodando. O service pode ser recriado, acumulando uma nova coroutine que faz o mesmo trabalho em paralelo com a anterior. O objeto `Service` destruído, que a coroutine ainda referencia via captura de variáveis ou lambdas, não pode ser coletado pelo GC enquanto a coroutine estiver viva — isso é o vazamento. Em serviços de monitoramento contínuo, onde o service pode ser destruído e recriado pelo OS para liberar memória, esse padrão causa acúmulo progressivo de coroutines e de referências ao service antigo.

O padrão correto para services é criar um `CoroutineScope` vinculado ao ciclo de vida do próprio service: `CoroutineScope(Dispatchers.IO + SupervisorJob())` declarado como propriedade da classe, e `scope.cancel()` chamado no `onDestroy()`. Todas as coroutines lançadas nesse escopo são automaticamente canceladas quando o service morre. A escolha de `SupervisorJob` aqui, em vez do `Job` simples, é o que impede que a falha de uma coroutine de coleta (por exemplo, uma exceção ao ler `UsageStatsManager`) derrube as coroutines irmãs que estão fazendo outras tarefas — isso é detalhado em `## 6.`.

```kotlin
class MonitorService : Service() {
    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        serviceScope.launch { coletarEventosDeUso() }
        serviceScope.launch { sincronizarComBackend() }
        return START_STICKY
    }

    override fun onDestroy() {
        serviceScope.cancel()           // cancela todas as coroutines filhas — sem vazamento
        super.onDestroy()
    }
}
```

A distinção entre `CoroutineScope(Job())` e `CoroutineScope(SupervisorJob())` impacta o comportamento quando uma das coroutines filhas lança uma exceção. Com `Job` simples, a exceção cancela o pai e, por consequência, todas as irmãs — um único evento inesperado derruba todo o escopo. Com `SupervisorJob`, a falha de um filho não escala para o pai: as irmãs continuam. Para um service que coleta dados de múltiplas fontes independentes, `SupervisorJob` é a escolha natural; para pipelines onde a falha de qualquer etapa invalida as demais, `Job` simples faz sentido. Voltaremos a esse trade-off com detalhamento mecânico em `## 6.`, quando o `CoroutineExceptionHandler` entrar na equação.

**Fontes utilizadas:**

- [Job and children awaiting in Kotlin Coroutines — kt.academy](https://kt.academy/article/cc-job)
- [Coroutines basics — Kotlin Documentation](https://kotlinlang.org/docs/coroutines-basics.html)
- [Cancellation and timeouts — Kotlin Documentation](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [Use Kotlin coroutines with lifecycle-aware components — Android Developers](https://developer.android.com/topic/libraries/architecture/coroutines)
- [GlobalScope.launch in Activity — It's not good. You can get memory leak. — Medium](https://medium.com/@startandroid/globalscope-launch-in-activity-its-not-good-you-can-get-memory-leak-62a2300044e8)
- [Understanding supervisorScope, SupervisorJob, coroutineScope, and Job in Kotlin — Medium](https://medium.com/@adityamishra2217/understanding-supervisorscope-supervisorjob-coroutinescope-and-job-in-kotlin-a-deep-dive-into-bcd0b80f8c6f)
## 3. `launch` vs `async`/`await` — quando retornar `Job` vs `Deferred<T>`, como compor resultados de tarefas paralelas e como exceções se propagam em cada builder

O escopo descrito em `## 2.` delimita o tempo de vida das coroutines; o que o escopo não decide é se a tarefa precisa de um resultado de volta. Essa é a divisão central entre `launch` e `async`: `launch` é disparo sem retorno de valor — o chamador obtém um `Job` que representa a coroutine mas não carrega dados —, enquanto `async` é decomposição paralela com resultado — o chamador obtém um `Deferred<T>`, que é um futuro não-bloqueante. `Deferred<T>` implementa `Job` e adiciona `await()`, a função suspensa que retoma a coroutine chamadora com o valor produzido (ou relança a exceção, se houver).

A escolha entre os dois não é arbitrária nem estética — ela segue o contrato de uso. `launch` se encaixa onde o trabalho é um efeito colateral: escrever num banco, enviar um evento para um canal, disparar uma sincronização com backend. O chamador não precisa esperar o resultado; ele só precisa que o trabalho aconteça dentro do escopo correto. `async` se encaixa onde o trabalho produz um valor que o chamador precisa consumir: buscar dados de duas fontes em paralelo e combiná-los, carregar configurações de dois endpoints antes de montar um estado inicial. Se você usar `launch` nesses casos, o único jeito de obter o resultado é via mecanismos externos (canal, `StateFlow`, variável compartilhada) — o que é mais código e mais superfície para race condition.

```kotlin
// Caso launch — efeito colateral, sem retorno de valor
serviceScope.launch(Dispatchers.IO) {
    room.eventoDao().inserir(evento)
}

// Caso async — resultado necessário; as duas buscas rodam em paralelo
suspend fun carregarEstadoInicial(): EstadoInicial = coroutineScope {
    val config   = async { configRepository.buscar() }
    val historico = async { eventoRepository.buscarUltimos(50) }
    EstadoInicial(config.await(), historico.await())
}
```

No segundo trecho, `coroutineScope { }` cria um escopo filho do escopo corrente. Os dois `async` dentro dele são lançados imediatamente e rodam em paralelo no `Dispatchers.IO` herdado. A função só retorna quando ambos os `await()` resolverem — se qualquer um falhar, o outro é cancelado e a exceção sobe para quem chamou `carregarEstadoInicial`. Esse padrão é o que a documentação oficial chama de parallel decomposition com structured concurrency: a composição paralela está delimitada pelo `coroutineScope`, de modo que nenhuma coroutine filha escapa do tempo de vida do bloco.

Uma alternativa para coletar múltiplos `Deferred` de uma lista é `awaitAll()`. Ele é diferente de chamar `await()` em sequência com `map`:

```kotlin
val deferred = listOf(
    async { buscarDadosA() },
    async { buscarDadosB() },
    async { buscarDadosC() }
)
val resultados = deferred.awaitAll()          // falha imediatamente ao primeiro erro
// vs:
val resultados = deferred.map { it.await() } // falha só ao chegar na posição que errou
```

`awaitAll` falha no instante em que qualquer `Deferred` da lista completa com exceção — sem esperar os outros. `map { it.await() }` processa em ordem e só descobre a falha quando a iteração chega ao item problemático, ou seja, os anteriores na lista já esperaram. Para um service que coleta de N fontes ao mesmo tempo, `awaitAll` é a escolha mais responsiva.

A diferença mais crítica entre `launch` e `async` está na **propagação de exceção**, e ela é assimétrica. Uma coroutine lançada com `launch` que lança uma exceção não tratada cancela o pai imediatamente — a exceção sobe pela hierarquia de `Job`s sem passar pelo código de quem chamou o `launch`. O único ponto de interceptação é um `CoroutineExceptionHandler` instalado no escopo. Com `async`, o comportamento depende de ser raiz ou filho:

- **`async` raiz** (lançado diretamente num `GlobalScope` ou similar): a exceção é capturada e armazenada no `Deferred`. Ela só é relançada quando `await()` for chamado — e o `CoroutineExceptionHandler` não tem efeito sobre ela.
- **`async` filho** (lançado dentro de `coroutineScope` ou de outro escopo pai): a exceção ainda propaga para o pai assim que a coroutine falha, sem esperar o `await()`. O fato de ser `async` não suspende a propagação para cima — o que muda é que o `Deferred` também armazena a exceção para quem chamar `await()`.

```kotlin
// Armadilha clássica: async filho propaga mesmo sem await()
serviceScope.launch {
    val d = async {
        throw RuntimeException("falha na coleta")
    }
    delay(500)       // a exceção já propagou para serviceScope antes de chegar aqui
    d.await()        // este ponto pode nunca ser atingido
}
```

O resultado prático para um service de monitoramento: use `launch` para tarefas de escrita ou disparo que não retornam valor e que precisam que uma falha cancele o escopo (ou seja absorvida por `SupervisorJob`, assunto de `## 6.`). Use `async` dentro de `coroutineScope` quando precisar agregar resultados de tarefas independentes numa única operação suspensa. Não use `async` como substituto de `launch` esperando que as exceções fiquem "enclausuradas" no `Deferred` — em contextos filho, elas escapam antes do `await()`.

**Fontes utilizadas:**

- [Composing suspending functions — Kotlin Documentation](https://kotlinlang.org/docs/composing-suspending-functions.html)
- [Coroutine exceptions handling — Kotlin Documentation](https://kotlinlang.org/docs/exception-handling.html)
- [async — kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/async.html)
- [awaitAll — kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/await-all.html)
- [Exception handling in Kotlin Coroutines — kt.academy](https://kt.academy/article/cc-exception-handling)
- [Improve app performance with Kotlin coroutines — Android Developers](https://developer.android.com/kotlin/coroutines/coroutines-adv)
## 4. `Dispatchers` e `withContext` — `Dispatchers.IO`, `Main` e `Default`, a regra de nunca bloquear a thread principal e o custo de troca de contexto

Os conceitos anteriores estabeleceram como uma coroutine suspende (`## 1.`), dentro de qual escopo ela existe (`## 2.`) e qual builder usa (`## 3.`). O que ainda não foi decidido é: em qual thread a coroutine efetivamente roda? Um `launch` sem contexto de dispatcher herda o dispatcher do escopo pai — e dependendo do que estiver nesse escopo, pode acabar rodando na thread principal, o que é exatamente o problema que dispatchers resolvem.

Um `CoroutineDispatcher` é o elemento do `CoroutineContext` responsável por decidir em qual thread (ou pool de threads) uma coroutine executa. O dispatcher intercepta a continuação antes de cada resume e enfileira o bloco de código no pool correto. Sem dispatcher, um `runBlocking` ou um scope sem contexto explícito pode rodar diretamente na thread que criou o scope — perigoso em Android, onde a thread principal tem responsabilidade exclusiva de renderização e eventos de toque.

Os três dispatchers canônicos têm propósitos e pools distintos:

| Dispatcher | Pool | Tamanho do pool | Caso de uso |
|---|---|---|---|
| `Dispatchers.Main` | Thread principal (Looper) | 1 (a main thread) | Atualizar UI, `LiveData`, chamar funções `@MainThread` |
| `Dispatchers.Default` | Pool compartilhado | `max(2, num_cores)` | CPU intensivo: sort de listas, parsing, compressão |
| `Dispatchers.IO` | Pool compartilhado (limite estendido) | `max(64, num_cores)` | Leitura/escrita de arquivo, JDBC, chamadas de rede bloqueantes |

O dado contra-intuitivo da tabela é que `Dispatchers.Default` e `Dispatchers.IO` **compartilham o mesmo pool físico de threads** — não são dois pools separados. O que muda é qual limite ativo a thread conta para: uma thread rodando código de `Dispatchers.IO` conta para o limite de 64, e a mesma thread rodando código de `Dispatchers.Default` conta para o limite de cores. Isso tem uma consequência direta para `withContext`: quando uma coroutine troca de `Dispatchers.Default` para `Dispatchers.IO`, o runtime frequentemente reutiliza a mesma thread, apenas mudando a "lotação" contabilizada — o que elimina o custo de troca real de thread na maioria dos casos.

`withContext` é a função suspensa que troca o dispatcher de uma coroutine pelo tempo de um bloco:

```kotlin
// Exemplo típico num service de coleta: I/O em IO, resultado processado no Default
suspend fun carregarEventos(): List<Evento> = withContext(Dispatchers.IO) {
    // bloco roda em thread do pool IO — leitura de banco ou arquivo
    room.eventoDao().buscarTodos()
}

suspend fun calcularEstatisticas(eventos: List<Evento>): Estatisticas =
    withContext(Dispatchers.Default) {
        // bloco roda em thread do pool Default — processamento CPU
        eventos.groupBy { it.pacote }.mapValues { it.value.size }
            .let { Estatisticas(it) }
    }
```

Quando `withContext` é chamado com um dispatcher diferente do contexto corrente, o runtime suspende a coroutine, enfileira o bloco no novo dispatcher e, quando o bloco termina, reenfileira a retomada no dispatcher original. Cada transição de dispatcher diferente que envolve threads fisicamente distintas tem um custo real: o `Continuation` precisa ser colocado na fila do scheduler do novo pool, o que envolve um `park`/`unpark` de thread ou enfileiramento de tarefa — operações na faixa de microssegundos, mas que se multiplicam quando `withContext` é chamado em loop apertado.

A regra prática de uso emerge diretamente dos propósitos dos pools. `Dispatchers.Main` existe para garantir acesso à UI thread — qualquer operação que toca `View`, `LiveData.setValue()` ou `Composable` em recomposição precisa estar no `Main`. Em serviços de monitoramento sem UI própria, `Dispatchers.Main` raramente aparece no código de coleta, mas aparece ao emitir para um `StateFlow` que um `ViewModel` observa. `Dispatchers.Default` cobre tudo que é CPU: agrupar eventos por pacote, serializar JSON, calcular durações de uso. `Dispatchers.IO` cobre tudo que bloqueia thread à espera de I/O externo: `Room` (mesmo usando `suspend` com Room, internamente o I/O é bloqueante no nível do SQLite), `Retrofit` com OkHttp em modo síncrono, leitura de `/proc/`, chamadas a `UsageStatsManager.queryUsageStats()`.

```kotlin
// Padrão no service de monitoramento: scope em IO, troca para Default quando precisar
class MonitorService : Service() {
    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        serviceScope.launch {
            // já em Dispatchers.IO — busca bloqueante no banco
            val eventos = room.eventoDao().buscarNaoSincronizados()

            // troca para Default para processamento CPU
            val payload = withContext(Dispatchers.Default) {
                serializarParaJson(eventos)
            }

            // volta ao IO para a chamada de rede
            apiService.enviarLote(payload)
        }
        return START_STICKY
    }
}
```

No trecho acima, a coroutine nasce em `Dispatchers.IO` (herdado do `serviceScope`), comuta para `Dispatchers.Default` apenas no bloco de serialização e retorna automaticamente ao `IO` após o `withContext`. As duas transições `IO → Default` e `Default → IO` provavelmente reutilizam a mesma thread física do pool compartilhado — o custo é a contabilidade de limite, não um wake-up de thread nova.

O erro mais comum com dispatchers em serviços Android é usar `Dispatchers.Main` no scope do service, o que força todo o código de I/O a chamar `withContext(Dispatchers.IO)` em cada operação, ou pior, omitir o `withContext` e bloquear a thread principal com `queryUsageStats()` — o que causa ANR (Application Not Responding) detectado pelo Watchdog do Android em operações que excedem 5 segundos no main thread. O padrão seguro é criar o scope do service em `Dispatchers.IO` e trocar para `Dispatchers.Default` somente quando o bloco for genuinamente CPU-intensivo — o que no context de coleta de logs raramente acontece fora da serialização de payloads grandes.

O mecanismo de cancelamento cooperativo — como `isActive`, `ensureActive()` e `delay()` viram pontos de cancelamento dentro de qualquer dispatcher — é o tema de `## 5.`, que completa o modelo de execução antes de introduzir `SupervisorJob` em `## 6.`.

**Fontes utilizadas:**

- [Coroutine context and dispatchers — Kotlin Documentation](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [Kotlin Coroutines dispatchers — kt.academy](https://kt.academy/article/cc-dispatchers)
- [IO — kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-dispatchers/-i-o.html)
- [withContext — kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-context.html)
- [Improve app performance with Kotlin coroutines — Android Developers](https://developer.android.com/kotlin/coroutines/coroutines-adv)
- [IO and Default Dispatchers in Kotlin Coroutines — Baeldung on Kotlin](https://www.baeldung.com/kotlin/io-and-default-dispatcher)

## 5. Cancelamento cooperativo — como `isActive`, `ensureActive()` e `delay()` viram pontos de cancelamento, o comportamento de `finally` em coroutines canceladas e por que o cancelamento exige cooperação do código

O modelo de dispatchers do `## 4.` garante que a coroutine rode na thread certa; ele não garante que a coroutine pare quando o escopo for cancelado. Um `scope.cancel()` chama `Job.cancel()` no `Job` raiz, que transita esse `Job` para o estado `Cancelling` e propaga o sinal recursivamente para todos os `Job`s filhos. O que acontece depois depende de cada coroutine individualmente: se o código não cooperar, o sinal fica pendente indefinidamente e a coroutine continua executando até o fim natural.

A razão de o cancelamento ser cooperativo está na transformação CPS descrita em `## 1.`. O runtime injeta a verificação de cancelamento no momento em que uma coroutine é retomada depois de suspender — ou seja, **nos pontos de suspensão**. Toda função `suspend` das `kotlinx.coroutines` (incluindo `delay`, `withContext`, `await`, `collect`, leituras via Room DAO com `suspend`) é implementada usando `suspendCancellableCoroutine` internamente. Esse mecanismo registra um handler de cancelamento no `CancellableContinuation`; quando `Job.cancel()` é chamado enquanto a coroutine está suspensa ali, o handler resume a coroutine imediatamente com `CancellationException` — sem precisar esperar o I/O terminar. Se o `Job` já estava cancelado antes de `suspendCancellableCoroutine` ser chamado, a exceção é lançada antes mesmo de suspender (a chamada prompt cancellation guarantee).

O problema aparece quando o corpo da coroutine tem computação contínua sem nenhuma chamada `suspend`:

```kotlin
// Esta coroutine ignora o cancelamento enquanto o loop rodar
serviceScope.launch {
    while (true) {
        val eventos = calcularEstatisticas(buffer)   // CPU puro, sem suspend
        salvarEmMemoria(eventos)
    }
}
```

`scope.cancel()` marca o `Job` como `Cancelling`, mas a coroutine nunca encontra um ponto de suspensão para checar — ela executa indefinidamente até o processo morrer. Para código assim, existem duas ferramentas:

**`isActive`** — propriedade booleana do `CoroutineScope` e do `CoroutineContext` que retorna `false` quando o `Job` está em estado `Cancelling` ou `Cancelled`. Usada em condicionais ou como guarda de laço:

```kotlin
serviceScope.launch {
    while (isActive) {                        // sai do laço quando o escopo for cancelado
        val eventos = calcularEstatisticas(buffer)
        salvarEmMemoria(eventos)
    }
    // execução chega aqui normalmente — sem CancellationException
}
```

**`ensureActive()`** — função suspensa que lança `CancellationException` se o `Job` não estiver ativo. É a forma compacta de `if (!isActive) throw CancellationException()`, mas com diagnóstico mais preciso na stack trace. Adequada para pontos de checagem no meio de uma sequência de operações:

```kotlin
serviceScope.launch {
    for (pacote in pacotesMonitorados) {
        ensureActive()                        // lança se cancelado, interrompendo o for
        val stats = queryUsageStatsBlocking(pacote)
        processarStats(stats)
    }
}
```

A diferença prática entre os dois: `isActive` devolve o controle ao chamador de forma suave (o código decide o que fazer quando `false`), enquanto `ensureActive()` interrompe abruptamente via exceção — o fluxo de execução não continua além do ponto de checagem. `delay(0)` também funciona como ponto de cancelamento mínimo em laços apertados (causa uma suspensão nominal que dispara a verificação), mas tem um custo ligeiramente maior que `ensureActive()` porque pode acionar redispatching.

Qualquer coroutine cancelada por qualquer um desses mecanismos recebe `CancellationException`. O runtime trata essa exceção de forma especial: ela não escala para o pai como uma exceção comum faria (o comportamento de escalada descrito no `## 3.`), porque o cancelamento é intencional — seria errado derrubar o escopo inteiro toda vez que um filho é cancelado cooperativamente. A `CancellationException` encerra a coroutine atual e notifica o pai de que ela completou com cancelamento, não com falha.

O bloco `finally` é executado de forma garantida quando uma coroutine é cancelada, tanto por `CancellationException` via ponto de suspensão quanto por `isActive`/`ensureActive()`. Ele é o lugar correto para liberar recursos: fechar cursors, cancelar jobs filhos manualmente, emitir eventos de limpeza. A armadilha é tentar chamar uma função `suspend` dentro do `finally` quando a coroutine já está em estado `Cancelling`:

```kotlin
serviceScope.launch {
    try {
        coletarContinuamente()
    } finally {
        // ERRADO: delay() verifica isActive e lança CancellationException imediatamente
        // porque o Job já está Cancelling — o finally é abortado no meio
        delay(100)
        notificarBackend("coleta encerrada")
    }
}
```

A solução é envolver o código suspendo do `finally` em `withContext(NonCancellable)`. `NonCancellable` é um `Job` singleton que nunca entra em estado `Cancelling` — suspender dentro do seu contexto não lança `CancellationException`, mesmo que o `Job` pai esteja cancelado:

```kotlin
serviceScope.launch {
    try {
        coletarContinuamente()
    } finally {
        withContext(NonCancellable) {
            delay(100)                        // seguro — NonCancellable ignora o estado do Job pai
            notificarBackend("coleta encerrada")
        }
    }
}
```

No service de monitoramento, esse padrão aparece sempre que o `onDestroy` cancela o escopo mas o código de cleanup precisa persistir o estado final antes de encerrar — por exemplo, marcar os eventos coletados naquela janela de tempo como "interrompidos" no Room. Sem `NonCancellable`, a escrita no banco dentro do `finally` falha silenciosamente e os dados da última janela se perdem.

O quadro completo das ferramentas de cancelamento cooperativo é:

| Ferramenta | Mecanismo | Resultado quando cancelado | Quando usar |
|---|---|---|---|
| Chamada `suspend` (delay, await, etc.) | `suspendCancellableCoroutine` | Lança `CancellationException` | Qualquer código com I/O ou espera |
| `isActive` | Leitura de flag do `Job` | `false` — o código decide o que fazer | Laço com saída suave, lógica condicional |
| `ensureActive()` | Checa flag e lança exceção | Lança `CancellationException` | Ponto de checagem no meio de sequência |
| `withContext(NonCancellable)` | Troca o Job para um que nunca cancela | Não lança — bloco executa até o fim | `finally` com chamadas `suspend` |

O `## 6.` fecha o ciclo com `SupervisorJob` e `CoroutineExceptionHandler`: enquanto este conceito trata do que acontece com a coroutine que é cancelada ou falha, o próximo trata do que acontece com as coroutines **irmãs** quando uma delas falha — que é o ponto onde a escolha de `Job` vs `SupervisorJob` no escopo do service se torna visível.

**Fontes utilizadas:**

- [Cancellation and timeouts — Kotlin Documentation](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [Cancellation in Kotlin Coroutines — kt.academy](https://kt.academy/article/cc-cancellation)
- [ensureActive — kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/ensure-active.html)
- [isActive — kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/is-active.html)
- [suspendCancellableCoroutine — kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/suspend-cancellable-coroutine.html)
- [Cancellation in coroutines — Android Developers / Florina Muntenescu](https://medium.com/androiddevelopers/cancellation-in-coroutines-aa6b90163629)
- [Internal Mechanism of Coroutine Cancellation in Kotlin — Medium](https://medium.com/@mahesh31.ambekar/internal-mechanism-of-coroutine-cancellation-in-kotlin-b239188f87a7)

## 6. `SupervisorJob` e `CoroutineExceptionHandler` — diferença entre `Job` e `SupervisorJob` na propagação de exceção, isolamento de falhas entre coroutines irmãs e como montar o escopo canônico de um service Android com esses dois elementos

O cancelamento cooperativo do `## 5.` trata do que acontece com a coroutine que recebe o sinal: ela para nos pontos de suspensão, executa o `finally` e termina com `CancellationException`. O que esses mecanismos não respondem é o que acontece com as coroutines vizinhas quando uma delas **falha** — não é cancelada, mas lança uma exceção não tratada. Essa distinção é onde `Job` e `SupervisorJob` divergem, e onde o escopo do service Android precisa de uma decisão explícita.

Com um `Job` simples no escopo (o que `CoroutineScope(Dispatchers.IO + Job())` produz), a propagação de exceção segue três passos fixos. Primeiro, a coroutine filha que falhou tenta propagar a exceção para seu `Job` pai. Segundo, o `Job` pai transita para o estado `Cancelling` e cancela todos os filhos restantes — os irmãos da coroutine que falhou. Terceiro, quando todos os filhos terminam (cancelados ou não), o `Job` pai completa com falha e propaga a exceção mais acima na hierarquia. O resultado é que uma única exceção em qualquer coroutine derruba o escopo inteiro e todas as tarefas concorrentes. Para pipelines onde a falha de qualquer etapa invalida o resultado (ex: as N tarefas precisam todas terminar com sucesso para que o resultado composto seja entregue), esse comportamento é correto. Para um service que coleta de múltiplas fontes independentes, é desastroso: uma `SecurityException` no `queryUsageStats` derrubaria a coroutine que faz a sincronização com o backend.

`SupervisorJob` muda exatamente esse segundo passo: a falha de um filho não transita o `SupervisorJob` para `Cancelling` e não cancela os irmãos. O cancelamento continua propagando para baixo normalmente (pai cancela todos os filhos), mas nunca sobe a partir de um filho com falha. A diferença mecânica é que `SupervisorJob` sobrepõe o método `childCancelled(cause)` da API interna de `Job` para retornar `false` quando a causa não é `CancellationException` — sinalizando ao runtime que não quer ser cancelado pelo filho.

```kotlin
// Com Job simples: uma falha derruba tudo
val scopeJob = CoroutineScope(Dispatchers.IO + Job())
scopeJob.launch { throw IOException("falha na coleta") }      // Job A
scopeJob.launch { sincronizarComBackend() }                   // Job B — cancelado quando A falha

// Com SupervisorJob: falha de A não afeta B
val scopeSupervisor = CoroutineScope(Dispatchers.IO + SupervisorJob())
scopeSupervisor.launch { throw IOException("falha na coleta") }  // Job A — falha; B continua
scopeSupervisor.launch { sincronizarComBackend() }               // Job B — executa normalmente
```

O isolamento do `SupervisorJob` resolve o problema das irmãs, mas cria uma responsabilidade nova: se a exceção não sobe para o pai, quem a trata? Com `Job` simples, a exceção escalava até algum ponto onde era interceptada ou derrubava o processo. Com `SupervisorJob`, a exceção que não é capturada dentro da coroutine filha (por um `try/catch` local) vai para o `CoroutineExceptionHandler` instalado no contexto — e se não houver nenhum, vai para o handler não tratado padrão da thread, que em Android derruba o processo com `FATAL EXCEPTION`.

`CoroutineExceptionHandler` é um elemento do `CoroutineContext` que funciona como o último recurso de interceptação de exceções não tratadas. A regra de quando ele é invocado é precisa: ele dispara apenas para exceções que chegam a uma coroutine **raiz** de `launch` — ou seja, coroutines lançadas diretamente num escopo com `SupervisorJob`, porque elas não propagam exceção para o pai e são tratadas como raiz. Coroutines filhas de um `Job` simples nunca invocam o `CoroutineExceptionHandler` do próprio contexto — elas delegam para o pai, que delega para o avô, até chegar à raiz. `async` tampouco dispara o handler — exceções ficam armazenadas no `Deferred` e só são relançadas via `await()`.

```kotlin
val handler = CoroutineExceptionHandler { context, exception ->
    Log.e("ServiceScope", "Exceção não tratada em coroutine: ${exception.message}", exception)
    // possível: notificar sistema de monitoramento, reiniciar tarefa específica
}

val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob() + handler)

serviceScope.launch {
    // esta coroutine é raiz do SupervisorJob — exceção não tratada invoca o handler
    coletarEventosDeUso()
}
```

Há uma distinção crítica sobre onde instalar o handler. Se o handler estiver no escopo mas **não** no contexto do `launch` específico, e o escopo usar `SupervisorJob`, as coroutines filhas são tratadas como raiz e o handler do escopo é visível para elas. Se o handler estiver apenas no `launch` filho, dentro de um `Job` simples, ele não é invocado — a exceção sobe para o pai antes de chegar ao handler. A instalação correta para serviços é colocar o handler diretamente no `CoroutineScope` junto com o `SupervisorJob`.

O escopo canônico de um service Android de monitoramento contínuo combina exatamente esses três elementos:

```kotlin
class MonitorService : Service() {
    private val exceptionHandler = CoroutineExceptionHandler { _, exception ->
        // log centralizado; CancellationException nunca chega aqui — é filtrada pelo runtime
        Log.e("MonitorService", "Coroutine falhou: ${exception::class.simpleName}", exception)
    }

    private val serviceScope = CoroutineScope(
        Dispatchers.IO + SupervisorJob() + exceptionHandler
    )

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        serviceScope.launch { coletarEventosDeUso() }       // falha aqui não derruba as outras
        serviceScope.launch { coletarEventosDeAcessib() }   // independente da anterior
        serviceScope.launch { sincronizarComBackend() }     // independente das anteriores
        return START_STICKY
    }

    override fun onDestroy() {
        serviceScope.cancel()   // cancela todas em cascata — CancellationException, não falha
        super.onDestroy()
    }
}
```

`Dispatchers.IO` como dispatcher raiz evita bloquear a main thread em qualquer operação do service. `SupervisorJob()` isola as falhas entre as três tarefas. `exceptionHandler` captura as exceções que escaparem dos `try/catch` internos e impede o crash do processo. `scope.cancel()` no `onDestroy` ainda cancela todas as filhas em cascata — o `SupervisorJob` só muda a propagação de falha para cima, não a propagação de cancelamento para baixo.

Uma armadilha comum é criar o escopo com `SupervisorJob` mas instalar o handler apenas nos `launch`s filhos:

```kotlin
// ERRADO: handler no filho com SupervisorJob não é invocado da forma esperada em alguns casos
serviceScope.launch(CoroutineExceptionHandler { _, e -> Log.e("tag", e.message ?: "") }) {
    coletarEventosDeUso()
}
```

Esse padrão funciona quando o `launch` é filho direto do `SupervisorJob` (porque filhos diretos são tratados como raiz), mas falha silenciosamente quando há um nível extra de aninhamento: se dentro de `coletarEventosDeUso()` houver um `launch` filho que falha, a exceção sobe para `coletarEventosDeUso` (o pai imediato), não para o handler instalado no `launch` raiz. A instalação no escopo evita essa armadilha porque o handler do escopo é herdado por toda a cadeia.

A tabela compara o comportamento das combinações relevantes para o service:

| Escopo | Falha de filho A | Irmão B | Handler invocado |
|---|---|---|---|
| `Job()` simples | Cancela o pai e B | Cancelado | Não (exceto se A for raiz real) |
| `SupervisorJob()` sem handler | Não cancela B | Continua | Não — crash do processo |
| `SupervisorJob()` + handler no escopo | Não cancela B | Continua | Sim — exceção capturada |
| `SupervisorJob()` + handler no `launch` filho | Não cancela B | Continua | Sim (só para diretos) |

O escopo canônico com `SupervisorJob() + handler no escopo` é o que aparecerá em todos os serviços dos capítulos seguintes — `02-services-no-android-moderno/` e `03-foreground-service-estavel/` constroem sobre esse padrão, acrescentando o ciclo de vida completo do service e as restrições de `startForeground`. Os conceitos de `Flow` e `StateFlow` do próximo subcapítulo (`02-flow-e-operadores/`) também partem desse escopo como dado implícito: o `collect` de um `Flow` vive dentro de uma coroutine desse mesmo `serviceScope`.

**Fontes utilizadas:**

- [Coroutine exceptions handling — Kotlin Documentation](https://kotlinlang.org/docs/exception-handling.html)
- [Exception handling in Kotlin Coroutines — kt.academy](https://kt.academy/article/cc-exception-handling)
- [SupervisorJob — kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-supervisor-job.html)
- [CoroutineExceptionHandler — kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-exception-handler/)
- [SupervisorJob and CoroutineExceptionHandler in Kotlin Coroutines — TechYourChance](https://www.techyourchance.com/kotlin-coroutines-supervisorjob/)
- [Understanding SupervisorJob in Kotlin Coroutines — RevenueCat Engineering](https://www.revenuecat.com/blog/engineering/supervisorjob-kotlin/)
- [Constructing a coroutine scope — kt.academy](https://kt.academy/article/cc-constructing-scope)
- [Exceptions in coroutines — Android Developers / Manuel Vivo](https://medium.com/androiddevelopers/exceptions-in-coroutines-ce8da1ec060c)

<!-- AULAS-END -->

---

**Próximo subcapítulo** → [`Flow` e Operadores](../02-flow-e-operadores/CONTENT.md)
