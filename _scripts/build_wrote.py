"""Build the combined /wrote archive index.

This is the single source of truth for ajin.im/wrote/index.html. It pulls the
piece lists straight from the essay and comedy generators, so the index can
never drift from the pieces that actually exist on disk.

To add an essay: drop its markdown in is/writing/essays/_src/ and register it in
build_essays.POST_DEFS (or, for a hand-built bespoke page, add it to
BESPOKE_ESSAYS below). To add comedy: it flows in from build_comedy. Either way
it appears here automatically — there are no hand-maintained index links.

Run order (see publish.sh): build_comedy.py, build_essays.py, then this.
"""

from __future__ import annotations

import html
from pathlib import Path

import build_comedy
import build_essays

REPO_ROOT = Path(__file__).resolve().parents[1]
WROTE_ROOT = REPO_ROOT / "wrote"

# Per-essay presentation for the combined index: an optional badge after the
# "essay" tag, and whether the essay shows its excerpt.
ESSAY_BADGES = {
    "the-house-chips-of-ai": "New &middot; 2026",
    "already-seen": "Featured",
}
FEATURED_ESSAY_SLUGS = {"the-house-chips-of-ai", "every-few-years", "already-seen"}

# Bespoke essays: hand-authored pages the essay generator does not build (their
# form is part of the art). They live at /wrote/<slug>/ and are listed here so
# they still appear in the index. `order` slots them among the generated essays.
BESPOKE_ESSAYS = [
    {
        "slug": "every-few-years",
        "title": "Every Few Years, The Country Goes Off",
        "order": 0.5,
        "excerpt": "I am Korean. I grew up inside these explosions. Four cases — PC bangs, coffee shops, jjimjilbang, the run — and a pattern that keeps repeating.",
    },
]


def collect_essays() -> list[dict]:
    items: list[dict] = []
    for post in build_essays.load_posts():
        items.append(
            {
                "slug": post.slug,
                "title": post.title,
                "order": float(post.order),
                "excerpt": post.excerpt,
            }
        )
    for bespoke in BESPOKE_ESSAYS:
        items.append(
            {
                "slug": bespoke["slug"],
                "title": bespoke["title"],
                "order": float(bespoke["order"]),
                "excerpt": bespoke.get("excerpt", ""),
            }
        )
    items.sort(key=lambda item: item["order"])
    return items


def essay_card(item: dict) -> str:
    badge = ESSAY_BADGES.get(item["slug"], "")
    badge_html = f" {badge}" if badge else ""
    excerpt_html = ""
    if item["slug"] in FEATURED_ESSAY_SLUGS and item["excerpt"]:
        excerpt_html = f'\n              <p>{html.escape(item["excerpt"])}</p>'
    return f"""            <article class="archive-card">
              <p class="archive-meta"><span class="loose-tag loose-tag-essay">essay</span>{badge_html}</p>
              <h2>
                <a href="/wrote/{item['slug']}/">{html.escape(item['title'])}</a>
              </h2>{excerpt_html}
            </article>"""


def comedy_card(post, meta_label: str) -> str:
    return f"""            <article class="archive-card">
              <p class="archive-meta"><span class="loose-tag loose-tag-comedy">comedy</span> {meta_label}</p>
              <h2>
                <a href="/wrote/{post.slug}/">{html.escape(post.title)}</a>
              </h2>
            </article>"""


def render_index() -> str:
    essay_cards = "\n".join(essay_card(item) for item in collect_essays())

    medium_posts, standalone_posts = build_comedy.load_posts()
    comedy_blocks = [
        comedy_card(post, "Standalone")
        for post in sorted(standalone_posts, key=lambda item: item.order)
    ]
    comedy_blocks += [comedy_card(post, post.date.strftime("%b %Y")) for post in medium_posts]
    comedy_cards = "\n".join(comedy_blocks)

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="icon" type="image/png" href="/img/a3.png" />
    <link rel="apple-touch-icon" href="/img/a3.png" />
    <title>ajin.im/wrote</title>
    <meta
      name="description"
      content="Things Ajin Im wrote &mdash; essays in the present voice and a comedy archive from the Medium years (2022&ndash;2023)."
    />
    <link rel="canonical" href="https://ajin.im/wrote/" />
    <meta property="og:site_name" content="ajin.im" />
    <meta property="og:title" content="ajin.im/wrote" />
    <meta property="og:description" content="Essays in the present voice and a comedy archive from the Medium years." />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://ajin.im/wrote/" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=DM+Mono:wght@300;400;500&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="/creative-house.css" />
    <script src="/analytics.js" defer></script>
    <style>
      .loose-tag {{
        display: inline-block;
        font-family: var(--mono);
        font-size: 0.66rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        padding: 0.18rem 0.5rem 0.16rem;
        margin-right: 0.6rem;
        border-radius: 2px;
        vertical-align: 0.06em;
      }}
      .loose-tag-essay {{
        background: rgba(138, 168, 190, 0.08);
        color: rgba(158, 185, 205, 0.78);
        border: 1px solid rgba(138, 168, 190, 0.14);
      }}
      .loose-tag-comedy {{
        background: rgba(210, 168, 122, 0.08);
        color: rgba(220, 182, 140, 0.78);
        border: 1px solid rgba(210, 168, 122, 0.16);
      }}
      .loose-divider {{
        margin: 2.2rem 0 0.6rem;
        padding-top: 1.4rem;
        border-top: 1px solid rgba(242, 232, 218, 0.08);
        font-family: var(--mono);
        font-size: 0.72rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--text-faint);
      }}
    </style>
  </head>
  <body class="archive-page">
    <main class="archive-shell">
      <header class="archive-head">
        <a class="back-link" href="/is/writing/">Back to writing</a>
        <h1 class="house-title"><span class="prefix"><a href="/" target="_self">ajin.im</a></span> <span class="verb">wrote</span></h1>
      </header>

      <section class="archive-grid">
        <article class="archive-panel archive-panel-wide">
          <h2 class="panel-title">Essays</h2>

          <div class="archive-list">

{essay_cards}

            <p class="loose-divider">The Medium years</p>

{comedy_cards}

          </div>
        </article>
      </section>

      <footer class="house-footer">
        <p class="house-footer-line">
          <span><a href="mailto:contact@ajin.im">contact@ajin.im</a></span>
        </p>
      </footer>
    </main>
  </body>
</html>
"""


def main() -> None:
    WROTE_ROOT.mkdir(parents=True, exist_ok=True)
    (WROTE_ROOT / "index.html").write_text(render_index(), encoding="utf-8")
    print(f"built {WROTE_ROOT / 'index.html'}")


if __name__ == "__main__":
    main()
