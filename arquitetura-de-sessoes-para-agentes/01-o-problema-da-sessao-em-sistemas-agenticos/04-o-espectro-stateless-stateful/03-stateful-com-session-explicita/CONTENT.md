# Stateful com Session Explícita

![capa](cover.png)

O conceito anterior terminou num ponto preciso: o padrão Lambda + MongoDB com injeção de histórico transforma o modelo de linguagem no único intérprete de estado — toda pergunta operacional sobre o que o agente está fazendo passa pelo custo de uma leitura do texto. Isso não é uma limitação acidental; é uma consequência estrutural de não ter um session object. O que muda quando esse objeto finalmente existe é o tema deste conceito, e a mudança é qualitativa, não incremental.

A transição para stateful com session explícita começa pela existência de uma entidade persistida cuja responsabilidade exclusiva é representar o estado corrente da sessão — não o log do que aconteceu, mas a fotografia do que está acontecendo agora. Essa entidade tem um identificador próprio (`session_id`) que é independente do `user_id` e do histórico de mensagens. O `session_id` não é apenas uma chave de filtro numa coleção de mensagens, como visto no conceito anterior — é a chave primária de um documento de primeiro nível cujos campos expressam estado operacional com semântica própria.

O ciclo de vida por turno é o que torna essa posição do espectro estruturalmente diferente. Em vez do handler buscar mensagens e injetar texto, ele executa uma sequência diferente:

```
Turno chegando:
  1. Carregar session_id da requisição
  2. Buscar o session object do store (MongoDB, Redis, DynamoDB)
  3. Ler campos estruturados → tomar decisões de controle (expirado? compactação necessária?)
  4. Montar janela de contexto usando tanto o session object quanto o histórico de mensagens
  5. Executar inferência / tool calls
  6. Atualizar campos do session object (status, intent, token count, pending_actions)
  7. Persistir session object atualizado
  8. Retornar resposta
```

O ponto crítico está nos passos 3 e 6. No padrão com histórico injetado, essas posições não existem — não há "ler campos estruturados" porque os campos não existem, e não há "atualizar session object" porque o objeto não existe. Tudo que o handler faz é ler mensagens e gravar mensagens. Com session explícita, o handler tem acesso a campos que o código pode inspecionar e modificar diretamente, sem passar pelo modelo.

Um session object funcional para o contexto do leitor — Lambda com Gemini e tool calling via Haystack — contém ao menos os seguintes campos:

```json
{
  "session_id": "sess_a7f3bc901d",
  "user_id": "usr_456",
  "created_at": "2026-04-23T10:00:00Z",
  "last_activity": "2026-04-23T14:52:11Z",
  "status": "waiting_for_confirmation",
  "current_intent": "create_clickup_task",
  "intent_metadata": {
    "list_id": "901234",
    "name": "Corrigir bug no endpoint /auth/refresh",
    "assignee_id": "user_joao",
    "priority": 2
  },
  "pending_actions": [
    {
      "type": "awaiting_user_approval",
      "action": "create_clickup_task",
      "payload": { "list_id": "901234", "name": "Corrigir bug no endpoint /auth/refresh" },
      "expires_at": "2026-04-23T15:00:00Z"
    }
  ],
  "context_tokens_used": 4870,
  "message_count": 18,
  "tool_calls_this_session": 7,
  "last_tool_call": {
    "tool": "clickup_list_tasks",
    "result_summary": "Retornou 12 tarefas abertas no projeto Backend",
    "timestamp": "2026-04-23T14:51:44Z"
  }
}
```

Cada campo tem função operacional concreta. `status` diz ao handler em que estado a conversa está — `idle`, `running`, `waiting_for_confirmation`, `suspended`, `expired` — e o handler pode tomar decisões de controle antes mesmo de chamar o modelo. Se o status é `waiting_for_confirmation` e a nova mensagem do usuário é "pode criar", o handler sabe que deve executar a ação pendente antes de qualquer inferência. Se o status é `expired`, o handler pode responder imediatamente com uma mensagem de retomada sem invocar o Gemini.

`current_intent` e `intent_metadata` capturam o objetivo ativo da sessão como dado estruturado. Isso elimina a dependência de que o modelo releia as últimas N mensagens para "lembrar" o que estava tentando fazer. O código sabe. `pending_actions` vai além: é uma fila explícita de ações que o agente iniciou mas que aguardam confirmação, aprovação ou resultado externo — com `expires_at` para gestão de timeout programática, sem inferência.

`context_tokens_used` e `message_count` são os campos que habilitam gestão de contexto baseada em código, não em heurística do modelo. Quando `context_tokens_used` ultrapassar um threshold — digamos, 80% do limite de tokens do modelo — o handler pode disparar compactação antes de construir o prompt. Isso é uma decisão de infraestrutura, não uma decisão do modelo; o modelo não precisa "saber" que está ficando sem contexto. `last_tool_call` permite que o handler evite re-executar a mesma tool em sequência rápida — uma salvaguarda contra loops que novamente não depende de inferência do modelo para funcionar.

A mecânica de acesso por turno que frameworks como Google ADK, OpenAI Agents SDK e AWS Bedrock AgentCore convergem para o mesmo padrão: o runner carrega o session object antes de invocar o agente, o agente recebe o objeto como parte do contexto de execução, e o runner grava o objeto atualizado após o turno. No ADK, o `Session` é uma entidade de primeiro nível com campos `id`, `userId`, `state` (mapa de dados arbitrários persistidos) e `events` (histórico de interações); o `Runner` chama `sessionService.append_event()` ao final de cada turno para manter o estado sincronizado. No AgentCore da AWS, o `session_id` é passado via header HTTP, e o serviço garante affinity de roteamento — requisições com o mesmo `session_id` chegam ao mesmo contexto de execução durante a janela ativa da sessão.

A diferença de isolamento é outro aspecto que só existe com session explícita. Com histórico injetado e apenas `user_id` como chave, dois contextos de conversa do mesmo usuário (por exemplo, uma sessão no Slack e outra via API direta) compartilham o mesmo log — não há fronteira entre as duas conversas. Com `session_id` como entidade de primeiro nível, cada contexto é isolado por design: o estado da sessão Slack não vaza para a sessão API, as intenções em andamento numa não afetam a outra, e as políticas de expiração são aplicadas independentemente.

```python
# Handler com session object explícito
def handle(event):
    session_id = event.get("session_id")  # obrigatório; ausência é erro
    user_message = event["message"]
    
    # 1. Carregar session object — entidade de primeiro nível
    session = session_store.get(session_id)
    if not session:
        return {"error": "session_not_found"}
    
    # 2. Decisões de controle baseadas em campos — sem LLM
    if session.is_expired():
        return {"error": "session_expired", "session_id": session_id}
    
    if session.status == "waiting_for_confirmation":
        if is_confirmation(user_message):
            result = execute_pending_action(session.pending_actions[0])
            session.clear_pending_actions()
            session.status = "idle"
            session_store.save(session)
            return {"result": result}
    
    # 3. Verificar se compactação é necessária — sem LLM
    if session.context_tokens_used > TOKEN_COMPACT_THRESHOLD:
        compact_session_history(session)
    
    # 4. Montar janela de contexto com session object + histórico relevante
    messages = build_context(session, user_message)
    
    # 5. Inferência
    response, tool_calls = gemini.generate(messages)
    
    # 6. Atualizar campos do session object após turno
    session.last_activity = now()
    session.message_count += 2
    session.context_tokens_used = count_tokens(messages) + count_tokens(response)
    if tool_calls:
        session.last_tool_call = summarize_tool_calls(tool_calls)
        session.tool_calls_this_session += len(tool_calls)
    
    # 7. Persistir
    session_store.save(session)
    
    return {"response": response, "session_id": session_id}
```

O que este código exibe é o padrão que o conceito anterior declarava impossível com injeção de histórico: `is_expired()`, `status == "waiting_for_confirmation"`, `context_tokens_used > threshold` — todas essas são verificações de código em O(1), não inferências do modelo. O modelo só é invocado no passo 5, depois que todas as decisões de controle já foram tomadas pelo handler. Isso não só torna o sistema mais eficiente em custo; torna o comportamento determinístico. O mesmo `session.status` produz o mesmo branch de execução, sempre — independente do humor do modelo, do prompt de sistema, ou de variação de temperatura.

As armadilhas reais dessa posição valem nomear porque aparecem em produção. A primeira é o race condition entre invocações paralelas: se o usuário envia duas mensagens rapidamente (ou se há um timeout de rede que gera retry), dois handlers podem carregar o mesmo session object simultaneamente, processar de forma independente, e gravar de volta — uma gravação anula a outra. A solução é optimistic locking (campo `version` no documento, atualizado atomicamente) ou locks distribuídos via Redis, dependendo da tolerância ao retry. O MongoDB suporta operações atômicas via `findOneAndUpdate` com condição no campo `version`, o que resolve o problema sem lock explícito para a maioria dos casos:

```python
# Atualização atômica com versão — evita sobrescrita por race condition
result = sessions.find_one_and_update(
    {"session_id": session_id, "version": session.version},
    {"$set": {**session.to_dict(), "version": session.version + 1}},
    return_document=True
)
if not result:
    raise SessionConflictError("Session foi modificada por outro processo")
```

A segunda armadilha é o crescimento não supervisionado do session object. Ao contrário do log de mensagens — que cresce de forma previsível — campos como `pending_actions` e `intent_metadata` podem acumular entradas obsoletas se não houver limpeza explícita. Uma ação pendente cujo `expires_at` passou há horas ainda no documento é lixo estruturado; o handler precisa de uma política de limpeza executada a cada carregamento.

A terceira armadilha é a ausência de `session_id` na requisição — que ocorre quando o cliente não implementou corretamente o protocolo. Ao contrário do padrão com `user_id` (que aceita silenciosamente qualquer mensagem sem sessão), o handler com session explícita deve rejeitar requisições sem `session_id` com erro claro, forçando o cliente a criar uma sessão antes de interagir. Isso é uma mudança de contrato de API que precisa ser versionada.

A quarta armadilha é misturar o session object com o log de mensagens no mesmo documento. A separação é arquiteturalmente importante: o log cresce linearmente e é lido em fatias; o session object é pequeno, lido inteiro e reescrito inteiro a cada turno. Colocá-los no mesmo documento MongoDB significa que uma operação de read do session object carrega kilobytes de histórico de mensagens desnecessariamente. A separação em coleções distintas (`sessions` para o objeto de estado, `messages` com `session_id` como chave estrangeira para o histórico) mantém as leituras do session object em sub-milissegundo independente do tamanho do histórico.

O que essa posição do espectro entrega, em contraste com as duas anteriores, fica claro numa tabela de capacidades:

| Capacidade operacional | Stateless puro | Histórico injetado | Session explícita |
|---|---|---|---|
| Saber status atual sem LLM | Impossível | Impossível | `session.status` |
| Detectar intenção em progresso | Impossível | Inferência do modelo | `session.current_intent` |
| Expirar sessão por TTL | Impossível | Calcular via timestamp de mensagem | `session.last_activity` + cron |
| Gerenciar tokens antes da inferência | Impossível | Contar post-hoc | `session.context_tokens_used` |
| Isolar sessões simultâneas do mesmo usuário | Impossível | Inviável sem refatoração | `session_id` como chave primária |
| Retomar workflow após falha | Impossível | Reconstruir do zero | `session.pending_actions` |
| Detectar loop antes que o modelo alucine | Impossível | Impossível | `tool_calls_this_session` + threshold |

A posição "stateful com session explícita" não é o topo do espectro — o próximo conceito descreve arquiteturas como Letta/MemGPT com memória episódica completa, que adicionam camadas de memória semântica e procedural acima desse session object. Mas para a maior parte dos sistemas agênticos em produção que o leitor encontrará, ela representa o salto qualitativo central: é aqui que o sistema deixa de ser "um Lambda que injeta texto" e se torna "um agente que carrega e persiste estado estruturado". Os capítulos seguintes — state machines para o ciclo de vida, persistência, compactação — todos pressupõem que esse session object existe como entidade de primeira classe.

## Fontes utilizadas

- [Session: Tracking Individual Conversations — Google ADK](https://adk.dev/sessions/session/)
- [Overview: Sessions — OpenAI Agents SDK](https://openai.github.io/openai-agents-python/sessions/)
- [Use isolated sessions for agents — Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-sessions.html)
- [Stateful Agents — Agent Communication Protocol](https://agentcommunicationprotocol.dev/core-concepts/stateful-agents)
- [Stateful vs Stateless AI Agents: Architecture Patterns That Matter — Ruh.ai](https://www.ruh.ai/blogs/stateful-vs-stateless-ai-agents)
- [Stateful vs. stateless agents: Why stateful architecture is essential for agentic AI — ZBrain](https://zbrain.ai/stateful-architecture-for-agentic-ai-systems/)
- [Cross Session Leak: LLM security vulnerability and detection guide — Giskard](https://www.giskard.ai/knowledge/cross-session-leak-when-your-ai-assistant-becomes-a-data-breach)
- [Session Management — Redis](https://redis.io/solutions/session-management/)

---

**Próximo conceito** → [Agentes com Memória Episódica Completa](../04-agentes-com-memoria-episodica-completa/CONTENT.md)
