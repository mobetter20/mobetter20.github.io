"""Shared rendering for legacy writing readers and compatibility routes.

Individual pieces retain durable URLs, but use the same paper palette and
typography as /is/writing. The former indexes are crawl-safe routes to that
unified archive.
"""

from __future__ import annotations

import hashlib
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    '    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    '    <link\n'
    '      href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=IBM+Plex+Mono:wght@400;500&display=swap"\n'
    '      rel="stylesheet"\n'
    '    />'
)


def share_assets() -> str:
    """Version the small, local reader enhancement independently of page styles."""
    def asset(name: str) -> str:
        path = f"assets/paper/{name}"
        version = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()[:10]
        return f"/{path}?v={version}"

    return (f'<link rel="stylesheet" href="{asset("share.css")}" />\n'
            f'    <script src="{asset("share.js")}" defer></script>')


def share_control(title: str, canonical: str) -> str:
    """Keep the payload on the piece itself, including after a slide swap."""
    return (f'<div class="piece-share" hidden><button class="share-button" type="button" '
            f'data-share-title="{html.escape(title, quote=True)}" '
            f'data-share-url="{html.escape(canonical, quote=True)}" hidden>Share</button>'
            '<span class="share-status" role="status" aria-live="polite" '
            'aria-atomic="true"></span></div>')


def head(
    title: str, description: str, canonical: str, *, og_type: str = "website", feed_url: str = "",
    sharing: bool = False,
) -> str:
    """The shared <head> block. `title` and `description` are escaped here.

    `feed_url`, when set, emits an Atom autodiscovery <link>. Only pages that
    belong to that feed (the essays + the /writes index) pass it; comedy and
    /wrote leave it empty so the essays-only feed isn't advertised there."""
    t = html.escape(title)
    d = html.escape(description)
    feed_link = (
        f'\n    <link rel="alternate" type="application/atom+xml" '
        f'title="ajin.im — Collected Writing" href="{feed_url}" />'
        if feed_url
        else ""
    )
    return f"""  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="icon" type="image/png" href="/img/a3.png" />
    <link rel="apple-touch-icon" href="/img/a3.png" />
    <title>{t}</title>
    <meta name="description" content="{d}" />
    <link rel="canonical" href="{canonical}" />{feed_link}
    <meta property="og:site_name" content="ajin.im" />
    <meta property="og:title" content="{t}" />
    <meta property="og:description" content="{d}" />
    <meta property="og:type" content="{og_type}" />
    <meta property="og:url" content="{canonical}" />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="{t}" />
    <meta name="twitter:description" content="{d}" />
    {FONTS}
    <link rel="stylesheet" href="/writes.css?v=paper-r12" />
    <script src="/analytics.js" defer></script>
    {share_assets() if sharing else ""}
  </head>"""


FOOTER = '    <footer class="site-foot"><a href="mailto:hi@ajin.im">hi@ajin.im</a></footer>'


def reading_page(
    *,
    title: str,
    body_html: str,
    canonical: str,
    description: str,
    kicker: str,
    back_href: str,
    back_label: str,
    subtitle: str = "",
    note_html: str = "",
    feed_url: str = "",
) -> str:
    """A single piece. `body_html` is already-rendered HTML (indented)."""
    subtitle_html = (
        f'      <p class="post-subtitle">{html.escape(subtitle)}</p>\n' if subtitle else ""
    )
    note_block = f"      {note_html}\n" if note_html else ""
    return f"""<!DOCTYPE html>
<html lang="en">
{head(title, description, canonical, og_type="article", feed_url=feed_url, sharing=True)}
  <body class="read-page">
    <main class="shell">
      <a class="back" href="{back_href}" target="_self">{html.escape(back_label)}</a>
      <p class="kick">{html.escape(kicker)}</p>
      <h1>{html.escape(title)}</h1>
{subtitle_html}{note_block}      <article class="body">
{body_html}
      </article>
    </main>
    <footer class="site-foot piece-actions"><a href="mailto:hi@ajin.im">hi@ajin.im</a>{share_control(title, canonical)}</footer>
  </body>
</html>
"""


def log_line(href: str, title: str, *, date: str = "", new: bool = False, dek: str = "") -> str:
    """One row in a log index."""
    new_html = '<span class="new">new</span>' if new else ""
    dek_html = f'<span class="dek">{html.escape(dek)}</span>' if dek else ""
    date_html = f'<span class="d">{html.escape(date)}</span>' if date else ""
    return (
        f'        <a class="line" href="{href}">{date_html}'
        f'<span class="t">{html.escape(title)}{new_html}{dek_html}</span></a>'
    )


def log_page(
    *,
    title: str,
    description: str,
    canonical: str,
    bar_text: str,
    bar_href: str,
    note_html: str,
    body_html: str,
    feed_url: str = "",
) -> str:
    """A log index (/writes or /wrote). `body_html` is the rendered .log block."""
    return f"""<!DOCTYPE html>
<html lang="en">
{head(title, description, canonical, feed_url=feed_url)}
  <body class="log-page">
    <main class="shell">
      <div class="bar"><a href="{bar_href}">{html.escape(bar_text)}</a></div>
      <p class="note">{note_html}</p>
      <div class="rule"></div>
{body_html}
    </main>
{FOOTER}
  </body>
</html>
"""


def redirect_stub(
    target_url: str, *, title: str = "Moved", canonical: str | None = None
) -> str:
    """A tiny, visible noindex compatibility redirect."""
    canonical_url = canonical or f"https://ajin.im{target_url}"
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="robots" content="noindex,follow" />
    <title>{html.escape(title)}</title>
    <meta http-equiv="refresh" content="0; url={target_url}" />
    <link rel="canonical" href="{canonical_url}" />
  </head>
  <body>
    <p>Moved to <a href="{target_url}" target="_self">ajin.im{target_url}</a>.</p>
  </body>
</html>
"""
