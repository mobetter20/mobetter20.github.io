#!/usr/bin/env python3
"""Build Home and the stats pages from templates and committed content.

Home reads its pinned cartoon and running stats through paper_site. Running,
Reading and Learning read content/stats.md. The daily running adapter relies on
this output set; Writing and Building belong to the explicit build_sections
publisher, never this daily entry point.

Usage:
    python3 _scripts/build_root.py
    python3 _scripts/build_root.py --root-only
    python3 _scripts/build_root.py --check
    python3 _scripts/build_root.py --check-home
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import home_catalog
import paper_site

ROOT = Path(__file__).resolve().parent.parent
ROOT_TEMPLATE_PATH = ROOT / "templates" / "root.html"
RUNNING_TEMPLATE_PATH = ROOT / "templates" / "running.html"
READING_TEMPLATE_PATH = ROOT / "templates" / "reading.html"
LEARNING_TEMPLATE_PATH = ROOT / "templates" / "learning.html"
STATS_PATH = ROOT / "content" / "stats.md"
INDEX_PATH = ROOT / "index.html"
RUNNING_INDEX_PATH = ROOT / "is" / "running" / "index.html"
READING_INDEX_PATH = ROOT / "is" / "reading" / "index.html"
LEARNING_INDEX_PATH = ROOT / "is" / "learning" / "index.html"
BUILDING_INDEX_PATH = ROOT / "is" / "building" / "index.html"

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


def as_of_label(raw: str) -> str:
    """`as_of: 2026-07` -> "to July 2026". Empty when the key is absent.

    The Strava adapter sets it on every good sync, so the home run-line never
    presents a frozen total as current.
    """
    raw = raw.strip()
    if not raw:
        return ""
    try:
        stamp = datetime.strptime(raw, "%Y-%m")
    except ValueError as e:
        raise StatsError(f"[running] as_of must be YYYY-MM, got: {raw!r}") from e
    return f"to {stamp:%B %Y}"


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


def with_generated_banner(output: str, template_path: Path) -> str:
    """Insert a GENERATED-FILE banner just under the doctype.

    The banner is what makes these pages safe to leave around: it trips
    ~/.claude/hooks/upstream-awareness-guard.py and tells any human/agent
    reading the file that edits belong in the template, not the output.
    Placed *after* the doctype line so it never triggers quirks mode.
    """
    banner = (
        f"<!-- GENERATED FILE — DO NOT EDIT. "
        f"Source: templates/{template_path.name} · built by _scripts/build_root.py. "
        f"Edits here are overwritten on the next build "
        f"(.github/workflows/rebuild-root-on-stats.yml). -->\n"
    )
    if output.lstrip()[:9].lower() == "<!doctype":
        nl = output.find("\n")
        if nl == -1:
            return output + "\n" + banner
        return output[: nl + 1] + banner + output[nl + 1 :]
    return banner + output


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
    if "{{" in output:
        raise StatsError(f"unresolved template token in {template_path}")
    return with_generated_banner(output, template_path)


def replacements_for_root() -> dict[str, str]:
    sections = parse_stats(STATS_PATH)

    running_kv = parse_kv(require(sections, "running"), "running")
    total_km = require_int(running_kv, "total_km", "running")
    if total_km < 0:
        raise StatsError(f"running.total_km must be non-negative, got {total_km}")
    since_year = require_int(running_kv, "since_year", "running")
    running_as_of = as_of_label(running_kv.get("as_of", ""))

    total_km_fmt = f"{total_km:,}"
    remaining_km = MOON_KM - total_km
    remaining_fmt = f"{remaining_km:,}"
    moon_pct_fmt = f"{round(total_km / MOON_KM * 100, 1)}"
    earth = earth_prose(total_km)
    earth_mult = earth_multiplier(total_km)

    books_current = parse_books(require(sections, "reading_current"), "reading_current")
    reading_current_html = render_reading_current(books_current)

    books_year = parse_books(require(sections, "reading_year"), "reading_year")
    reading_year_str = render_reading_year(books_year)

    learning = parse_text(require(sections, "learning"))
    if not learning:
        raise StatsError("learning: section body is empty")

    paper_home = paper_site.render_home(total_km, since_year, running_as_of)

    return {
        "{{running_total_km}}": total_km_fmt,
        "{{running_since}}": str(since_year),
        "{{running_earth_prose}}": earth,
        "{{running_earth_multiplier}}": earth_mult,
        "{{running_moon_remaining}}": remaining_fmt,
        "{{running_moon_pct}}": moon_pct_fmt,
        "{{reading_current}}": reading_current_html,
        "{{reading_year}}": reading_year_str,
        "{{learning}}": learning,
        "{{running_as_of}}": running_as_of,
        "{{paper_home}}": paper_home,
        "{{paper_head}}": paper_site.head("home"),
    }


def expected_root() -> str:
    """Return the exact current source-derived home document."""
    return render(ROOT_TEMPLATE_PATH, replacements_for_root())


def check_home() -> None:
    """Fail loudly when the generated home file is stale or malformed."""
    if not INDEX_PATH.is_file():
        raise StatsError(f"generated home file not found: {INDEX_PATH}")
    expected = expected_root()
    actual = INDEX_PATH.read_text(encoding="utf-8")
    if actual != expected:
        raise StatsError(
            "index.html is stale relative to its template, essay registry, or content source; "
            "run python3 _scripts/build_root.py"
        )
    for token in ("{{home_worlds}}", "{{home_building}}", "{{home_essays}}", "{{running_as_of}}"):
        if token in actual:
            raise StatsError(f"index.html contains unresolved token: {token}")


def build(check_only: bool = False, root_only: bool = False) -> None:
    replacements = replacements_for_root()

    targets: list[tuple[Path, Path]] = [(ROOT_TEMPLATE_PATH, INDEX_PATH)]
    if not root_only:
        targets.extend(
            [
                (RUNNING_TEMPLATE_PATH, RUNNING_INDEX_PATH),
                (READING_TEMPLATE_PATH, READING_INDEX_PATH),
                (LEARNING_TEMPLATE_PATH, LEARNING_INDEX_PATH),
            ]
        )

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
    parser.add_argument("--root-only", action="store_true", help="write only index.html")
    parser.add_argument("--check-home", action="store_true", help="fail unless index.html matches its sources")
    args = parser.parse_args()

    try:
        if args.check_home:
            check_home()
            print(f"checked {INDEX_PATH}")
        else:
            build(check_only=args.check, root_only=args.root_only)
    except (StatsError, home_catalog.CatalogError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
