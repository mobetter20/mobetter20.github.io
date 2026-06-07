#!/usr/bin/env python3
"""Build sitemap.xml at the repo root from the served HTML tree.

Walks every served *.html under REPO_ROOT, maps each to its public URL on
https://ajin.im, and writes a sitemaps.org urlset to REPO_ROOT/sitemap.xml.

Rules:
  - Excludes anything under /.git/, /.claude/, /_archive/, /_lab/, /templates/,
    and excludes 404.html.
  - Skips redirect stubs (meta-refresh) and noindex pages — neither should be
    advertised as a canonical URL.
  - ".../index.html" maps to its directory URL (root index.html -> site root).
  - Any other "*.html" maps to its own .html URL.
  - Future-dated Municipal Coo issues (is/writing/bird-coo/issues/YYYY-MM-DD.html
    where the date is after today) are skipped.
  - <lastmod> comes from `git log -1 --format=%cI -- <relpath>`; if git yields
    nothing (untracked, shallow CI clone, no git) it falls back to the file mtime
    as an ISO date.

Usage:
    python3 _scripts/build_sitemap.py
"""

from __future__ import annotations

import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SITEMAP_PATH = REPO_ROOT / "sitemap.xml"

BASE_URL = "https://ajin.im"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

# Path fragments that exclude a file from the sitemap. Compared against the
# POSIX relative path with leading+trailing slashes so "/foo/" matches a
# directory component named exactly "foo".
EXCLUDE_DIRS = ("/.git/", "/.claude/", "/_archive/", "/_lab/", "/templates/")
EXCLUDE_FILES = {"404.html"}

# Municipal Coo issues live here as YYYY-MM-DD.html; future-dated ones are held.
COO_ISSUES_DIR = "is/writing/bird-coo/issues"


def is_excluded(rel_posix: str) -> bool:
    """True if the relative POSIX path should be left out of the sitemap."""
    # Jekyll never serves a file or directory whose name starts with "_", so it
    # must not be advertised in the sitemap (e.g. is/.../_template.html -> 404).
    if any(part.startswith("_") for part in rel_posix.split("/")):
        return True
    guarded = f"/{rel_posix}/"
    if any(frag in guarded for frag in EXCLUDE_DIRS):
        return True
    if rel_posix in EXCLUDE_FILES:
        return True
    return False


def is_future_coo_issue(rel_posix: str, today: date) -> bool:
    """True for a bird-coo issue whose YYYY-MM-DD filename is after today."""
    prefix = f"{COO_ISSUES_DIR}/"
    if not rel_posix.startswith(prefix):
        return False
    stem = rel_posix[len(prefix):].removesuffix(".html")
    try:
        issue_date = datetime.strptime(stem, "%Y-%m-%d").date()
    except ValueError:
        # Non-date filename in the issues dir (e.g. index.html) — not a future issue.
        return False
    return issue_date > today


def is_noindex_or_redirect(path: Path) -> bool:
    """True for redirect stubs (meta-refresh) and noindex pages — neither
    belongs in the sitemap as a canonical URL."""
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:8192].lower()
    except OSError:
        return False
    if 'http-equiv="refresh"' in head or "http-equiv='refresh'" in head:
        return True
    if 'name="robots"' in head and "noindex" in head:
        return True
    return False


def url_for(rel_posix: str) -> str:
    """Map a served HTML relative path to its public https://ajin.im URL."""
    if rel_posix == "index.html":
        return f"{BASE_URL}/"
    if rel_posix.endswith("/index.html"):
        directory = rel_posix[: -len("index.html")]  # keeps trailing slash
        return f"{BASE_URL}/{directory}"
    return f"{BASE_URL}/{rel_posix}"


def git_lastmod(rel_posix: str) -> str | None:
    """Committer ISO date for the file's last commit, or None if unavailable."""
    try:
        proc = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", rel_posix],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
    except Exception:  # noqa: BLE001 — git missing / not a repo: fall back to mtime
        return None
    if proc.returncode != 0:
        return None
    stamp = proc.stdout.strip()
    return stamp or None


def mtime_lastmod(path: Path) -> str:
    """File mtime as an ISO-8601 date (UTC)."""
    ts = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return ts.date().isoformat()


def lastmod_for(path: Path, rel_posix: str) -> str:
    return git_lastmod(rel_posix) or mtime_lastmod(path)


def collect_urls() -> list[tuple[str, str]]:
    """Return [(loc, lastmod)] for every included page, sorted by loc."""
    today = date.today()
    entries: list[tuple[str, str]] = []
    for path in REPO_ROOT.rglob("*.html"):
        rel_posix = path.relative_to(REPO_ROOT).as_posix()
        if is_excluded(rel_posix):
            continue
        if is_future_coo_issue(rel_posix, today):
            continue
        if is_noindex_or_redirect(path):
            continue
        loc = url_for(rel_posix)
        lastmod = lastmod_for(path, rel_posix)
        entries.append((loc, lastmod))
    entries.sort(key=lambda e: e[0])
    return entries


def render_xml(entries: list[tuple[str, str]]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<urlset xmlns="{SITEMAP_NS}">',
    ]
    for loc, lastmod in entries:
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main() -> int:
    entries = collect_urls()
    SITEMAP_PATH.write_text(render_xml(entries), encoding="utf-8")
    print(f"wrote {SITEMAP_PATH} ({len(entries)} urls)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
