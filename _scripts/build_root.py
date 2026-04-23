#!/usr/bin/env python3
"""Build ajin.im pages from templates/ + content/stats.md.

Renders:
  - index.html              (root sentence page) from templates/root.html
  - is/running/index.html   (personal stats page) from templates/running.html

Usage:
    python3 _scripts/build_root.py          # write both
    python3 _scripts/build_root.py --check  # print output sizes, don't write
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROOT_TEMPLATE_PATH = ROOT / "templates" / "root.html"
RUNNING_TEMPLATE_PATH = ROOT / "templates" / "running.html"
STATS_PATH = ROOT / "content" / "stats.md"
INDEX_PATH = ROOT / "index.html"
RUNNING_INDEX_PATH = ROOT / "is" / "running" / "index.html"

EARTH_KM = 40075
MOON_KM = 384400

BOOK_SEPARATORS = (" — ", " – ", " -- ")


class StatsError(Exception):
    pass


def parse_stats(path: Path) -> dict[str, list[str]]:
    """Parse the stats markdown into {section_name: [raw_lines]}.

    Sections start with `##`. Lines starting with `#` inside a section body
    are comments and ignored. Content above the first `##` is ignored.
    """
    if not path.is_file():
        raise StatsError(f"stats file not found: {path}")

    sections: dict[str, list[str]] = {}
    current: str | None = None
    current_lines: list[str] = []

    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if stripped.startswith("##"):
            if current is not None:
                sections[current] = current_lines
            current = stripped[2:].strip()
            current_lines = []
        elif current is None:
            continue
        elif stripped.startswith("#"):
            continue
        else:
            current_lines.append(raw)

    if current is not None:
        sections[current] = current_lines

    return sections


def require(sections: dict[str, list[str]], name: str) -> list[str]:
    if name not in sections:
        raise StatsError(f"missing required section: ## {name}")
    return sections[name]


def parse_kv(lines: list[str], section: str) -> dict[str, str]:
    kv: dict[str, str] = {}
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if ":" not in s:
            raise StatsError(f"[{section}] expected `key: value`, got: {s!r}")
        key, value = s.split(":", 1)
        kv[key.strip()] = value.strip()
    return kv


def parse_books(lines: list[str], section: str) -> list[tuple[str, str]]:
    """Each bullet is `- TITLE — AUTHOR`. Returns [(title, author_plus_tags)]."""
    books: list[tuple[str, str]] = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if not s.startswith("-"):
            raise StatsError(f"[{section}] expected `- title — author`, got: {s!r}")
        s = s[1:].strip()
        for sep in BOOK_SEPARATORS:
            if sep in s:
                title, author = s.split(sep, 1)
                books.append((title.strip(), author.strip()))
                break
        else:
            books.append((s, ""))
    return books


def parse_text(lines: list[str]) -> str:
    return "\n".join(l.rstrip() for l in lines if l.strip()).strip()


def require_int(kv: dict[str, str], key: str, section: str) -> int:
    if key not in kv:
        raise StatsError(f"[{section}] missing required key: {key}")
    raw = kv[key]
    try:
        return int(raw.replace(",", "").replace("_", ""))
    except ValueError as e:
        raise StatsError(f"[{section}] {key} must be an integer, got: {raw!r}") from e


def earth_prose(total_km: int) -> str:
    ratio = total_km / EARTH_KM
    if ratio < 1.0:
        pct = round(ratio * 100)
        return f"{pct}% of the way around earth"
    if ratio < 1.7:
        return f"{ratio:.1f} times around earth"
    if ratio < 2.0:
        return "nearly twice around earth"
    if ratio <= 2.2:
        return "about twice around earth"
    return f"{ratio:.1f} times around earth"


def earth_multiplier(total_km: int) -> str:
    return f"{total_km / EARTH_KM:.2f}×"


def render_reading_current(books: list[tuple[str, str]]) -> str:
    if not books:
        raise StatsError("reading_current: at least one book required")
    parts: list[str] = []
    for i, (title, author) in enumerate(books):
        is_last = i == len(books) - 1
        suffix = "" if is_last else "<br>"
        if author:
            parts.append(f'<span class="work-title">{title}</span> by {author}.{suffix}')
        else:
            parts.append(f'<span class="work-title">{title}</span>.{suffix}')
    return "\n      ".join(parts)


def render_reading_year(books: list[tuple[str, str]]) -> str:
    if not books:
        raise StatsError("reading_year: at least one book required")
    actives: list[str] = []
    paused: list[str] = []
    for title, author in books:
        combined = f"{title} {author}".lower()
        if "(paused)" in combined:
            clean_title = title.replace("(paused)", "").replace("(Paused)", "").strip()
            paused.append(clean_title)
        else:
            actives.append(title)
    out = ", ".join(actives)
    for p in paused:
        out += f". {p}, paused"
    out += "."
    return out


def render(template_path: Path, replacements: dict[str, str]) -> str:
    if not template_path.is_file():
        raise StatsError(f"template not found: {template_path}")
    template = template_path.read_text(encoding="utf-8")
    used = {t: v for t, v in replacements.items() if t in template}
    if not used:
        raise StatsError(f"template uses no known tokens: {template_path}")
    output = template
    for token, value in used.items():
        output = output.replace(token, value)
    leftover = [t for t in used if t in output]
    if leftover:
        raise StatsError(f"unresolved tokens after substitution in {template_path.name}: {leftover}")
    return output


def build(check_only: bool = False) -> None:
    sections = parse_stats(STATS_PATH)

    running_kv = parse_kv(require(sections, "running"), "running")
    total_km = require_int(running_kv, "total_km", "running")
    if total_km < 0:
        raise StatsError(f"running.total_km must be non-negative, got {total_km}")
    since_year = require_int(running_kv, "since_year", "running")

    total_km_fmt = f"{total_km:,}"
    remaining_km = MOON_KM - total_km
    remaining_fmt = f"{remaining_km:,}"
    earth = earth_prose(total_km)
    earth_mult = earth_multiplier(total_km)

    books_current = parse_books(require(sections, "reading_current"), "reading_current")
    reading_current_html = render_reading_current(books_current)

    books_year = parse_books(require(sections, "reading_year"), "reading_year")
    reading_year_str = render_reading_year(books_year)

    learning = parse_text(require(sections, "learning"))
    if not learning:
        raise StatsError("learning: section body is empty")

    replacements = {
        "{{running_total_km}}": total_km_fmt,
        "{{running_since}}": str(since_year),
        "{{running_earth_prose}}": earth,
        "{{running_earth_multiplier}}": earth_mult,
        "{{running_moon_remaining}}": remaining_fmt,
        "{{reading_current}}": reading_current_html,
        "{{reading_year}}": reading_year_str,
        "{{learning}}": learning,
    }

    targets: list[tuple[Path, Path]] = [
        (ROOT_TEMPLATE_PATH, INDEX_PATH),
        (RUNNING_TEMPLATE_PATH, RUNNING_INDEX_PATH),
    ]

    print(f"running: {total_km_fmt} km since {since_year} — {earth} ({earth_mult}) — {remaining_fmt} km left")
    print(f"reading_current: {len(books_current)} book(s)")
    print(f"reading_year: {len(books_year)} book(s) (actives + paused combined)")
    print(f"learning: {learning!r}")

    for tpl, out_path in targets:
        output = render(tpl, replacements)
        if check_only:
            print(f"--check mode: would write {out_path} ({len(output)} bytes)")
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(output, encoding="utf-8")
            print(f"wrote {out_path} ({len(output)} bytes)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build ajin.im/index.html from stats.md")
    parser.add_argument("--check", action="store_true", help="print output, don't write")
    args = parser.parse_args()

    try:
        build(check_only=args.check)
    except StatsError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
