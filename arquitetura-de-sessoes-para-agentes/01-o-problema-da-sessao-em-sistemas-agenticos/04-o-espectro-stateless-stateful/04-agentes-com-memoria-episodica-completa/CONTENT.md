# Agentes com Memória Episódica Completa

![capa](cover.png)

O conceito anterior — stateful com session explícita — representa o salto qualitativo central do espectro: o momento em que o sistema deixa de injetar texto e passa a carregar estado estruturado. Mas a posição "stateful com session explícita" ainda tem um teto. O session object contém campos operacionais (`status`, `current_intent`, `pending_actions`) que o código pode manipular diretamente — mas toda a memória de longo prazo ainda é tratada como um log de mensagens que o modelo precisa ler. A sessão persiste estado de curto prazo com precisão; o que veio antes da última sessão, o que o agente aprendeu sobre o usuário ao longo de semanas, quais workflows falharam repetidamente no passado — tudo isso continua invisível ao código e acessível apenas se o modelo ler o histórico completo. A posição que fecha o espectro neste subcapítulo é a que trata essa lacuna como problema de primeira classe.

A arquitetura de memória episódica completa parte de uma analogia que não é cosmética: sistemas operacionais resolveram o problema de memória limitada separando memória rápida volátil (RAM) de armazenamento lento persistente (disco) e implementando paginação — o movimento automático de dados entre os dois níveis conforme a demanda. O paper MemGPT (2023) transpôs essa estrutura para agentes: o context window do modelo é a RAM, finita e volátil; bancos de dados externos são o disco, ilimitados e persistentes; e o próprio agente — via tool calling — gerencia o que entra e sai da RAM. A Letta é a evolução de produção desse padrão.

O que isso significa concretamente é que o agente tem ferramentas de gerenciamento de memória como parte do seu conjunto de actions, não apenas ferramentas de domínio (Slack, ClickUp, APIs externas). Quando o contexto está lotando, o modelo não simplesmente trunca o histórico mais antigo — ele decide o que comprimir, o que arquivar e o que manter ativo, por conta própria. Essa autonomia sobre a própria memória é o que distingue fundamentalmente essa posição das anteriores.

A estrutura de memória que Letta e sistemas similares gerenciam é organizada em três camadas com papéis diferentes:

| Camada | Analogia | Características | Exemplo de conteúdo |
|---|---|---|---|
| Core Memory (blocos em contexto) | RAM | Sempre visível no context window; editável diretamente pelo agente via tools | Persona do agente, perfil do usuário, fatos críticos da sessão atual |
| Recall Memory (histórico pesquisável) | Cache de disco | Fora do contexto mas indexada; o agente busca via tool call com query semântica | Histórico de conversas passadas, episódios anteriores relevantes |
| Archival Memory (armazenamento frio) | Disco frio | Armazenamento de longo prazo; o agente insere e recupera via tool calls explícitos | Fatos aprendidos sobre o usuário, resultados de workflows passados, conhecimento acumulado |

A Core Memory é a inovação central do modelo. Em vez de um system prompt estático que o desenvolvedor escreve e nunca muda, os blocos de core memory são seções do context window que o agente pode editar diretamente usando ferramentas como `memory_replace` e `memory_insert`. Um bloco `<human>` pode começar vazio e, ao longo de semanas de interação, ser preenchido com preferências, padrões de comportamento e contexto pessoal que o agente aprendeu — e que persiste entre sessões porque é gravado no banco de dados ao final de cada turno, não apenas mantido no context window.

```python
# Ferramentas de memória disponíveis para o agente Letta
# (não são chamadas pelo código — são chamadas pelo modelo)

# Editar core memory diretamente
memory_replace(old_content="João prefere tasks no ClickUp sem assignee",
               new_content="João prefere tasks no ClickUp com assignee automático para ele mesmo")

# Inserir em archival memory (long-term storage)
archival_memory_insert(content="2026-04-10: João pediu para criar 3 tasks similares no mesmo sprint. "
                                "Padrão recorrente: prefere agrupar trabalho por sprint, não por projeto.")

# Recuperar da archival memory por semântica
results = archival_memory_search(query="preferências de João sobre organização de tasks")

# Buscar no histórico de conversas
episodes = conversation_search(query="deploy falhou")
```

O mecanismo de gestão de pressão de contexto é o que torna isso operacionalmente diferente de apenas "ter mais memória". Quando o uso de tokens do context window atinge um threshold configurável (a Letta usa 70% por padrão), o sistema injeta um alerta interno na conversa — uma mensagem de sistema que o modelo vê como parte do fluxo. Ao receber esse alerta, o modelo pausa o raciocínio corrente, examina o que está em core memory e recall memory, decide o que pode ser comprimido em um resumo, o que deve ser arquivado literalmente, e o que precisa permanecer ativo. Ele então executa as tool calls necessárias para executar essas movimentações e retoma o raciocínio. O desenvolvedor não escreve essa lógica — o modelo a executa porque as ferramentas estão disponíveis e a instrução de gerenciar a própria memória está no system prompt.

```
Fluxo de paginação quando contexto atinge threshold:

[usuário envia mensagem]
  ↓
[modelo recebe alerta: "Aviso: contexto em 71% da capacidade"]
  ↓
[modelo raciocina: o que posso arquivar?]
  → archival_memory_insert("resumo dos últimos 5 episódios...")
  → memory_replace(bloco obsoleto → versão comprimida)
  ↓
[contexto liberado]
  ↓
[modelo responde a mensagem do usuário]
```

A separação entre os três tipos de memória a longo prazo — episódica, semântica e procedural — não é apenas taxonomia acadêmica; ela tem implicações de implementação. A **memória episódica** armazena episódios específicos com contexto temporal: "na sessão de 10 de abril, o usuário pediu X, o agente fez Y, o resultado foi Z". A **memória semântica** armazena fatos generalizados extraídos de episódios: "o usuário prefere tasks com assignee automático" — sem o contexto temporal do episódio que gerou essa conclusão. A **memória procedural** armazena comportamentos e heurísticas aprendidos: "quando o usuário diz 'cria um ticket para isso', ele quer que o ticket vá para o sprint ativo, não para o backlog". O framework CoALA (publicado por pesquisadores de Princeton) formaliza essas três categorias mais a memória de trabalho in-context como os quatro tipos de memória de agentes, derivados da ciência cognitiva e da arquitetura SOAR.

Em Letta, essas distinções se mapeiam concretamente: blocos de core memory editáveis funcionam como memória semântica ativa ("o que sei sobre este usuário agora"); a archival memory indexada com embeddings armazena tanto episódios quanto fatos derivados; e o próprio system prompt — que o agente pode modificar via ferramentas — funciona como memória procedural, podendo ser atualizado quando o agente aprende uma nova regra de comportamento.

A pergunta prática que essa posição do espectro levanta é direta: quando essa complexidade é justificada?

Os sinais que indicam que memória episódica completa é a resposta certa são precisos. Primeiro, **persistência de identidade cross-sessão**: o agente precisa conhecer o usuário profundamente ao longo de semanas ou meses — preferências, histórico de decisões, padrões de comportamento — e não apenas dentro de uma única sessão. Assistentes pessoais do tipo Pi.dev são o caso canônico. Segundo, **aprendizado adaptativo**: o sistema precisa mudar seu comportamento com base no feedback acumulado ao longo do tempo — não apenas nesta sessão, mas em todas as sessões anteriores. Terceiro, **contextos que excedem qualquer janela de contexto razoável**: quando a história relevante para tomar uma decisão correta hoje está distribuída em centenas de sessões passadas, paginação automática é a única solução que não requer que o desenvolvedor decida manualmente o que incluir no prompt. Quarto, **agentes que operam de forma autônoma por longos períodos** — dias ou semanas sem interação humana constante — precisando lembrar o que iniciaram e o que ficou pendente.

Os sinais que indicam overengineering são igualmente claros. Se o agente sempre começa cada sessão do zero sem precisar de contexto de sessões anteriores — um agente de suporte técnico que responde tickets independentes, por exemplo — o session object do conceito anterior é mais que suficiente. Se a complexidade do workflow cabe na janela de contexto do modelo (que em 2026 já chega a centenas de milhares de tokens para Gemini e Claude), paginação automática resolve um problema que não existe. Se a equipe não tem capacidade operacional para gerenciar a infraestrutura adicional — servidor Letta dedicado, banco de dados vetorial para archival memory, monitoramento dos ciclos de paginação — a complexidade operacional supera o benefício.

Há uma armadilha específica dessa posição que merece atenção: o agente gerencia sua própria memória, o que significa que ele pode gerenciar mal. Um modelo mal instruído pode arquivar informação crítica por achar que é desnecessária, ou pode lotar a core memory com detalhes irrelevantes por não entender o que é importante. A qualidade do gerenciamento de memória depende diretamente da qualidade das instruções no system prompt sobre o que preservar, o que comprimir e o que descartar. Esse é o ponto onde a analogia com o sistema operacional quebra: um OS tem regras determinísticas de paginação; um agente com memória episódica tem heurísticas probabilísticas. A testabilidade do comportamento de memória é por isso muito mais difícil — não há um teste unitário para "o agente decidiu arquivar a coisa certa".

Para o projeto do leitor — Lambda com Gemini e tool calling via Haystack — a memória episódica completa é provável overengineering no horizonte imediato. O objetivo declarado é atingir algo como o Pi.dev em termos de sessão persistente e interação em tempo real via API Gateway; mas o Pi.dev, por ser um assistente pessoal de uso diário, é um dos casos canônicos para memória episódica. Um agente que processa tickets no ClickUp e mensagens no Slack, com sessões de minutos a horas, atinge o que precisa com stateful com session explícita bem implementado. O próximo conceito deste subcapítulo fornece os critérios objetivos para essa avaliação — como identificar com precisão em qual posição do espectro um sistema está e qual é a próxima posição racional a atingir sem queimar etapas.

## Fontes utilizadas

- [MemGPT: Towards LLMs as Operating Systems — arXiv](https://arxiv.org/abs/2310.08560)
- [Agent Memory: How to Build Agents that Learn and Remember — Letta](https://www.letta.com/blog/agent-memory)
- [Memory Blocks: The Key to Agentic Context Management — Letta](https://www.letta.com/blog/memory-blocks)
- [Understanding memory management — Letta Docs](https://docs.letta.com/advanced/memory-management/)
- [Introduction to Stateful Agents — Letta Docs](https://docs.letta.com/guides/agents/memory/)
- [Types of AI Agent Memory: Semantic, Episodic, Procedural — Atlan](https://atlan.com/know/types-of-ai-agent-memory/)
- [AI agent memory: types, architecture and implementation — Redis Blog](https://redis.io/blog/ai-agent-memory-stateful-systems/)
- [Build agents to learn from experiences using Amazon Bedrock AgentCore episodic memory — AWS Blog](https://aws.amazon.com/blogs/machine-learning/build-agents-to-learn-from-experiences-using-amazon-bedrock-agentcore-episodic-memory/)
- [Beyond Short-term Memory: The 3 Types of Long-term Memory AI Agents Need — MachineLearningMastery](https://machinelearningmastery.com/beyond-short-term-memory-the-3-types-of-long-term-memory-ai-agents-need/)
- [Stateful Agents: The Missing Link in LLM Intelligence — Letta](https://www.letta.com/blog/stateful-agents)

---

**Próximo conceito** → [O Critério de Posicionamento no Espectro](../05-o-criterio-de-posicionamento-no-espectro/CONTENT.md)
