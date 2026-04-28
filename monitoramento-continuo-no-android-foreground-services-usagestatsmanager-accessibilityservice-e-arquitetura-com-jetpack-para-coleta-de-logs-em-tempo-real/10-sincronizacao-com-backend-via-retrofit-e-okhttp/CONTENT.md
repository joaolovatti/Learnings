# Sincronização com Backend via Retrofit e OkHttp

![capa](cover.png)

## Sobre este capítulo

O Room é o buffer local — os eventos coletados precisam chegar ao backend para que os responsáveis acessem os dados de qualquer dispositivo. Este capítulo implementa a camada de sincronização: a API de upload de logs modelada com Retrofit, a configuração de OkHttp com interceptors de autenticação, a estratégia de retry em caso de falha e o mecanismo de sync incremental que usa o Room como buffer e evita reenvio de dados já sincronizados. O WorkManager do capítulo 4 orquestra o disparo periódico; este capítulo implementa o worker de sync.

O leitor tem background sólido em desenvolvimento backend e em chamadas HTTP via Flutter/Dart — o que significa que Retrofit não é novidade conceitual, mas os detalhes de integração com Room, o tratamento de retry com backoff e a lógica de marcação de registros como "sincronizados" são o foco real deste capítulo.

## Estrutura

Os grandes blocos são: (1) modelagem da API de upload — `@POST` com `@Body` de lista de eventos, `Response<T>` vs resultado tipado, tratamento de erros HTTP com `HttpException` e erros de rede com `IOException`; (2) configuração de OkHttp — `OkHttpClient.Builder` com `authenticator` para token refresh, `addInterceptor` para headers de autenticação, `addNetworkInterceptor` para logging, timeouts de connect/read/write; (3) sync incremental com Room como buffer — coluna `syncedAt` na entidade de evento, query de eventos não sincronizados, batch upload com tamanho configurável e marcação de `syncedAt` após sucesso; (4) retry policy — `WorkManager` `RetryPolicy.EXPONENTIAL` vs retry manual com `kotlinx.coroutines.delay`, limite de tentativas e circuit breaker para evitar storm de requests; (5) `SyncWorker` completo — implementação do worker que lê Room, chama Retrofit, marca como sincronizado e reporta `Result.success/failure/retry` ao WorkManager com dados de diagnóstico.

## Objetivo

Ao terminar este capítulo, o leitor terá implementado o `SyncWorker` completo: lê eventos não sincronizados do Room em batches, envia via Retrofit com autenticação, marca os enviados como sincronizados e retorna ao WorkManager com resultado correto para retry em caso de falha. A camada de coleta local terá seu canal de saída para o backend.

## Fontes utilizadas

- [Retrofit — Square](https://square.github.io/retrofit/)
- [OkHttp — Square](https://square.github.io/okhttp/)
- [Make network requests with WorkManager — Android Developers](https://developer.android.com/topic/libraries/architecture/workmanager/advanced/retrofit)
- [nowinandroid Architecture Learning Journey — GitHub/android](https://github.com/android/nowinandroid/blob/main/docs/ArchitectureLearningJourney.md)
- [Save data in a local database using Room — Android Developers](https://developer.android.com/training/data-storage/room)
- [The Ultimate Android Developer Roadmap 2026 — Medium](https://tiwariashuism.medium.com/the-ultimate-android-developer-roadmap-2026-from-novice-to-expert-afd14fc97d1b)
