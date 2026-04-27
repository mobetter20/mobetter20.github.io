#!/usr/bin/env python3
"""Lint bird-universe HTML for case numbers and form IDs against the registry.

Reads:
  - _scripts/bird-universe/bird_universe_graph.json (cases, sites)
  - All HTML files under each registered site's canonicalPath

Checks:
  - Case-number format consistency. Pattern: AMNC-YYYY-NNN[A-Z].
    - Exact match against registered case  → silent
    - Case-variant of a registered case    → ERROR (likely typo)
    - Plausible but unregistered           → WARNING (new case to add, or typo)
  - Form-ID format. Pattern: CL-XX-NN.
    - Canonical uppercase format           → silent
    - Lowercase or mixed-case variant      → ERROR
    - Unregistered uppercase form          → WARNING (new form to add)

Character names are intentionally NOT linted in v1 — single-token names like
"Conrad" / "Dennis" / "Robin" collide with English words and produce a
false-positive flood. graph.json's characters[].mentions is available for
manual cross-check.

Forms are tracked here even though they are not yet in the graph schema; the
checker treats every uppercase form-ID it finds as "unregistered" and warns,
which is the safe default until the graph adds a forms section.

Exit code: 0 if no errors (warnings allowed). Non-zero if any error.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
GRAPH_PATH = SCRIPT_DIR / "bird_universe_graph.json"

CASE_PATTERN = re.compile(r"\bAMNC-\d{4}-\d+[A-Za-z]\b", re.IGNORECASE)
FORM_PATTERN = re.compile(r"\bCL-[A-Za-z]{2}-\d+\b", re.IGNORECASE)


def fail(message: str) -> None:
    print(f"[lint-identifiers] ERROR: {message}", file=sys.stderr)


def warn(message: str) -> None:
    print(f"[lint-identifiers] WARN: {message}")


def load_graph() -> dict:
    if not GRAPH_PATH.exists():
        sys.exit(
            f"ERROR: {GRAPH_PATH.name} not found. "
            "Run generate_graph.py first."
        )
    return json.loads(GRAPH_PATH.read_text(encoding="utf-8"))


def collect_html_files(sites: list[dict]) -> list[Path]:
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


def main() -> int:
    graph = load_graph()
    sites = graph.get("sites", [])
    cases = graph.get("cases", [])

    registered_cases: set[str] = {c["number"] for c in cases if c.get("number")}
    registered_cases_lower: dict[str, str] = {c.lower(): c for c in registered_cases}

    errors: list[str] = []
    warnings: list[str] = []
    seen_unregistered_cases: set[str] = set()
    seen_unregistered_forms: set[str] = set()

    for html_file in collect_html_files(sites):
        rel = str(html_file.relative_to(REPO_ROOT))
        text = html_file.read_text(encoding="utf-8", errors="ignore")

        for case in set(CASE_PATTERN.findall(text)):
            if case in registered_cases:
                continue
            canonical = registered_cases_lower.get(case.lower())
            if canonical:
                errors.append(
                    f"{rel}: case identifier {case!r} is a case-variant of "
                    f"registered {canonical!r} — fix the casing in the HTML"
                )
            elif case not in seen_unregistered_cases:
                seen_unregistered_cases.add(case)
                warnings.append(
                    f"case {case!r} appears in HTML (first seen in {rel}) "
                    f"but is not in the registry — add to 02-registry.md or fix typo"
                )

        for form in set(FORM_PATTERN.findall(text)):
            canonical = form.upper()
            if form != canonical:
                errors.append(
                    f"{rel}: form identifier {form!r} is not in canonical "
                    f"uppercase form (expected {canonical!r})"
                )
            elif form not in seen_unregistered_forms:
                seen_unregistered_forms.add(form)
                warnings.append(
                    f"form {form!r} appears in HTML (first seen in {rel}) — "
                    f"once forms are tracked in the graph, this should resolve to "
                    f"a registered form or be added to 02-registry.md"
                )

    for w in warnings:
        warn(w)
    for e in errors:
        fail(e)

    if errors:
        return 1
    print(
        f"[lint-identifiers] OK: {len(registered_cases)} cases registered, "
        f"{len(warnings)} warning(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
