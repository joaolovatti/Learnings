---
name: gerar-imagem
description: Gera uma imagem via API da OpenAI (gpt-image-1-mini, quality=medium) a partir de um prompt textual e salva no caminho indicado. Use esta skill sempre que o usuário pedir para "gerar uma imagem", "criar uma ilustração", "fazer uma capa", "desenhar uma cena", "produzir um visual", ou quando outra skill precisar materializar uma imagem (ex: capa de livro em `estudo-listar-dominios`, thumbnail, ilustração de conceito). Dispare também quando o pedido mencionar "imagem de X", "figura para Y", "arte visual", "render", "cover art" — mesmo que o usuário não diga explicitamente "gerar". É uma skill utilitária reutilizável, pensada para ser composta por outras skills.
---

# gerar-imagem

Skill utilitária que gera uma imagem via OpenAI e salva num caminho do disco. Desenhada para ser **reutilizada** por outras skills (ex: `estudo-listar-dominios` usa ela para gerar a capa do livro) e também invocável diretamente pelo usuário.

## Quando usar

- Usuário pede explicitamente: "gera uma imagem de X", "cria uma ilustração de Y", "faz uma capa para Z".
- Outra skill precisa de uma imagem como parte do seu fluxo — a skill consumidora invoca esta.
- Há um prompt textual razoavelmente descritivo e um caminho de destino definido (ou passível de ser definido a partir do contexto).

## Entradas

Três parâmetros:

1. **prompt** (obrigatório) — descrição textual da imagem. Idealmente em inglês (modelos de imagem rendem melhor em EN), mas funciona em pt-BR.
2. **output** (obrigatório) — caminho completo do arquivo PNG de saída. Ex: `./meu-livro/cover.png`. O diretório pai é criado se não existir.
3. **size** (opcional) — padrão `1536x1024` (landscape). Valores aceitos: `1024x1024`, `1536x1024`, `1024x1536`.

Se alguma entrada estiver faltando (ex: o usuário disse "gera uma imagem" sem descrever do quê ou sem dizer onde salvar), **pergunte uma vez** o que falta antes de prosseguir.

## Como gerar

Execute o script `scripts/generate_image.py` via `Bash`:

```bash
python .claude/skills/gerar-imagem/scripts/generate_image.py \
  --prompt "<prompt em ingles descrevendo a cena>" \
  --output "<caminho/para/arquivo.png>" \
  --size 1536x1024
```

O script:
- Lê `OPENAI_API_KEY` do `.env` mais próximo (sobe diretórios a partir do `--output`).
- Chama `POST https://api.openai.com/v1/images/generations` com modelo `gpt-image-1-mini` e `quality=medium`.
- Decodifica o `b64_json` da resposta e salva o PNG no caminho indicado.
- Imprime o caminho absoluto do arquivo no stdout.

## Guia para escrever bons prompts

Os modelos de imagem rendem muito mais quando o prompt é:

- **Em inglês** — a maioria do treinamento está em EN; termos técnicos e estilísticos são mais reconhecidos.
- **Específico sobre estilo** — "digital painting", "isometric illustration", "watercolor", "minimal geometric composition", "cinematic photograph", "oil painting". Escolha um e mantenha.
- **Descritivo quanto à cena** — sujeito, ação, ambiente, iluminação, paleta. Ex: "a vast library of glowing books floating in a cosmic void, deep blues and warm gold highlights, dramatic lighting".
- **Explícito sobre o que evitar** — imagens de IA frequentemente inserem texto indesejado. Adicione `"no text, no letters, no words, no typography"` quase sempre.
- **Sem elementos contraditórios** — se pedir "calm minimal" e "vibrant chaotic" na mesma frase, o modelo confunde.

Para **capas/covers** (landscape), prefira metáforas visuais em vez de fotografia literal — o objetivo é evocar o conceito, não ilustrá-lo de forma redundante.

## Composição com outras skills

Outras skills podem invocar esta de duas formas equivalentes:

1. **Via Skill tool** — útil quando a skill consumidora quer delegar a decisão de prompt para aqui. Exemplo: `Skill(gerar-imagem, "prompt: ..., output: ...")`.
2. **Executando o script direto** — útil quando a skill consumidora já sabe exatamente o prompt. Basta rodar `python .claude/skills/gerar-imagem/scripts/generate_image.py --prompt "..." --output "..."`.

Em ambos os casos, o contrato é: **prompt + output path → PNG salvo no disco**.

## Saída ao usuário

Após a geração, informe em uma linha:

> _Imagem gerada em `<caminho absoluto>`._

Não descreva a imagem (o usuário vai abri-la). Não inline a imagem em base64 na resposta.

## O que evitar

- **Não** gerar sem ter um caminho de saída claro — sempre pergunte se faltar.
- **Não** inventar outro modelo — `gpt-image-1-mini` é o padrão deste projeto.
- **Não** remover `quality=medium` do payload sem pedido explícito do usuário.
- **Não** inserir texto dentro da imagem a menos que o prompt peça — adicione `"no text"` por padrão.
- **Não** tentar embutir a lógica Python no SKILL.md — o código vive em `scripts/generate_image.py`.
