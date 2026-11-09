"""Build Writing and Building from committed catalogs and the essay registry.

Explicit publishing owns these outputs. Daily running sync calls build_root
only and must never rewrite these sections.
"""
from pathlib import Path
import argparse

import build_writes
import image_pieces
import paper_site

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT
ALIASES = ('comedy', 'desk', 'loose', 'essays')


def redirect_page():
    return '''<!doctype html>
<!-- GENERATED FILE: DO NOT EDIT. Built by _scripts/build_sections.py. -->
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Writing by Ajin</title><meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0;url=/is/writing/#all">
<link rel="canonical" href="https://ajin.im/is/writing/">
</head><body><p><a href="/is/writing/#all" target="_self">All writing by Ajin</a></p></body></html>
'''


def expected_sections():
    result = {}
    for page, body in [('writing', paper_site.render_writing(build_writes.collect_items())),
                       ('building', paper_site.render_building())]:
        template = (ROOT / 'templates' / f'{page}.html').read_text()
        output = template.replace('{{paper_head}}', paper_site.head(page)).replace('{{paper_body}}', body)
        if '{{' in output:
            raise ValueError(f'unresolved token in {page}')
        banner = f'<!-- GENERATED FILE: DO NOT EDIT. Source: templates/{page}.html, content catalogs and _scripts/paper_site.py. Built by _scripts/build_sections.py. -->\n'
        output = output.replace('<!doctype html>\n', '<!doctype html>\n' + banner, 1)
        result[f'is/{page}/index.html'] = output
    for alias in ALIASES:
        result[f'is/writing/{alias}/index.html'] = redirect_page()
    for piece in image_pieces.load_catalog(root=ROOT)["pieces"]:
        result[f'is/writing/{piece["slug"]}/index.html'] = image_pieces.render_piece(piece)
    return result


def build(check=False):
    for relative, output in expected_sections().items():
        path = OUTPUT_ROOT / relative
        if check:
            if not path.is_file() or path.read_text() != output:
                raise ValueError(f'{relative} is stale; run _scripts/build_sections.py')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(output)
            print(f'built {path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    build(check=parser.parse_args().check)
