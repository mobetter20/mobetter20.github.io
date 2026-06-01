#!/usr/bin/env python3
"""Site-wide internal link checker — fast, pre-push friendly.

Walks every served *.html under REPO_ROOT and resolves each INTERNAL href=/src=
target to disk. Broken internal links are printed and the script exits 1, so it
can gate a pre-push hook. External links, fragments, and JS-constructed values
are ignored.

What is checked:
  - Root-relative "/x/y" -> REPO_ROOT/x/y
  - Relative "../x", "./x", "x" -> resolved against the file's own directory
  - A target ending in "/" (or extensionless and resolving to a directory)
    must contain an index.html
  - Resolution is CASE-SENSITIVE even on a case-insensitive macOS filesystem:
    each path component must match the on-disk name exactly.

What is ignored (never flagged):
  - External / protocol links: http:, https:, mailto:, tel:, protocol-relative //
  - Pure fragments ("#...", including hash-router "#/")
  - data: URIs, javascript:
  - Values that look JS-constructed (contain + { or a quote mid-value)
  - Anything under /lemon/ (a separate GitHub Pages deployment)

Files containing a <base href> tag are skipped (reported as "skipped: has <base>"),
since their relative targets resolve against the base, not the file location.

Exclusions match the sitemap builder: /.git/, /.claude/, /_archive/, /_lab/,
/templates/, and 404.html.

Usage:
    python3 _scripts/check_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

EXCLUDE_DIRS = ("/.git/", "/.claude/", "/_archive/", "/_lab/", "/templates/")
EXCLUDE_FILES = {"404.html"}

# Targets under these prefixes are treated as external (separate deployments).
ALLOW_EXTERNAL_PREFIXES = ("/lemon/",)

# Protocol / non-navigational schemes we never resolve to disk.
IGNORED_SCHEMES = ("http:", "https:", "mailto:", "tel:", "data:", "javascript:")

# href="..." / href='...' and the same for src=. Captures the quoted value.
ATTR_RE = re.compile(r"""\b(?:href|src)\s*=\s*(["'])(.*?)\1""", re.IGNORECASE | re.DOTALL)
BASE_RE = re.compile(r"<base\b[^>]*\bhref\s*=", re.IGNORECASE)
# Inline <script> BODIES are dropped before scanning (opening <script src> tags
# are kept) so JS-assembled values like  el.src = "./data-" + id  aren't treated
# as links. Keeping the opening tag means real external <script src> stays checked.
SCRIPT_BODY_RE = re.compile(r"(<script\b[^>]*>).*?(</script>)", re.IGNORECASE | re.DOTALL)


def is_excluded(rel_posix: str) -> bool:
    guarded = f"/{rel_posix}/"
    if any(frag in guarded for frag in EXCLUDE_DIRS):
        return True
    return rel_posix in EXCLUDE_FILES


def should_ignore_target(raw: str) -> bool:
    """True if a target value is external / fragment / JS-constructed."""
    value = raw.strip()
    if not value:
        return True
    if value.startswith("#"):  # pure fragment, incl. hash-router "#/"
        return True
    if value.startswith("//"):  # protocol-relative -> external
        return True
    low = value.lower()
    if any(low.startswith(scheme) for scheme in IGNORED_SCHEMES):
        return True
    # Conservative JS / template detection: a "+", "{", or a stray quote inside
    # the value means it was likely assembled in script — don't guess.
    if "+" in value or "{" in value or '"' in value or "'" in value or "`" in value:
        return True
    if any(value.startswith(prefix) for prefix in ALLOW_EXTERNAL_PREFIXES):
        return True
    return False


def strip_target(value: str) -> str:
    """Drop a trailing #fragment and ?query, returning just the path part."""
    for sep in ("#", "?"):
        idx = value.find(sep)
        if idx != -1:
            value = value[:idx]
    return value


def resolve_target(value: str, page: Path) -> Path:
    """Resolve an internal target to an absolute filesystem path (not validated)."""
    if value.startswith("/"):
        return (REPO_ROOT / value.lstrip("/")).resolve()
    return (page.parent / value).resolve()


def exists_case_sensitive(target: Path) -> bool:
    """True iff target exists with every path component matching on-disk case.

    macOS's default filesystem is case-insensitive, so Path.exists() would
    accept "/IS/Writing". We re-check each component against the real directory
    listing to enforce the case the published URL will actually serve.
    """
    try:
        target.relative_to(REPO_ROOT)
    except ValueError:
        # Resolved outside the repo (e.g. too many "../"). Treat as broken.
        return False
    current = REPO_ROOT
    for part in target.relative_to(REPO_ROOT).parts:
        try:
            names = {entry.name for entry in current.iterdir()}
        except (NotADirectoryError, FileNotFoundError):
            return False
        if part not in names:
            return False
        current = current / part
    return True


def check_one(value: str, page: Path) -> str | None:
    """Return a failure reason for an internal target, or None if it resolves."""
    path_part = strip_target(value)
    if not path_part:
        # Was "page.html#frag" with empty path -> same-page fragment; skip.
        return None

    target = resolve_target(path_part, page)
    wants_dir = path_part.endswith("/")

    if not exists_case_sensitive(target):
        return "not found"

    if target.is_dir():
        index = target / "index.html"
        if not exists_case_sensitive(index):
            return "directory has no index.html"
        return None

    # Resolved to a file. A target that explicitly asked for a directory
    # ("foo/") but landed on a file is a mismatch.
    if wants_dir:
        return "expected directory, found file"
    return None


def extract_targets(text: str) -> list[str]:
    return [m.group(2) for m in ATTR_RE.finditer(text)]


def main() -> int:
    pages: list[Path] = []
    for path in REPO_ROOT.rglob("*.html"):
        rel_posix = path.relative_to(REPO_ROOT).as_posix()
        if is_excluded(rel_posix):
            continue
        pages.append(path)
    pages.sort()

    broken: list[tuple[str, str, str]] = []
    skipped: list[str] = []
    checked_links = 0

    for page in pages:
        rel = page.relative_to(REPO_ROOT).as_posix()
        text = page.read_text(encoding="utf-8", errors="replace")

        if BASE_RE.search(text):
            skipped.append(rel)
            continue

        scannable = SCRIPT_BODY_RE.sub(r"\1\2", text)
        for value in extract_targets(scannable):
            if should_ignore_target(value):
                continue
            checked_links += 1
            reason = check_one(value, page)
            if reason is not None:
                broken.append((rel, value, reason))

    for rel in skipped:
        print(f"skipped: has <base> — {rel}")

    if broken:
        for rel, value, reason in broken:
            print(f"{rel} -> {value} ({reason})")
        print(
            f"FAIL: {len(broken)} broken of {checked_links} internal links "
            f"across {len(pages)} pages"
        )
        return 1

    print(f"OK: {checked_links} links across {len(pages)} pages, 0 broken")
    return 0


if __name__ == "__main__":
    sys.exit(main())
