# Estrutura do Livro

> Mapa rapido da organizacao do livro: capitulos, subcapitulos e conceitos. Mantido automaticamente pela skill `estudo-atualizar-struct` — nao edite a mao.

```
monitoramento-continuo-no-android-foreground-services-usagestatsmanager-accessibilityservice-e-arquitetura-com-jetpack-para-coleta-de-logs-em-tempo-real/ — Monitoramento Contínuo no Android — Foreground Services, UsageStatsManager, AccessibilityService e Arquitetura com Jetpack para Coleta de Logs em Tempo Real
├── 01-kotlin-para-devs-java-e-flutter/ — coroutines, sealed classes, extension functions e null safety aplicados a contextos de serviços Android
│   ├── 01-coroutines-e-suspend-fun/ — `CoroutineScope`, `launch`, `async`, `withContext`, `Dispatchers`, cancelamento cooperativo e `SupervisorJob`
│   ├── 02-flow-e-operadores/ — `flow {}`, `collect`, `map`, `filter`, `onEach`, `conflate`, e a distinção entre `Flow` frio e `StateFlow`/`SharedFlow` quentes
│   ├── 03-sealed-classes-e-when-expressivo/ — modelagem de estados do serviço e tipos de evento com sealed hierarchies e `when` exaustivo sem `else`
│   ├── 04-extension-functions-e-scope-functions/ — `let`, `also`, `apply`, `run`, `with` em contextos reais de setup de notificações e verificação de permissões
│   ├── 05-null-safety-na-pratica/ — interoperabilidade com APIs Android que retornam `null` em Java, `?.`, `?:`, `requireNotNull` e platform types
│   └── 06-kotlin-idiomatico-em-servicos-android/ — integração dos quatro blocos num esqueleto completo de `LifecycleService` com `StateFlow` de estado e extension functions de arranque
├── 02-services-no-android-moderno/ — tipos de Service, ciclo de vida completo, comunicação com componentes e a notificação obrigatória do foreground
├── 03-foreground-service-estavel/ — implementação de um ForegroundService resiliente com tipos declarados, startForeground, stopSelf e sobrevivência a crashes
├── 04-background-work-de-longa-duracao/ — WorkManager para tarefas garantidas, BOOT_COMPLETED receiver e restrições de bateria do Android 8 ao 15
├── 05-coleta-de-eventos-com-usagestatsmanager/ — permissão PACKAGE_USAGE_STATS, QueryUsageStats, UsageEvents e granularidade de dados por janela de tempo
├── 06-eventos-granulares-com-accessibilityservice/ — estrutura de AccessibilityService, eventos TYPE_WINDOW_STATE_CHANGED, captura de notificações e limites do Google Play
├── 07-verificacao-de-permissoes-especiais-em-runtime/ — AppOpsManager, OP_GET_USAGE_STATS, direcionamento ao Settings e fallback quando permissões são negadas
├── 08-persistencia-local-com-room/ — entidades de eventos, DAOs com Flow, migrations e estratégia de retenção e limpeza de logs antigos
├── 09-stateflow-viewmodel-e-fluxo-reativo/ — pipeline de dados do serviço ao ViewModel, backpressure, ciclo de vida e separação entre coleta e apresentação
├── 10-sincronizacao-com-backend-via-retrofit-e-okhttp/ — modelagem da API de upload de logs, interceptors de autenticação, retry policy e sync incremental com Room como buffer
├── 11-dashboard-do-responsavel-com-jetpack-compose/ — Composables para tempo de uso e eventos por app, integração com StateFlow e navegação entre telas
└── 12-integracao-end-to-end/ — ligando Foreground Service, APIs de coleta, Room e Retrofit num fluxo coeso, testes manuais e checklist pré-publicação
```
