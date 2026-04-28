"""Gera uma imagem via OpenAI (gpt-image-1-mini, quality=medium) e salva no caminho indicado.

Uso:
    python generate_image.py --prompt "<descricao>" --output <caminho/arquivo.png> [--size 1536x1024]

Tamanhos validos: 1024x1024 (quadrado), 1536x1024 (landscape), 1024x1536 (portrait).
Le OPENAI_API_KEY do .env (procura subindo a partir de --output ate encontrar).
Imprime o caminho absoluto do arquivo salvo no stdout.
"""

import argparse
import base64
import json
import os
import pathlib
import sys
import urllib.request
import urllib.error


VALID_SIZES = {"1024x1024", "1536x1024", "1024x1536"}


def load_env(start: pathlib.Path) -> None:
    for parent in [start, *start.parents]:
        env_path = parent / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            return
    raise FileNotFoundError(
        "Arquivo .env nao encontrado subindo a partir de " + str(start)
    )


def generate(output: pathlib.Path, prompt: str, size: str) -> pathlib.Path:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY ausente no ambiente/.env")

    if size not in VALID_SIZES:
        raise ValueError(f"size invalido: {size}. Use um de {sorted(VALID_SIZES)}")

    payload = json.dumps(
        {
            "model": "gpt-image-1-mini",
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": "high",
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(
            f"OpenAI API HTTP {e.code}: {e.read().decode('utf-8', 'replace')}"
        ) from e

    b64 = body["data"][0]["b64_json"]
    img_bytes = base64.b64decode(b64)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(img_bytes)
    return output


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--prompt", required=True, help="Prompt descritivo (idealmente em ingles)"
    )
    p.add_argument(
        "--output",
        required=True,
        help="Caminho do arquivo de saida (ex: ./dir/cover.png)",
    )
    p.add_argument(
        "--size",
        default="1536x1024",
        choices=sorted(VALID_SIZES),
        help="Tamanho da imagem",
    )
    args = p.parse_args()

    output = pathlib.Path(args.output).resolve()
    load_env(output.parent if output.parent.exists() else pathlib.Path.cwd())
    out = generate(output, args.prompt, args.size)
    print(str(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
