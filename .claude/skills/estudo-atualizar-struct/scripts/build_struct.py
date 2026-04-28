#!/usr/bin/env python3
"""
build_struct.py — Reconstroi `STRUCT.md` na raiz de um livro de estudo.

STRUCT.md eh um indice em formato de arvore dos capitulos, subcapitulos e
conceitos materializados no disco, com uma descricao de 1 linha em cada
no. As descricoes sao extraidas das listagens curadas do CONTENT.md/
INTRODUCTION.md do diretorio pai (## Capitulos, ## Subcapitulos,
## Conceitos). Quando ainda nao existe listagem, cai para o H1 do
proprio CONTENT.md como fallback.

Uso:
  python build_struct.py <book-dir>

<book-dir> precisa conter `INTRODUCTION.md`. O script varre subdiretorios
em qualquer profundidade que sigam o padrao `NN-slug/`.
"""

import argparse
import re
import sys
from pathlib import Path


SLUG_RE = re.compile(r'^\d{2}-')

# Captura itens "1. [Nome](slug/CONTENT.md) - descricao" tolerando travessao
# longo (em-dash) ou hifen e qualquer numero de espacos em volta.
LIST_ITEM_RE = re.compile(
    r'^\d+\.\s+\[(?P<name>[^\]]+)\]\((?P<path>[^)]+)\)\s*[\u2014\-]\s*(?P<desc>.*)$'
)


def find_subdirs(parent: Path):
    """Retorna subdirs cujo nome comeca com NN- (ordenados pelo prefixo)."""
    if not parent.is_dir():
        return []
    return sorted(
        (p for p in parent.iterdir() if p.is_dir() and SLUG_RE.match(p.name)),
        key=lambda p: p.name,
    )


def read_h1(md_path: Path) -> str:
    """Primeira linha que comeca com '# ' do markdown, ou '' se nao houver."""
    if not md_path.is_file():
        return ''
    for line in md_path.read_text(encoding='utf-8').splitlines():
        if line.startswith('# '):
            return line[2:].strip()
    return ''


def parse_listing(md_path: Path, section_title: str) -> dict:
    """
    Le `md_path` e devolve {slug: descricao} para os itens da secao
    `## <section_title>`. Retorna {} se a secao nao existe.
    """
    if not md_path.is_file():
        return {}
    content = md_path.read_text(encoding='utf-8')
    lines = content.splitlines()
    section_re = re.compile(rf'^##\s+{re.escape(section_title)}\s*$')
    items = {}
    in_section = False
    for line in lines:
        if section_re.match(line):
            in_section = True
            continue
        if in_section and line.startswith('## '):
            break
        if not in_section:
            continue
        m = LIST_ITEM_RE.match(line.strip())
        if not m:
            continue
        path = m.group('path')
        slug = path.split('/')[0]
        items[slug] = m.group('desc').strip()
    return items


def description_for(dir_path: Path, parent_listing: dict) -> str:
    """
    Resolve a descricao de 1 linha para `dir_path`. Tenta a listagem do pai
    primeiro; cai para o H1 do CONTENT.md proprio se ausente.
    """
    desc = parent_listing.get(dir_path.name, '').strip()
    if desc:
        return desc
    title = read_h1(dir_path / 'CONTENT.md')
    return title or '(sem descricao)'


def render_tree(book_dir: Path) -> str:
    """Monta o conteudo completo do STRUCT.md."""
    book_intro = book_dir / 'INTRODUCTION.md'
    book_title = read_h1(book_intro) or book_dir.name
    chapter_listing = parse_listing(book_intro, 'Capítulos')

    out = []
    out.append('# Estrutura do Livro')
    out.append('')
    out.append(
        '> Mapa rapido da organizacao do livro: capitulos, subcapitulos e '
        'conceitos. Mantido automaticamente pela skill `estudo-atualizar-struct` '
        '— nao edite a mao.'
    )
    out.append('')
    out.append('```')
    out.append(f'{book_dir.name}/ — {book_title}')

    chapters = find_subdirs(book_dir)
    for ci, chapter in enumerate(chapters):
        is_last_chap = ci == len(chapters) - 1
        chap_branch = '└── ' if is_last_chap else '├── '
        chap_pipe = '    ' if is_last_chap else '│   '
        out.append(f'{chap_branch}{chapter.name}/ — {description_for(chapter, chapter_listing)}')

        sub_listing = parse_listing(chapter / 'CONTENT.md', 'Subcapítulos')
        subs = find_subdirs(chapter)
        for si, sub in enumerate(subs):
            is_last_sub = si == len(subs) - 1
            sub_branch = '└── ' if is_last_sub else '├── '
            sub_pipe = '    ' if is_last_sub else '│   '
            out.append(
                f'{chap_pipe}{sub_branch}{sub.name}/ — {description_for(sub, sub_listing)}'
            )

            concept_listing = parse_listing(sub / 'CONTENT.md', 'Conceitos')
            concepts = find_subdirs(sub)
            for ki, concept in enumerate(concepts):
                is_last_k = ki == len(concepts) - 1
                k_branch = '└── ' if is_last_k else '├── '
                out.append(
                    f'{chap_pipe}{sub_pipe}{k_branch}{concept.name}/ — '
                    f'{description_for(concept, concept_listing)}'
                )

    out.append('```')
    out.append('')
    return '\n'.join(out)


def main():
    parser = argparse.ArgumentParser(
        description='Reconstroi STRUCT.md na raiz de um livro de estudo.'
    )
    parser.add_argument(
        'book_dir',
        help='Caminho do diretorio do livro (deve conter INTRODUCTION.md).',
    )
    args = parser.parse_args()

    book_dir = Path(args.book_dir).expanduser().resolve()
    if not (book_dir / 'INTRODUCTION.md').is_file():
        print(
            f'Erro: {book_dir}/INTRODUCTION.md nao encontrado. '
            'Aponte para o diretorio raiz do livro.',
            file=sys.stderr,
        )
        sys.exit(1)

    content = render_tree(book_dir)
    struct_path = book_dir / 'STRUCT.md'
    struct_path.write_text(content, encoding='utf-8')
    print(str(struct_path))


if __name__ == '__main__':
    main()
