"""Validate and render the image-led pieces in the unified Writing archive."""

from __future__ import annotations

from datetime import date
import hashlib
import html
import json
from pathlib import Path
import re

import writes_common


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "content" / "image-pieces.json"
GENERATOR_MARKER = "<!-- GENERATED IMAGE PIECE: _scripts/image_pieces.py -->"
CREDIT = "Words and ideas by Ajin. Illustrations generated with AI."
_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")


def _fail(message: str) -> None:
    raise ValueError(f"image-pieces catalog: {message}")


def _png_dimensions(path: Path) -> tuple[int, int]:
    with path.open('rb') as image:
        data = image.read(24)
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        _fail(f"{path}: invalid PNG header")
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def _webp_dimensions(path: Path) -> tuple[int, int]:
    with path.open('rb') as image:
        data = image.read(64)
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        _fail(f"{path}: invalid WebP header")
    kind = data[12:16]
    if kind == b"VP8X":
        return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
    if kind == b"VP8 ":
        if data[23:26] != b"\x9d\x01\x2a":
            _fail(f"{path}: invalid VP8 WebP header")
        return int.from_bytes(data[26:28], "little") & 0x3FFF, int.from_bytes(data[28:30], "little") & 0x3FFF
    if kind == b"VP8L":
        if data[20] != 0x2F:
            _fail(f"{path}: invalid VP8L WebP header")
        bits = int.from_bytes(data[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    _fail(f"{path}: unsupported WebP chunk {kind!r}")


def image_dimensions(path: Path) -> tuple[int, int]:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return _png_dimensions(path)
    if suffix == ".webp":
        return _webp_dimensions(path)
    _fail(f"{path}: expected a PNG or WebP image")


def _catalog_image_path(image: object, root: Path) -> tuple[str, Path]:
    if not isinstance(image, str) or not (image.startswith("assets/") or image.startswith("/assets/")):
        _fail("each image must be an assets/... or /assets/... path")
    relative = Path(image.lstrip("/"))
    if relative.is_absolute() or ".." in relative.parts:
        _fail(f"unsafe image path {image!r}")
    path = root / relative
    if not path.is_file():
        _fail(f"image is missing: {image}")
    return '/' + relative.as_posix(), path


def _existing_route_is_owned(slug: str, root: Path) -> bool:
    index = root / "is" / "writing" / slug / "index.html"
    return index.is_file() and GENERATOR_MARKER in index.read_text(encoding="utf-8")


def load_catalog(path: Path | None = None, root: Path | None = None) -> dict:
    """Return a validated catalog, adding each piece's durable public href."""
    root = root or ROOT
    path = path or CATALOG_PATH
    try:
        source = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"image-pieces catalog is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"image-pieces catalog is invalid JSON: {exc}") from exc
    if not isinstance(source, dict) or source.get("schema_version") != 1:
        _fail("schema_version must be 1")
    fallback_slug = source.get("fallback_slug")
    pieces = source.get("pieces")
    if not isinstance(fallback_slug, str) or not _SLUG.fullmatch(fallback_slug):
        _fail("fallback_slug must be a safe slug")
    if not isinstance(pieces, list) or not pieces:
        _fail("pieces must be a non-empty list")

    clean: list[dict] = []
    slugs: set[str] = set()
    required = {"slug", "title", "published_date", "image", "width", "height", "alt", "caption", "featured"}
    optional = {"mobile_panels", "show_title"}
    for piece in pieces:
        if not isinstance(piece, dict) or not required <= set(piece) or set(piece) - required - optional:
            _fail("each piece needs slug, title, published_date, image, width, height, alt, caption, featured; only mobile_panels and show_title are optional")
        slug = piece["slug"]
        if not isinstance(slug, str) or not _SLUG.fullmatch(slug):
            _fail(f"invalid slug {slug!r}")
        if slug in slugs:
            _fail(f"duplicate slug {slug}")
        slugs.add(slug)
        if (root / "is" / "writing" / slug).exists() and not _existing_route_is_owned(slug, root):
            _fail(f"slug {slug} collides with an existing writing route")
        for key in ("title", "alt"):
            if not isinstance(piece[key], str) or not piece[key].strip():
                _fail(f"{slug}: {key} must be non-empty text")
        if not isinstance(piece["caption"], str):
            _fail(f"{slug}: caption must be text")
        published_date = piece["published_date"]
        if not isinstance(published_date, str) or (published_date and not _DATE.fullmatch(published_date)):
            _fail(f"{slug}: published_date must be ISO yyyy-mm-dd or blank")
        if published_date:
            try:
                date.fromisoformat(published_date)
            except ValueError as exc:
                raise ValueError(f"image-pieces catalog: {slug}: invalid published_date") from exc
        if type(piece["featured"]) is not bool:
            _fail(f"{slug}: featured must be boolean")
        if "show_title" in piece and type(piece["show_title"]) is not bool:
            _fail(f"{slug}: show_title must be boolean")
        for key in ("width", "height"):
            if type(piece[key]) is not int or piece[key] <= 0:
                _fail(f"{slug}: {key} must be a positive integer")
        if "mobile_panels" in piece:
            if type(piece["mobile_panels"]) is not int or piece["mobile_panels"] != 2:
                _fail(f"{slug}: mobile_panels must be the integer 2")
            if piece["width"] != 2 * piece["height"]:
                _fail(f"{slug}: mobile_panels requires a 2:1 image with two equal square panels")
        image, image_path = _catalog_image_path(piece["image"], root)
        actual_width, actual_height = image_dimensions(image_path)
        if (piece["width"], piece["height"]) != (actual_width, actual_height):
            _fail(f"{slug}: declared dimensions do not match {image}")
        clean.append({**piece, "image": image, "href": f"/is/writing/{slug}/"})

    if fallback_slug not in slugs:
        _fail("fallback_slug must name a piece")
    fallback = next(piece for piece in clean if piece["slug"] == fallback_slug)
    if not fallback["featured"]:
        _fail("fallback_slug must be featured")
    return {"schema_version": 1, "fallback_slug": fallback_slug, "pieces": clean}


def render_piece(piece: dict) -> str:
    """Render one standalone, accessible reader page for a validated piece."""
    title = html.escape(piece["title"])
    image = html.escape(piece["image"], quote=True)
    if not image.startswith("/"):
        image = "/" + image
    canonical = f"https://ajin.im{piece['href']}"
    style_version = hashlib.sha256((ROOT / 'assets/paper/image-pieces.css').read_bytes()).hexdigest()[:10]
    caption = (
        f'          <figcaption>{html.escape(piece["caption"])}</figcaption>\n'
        if piece["caption"]
        else ""
    )
    social = f'''    <meta property="og:image" content="https://ajin.im{image}" />
    <meta property="og:image:width" content="{piece['width']}" />
    <meta property="og:image:height" content="{piece['height']}" />
    <meta property="og:image:alt" content="{html.escape(piece['alt'], quote=True)}" />
    <link rel="stylesheet" href="/assets/paper/image-pieces.css?v={style_version}" />'''
    document_head = writes_common.head(
        piece["title"], piece["alt"], canonical, og_type="article", sharing=True
    ).replace(
        '<meta name="twitter:card" content="summary" />',
        '<meta name="twitter:card" content="summary_large_image" />',
    ).replace("  </head>", f"\n{social}\n  </head>")
    alt = html.escape(piece['alt'], quote=True)
    complete_class = ' class="piece-complete"' if piece.get('mobile_panels') == 2 else ''
    art = f'<img{complete_class} src="{image}" width="{piece["width"]}" height="{piece["height"]}" alt="{alt}" />'
    if piece.get('mobile_panels') == 2:
        # Present both disjoint halves in reading order on phones. The underlying
        # asset and native full-size link remain the complete original strip.
        panel = f'<span class="piece-panel" aria-hidden="true"><img src="{image}" width="{piece["width"]}" height="{piece["height"]}" alt="" /></span>'
        art += f'\n          <span class="piece-panels" role="img" aria-label="{alt}">{panel}{panel}</span>'
    body_attributes = 'class="read-page image-piece"'
    if piece.get('show_title', False):
        # Keep the title, artwork and page furniture aligned when a portrait
        # image is constrained by viewport height on larger screens.
        ratio = piece['width'] / piece['height']
        body_attributes = f'class="read-page image-piece piece-with-title" style="--piece-ratio: {ratio:.8f}"'
    return f'''<!doctype html>
{GENERATOR_MARKER}
<html lang="en">
{document_head}
  <body {body_attributes}>
    <main class="shell">
      <nav class="piece-nav" aria-label="Cartoon navigation"><a class="back" href="/is/writing/cartoons/#{piece['slug']}" target="_self">All cartoons</a></nav>
      <h1 class="piece-title">{title}</h1>
      <figure class="piece-art">
        <a href="{image}" target="_self" aria-label="View {title} full size">
          {art}
        </a>
{caption}      </figure>
      <p class="piece-credit">{CREDIT}</p>
    </main>
    <footer class="site-foot piece-actions"><a class="back" href="/is/writing/#all" target="_self">← Back to writing</a>{writes_common.share_control(piece["title"], canonical)}</footer>
  </body>
</html>
'''
