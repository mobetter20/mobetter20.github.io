#!/usr/bin/env python3
"""Proof-of-pipeline: render two metro networks at one shared scale (SVG).

Fetches raw per-city GeoJSON from the OSM subway-validator CDN, projects it
(equirectangular, km units, north-up), and draws both networks side by side at a
single pixels-per-km scale with their real OSM line colours. This is the data
proof behind Compare/Shape — NOT a design mock. Output goes to /tmp (binaries and
generated art stay out of git).

Usage: python3 _scripts/world_metros/proof_same_scale.py
"""

import json
import math
import urllib.request

CDN = "https://cdn.organicmaps.app/subway/"
OUT = "/tmp/world-metros-proof.svg"
PX_PER_KM = 14
PAD = 40

# (title, slug, refs to draw — None = all). Seoul L1 excluded pending scope rule
# (DATA-CONTRACT.md): its OSM network carries ~26 Korail through-running variants.
PANELS = [
    ("SEOUL · lines 2–9 (L1 scope TBD)", "seoul", {str(i) for i in range(2, 10)}),
    ("PARIS · Métro 1–14", "paris",
     {"1", "2", "3", "3bis", "4", "5", "6", "7", "7bis", "8", "9", "10", "11", "12", "13", "14"}),
]


def load_city(slug, ref_filter):
    req = urllib.request.Request(f"{CDN}{slug}.geojson",
                                 headers={"User-Agent": "world-metros-atlas-proof"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        gj = json.load(resp)
    segs = []
    for f in gj["features"]:
        if f["geometry"]["type"] != "LineString":
            continue
        p = f["properties"]
        if ref_filter and p.get("ref") not in ref_filter:
            continue
        segs.append((p.get("stroke", "#888"), f["geometry"]["coordinates"]))
    return segs


def project(segs):
    """Equirectangular into km, y flipped so north is up."""
    n = sum(len(cs) for _, cs in segs)
    lat0 = sum(c[1] for _, cs in segs for c in cs) / n
    k = math.cos(math.radians(lat0))
    return [(color, [(c[0] * 111.32 * k, -c[1] * 110.57) for c in cs])
            for color, cs in segs]


def bbox(segs):
    xs = [p[0] for _, cs in segs for p in cs]
    ys = [p[1] for _, cs in segs for p in cs]
    return min(xs), min(ys), max(xs), max(ys)


def main():
    cells, offx, maxh = [], PAD, 0.0
    for title, slug, refs in PANELS:
        segs = project(load_city(slug, refs))
        x0, y0, x1, y1 = bbox(segs)
        w, h = (x1 - x0) * PX_PER_KM, (y1 - y0) * PX_PER_KM
        cells.append((title, segs, offx, x0, y0, h))
        offx += w + PAD * 2
        maxh = max(maxh, h)

    W, H = offx, maxh + PAD * 2 + 30
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}"'
           f' font-family="monospace">',
           f'<rect width="{W:.0f}" height="{H:.0f}" fill="#070A14"/>']
    for title, segs, ox, x0, y0, h in cells:
        oy = PAD + (maxh - h) / 2 + 20
        svg.append(f'<text x="{ox:.0f}" y="{PAD - 10}" fill="#F2EAD8" font-size="15">{title}</text>')
        for color, cs in segs:
            pts = " ".join(f"{ox + (x - x0) * PX_PER_KM:.1f},{oy + (y - y0) * PX_PER_KM:.1f}"
                           for x, y in cs)
            svg.append(f'<polyline points="{pts}" fill="none" stroke="{color}"'
                       f' stroke-width="2.2" stroke-linecap="round" opacity="0.92"/>')
    sb = 10 * PX_PER_KM
    svg.append(f'<line x1="{PAD}" y1="{H - 18:.0f}" x2="{PAD + sb}" y2="{H - 18:.0f}"'
               f' stroke="#F2EAD8" stroke-width="2"/>')
    svg.append(f'<text x="{PAD + sb + 8}" y="{H - 13:.0f}" fill="#F2EAD8" font-size="13">'
               f'10 km · one shared scale · north-up · OSM (ODbL)</text>')
    svg.append("</svg>")
    with open(OUT, "w") as fh:
        fh.write("\n".join(svg))
    print(f"wrote {OUT} ({W:.0f}x{H:.0f})")


if __name__ == "__main__":
    main()
