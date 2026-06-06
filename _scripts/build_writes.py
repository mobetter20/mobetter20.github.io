"""Build /writes/index.html — the living log of thoughts.

A present-tense running log of the essays (direct, unmasked writing). Pulls the
essay list straight from build_essays so the log can never drift from the pieces
on disk. Bespoke essays (hand-built; their form is part of the art) live at
/writes/<slug>/ and are listed via BESPOKE_ESSAYS.

Dates are optional: add `date: YYYY-MM-DD` to an essay's front matter and its year
appears in the log. Until then the log renders dateless (newest first by `order`).

The sealed comedy archive is a separate twin at /wrote/ (see build_wrote.py).
Run order (publish.sh): build_comedy, build_essays, build_writes, build_wrote.
"""

from __future__ import annotations

from pathlib import Path

import build_essays
import writes_common

REPO_ROOT = Path(__file__).resolve().parents[1]
WRITES_ROOT = REPO_ROOT / "writes"

# Hand-built essays the generator does not render. They live at /writes/<slug>/.
BESPOKE_ESSAYS = [
    {
        "slug": "every-few-years",
        "title": "Every Few Years, The Country Goes Off",
        "order": 0.5,
        "date": "",
        "excerpt": "I am Korean. I grew up inside these explosions. Four cases — and a pattern that keeps repeating.",
    },
]

NOTE_HTML = '# a running log of thoughts. the comedy years &rarr; <a href="/wrote/">ajin.im/wrote</a>'


def collect_items() -> list[dict]:
    items: list[dict] = []
    for post in build_essays.load_posts():
        items.append(
            {
                "slug": post.slug,
                "title": post.title,
                "order": float(post.order),
                "date": post.date,
                "excerpt": post.excerpt,
            }
        )
    for bespoke in BESPOKE_ESSAYS:
        items.append(
            {
                "slug": bespoke["slug"],
                "title": bespoke["title"],
                "order": float(bespoke["order"]),
                "date": bespoke.get("date", ""),
                "excerpt": bespoke.get("excerpt", ""),
            }
        )
    items.sort(key=lambda item: item["order"])
    return items


def render_index() -> str:
    items = collect_items()
    has_dates = any(item["date"] for item in items)
    lines = []
    for idx, item in enumerate(items):
        year = item["date"][:4] if item["date"] else ""
        # the two most recent carry a one-line dek; the rest stand on their titles
        dek = item["excerpt"] if idx < 2 else ""
        lines.append(
            writes_common.log_line(
                f'/writes/{item["slug"]}/',
                item["title"],
                date=year,
                new=(idx == 0),
                dek=dek,
            )
        )
    log_class = "log" if has_dates else "log nodate"
    body = f'      <div class="{log_class}">\n' + "\n".join(lines) + "\n      </div>"
    return writes_common.log_page(
        title="ajin.im writes",
        description="A running log of thoughts — essays in the present voice.",
        canonical="https://ajin.im/writes/",
        bar_text="ajin.im/writes",
        bar_href="/",
        note_html=NOTE_HTML,
        body_html=body,
    )


def main() -> None:
    WRITES_ROOT.mkdir(parents=True, exist_ok=True)
    (WRITES_ROOT / "index.html").write_text(render_index(), encoding="utf-8")
    print(f"built {WRITES_ROOT / 'index.html'}")


if __name__ == "__main__":
    main()
