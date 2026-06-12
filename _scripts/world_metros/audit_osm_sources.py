#!/usr/bin/env python3
"""Audit the OSM subway-validator CDN for World Metros Atlas candidate cities.

For every candidate: is the network validating GOOD on the subway preprocessor
(cdn.organicmaps.app/subway/), and how big is its raw GeoJSON? Re-run any time;
network access only, writes nothing. See DATA-CONTRACT.md for what this feeds.
"""

import re
import sys
import urllib.request

CDN = "https://cdn.organicmaps.app/subway/"

# city slug -> validator country page
CITIES = {
    "shanghai": "china.html",
    "beijing": "china.html",
    "hong_kong": "china.html",
    "tokyo": "japan.html",
    "seoul": "south-korea.html",
    "singapore": "singapore.html",
    "delhi": "india.html",
    "london": "uk.html",
    "paris": "france.html",
    "new_york_city": "usa.html",
    "mexico_city": "mexico.html",
    "moscow": "russia.html",
    "cairo": "egypt.html",
    # D23 newcomers (Beijing was already a candidate above)
    "madrid": "spain.html",
    "copenhagen": "denmark.html",
    "guangzhou": "china.html",
}

ROW_RE = re.compile(r'<tr id="([^"]+)">\s*<td class="bold (color\d)">')


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "world-metros-atlas-audit"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def main() -> int:
    pages = {}
    failures = 0
    for slug, page in CITIES.items():
        if page not in pages:
            try:
                pages[page] = fetch(CDN + page).decode("utf-8", "replace")
            except OSError as e:
                print(f"FETCH FAIL {page}: {e}")
                pages[page] = ""
        statuses = dict(ROW_RE.findall(pages[page]))
        color = statuses.get(slug)
        status = {"color1": "GOOD", "color0": "ERRORS"}.get(color, "NOT FOUND")
        size = "?"
        try:
            req = urllib.request.Request(
                f"{CDN}{slug}.geojson", method="HEAD",
                headers={"User-Agent": "world-metros-atlas-audit"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                size = f"{int(resp.headers.get('Content-Length', 0)) / 1024:.0f} KB"
        except OSError:
            status = status + " (geojson HEAD failed)"
        if status != "GOOD":
            failures += 1
        print(f"{slug:16s} {status:10s} {size:>9s}  ({page})")
    print(f"\n{len(CITIES) - failures}/{len(CITIES)} candidates GOOD")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
