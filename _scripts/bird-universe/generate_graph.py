#!/usr/bin/env python3
"""Generate bird_universe_graph.json — precomputed cross-reference cache.

Reads:
  - _scripts/bird-universe/config.json — must contain "registryRepoPath"
  - _scripts/bird-universe/bird_universe_registry.json — site topology
  - <registryRepoPath>/02-registry.md — characters and cases tables
  - All HTML files under each registered site's canonicalPath

Writes:
  - _scripts/bird-universe/bird_universe_graph.json

Schema v1:
  {
    "version": 1,
    "registry_source_sha": "<sha256 of 02-registry.md>",
    "sites": [...],         # verbatim from bird_universe_registry.json
    "characters": [          # parsed from 02-registry.md Characters table
      {"name", "species", "location", "key_facts", "active_cases": [...], "mentions": [...]}
    ],
    "cases": [               # parsed from 02-registry.md Cases table
      {"number", "type", "parties", "filed", "status", "key_facts",
       "mentions": [...], "dedicated_page": <path or null>}
    ]
  }

Future entity types (locations, ordinances, forms) are intentionally
deferred until a downstream consumer needs them.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
SITES_REGISTRY_PATH = SCRIPT_DIR / "bird_universe_registry.json"
GRAPH_OUTPUT_PATH = SCRIPT_DIR / "bird_universe_graph.json"

CASE_NUMBER_PATTERN = re.compile(r"AMNC-\d{4}-\d+[A-Z]")


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        sys.exit(
            f"ERROR: config not found at {CONFIG_PATH}.\n"
            "Create it as JSON with key 'registryRepoPath' pointing at the "
            "bird-universe registry repo (the directory containing 02-registry.md)."
        )
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def parse_table(content: str, header_text: str) -> list[dict]:
    """Find the markdown table under '#### {header_text}' and return rows as dicts."""
    headers: list[str] | None = None
    rows: list[dict] = []
    in_section = False
    for line in content.split("\n"):
        stripped = line.strip()
        if not in_section:
            if stripped.startswith("####") and stripped[4:].strip() == header_text:
                in_section = True
            continue
        if stripped.startswith("####") or stripped.startswith("---"):
            break
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells if c):
            continue  # divider row
        if headers is None:
            headers = cells
        else:
            rows.append(dict(zip(headers, cells)))
    return rows


def parse_characters(content: str) -> list[dict]:
    return [
        {
            "name": r.get("Name", "").strip(),
            "species": r.get("Species", "").strip(),
            "location": r.get("Location", "").strip(),
            "key_facts": r.get("Key Facts", "").strip(),
            "active_cases": [
                c.strip()
                for c in r.get("Active Cases", "").split(",")
                if c.strip() and c.strip() != "—"
            ],
        }
        for r in parse_table(content, "Characters")
        if r.get("Name", "").strip()
    ]


def parse_cases(content: str) -> list[dict]:
    return [
        {
            "number": r.get("Case No.", "").strip(),
            "type": r.get("Type", "").strip(),
            "parties": r.get("Parties", "").strip(),
            "filed": r.get("Filed", "").strip(),
            "status": r.get("Status", "").strip(),
            "key_facts": r.get("Key Dates/Facts", "").strip(),
        }
        for r in parse_table(content, "Cases")
        if r.get("Case No.", "").strip()
    ]


def collect_html_files(sites: list[dict]) -> list[Path]:
    """All HTML files under any registered site's canonicalPath."""
    seen: set[Path] = set()
    files: list[Path] = []
    for site in sites:
        canonical = site.get("canonicalPath", "").lstrip("/")
        if not canonical:
            continue
        site_root = REPO_ROOT / canonical
        if not site_root.exists():
            continue
        for f in sorted(site_root.rglob("*.html")):
            if f not in seen:
                seen.add(f)
                files.append(f)
    return files


def collect_case_mentions(case_number: str, html_files: list[Path]) -> tuple[list[str], str | None]:
    """Return (mentions, dedicated_page).

    dedicated_page = the file whose <title> contains this case number, if any.
    A case can have at most one dedicated page; ties resolve to the first found.
    """
    mentions: list[str] = []
    dedicated: str | None = None
    title_pattern = re.compile(rf"<title>[^<]*{re.escape(case_number)}[^<]*</title>")
    case_pattern = re.compile(re.escape(case_number))
    for f in html_files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        if not case_pattern.search(text):
            continue
        rel = str(f.relative_to(REPO_ROOT))
        mentions.append(rel)
        if dedicated is None and title_pattern.search(text):
            dedicated = rel
    return mentions, dedicated


def collect_character_mentions(name: str, html_files: list[Path]) -> list[str]:
    """File paths where this character name appears as a whole-word match."""
    mentions: list[str] = []
    pattern = re.compile(rf"\b{re.escape(name)}\b")
    for f in html_files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        if pattern.search(text):
            mentions.append(str(f.relative_to(REPO_ROOT)))
    return mentions


def main() -> int:
    config = load_config()
    registry_path_str = config.get("registryRepoPath")
    if not registry_path_str:
        sys.exit(
            f"ERROR: config at {CONFIG_PATH} missing 'registryRepoPath'."
        )
    registry_root = Path(registry_path_str).expanduser()
    registry_md = registry_root / "02-registry.md"
    if not registry_md.exists():
        sys.exit(f"ERROR: registry markdown not found at {registry_md}.")

    registry_text = registry_md.read_text(encoding="utf-8")
    registry_sha = hashlib.sha256(registry_text.encode("utf-8")).hexdigest()

    sites_data = json.loads(SITES_REGISTRY_PATH.read_text(encoding="utf-8"))
    sites = sites_data.get("sites", [])

    characters = parse_characters(registry_text)
    cases = parse_cases(registry_text)

    html_files = collect_html_files(sites)

    for case in cases:
        mentions, dedicated = collect_case_mentions(case["number"], html_files)
        case["mentions"] = mentions
        case["dedicated_page"] = dedicated

    for char in characters:
        char["mentions"] = collect_character_mentions(char["name"], html_files)

    output = {
        "version": 1,
        "registry_source_sha": registry_sha,
        "sites": sites,
        "characters": characters,
        "cases": cases,
    }

    GRAPH_OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"[generate_graph] Wrote {GRAPH_OUTPUT_PATH.name} "
        f"({len(sites)} sites, {len(characters)} characters, "
        f"{len(cases)} cases, {len(html_files)} files scanned)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
