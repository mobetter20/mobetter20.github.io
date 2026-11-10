"""Build the /writes/ compatibility route and refresh the unified Writing page.

The essay source directory remains the registry. collect_items also includes
hand-built essays declared in BESPOKE_ESSAYS. Normal publication updates the
Writing archive and refreshes Home without changing either page's hand-picked
selection. The publisher verifies the exact archive link, source and reader.
"""

from __future__ import annotations

from pathlib import Path

import build_essays
import writes_common

REPO_ROOT = Path(__file__).resolve().parents[1]
WRITES_ROOT = REPO_ROOT / "writes"

# Hand-built essays the generator does not render. They live at /writes/<slug>/.
# (every-few-years moved to seoulcrushing.com/every-few-years/ on 2026-06-08;
# /writes/ + /wrote/every-few-years/ are now redirect stubs.)
BESPOKE_ESSAYS: list[dict] = []

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
    items.sort(key=lambda item: item["order"], reverse=True)
    return items


def render_index() -> str:
    """Keep the old archive URL useful without maintaining a second archive."""
    return writes_common.redirect_stub(
        "/is/writing/#all",
        title="Writing moved to ajin.im/is/writing",
    )


def main() -> None:
    WRITES_ROOT.mkdir(parents=True, exist_ok=True)
    (WRITES_ROOT / "index.html").write_text(render_index(), encoding="utf-8")
    print(f"built {WRITES_ROOT / 'index.html'}")
    # Local import avoids a renderer cycle while ensuring a newly published
    # essay is listed in the unified archive.
    import build_sections
    build_sections.build()
    import build_root
    build_root.build(root_only=True)
    build_root.check_home()


if __name__ == "__main__":
    main()
