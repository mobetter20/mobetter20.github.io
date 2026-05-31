#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


VALID_KINDS = {
    "official_hub",
    "official_service",
    "media",
    "community",
    "practitioner",
    "record_surface",
    "meta_directory",
    "listed_only",
}

VALID_STATUS = {"planned", "live", "listed_only"}


def fail(message: str) -> None:
    print(f"[bird-universe-check] ERROR: {message}", file=sys.stderr)


def warn(message: str) -> None:
    print(f"[bird-universe-check] WARNING: {message}")


def find_site(sites: list[dict], slug: str) -> dict | None:
    for site in sites:
        if site.get("slug") == slug:
            return site
    return None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_hrefs(text: str) -> list[str]:
    return re.findall(r'href="([^"]+)"', text)


def require_substrings(text: str, required: list[str], context: str, errors: list[str]) -> None:
    for needle in required:
        if needle not in text:
            errors.append(f"{context}: missing required reference {needle!r}")


_A_ANCHOR_PATTERN = re.compile(r'<a\b[^>]*\bhref="#([^"]+)"', re.IGNORECASE)


def check_anchor_targets(repo_root: Path, sites: list[dict], errors: list[str]) -> None:
    """Verify every <a href="#X"> in bird-universe pages has a matching id="X" on the same page.

    Scoped to <a> elements only. SVG textPath/use/clipPath href="#..." references
    resolve through <defs>, not body ids, and are intentionally not checked here.
    """
    seen_files: set[Path] = set()
    for site in sites:
        canonical = site.get("canonicalPath", "").lstrip("/")
        if not canonical:
            continue
        site_root = repo_root / canonical
        if not site_root.exists():
            continue
        for html_file in sorted(site_root.rglob("*.html")):
            if html_file in seen_files:
                continue
            seen_files.add(html_file)
            text = html_file.read_text(encoding="utf-8", errors="ignore")
            for anchor in sorted(set(_A_ANCHOR_PATTERN.findall(text))):
                if not re.search(rf'\bid="{re.escape(anchor)}"', text):
                    rel = html_file.relative_to(repo_root)
                    errors.append(
                        f'{rel}: <a href="#{anchor}"> has no matching id="{anchor}" on the page'
                    )


def main() -> int:
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[2]
    registry_path = script_path.with_name("bird_universe_registry.json")

    data = json.loads(registry_path.read_text(encoding="utf-8"))
    errors: list[str] = []

    sites = data.get("sites", [])
    slugs: set[str] = set()
    paths: set[str] = set()

    official_hub_slug = data.get("officialHubSlug")
    meta_directory_slug = data.get("metaDirectorySlug")

    if not official_hub_slug:
        errors.append("Registry missing officialHubSlug.")
    if not meta_directory_slug:
        errors.append("Registry missing metaDirectorySlug.")

    for site in sites:
        slug = site.get("slug")
        kind = site.get("kind")
        status = site.get("status")
        canonical_path = site.get("canonicalPath")
        parent = site.get("parent")

        if not slug:
            errors.append("Site entry missing slug.")
            continue
        if slug in slugs:
            errors.append(f"Duplicate slug: {slug}")
        slugs.add(slug)

        if kind not in VALID_KINDS:
            errors.append(f"{slug}: invalid kind {kind!r}")
        if status not in VALID_STATUS:
            errors.append(f"{slug}: invalid status {status!r}")

        if status in {"live", "planned"}:
            if not canonical_path:
                errors.append(f"{slug}: live/planned site missing canonicalPath")
            else:
                if not canonical_path.startswith("/is/writing/"):
                    errors.append(f"{slug}: canonicalPath must start with /is/writing/: {canonical_path}")
                if not canonical_path.endswith("/"):
                    errors.append(f"{slug}: canonicalPath must end with /: {canonical_path}")
                if canonical_path in paths:
                    errors.append(f"{slug}: duplicate canonicalPath {canonical_path}")
                paths.add(canonical_path)

        if status == "live" and canonical_path:
            local_index = repo_root / canonical_path.lstrip("/") / "index.html"
            if not local_index.exists():
                errors.append(f"{slug}: live site missing file {local_index}")

        if kind == "record_surface" and parent != "nest-court":
            errors.append(f"{slug}: record_surface parent must be nest-court")

        if slug == official_hub_slug and kind != "official_hub":
            errors.append(f"{slug}: officialHubSlug must point to an official_hub")
        if slug == meta_directory_slug and kind != "meta_directory":
            errors.append(f"{slug}: metaDirectorySlug must point to a meta_directory")

    if official_hub_slug and official_hub_slug not in slugs:
        errors.append(f"officialHubSlug {official_hub_slug!r} not found in registry")
    if meta_directory_slug and meta_directory_slug not in slugs:
        errors.append(f"metaDirectorySlug {meta_directory_slug!r} not found in registry")

    avian_site = find_site(sites, "avian-district")
    avian_live = bool(avian_site and avian_site.get("status") == "live")
    avian_index = repo_root / "is/writing/avian-district/index.html"
    writing_index = repo_root / "is/writing/index.html"
    secondnest_index = repo_root / "is/writing/secondnest/index.html"

    if official_hub_slug == "avian-district":
        required_root_relative = [
            '/is/writing/nest-court/',
            '/is/writing/bird-coo/',
            '/is/writing/secondnest/',
            '/is/writing/perch-chat/',
            '/is/writing/karen-hawk/',
        ]

        # The hardcoded list above is the independent enforcement assertion — a
        # second pair of eyes on what avian-district must link, deliberately not
        # auto-derived from the registry. Cross-check it against the registry's
        # showInOfficialHub flags so the two cannot silently drift: a newly
        # flagged hub site that nobody added here would otherwise go unguarded,
        # and a leftover entry here would outlive its flag.
        flagged_hub_paths = {
            site_entry.get("canonicalPath")
            for site_entry in sites
            if site_entry.get("showInOfficialHub") and site_entry.get("slug") != official_hub_slug
        }
        required_paths = set(required_root_relative)
        for missing in sorted(flagged_hub_paths - required_paths):
            errors.append(
                f"avian-district: {missing} is showInOfficialHub in the registry "
                "but missing from the checker's required-link set"
            )
        for stale in sorted(required_paths - flagged_hub_paths):
            errors.append(
                f"avian-district: {stale} is in the checker's required-link set "
                "but not showInOfficialHub in the registry"
            )

        if not avian_index.exists():
            warn("avian-district is still planned; parent-link migration has not started yet.")
        else:
            avian_text = read_text(avian_index)
            avian_hrefs = extract_hrefs(avian_text)

            if 'href="#"' in avian_text:
                errors.append("avian-district: structural page still contains href=\"#\" placeholders")

            require_substrings(
                avian_text,
                required_root_relative,
                "avian-district",
                errors,
            )

            if any("bird-docket" in href for href in avian_hrefs):
                errors.append("avian-district: official hub should not point to bird-docket as a primary district destination")

            bird_site_slugs = [
                "nest-court",
                "bird-coo",
                "secondnest",
                "perch-chat",
                "karen-hawk",
                "bird-docket",
                "nest-court-proceedings",
                "nest-court-proceedings-pigeon",
                "nest-court-proceedings-starling",
            ]
            for href in avian_hrefs:
                if any(slug in href for slug in bird_site_slugs):
                    if not href.startswith("/is/writing/"):
                        errors.append(
                            f"avian-district: structural bird-universe link must be root-relative, got {href!r}"
                        )

        if avian_live:
            if writing_index.exists():
                writing_hrefs = extract_hrefs(read_text(writing_index))
                if any("bird-docket" in href for href in writing_hrefs):
                    errors.append("is/writing/index.html still links to bird-docket after avian-district went live")

            if secondnest_index.exists():
                secondnest_hrefs = extract_hrefs(read_text(secondnest_index))
                if any("bird-docket" in href for href in secondnest_hrefs):
                    errors.append("secondnest still links to bird-docket as district parent after avian-district went live")
        else:
            if writing_index.exists():
                writing_hrefs = extract_hrefs(read_text(writing_index))
                if any("bird-docket" in href for href in writing_hrefs):
                    warn("is/writing/index.html still routes to bird-docket; expected before avian-district cutover")

            if secondnest_index.exists():
                secondnest_hrefs = extract_hrefs(read_text(secondnest_index))
                if any("bird-docket" in href for href in secondnest_hrefs):
                    warn("secondnest still uses bird-docket as district parent; expected before avian-district cutover")

    check_anchor_targets(repo_root, sites, errors)

    if errors:
        for message in errors:
            fail(message)
        return 1

    print(f"[bird-universe-check] Registry OK: {len(sites)} entries checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
