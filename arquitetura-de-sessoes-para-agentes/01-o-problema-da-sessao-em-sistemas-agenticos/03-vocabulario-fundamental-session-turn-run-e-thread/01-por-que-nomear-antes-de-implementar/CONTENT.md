# Por que nomear antes de implementar

![capa](cover.png)

Um bug de arquitetura que não tem nome é um bug que volta sempre. Não porque o desenvolvedor seja descuidado, mas porque sem uma palavra precisa para designar o problema, cada tentativa de correção mira num sintoma diferente — e o núcleo da questão permanece intocado. Este é o ponto de partida do vocabulário que este subcapítulo vai fixar: antes de definir o que é uma session, um turn, um run ou uma thread, vale entender por que essas definições precisam existir em primeiro lugar.

O leitor que chegou até aqui já acumulou dois insumos importantes dos subcapítulos anteriores: a convicção de que agentes sem estado persistido falham de maneiras estruturais (não acidentais), e o reconhecimento dos sintomas concretos — perda de contexto entre tool calls, perguntas repetidas, decisões contraditórias em turnos consecutivos. O que esses dois subcapítulos descreveram foi essencialmente a fenomenologia do problema: como ele aparece. O que este subcapítulo trata é de nomear a etiologia — a estrutura causal por baixo dos sintomas.

A relação entre vocabulário e capacidade de resolver problemas não é metafórica. É mecânica. Quando um engenheiro diz "o agente está perdendo contexto", a afirmação é tecnicamente verdadeira mas diagnósticamente vaga: não indica em qual camada o estado está ausente, não distingue se a perda ocorre entre turns ou entre runs dentro de um mesmo turn, e não aponta se o problema é de persistência, de projeção ou de serialização. Três bugs arquiteturalmente distintos cabem nessa descrição. Três correções diferentes seriam necessárias. Mas com um vocabulário impreciso, a tendência é aplicar a mesma solução nos três casos — geralmente "passe mais histórico" — e se surpreender quando o problema persiste.

O Domain-Driven Design formalizou esse princípio como linguagem ubíqua (*ubiquitous language*): a ideia de que quando equipes de software usam o mesmo vocabulário para os mesmos conceitos — nas discussões, no código, nos documentos — a fricção de tradução desaparece e os bugs de comunicação deixam de existir. O princípio se aplica com igual força ao vocabulário de um único engenheiro trabalhando na própria arquitetura: quando os nomes que você usa mentalmente são precisos, seu raciocínio sobre o sistema ganha estrutura correspondente.

No contexto específico de sistemas agênticos, a imprecisão tem um custo ainda mais alto, porque os termos em questão — session, turn, run, thread — são usados por frameworks distintos com significados ligeiramente diferentes e às vezes incompatíveis. O LangGraph chama de "thread" o que o Haystack chama de "conversation"; o que a OpenAI Assistants API nomeia como "run" é conceitualmente mais próximo do que alguns frameworks chamam de "turn completo com tool calls"; o que alguns documentos chamam de "session" outros chamam de "context" ou "history". Essa polissemia entre ferramentas não é um problema de documentação ruim — é uma consequência natural de um campo novo onde os termos ainda estão se estabilizando. Mas para o leitor que opera um sistema real, não é aceitável importar essa ambiguidade para dentro do próprio codebase.

A diferença prática aparece no momento do bug. Considere um caso real: o agente executa dois tool calls consecutivos dentro de uma mesma invocação HTTP. O resultado do primeiro tool call não está disponível para o segundo. O desenvolvedor diagnostica como "o agente está perdendo contexto" e adiciona mais histórico de chat na chamada ao LLM. O bug persiste — porque o problema não era de histórico de sessão, mas de como os resultados de tool calls são passados de um ciclo de raciocínio para o próximo dentro de um único run. Esses são dois conceitos distintos (session state vs. run memory), e sem nomes diferentes para eles, a correção errada é quase inevitável.

```
sintoma vago: "o agente perdeu o contexto"
                    |
          diagnóstico impreciso
          (qual contexto? em qual camada?)
                    |
         ┌──────────┴──────────┐
         ↓                     ↓
  entre TURNS              dentro de um TURN
  (session state)          (entre RUNs/tool calls)
         |                     |
  solução: persistir     solução: passar tool
  session object         results corretamente
```

Nomear antes de implementar significa também resistir à tentação de começar a codar antes de ter clareza conceitual. Um session_id adicionado ao código antes de existir uma definição precisa do que a session contém (e do que ela deliberadamente não contém) tende a se transformar num campo que significa coisas diferentes em lugares diferentes do código — às vezes o identificador do usuário, às vezes o identificador da conversa, às vezes uma combinação dos dois. Esse tipo de ambiguidade fossilizada é difícil de remover porque o campo já está em produção, em documentos e em contratos de API.

O valor, portanto, de estabelecer os quatro termos — session, turn, run, thread — com definições precisas e mutuamente exclusivas não é burocrático. É arquitetural. Cada definição vai corresponder a uma responsabilidade distinta no sistema, a uma estrutura de dados específica, a um escopo de vida bem delimitado. Quando o leitor chegar nos capítulos 2 a 12 deste livro e encontrar "session", saberá exatamente a que estrutura aquele termo se refere — e o que não se refere. Essa precisão é o que torna as decisões de design comunicáveis, as code reviews produtivas e os bugs nomeáveis antes que se tornem irreversíveis.

## Fontes utilizadas

- [Ubiquitous Language — Martin Fowler](https://martinfowler.com/bliki/UbiquitousLanguage.html)
- [How Ubiquitous Language Can Solve Your Miscommunication Issues — DEV Community](https://dev.to/juliashevchenko/how-ubiquitous-language-can-solve-your-miscommunication-issues-38fo)
- [Ubiquitous Language and Naming — Enterprise Craftsmanship](https://enterprisecraftsmanship.com/posts/ubiquitous-language-naming/)
- [Naming Things is Hard — Suscosolutions](https://suscosolutions.com/naming-things-is-hard/)
- [Taming Names in Software Development — Simple Thread](https://www.simplethread.com/taming-names-in-software-development/)
- [The Importance of Ubiquitous Language — VMware Tanzu](https://blogs.vmware.com/tanzu/blog-the-importance-of-ubiquitous-language/)

---

**Próximo conceito** → [Session: o container de estado de longa duração](../02-session-o-container-de-estado-de-longa-duracao/CONTENT.md)
