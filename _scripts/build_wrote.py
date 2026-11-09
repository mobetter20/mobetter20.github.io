"""Build the /wrote/ compatibility route to the unified Writing archive.

Individual /wrote/<slug>/ readers keep their durable URLs and are generated
by build_comedy.py from committed public content.
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
    return writes_common.redirect_stub(
        "/is/writing/#all",
        title="Writing moved to ajin.im/is/writing",
    )


def main() -> None:
    WROTE_ROOT.mkdir(parents=True, exist_ok=True)
    (WROTE_ROOT / "index.html").write_text(render_index(), encoding="utf-8")
    print(f"built {WROTE_ROOT / 'index.html'}")


if __name__ == "__main__":
    main()
