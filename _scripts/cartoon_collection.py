"""Render the public cartoon overview and its native slide sequence.

Individual image-piece readers remain their canonical, durable URLs.  Slides
are a collection presentation of those same works and canonically point back
to the individual reader.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
import re

import image_pieces
import paper_site

ROOT = Path(__file__).resolve().parents[1]
BASE = "is/writing/cartoons"
OVERVIEW_ROUTE = "/is/writing/cartoons/"
SLIDES_ROUTE = "/is/writing/cartoons/slides/"


def ordered(catalog: dict) -> list[dict]:
    pieces = catalog.get("pieces", [])
    if not pieces:
        raise ValueError("cartoon collection needs at least one image piece")
    return sorted(pieces, key=lambda piece: piece["published_date"], reverse=True)


def collection_head(title: str, canonical: str, *, piece: dict | None = None) -> str:
    """Use the house head, replacing collection-specific canonical/social data."""
    head = paper_site.head("writing")
    # Writing's hash controller hides the normal Writing sections. Collection
    # routes have their own #cartoon / #piece anchors, so never inherit it.
    head = re.sub(r'\s*<script src="[^"]*/writing\.js[^"]*" defer></script>', '', head)
    head = re.sub(r"<title>.*?</title>", f"<title>{escape(title)}</title>", head, count=1)
    head = re.sub(r'<link rel="canonical" href="[^"]+">', f'<link rel="canonical" href="https://ajin.im{canonical}">', head, count=1)
    head = re.sub(r'<meta property="og:title" content="[^"]+">', f'<meta property="og:title" content="{escape(title, quote=True)}">', head, count=1)
    head = re.sub(r'<meta property="og:url" content="[^"]+">', f'<meta property="og:url" content="https://ajin.im{canonical}">', head, count=1)
    if piece:
        image = escape(piece["image"], quote=True)
        head = re.sub(r'<meta property="og:image" content="[^"]+">', f'<meta property="og:image" content="https://ajin.im{image}">', head, count=1)
        head = re.sub(r'<meta property="og:image:width" content="[^"]+">', f'<meta property="og:image:width" content="{piece["width"]}">', head, count=1)
        head = re.sub(r'<meta property="og:image:height" content="[^"]+">', f'<meta property="og:image:height" content="{piece["height"]}">', head, count=1)
        head = re.sub(r'<meta property="og:image:alt" content="[^"]+">', f'<meta property="og:image:alt" content="{escape(piece["alt"], quote=True)}">', head, count=1)
    collection_css = f'<link rel="stylesheet" href="{paper_site.asset("cartoons.css")}">'
    if "cartoons.css" not in head:
        head += "\n" + collection_css
    return head


def arrow(piece: dict | None, direction: str) -> str:
    if not piece:
        return f'<span class="slide-arrow-spacer slide-{direction}" aria-hidden="true"></span>'
    label = f'{direction.capitalize()} cartoon: {piece["title"]}'
    points = "15 4 7 12 15 20" if direction == "previous" else "9 4 17 12 9 20"
    return f'''<a class="slide-arrow slide-{direction}" data-slide-{direction}
      href="{SLIDES_ROUTE}{piece['slug']}/#cartoon" target="_self" aria-label="{escape(label, quote=True)}"><svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false"><polyline points="{points}" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></a>'''


def image(piece: dict, css_class: str = "", *, lazy: bool = False) -> str:
    classes = f' class="{css_class}"' if css_class else ""
    loading = 'lazy' if lazy else 'eager'
    return f'<img{classes} src="{escape(piece["image"], quote=True)}" alt="{escape(piece["alt"], quote=True)}" width="{piece["width"]}" height="{piece["height"]}" decoding="async" loading="{loading}">'


def mobile_panels(piece: dict) -> str:
    if piece.get("mobile_panels") != 2:
        return ""
    src = escape(piece["image"], quote=True)
    return f'''<span class="slide-panels" aria-hidden="true">
      <span><img src="{src}" alt="" width="{piece['width']}" height="{piece['height']}"></span>
      <span><img src="{src}" alt="" width="{piece['width']}" height="{piece['height']}"></span>
    </span>'''


def overview_page(pieces: list[dict]) -> str:
    entries = []
    for index, piece in enumerate(pieces):
        caption = f'<figcaption class="cartoon-caption external-caption">{escape(piece["caption"])}</figcaption>' if piece["caption"] else ""
        art_class = "austen-art" if piece["slug"] == "austen-at-work" else ""
        entries.append(f'''<li id="{piece['slug']}"><a class="cartoon-preview" href="{SLIDES_ROUTE}{piece['slug']}/#cartoon" target="_self" aria-label="Open {escape(piece['title'], quote=True)}">
          <h3 class="preview-title">{escape(piece['title'])}</h3><figure>{image(piece, art_class, lazy=index >= 2)}{caption}</figure></a></li>''')
    head = collection_head("Cartoons · ajin.im", OVERVIEW_ROUTE)
    return f'''<!doctype html><html lang="en" data-paper="blue"><head>{head}</head><body class="paper-page page-cartoons">
<a class="skip-link" href="#main">Skip to content</a>{paper_site.header('writing')}
<main class="cartoon-gallery wrap" id="main" aria-labelledby="gallery-title"><header class="gallery-heading"><h1 class="visually-hidden" id="gallery-title">Cartoons</h1><a class="gallery-view-link" href="{SLIDES_ROUTE}#cartoon" target="_self">One at a time →</a></header><ol class="cartoon-grid">{''.join(entries)}</ol></main>
<footer class="foot gallery-footer"><p class="gallery-credit">{escape(image_pieces.CREDIT)}</p><div class="collection-footer-links"><a class="collection-back" href="/is/writing/#cartoons" target="_self">← Back to writing</a></div></footer></body></html>'''


def slide_page(pieces: list[dict], index: int) -> str:
    piece = pieces[index]
    previous = pieces[index - 1] if index else None
    following = pieces[index + 1] if index + 1 < len(pieces) else None
    head = collection_head(f'{piece["title"]} · Cartoons · ajin.im', piece['href'], piece=piece)
    head += f'\n<script src="{paper_site.asset("cartoons.js")}" defer></script>'
    image_class = "slide-image" + (" austen-art" if piece["slug"] == "austen-at-work" else "") + (" with-mobile-panels" if piece.get("mobile_panels") == 2 else "")
    caption = f'<figcaption>{escape(piece["caption"])}</figcaption>' if piece["caption"] else ""
    return f'''<!doctype html><html lang="en" data-paper="blue" class="slide-document"><head>{head}</head><body class="paper-page page-slides">
<a class="skip-link" href="#cartoon">Skip to cartoon</a>{paper_site.header('writing')}
<main class="slide-shell wrap" id="cartoon" aria-labelledby="slide-title" data-first-slide="{SLIDES_ROUTE}{pieces[0]['slug']}/"><div class="slide-context"><h1 id="slide-title">{escape(piece['title'])}</h1><a href="{OVERVIEW_ROUTE}#{piece['slug']}" target="_self">All cartoons</a></div><article aria-labelledby="slide-title"><figure class="slide-art"><div class="slide-stage" style="--slide-ratio:{piece['width'] / piece['height']}">{arrow(previous, 'previous')}<a class="slide-image-link" href="{escape(piece['image'], quote=True)}" target="_blank" rel="noopener" aria-label="Open full-size image: {escape(piece['alt'], quote=True)}">{image(piece, image_class)}{mobile_panels(piece)}</a>{arrow(following, 'next')}</div>{caption}</figure><nav class="slide-pagination" aria-label="Cartoon sequence">{arrow(previous, 'previous')}<span class="slide-position" aria-label="Cartoon {index + 1} of {len(pieces)}">{index + 1} / {len(pieces)}</span>{arrow(following, 'next')}</nav><div class="slide-bottom"><p>{escape(image_pieces.CREDIT)}</p><a class="collection-back" href="/is/writing/#cartoons" target="_self">← Back to writing</a></div></article></main></body></html>'''


def expected_pages(catalog: dict | None = None) -> dict[str, str]:
    pieces = ordered(catalog if catalog is not None else image_pieces.load_catalog())
    pages = {f'{BASE}/index.html': overview_page(pieces)}
    for index, piece in enumerate(pieces):
        pages[f'{BASE}/slides/{piece["slug"]}/index.html'] = slide_page(pieces, index)
    pages[f'{BASE}/slides/index.html'] = slide_page(pieces, 0)
    return pages
