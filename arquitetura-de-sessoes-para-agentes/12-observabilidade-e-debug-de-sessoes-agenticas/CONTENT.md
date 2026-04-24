# Observabilidade e Debug de Sessões Agênticas

![capa](cover.png)

## Sobre este capítulo

Debugar um agente stateful é fundamentalmente diferente de debugar uma função stateless: o comportamento errado num turno pode ser causado por algo que aconteceu três turnos atrás, e reproduzir o bug requer restaurar o estado exato da sessão naquele momento. Este capítulo fecha o livro cobrindo o que é necessário para operar um sistema agêntico com sessões em produção: tracing de sessão com OpenTelemetry (que o leitor já tem parcialmente implementado), métricas específicas de saúde de sessão, replay de runs para debug, e alertas para os problemas mais comuns em produção (loops infinitos, compactação excessiva, vazamento de sessões).

A posição deste capítulo no final é intencional: ele pressupõe que o leitor implementou a camada de sessão nos capítulos anteriores e agora precisa operar e manter o sistema. É o capítulo que fecha o ciclo do livro — do diagnóstico inicial (cap. 1) à operação em produção.

## Estrutura

Os grandes blocos são: (1) tracing de sessão com OpenTelemetry — extensão do tracing existente (o leitor já usa `tracer` e spans no projeto) para incluir session_id, turn_number e run_id como atributos de span; correlação de spans de tool calls com a sessão pai; exportação para o backend de observabilidade existente; (2) métricas de saúde de sessão — métricas específicas de agente: token usage por sessão por turno (curva de crescimento), taxa de compactação, tempo médio de turn, número de sessões ativas/suspensas/expiradas, e alertas para anomalias; (3) replay de runs para debug — como reconstruir exatamente o que o agente viu em cada turno (substrato + janela de contexto montada) a partir do log de eventos no MongoDB; uma ferramenta CLI mínima para replay interativo; (4) detecção de loops infinitos — patterns que indicam loop (tool call repetido com os mesmos argumentos, número de runs no mesmo turno acima de threshold) e como implementar circuit breakers na state machine; (5) gestão de incidentes — procedimentos para sessões corrompidas (corrigir estado diretamente no MongoDB), sessões presas em RUNNING após crash do container, e recover gracioso.

## Objetivo

Ao terminar este capítulo, o leitor será capaz de estender o OpenTelemetry existente com atributos de sessão, implementar métricas de saúde básicas, criar uma ferramenta de replay de sessão para debug, e configurar circuit breakers contra loops infinitos. O leitor encerrará o livro com um sistema agêntico observável, depurável e operável em produção.

## Fontes utilizadas

- [Strands Agents SDK: A technical deep dive into agent architectures and observability — AWS Blog](https://aws.amazon.com/blogs/machine-learning/strands-agents-sdk-a-technical-deep-dive-into-agent-architectures-and-observability/)
- [AI Agent Architecture: Build Systems That Work in 2026 — Redis](https://redis.io/blog/ai-agent-architecture/)
- [Reference Architecture: OpenClaw (Early Feb 2026 Edition) — robotpaper.ai](https://robotpaper.ai/reference-architecture-openclaw-early-feb-2026-edition-opus-4-6/)
- [Architecting efficient context-aware multi-agent framework for production — Google Developers Blog](https://developers.googleblog.com/architecting-efficient-context-aware-multi-agent-framework-for-production/)
- [Agentic AI with AWS: Infrastructure and Service Integration in 2026 — adspyder](https://adspyder.io/blog/agentic-ai-with-aws/)
