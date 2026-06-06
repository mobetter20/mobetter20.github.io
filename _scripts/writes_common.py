"""Shared rendering for the writes/wrote world.

One reading-page template (mono chrome + serif body) and one log-index template
(monospace), both styled by /writes.css. Imported by build_essays, build_comedy,
build_writes, and build_wrote so the four surfaces can never drift apart.
"""

from __future__ import annotations

import html

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    '    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    '    <link\n'
    '      href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&family=DM+Mono:wght@300;400;500&display=swap"\n'
    '      rel="stylesheet"\n'
    '    />'
)


def head(title: str, description: str, canonical: str, *, og_type: str = "website") -> str:
    """The shared <head> block. `title` and `description` are escaped here."""
    t = html.escape(title)
    d = html.escape(description)
    return f"""  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="icon" type="image/png" href="/img/a3.png" />
    <link rel="apple-touch-icon" href="/img/a3.png" />
    <title>{t}</title>
    <meta name="description" content="{d}" />
    <link rel="canonical" href="{canonical}" />
    <meta property="og:site_name" content="ajin.im" />
    <meta property="og:title" content="{t}" />
    <meta property="og:description" content="{d}" />
    <meta property="og:type" content="{og_type}" />
    <meta property="og:url" content="{canonical}" />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="{t}" />
    <meta name="twitter:description" content="{d}" />
    {FONTS}
    <link rel="stylesheet" href="/writes.css" />
    <script src="/analytics.js" defer></script>
  </head>"""


FOOTER = (
    '    <footer class="site-foot">&#8617; <a href="/">ajin.im</a> '
    '&nbsp;&middot;&nbsp; <a href="mailto:contact@ajin.im">contact@ajin.im</a></footer>'
)


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
) -> str:
    """A single piece. `body_html` is already-rendered HTML (indented)."""
    subtitle_html = (
        f'      <p class="post-subtitle">{html.escape(subtitle)}</p>\n' if subtitle else ""
    )
    note_block = f"      {note_html}\n" if note_html else ""
    return f"""<!DOCTYPE html>
<html lang="en">
{head(title, description, canonical, og_type="article")}
  <body class="read-page">
    <main class="shell">
      <a class="back" href="{back_href}">{html.escape(back_label)}</a>
      <p class="kick">{html.escape(kicker)}</p>
      <h1>{html.escape(title)}</h1>
{subtitle_html}{note_block}      <article class="body">
{body_html}
      </article>
    </main>
{FOOTER}
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
) -> str:
    """A log index (/writes or /wrote). `body_html` is the rendered .log block."""
    return f"""<!DOCTYPE html>
<html lang="en">
{head(title, description, canonical)}
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


def redirect_stub(target_url: str, *, title: str = "Moved") -> str:
    """A tiny meta-refresh redirect page (noindex), for an old URL that moved."""
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="robots" content="noindex" />
    <title>{html.escape(title)}</title>
    <meta http-equiv="refresh" content="0; url={target_url}" />
    <link rel="canonical" href="https://ajin.im{target_url}" />
  </head>
  <body>
    <p>Moved to <a href="{target_url}">ajin.im{target_url}</a>.</p>
  </body>
</html>
"""
