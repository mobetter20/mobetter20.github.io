#!/usr/bin/env python3
"""The map bake-off board (gate-2 spike, owner-locked 2026-06-11).

One judgment surface for the Explore-map direction: per city (Seoul / Tokyo /
Paris), three candidate looks side by side:

  1. POLISHED GEOGRAPHIC — our true OSM geometry, round-2 polish (Chaikin
     smoothing, white casing, recessive ghost rail, smoothed water). Rendered
     inline by importing build_geo_shape_mock.
  2. CONSISTENT SCHEMATIC — octolinear render of the same network (LOOM-class
     tooling). Embedded from assets/octi-<city>.svg when the feasibility run
     produced one; otherwise the cell explains exactly why not.
  3. THE FAMILIAR DIAGRAM — the per-city Commons recreation already shipped on
     the prototype (reference point; embedded from the page's assets).

Static approval artifact, no JS. Writes bakeoff-board.html next to this file.

Usage:
    python3 _scripts/world_metros/mocks/build_bakeoff_board.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import build_geo_shape_mock as gm  # noqa: E402
import build_page_geometry as bpg  # noqa: E402  (cache + projection helpers)

CELL_W, CELL_H = 396, 360
CITIES = ("seoul", "tokyo", "paris")

# Octolinear evidence: screenshots of LOOM's global deployment (the team's
# own planet-scale octilinearization of OSM), basemap + UI hidden, white
# ground. Caveats carried on the cell: their "subway-lightrail" network
# includes lines beyond our scope, station/line styling is theirs, colors are
# OSM's. The LOCAL pipeline (our scoped data, our colors, SVG out) is fully
# prepared — loom_convert.py emits verified line-graph GeoJSON for all three
# cities and the docker build is one admin click away (Docker Desktop's
# privileged-helper prompt can't be clicked from this session).
OCTI_STATUS = {
    "seoul": "assets/octi-demo-seoul.png",
    "tokyo": "assets/octi-demo-tokyo.png",
    "paris": "assets/octi-demo-paris.png",
}
OCTI_CREDIT = ("octolinear render: LOOM global demo, University of Freiburg "
               "(Chair of Algorithms and Data Structures) · data © OpenStreetMap "
               "contributors · shown scope wider than ours (incl. lightrail)")
OCTI_NOTE = "octolinear feasibility run pending"

DIAGRAM_META = {
    "seoul": ("seoul-diagram.svg",
              "“Seoul Metropolitan Subway network map” by Satellizer, "
              "Wikimedia Commons, CC BY-SA 4.0"),
    "tokyo": ("tokyo-diagram.svg",
              "“Tokyo Subway Linemap” by Yveltal, Wikimedia Commons, CC BY-SA 4.0"),
    "paris": ("paris-diagram.svg",
              "“Carte Métro de Paris” by Rigil, Wikimedia Commons, CC BY 3.0"),
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap');
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#e8e8e3; color:#17171c; display:flex; align-items:flex-start;
       justify-content:center; min-height:100vh; padding:24px 0;
       font-family:-apple-system,'Helvetica Neue','Segoe UI',Arial,sans-serif; }
.board { width:1280px; background:#f7f7f4; outline:1px solid #d8d8d2;
         box-shadow:0 1px 14px rgba(20,20,28,.10); }
header { display:flex; align-items:baseline; gap:20px; padding:14px 22px 11px;
         border-bottom:1px solid #d8d8d2; background:#fff; }
.wordmark { font-size:15px; font-weight:700; letter-spacing:.24em; }
.wordmark em { font-style:normal; color:#0052a4; }
.mockbadge { margin-left:auto; font-family:'DM Mono',monospace; font-size:9px;
             letter-spacing:.14em; color:#d96629; border:1px solid #d9662966;
             padding:3px 7px; border-radius:2px; background:#fff;
             white-space:nowrap; }
.intro { padding:9px 22px; font-size:11px; color:#8a8a85; background:#fff;
         border-bottom:1px solid #d8d8d2; line-height:1.5; }
.intro b { color:#17171c; font-weight:600; }
.colheads { display:flex; gap:14px; padding:12px 14px 0; }
.colheads div { flex:1; font-size:10px; letter-spacing:.16em; font-weight:700;
                color:#17171c; }
.colheads div small { display:block; font-weight:400; letter-spacing:.02em;
                      color:#8a8a85; font-size:9.5px; margin-top:3px; }
.cityrow { display:flex; gap:14px; padding:10px 14px 4px; align-items:stretch; }
.cityname { padding:14px 14px 0; font-size:12px; font-weight:800;
            letter-spacing:.2em; }
.cell { flex:1; position:relative; background:#fff; border:1px solid #d8d8d2;
        height:%(h)spx; min-width:0; overflow:hidden; display:flex;
        align-items:center; justify-content:center; }
.cell img { width:100%%; height:100%%; object-fit:contain; padding:6px; }
.cell .credit { position:absolute; bottom:6px; left:8px; right:8px;
                font-family:'DM Mono',monospace; font-size:7.5px; color:#b9b9b2;
                background:rgba(255,255,255,.9); padding:2px 4px;
                border-radius:2px; line-height:1.4; }
.cell .scale { position:absolute; bottom:8px; left:10px; display:flex;
               align-items:center; gap:7px; font-size:8.5px; color:#8a8a85;
               font-family:'DM Mono',monospace; }
.cell .scale .bar { height:3px; background:#17171c; display:inline-block;
                    border-radius:2px; }
.cell .miss { padding:22px; font-size:11px; line-height:1.65; color:#8a8a85;
              text-align:center; }
.cell .miss b { color:#d96629; font-family:'DM Mono',monospace; font-size:9px;
                letter-spacing:.14em; display:block; margin-bottom:8px; }
footer { display:flex; justify-content:space-between; padding:9px 22px;
         border-top:1px solid #d8d8d2; font-family:'DM Mono',monospace;
         font-size:9px; color:#8a8a85; background:#fff; margin-top:10px; }
""" % {"h": CELL_H}


def geo_cell(city):
    net = gm.load_network_with_k(city)
    x0, y0, x1, y1 = gm.net_bbox(net)
    bb = (x0 - gm.PAD_KM, y0 - gm.PAD_KM, x1 + gm.PAD_KM, y1 + gm.PAD_KM)
    k = net["k"]
    geo = (-bb[3] / 110.57, bb[0] / (111.32 * k),
           -bb[1] / 110.57, bb[2] / (111.32 * k))
    raw = gm.fetch_water(city, geo)
    polys, coast = gm.extract_water(raw, k, bb)
    cw, cl, strokes = gm.close_coastline(coast, bb)
    svg, s = gm.svg_map(net, polys, cw, cl, strokes, CELL_W, CELL_H)
    bar = 10 * s
    return (f'<div class="cell">{svg}<div class="scale">'
            f'<span class="bar" style="width:{bar:.0f}px"></span>'
            f'<span>10 km</span></div></div>')


def octi_cell(city):
    asset = OCTI_STATUS.get(city)
    if asset and os.path.exists(os.path.join(HERE, asset)):
        return (f'<div class="cell"><img src="{asset}" '
                f'alt="{city} octolinear schematic">'
                f'<div class="credit">{OCTI_CREDIT}</div></div>')
    return (f'<div class="cell"><div class="miss"><b>NOT RENDERED</b>'
            f'{OCTI_NOTE}</div></div>')


def diagram_cell(city):
    fname, credit = DIAGRAM_META[city]
    rel = f"../../../is/building/world-metros/assets/{fname}"
    return (f'<div class="cell"><img src="{rel}" alt="{city} familiar diagram">'
            f'<div class="credit">{credit}</div></div>')


def main():
    rows = []
    for city in CITIES:
        print(f"== {city}")
        rows.append(f'<div class="cityname">{city.upper()}</div>'
                    f'<div class="cityrow">{geo_cell(city)}{octi_cell(city)}'
                    f'{diagram_cell(city)}</div>')

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>world-metros mock — map bake-off</title>
<style>{CSS}</style></head><body><div class="board">
<header><div class="wordmark">WORLD METROS <em>ATLAS</em></div>
<span class="mockbadge">MAP BAKE-OFF · ONE VERDICT BOARD · NOT THE PRODUCT</span></header>
<div class="intro"><b>the bake-off:</b> pick the Explore-map direction. Column 1
is ours (true geometry, polish pass: smoothing + casing + water). Column 2 is the
consistent octolinear schematic (auto-generated from the same OSM data). Column 3
is the per-city Commons recreation the prototype ships today (the patchwork
reference). The winner resolves D13; Shape keeps true geometry regardless.</div>
<div class="colheads">
  <div>1 · POLISHED GEOGRAPHIC<small>ours · one style for all 12 · no labels yet</small></div>
  <div>2 · CONSISTENT SCHEMATIC<small>auto-octolinear (LOOM) · one style for all 12 · evidence via their global demo; local run prepped</small></div>
  <div>3 · THE FAMILIAR DIAGRAM<small>per-city Commons recreations · the patchwork</small></div>
</div>
{"".join(rows)}
<footer><span>geometry + water © OpenStreetMap contributors · ODbL · {gm.SNAPSHOT_NOTE}</span>
<span>made by ajin.im</span></footer>
</div></body></html>"""
    out = os.path.join(HERE, "bakeoff-board.html")
    with open(out, "w") as fh:
        fh.write(html)
    print(f"wrote {out}  ({os.path.getsize(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
