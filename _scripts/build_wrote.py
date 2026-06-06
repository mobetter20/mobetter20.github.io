"""Build /wrote/index.html — the sealed comedy archive (the Medium years).

The past-tense twin of /writes, in the same monospace log voice. Comedy only:
no essays (those moved to /writes/), no per-piece genre labels. Medium pieces are
grouped by year, newest first, with real dates; any standalone comedy is listed
dateless. A closing end-marker seals the record.

Pulls the piece list straight from build_comedy so the index can't drift from the
pages on disk. Run order (publish.sh): build_comedy, build_essays, build_writes,
then this.
"""

from __future__ import annotations

from pathlib import Path

import build_comedy
import writes_common

REPO_ROOT = Path(__file__).resolve().parents[1]
WROTE_ROOT = REPO_ROOT / "wrote"

NOTE_HTML = (
    "# the comedy years &mdash; 2022&ndash;23, complete. "
    'still writing &rarr; <a href="/writes/">ajin.im/writes</a>'
)


def render_index() -> str:
    medium_posts, standalone_posts = build_comedy.load_posts()
    total = len(medium_posts) + len(standalone_posts)

    blocks: list[str] = []

    # Standalone comedy (dateless) — its own block, single-column.
    if standalone_posts:
        s_lines = [
            writes_common.log_line(f"/wrote/{post.slug}/", post.title)
            for post in sorted(standalone_posts, key=lambda item: item.order)
        ]
        blocks.append(
            '      <div class="log nodate">\n'
            '        <p class="yr">## standalone</p>\n'
            + "\n".join(s_lines)
            + "\n      </div>"
        )

    # Medium pieces grouped by year, newest first.
    by_year: dict[int, list] = {}
    for post in medium_posts:
        by_year.setdefault(post.date.year, []).append(post)
    years = sorted(by_year, reverse=True)

    inner: list[str] = []
    for year in years:
        inner.append(f'        <p class="yr">## {year}</p>')
        for post in sorted(by_year[year], key=lambda item: item.date, reverse=True):
            inner.append(
                writes_common.log_line(
                    f"/wrote/{post.slug}/", post.title, date=post.date.strftime("%Y·%m")
                )
            )
    if years:
        earliest = years[-1]
        inner.append(
            f'        <p class="endmark">&#8718; {earliest} — start of record '
            f"&nbsp;·&nbsp; {total} entries, nothing after.</p>"
        )
    blocks.append('      <div class="log">\n' + "\n".join(inner) + "\n      </div>")

    return writes_common.log_page(
        title="ajin.im wrote",
        description="The comedy years — a sealed archive of Medium-era comedy (2022–23).",
        canonical="https://ajin.im/wrote/",
        bar_text="ajin.im/wrote",
        bar_href="/",
        note_html=NOTE_HTML,
        body_html="\n".join(blocks),
    )


def main() -> None:
    WROTE_ROOT.mkdir(parents=True, exist_ok=True)
    (WROTE_ROOT / "index.html").write_text(render_index(), encoding="utf-8")
    print(f"built {WROTE_ROOT / 'index.html'}")


if __name__ == "__main__":
    main()
