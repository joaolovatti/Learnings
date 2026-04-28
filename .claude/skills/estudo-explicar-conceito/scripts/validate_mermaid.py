#!/usr/bin/env python3
"""
validate_mermaid.py — Lint dos blocos Mermaid de um arquivo Markdown.

Checa as armadilhas recorrentes que a skill estudo-explicar-conceito
e seus agentes geram com frequencia:

  1. Palavras reservadas (loop, alt, opt, par, critical, break, rect, note)
     usadas como nome de participant/actor em diagramas de sequencia.
  2. Hifen em nome de participant/actor (Mermaid so aceita
     [A-Za-z_][A-Za-z0-9_]* em ids).
  3. Literal "\\n" dentro de labels (Mermaid nao expande — quebra o parse).
  4. Ponto-e-virgula ";" dentro de texto de "Note over ..." (Mermaid trata
     como separador de instrucao).
  5. Setas invalidas em sequenceDiagram (variantes com dashes/chevrons em
     numero errado, ex: '--->>', '->>>', '<->').

Uso:
  python validate_mermaid.py <arquivo.md>

Saida:
  - Sem violacoes: nada no stdout, exit code 0.
  - Com violacoes: cada uma listada no stderr, exit code 1.
  - Erro de I/O / arquivo nao encontrado: exit code 2.
"""

import argparse
import re
import sys
from pathlib import Path


RESERVED = {"loop", "alt", "opt", "par", "critical", "break", "rect", "note"}

MERMAID_BLOCK_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
# Identificador valido (alfanumerico+underscore).
PARTICIPANT_RE = re.compile(
    r"^\s*(?:participant|actor)\s+([A-Za-z_]\w*)",
    re.MULTILINE,
)
# Pega o primeiro token apos participant/actor mesmo que contenha caracteres
# invalidos (hifen, etc.) — usado para detectar ids malformados.
PARTICIPANT_LOOSE_RE = re.compile(
    r"^\s*(?:participant|actor)\s+(\S+)",
    re.MULTILINE,
)
# Captura o texto apos o ":" obrigatorio de "Note over <ids>: <texto>".
# Mermaid usa o primeiro ":" como separador, entao [^:\n]+ ate o primeiro ":".
NOTE_OVER_RE = re.compile(
    r"(?im)^\s*note\s+over\s+[^:\n]+:\s*(.*)$"
)
LITERAL_NL_RE = re.compile(r"\\n")
SEQUENCE_HEADER_RE = re.compile(r"^\s*sequenceDiagram\b", re.MULTILINE)
# Setas validas em sequenceDiagram (Mermaid):
#   ->, -->, ->>, -->>, -x, --x, -), --)
VALID_SEQ_ARROWS = {"->", "-->", "->>", "-->>", "-x", "--x", "-)", "--)"}
# Padrao de "linha de mensagem": <ator> <seta> <ator>: <texto>.
# Captura a seta no meio para validar.
SEQ_ARROW_RE = re.compile(
    r"^\s*[A-Za-z_]\w*\s*([-<>x)]+)\s*[A-Za-z_]\w*\s*:",
    re.MULTILINE,
)


def lint(text: str) -> list[str]:
    violations: list[str] = []
    for i, m in enumerate(MERMAID_BLOCK_RE.finditer(text), start=1):
        block = m.group(1)
        block_label = f"mermaid block #{i}"

        for pm in PARTICIPANT_RE.finditer(block):
            name = pm.group(1)
            if name.lower() in RESERVED:
                violations.append(
                    f"{block_label}: palavra reservada '{name}' usada como "
                    f"nome de participant/actor "
                    f"(reservadas: {', '.join(sorted(RESERVED))}). "
                    f"Renomeie (ex: '{name}' -> '{name.capitalize()}_Principal')."
                )

        for pm in PARTICIPANT_LOOSE_RE.finditer(block):
            raw = pm.group(1)
            if "-" in raw:
                fixed = raw.replace("-", "_")
                violations.append(
                    f"{block_label}: hifen no id de participant/actor: '{raw}' "
                    f"(Mermaid so aceita [A-Za-z_][A-Za-z0-9_]* em ids). "
                    f"Renomeie (ex: '{raw}' -> '{fixed}'); para o label visivel "
                    f"use 'as \"...\"'."
                )

        for line_no, line in enumerate(block.splitlines(), start=1):
            if LITERAL_NL_RE.search(line):
                violations.append(
                    f"{block_label}: '\\n' literal na linha {line_no}: "
                    f"{line.strip()!r}. Encurte o label ou divida em dois nos."
                )

        for nm in NOTE_OVER_RE.finditer(block):
            note_text = nm.group(1)
            if ";" in note_text:
                violations.append(
                    f"{block_label}: ';' dentro de 'Note over' "
                    f"(parser interpreta como separador de instrucao). "
                    f"Use virgula ou reformule. Texto: {note_text!r}"
                )

        if SEQUENCE_HEADER_RE.search(block):
            for am in SEQ_ARROW_RE.finditer(block):
                arrow = am.group(1)
                if arrow not in VALID_SEQ_ARROWS:
                    violations.append(
                        f"{block_label}: seta invalida '{arrow}' em sequenceDiagram "
                        f"(validas: {', '.join(sorted(VALID_SEQ_ARROWS))})."
                    )

    return violations


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Lint dos blocos Mermaid de um arquivo Markdown."
    )
    parser.add_argument("path", help="Caminho do arquivo .md a validar.")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.is_file():
        print(f"error: arquivo nao encontrado: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    violations = lint(text)
    if not violations:
        return 0

    print(
        f"Encontradas {len(violations)} violacao(oes) Mermaid em {path}:",
        file=sys.stderr,
    )
    for v in violations:
        print(f"  - {v}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
