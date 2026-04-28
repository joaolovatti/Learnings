#!/usr/bin/env python3
"""
compute_next_link.py — Anexa um bloco "Proximo" ao fim do CONCEPTS.md de um subcapitulo.

Regra de navegacao (nesta ordem):
  1. Proximo subcapitulo no mesmo capitulo (link para o CONTENT.md do subcap).
  2. Senao, proximo capitulo no livro (link para o CONTENT.md do capitulo).
  3. Senao, fim do livro.

O texto do link vem do H1 do CONTENT.md de destino. O caminho eh relativo ao
diretorio do subcapitulo atual, usando barras POSIX (/), para o link funcionar
tanto no sistema de arquivos quanto em qualquer renderizador de Markdown.

Uso:
  python compute_next_link.py <subchapter-dir> [--apply]

Sem `--apply`, imprime o bloco em stdout.
Com `--apply`, anexa (ou substitui, se ja existir um bloco anterior)
o bloco ao CONCEPTS.md do subcapitulo. A operacao eh idempotente.

Compatibilidade: este script foi simplificado quando o metodo abandonou o
modelo de um diretorio por conceito. Hoje, conceitos vivem como secoes H2
dentro de CONCEPTS.md no proprio diretorio do subcapitulo, e por isso a
unica regra de "proximo" relevante eh a do proximo subcapitulo (ou
proximo capitulo, ou fim do livro).
"""

import argparse
import os
import re
import sys
from pathlib import Path


SLUG_RE = re.compile(r"^\d{2}-")

# Marcadores do bloco "Proximo". Precisam bater com o que `_format_block`
# emite para que reaplicar o script substitua o bloco em vez de duplicar.
BLOCK_MARKER_RE = re.compile(
    r"\n---\n\n\*\*Pr(?:o|\u00f3)ximo (?:subcap(?:i|\u00ed)tulo|cap(?:i|\u00ed)tulo)\*\*[\s\S]*$"
)
END_MARKER_RE = re.compile(r"\n---\n\n_Fim do livro\.[\s\S]*$")


def _ordered_children(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        (p for p in directory.iterdir() if p.is_dir() and SLUG_RE.match(p.name)),
        key=lambda p: p.name,
    )


def _read_h1(content_md: Path) -> str | None:
    if not content_md.is_file():
        return None
    for line in content_md.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            return stripped[2:].strip()
    return None


def _relative_posix(target: Path, start: Path) -> str:
    rel = os.path.relpath(target, start)
    return rel.replace(os.sep, "/")


def _format_block(kind: str, title: str, rel_path: str) -> str:
    label = {
        "subchapter": "Próximo subcapítulo",
        "chapter": "Próximo capítulo",
    }[kind]
    return f"---\n\n**{label}** → [{title}]({rel_path})\n"


def compute(subchapter_dir: Path) -> str:
    """Return the markdown block to append (already ending with newline)."""
    subchapter_dir = subchapter_dir.resolve()
    if not subchapter_dir.is_dir():
        raise FileNotFoundError(f"subchapter directory not found: {subchapter_dir}")

    chapter_dir = subchapter_dir.parent
    book_dir = chapter_dir.parent

    # 1. Proximo subcapitulo no mesmo capitulo.
    sub_siblings = _ordered_children(chapter_dir)
    if subchapter_dir in sub_siblings:
        sub_idx = sub_siblings.index(subchapter_dir)
        if sub_idx + 1 < len(sub_siblings):
            nxt = sub_siblings[sub_idx + 1] / "CONTENT.md"
            title = _read_h1(nxt) or sub_siblings[sub_idx + 1].name
            return _format_block("subchapter", title, _relative_posix(nxt, subchapter_dir))

    # 2. Proximo capitulo no livro.
    chap_siblings = _ordered_children(book_dir)
    if chapter_dir in chap_siblings:
        chap_idx = chap_siblings.index(chapter_dir)
        if chap_idx + 1 < len(chap_siblings):
            nxt = chap_siblings[chap_idx + 1] / "CONTENT.md"
            title = _read_h1(nxt) or chap_siblings[chap_idx + 1].name
            return _format_block("chapter", title, _relative_posix(nxt, subchapter_dir))

    # 3. Fim do livro.
    return "---\n\n_Fim do livro. Parabéns pela jornada._\n"


def apply_to_concepts(subchapter_dir: Path) -> Path:
    """Rewrite subchapter CONCEPTS.md so it ends with the current 'Proximo' block."""
    concepts_md = subchapter_dir / "CONCEPTS.md"
    if not concepts_md.is_file():
        raise FileNotFoundError(f"CONCEPTS.md not found: {concepts_md}")

    block = compute(subchapter_dir)
    text = concepts_md.read_text(encoding="utf-8")

    # Remove qualquer bloco "Proximo"/"Fim do livro" ja presente para manter idempotencia.
    text = BLOCK_MARKER_RE.sub("", text)
    text = END_MARKER_RE.sub("", text)

    text = text.rstrip() + "\n\n" + block
    concepts_md.write_text(text, encoding="utf-8")
    return concepts_md


def main() -> int:
    # Arquivos sao sempre gravados em UTF-8, mas stdout no Windows cai em cp1252 por
    # padrao e engasga com setas/acentos. Forcamos UTF-8 se o stream suportar.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Compute/apply the 'Proximo' navigation block for a subchapter CONCEPTS.md."
    )
    parser.add_argument("subchapter_dir", help="Path to the subchapter directory.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Rewrite the subchapter CONCEPTS.md with the block appended (idempotent).",
    )
    args = parser.parse_args()

    subchapter_dir = Path(args.subchapter_dir)

    try:
        if args.apply:
            written = apply_to_concepts(subchapter_dir)
            print(str(written))
        else:
            sys.stdout.write(compute(subchapter_dir))
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
