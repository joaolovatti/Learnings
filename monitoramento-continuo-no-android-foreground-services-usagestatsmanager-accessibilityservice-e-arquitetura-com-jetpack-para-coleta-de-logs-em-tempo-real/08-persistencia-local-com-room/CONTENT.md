# Persistência Local com Room

![capa](cover.png)

## Sobre este capítulo

Os eventos coletados pelo Foreground Service via `UsageStatsManager` e `AccessibilityService` precisam ser persistidos localmente antes de serem sincronizados com o backend — o dispositivo pode estar offline, a sincronização pode falhar, e o app precisa sobreviver a restarts sem perder dados. Room é a camada de persistência do Jetpack que resolve esse problema: abstrai o SQLite com type safety, integra nativamente com Kotlin Flows e gerencia migrations de schema de forma explícita. Este capítulo constrói o schema de eventos do app de controle parental do zero.

O design do schema é o ponto central: events de `UsageStats` e de `AccessibilityService` têm estruturas diferentes e precisam ser modelados de forma que permitam queries eficientes por app, por janela de tempo e por tipo de evento. O capítulo também cobre a estratégia de retenção — logs antigos precisam ser apagados periodicamente para não lotar o armazenamento do dispositivo do filho — e como coordenar a limpeza com o WorkManager do capítulo 4.

## Estrutura

Os grandes blocos são: (1) entidades Room — `@Entity` para `UsageEvent` e `AppSession`, tipos de coluna, chaves primárias com `autoGenerate`, índices para queries por packageName e timestamp; (2) DAOs com Flow — `@Insert`, `@Query` com `Flow<List<T>>` para coleta reativa, queries por janela de tempo com parâmetros, `@Delete` e `@Transaction` para operações compostas; (3) `RoomDatabase` — configuração do `Room.databaseBuilder`, exportação de schema para migrations, `fallbackToDestructiveMigration` vs migrations explícitas e quando usar cada um; (4) migrations — `Migration(from, to)` com `execSQL`, adição de coluna com DEFAULT, renomeação de tabela e como testar migrations com `MigrationTestHelper`; (5) estratégia de retenção e limpeza — query de deleção por `timestamp < cutoff`, integração com `PeriodicWorkRequest` do WorkManager para rodar a limpeza fora do serviço principal, e configuração do período de retenção.

## Objetivo

Ao terminar este capítulo, o leitor terá o schema Room completo para o app de controle parental: entidades para eventos de uso e de acessibilidade, DAOs com Flows reativos para leitura e inserção, migrations configuradas e uma estratégia de retenção de logs integrada com WorkManager. O pipeline de coleta terá um buffer local robusto que alimenta a sincronização com o backend no capítulo 10.

## Fontes utilizadas

- [Save data in a local database using Room — Android Developers](https://developer.android.com/training/data-storage/room)
- [Room persistence library — Android Developers](https://developer.android.com/jetpack/androidx/releases/room)
- [Write asynchronous DAO queries — Android Developers](https://developer.android.com/training/data-storage/room/async-queries)
- [Migrate your Room database — Android Developers](https://developer.android.com/training/data-storage/room/migrating-db-versions)
- [nowinandroid Architecture Learning Journey — GitHub/android](https://github.com/android/nowinandroid/blob/main/docs/ArchitectureLearningJourney.md)
- [The Ultimate Android Developer Roadmap 2026 — Medium](https://tiwariashuism.medium.com/the-ultimate-android-developer-roadmap-2026-from-novice-to-expert-afd14fc97d1b)
