#!/usr/bin/env python3
"""Atlas-page landing board — the D15 direction, ratified pick: WALL.

Two sections on one approval board:

  1. THE WALL — the landing hero: every roster network as a small dark
     true-shape silhouette at ONE shared px-per-km, north-up, name + one
     number. Seoul / Tokyo / Paris render real (from the prototype's shipped
     shape JSONs); the other nine are labeled placeholders (D8 gate: no
     roster scale-up before prototype approval).
  2. THE DOSSIER — the dwell surface, Seoul shown: content is the hero
     (why-stories, dated facts, line-palette strip); the map is a medium
     FIGURE (round-2 geo dress), with the other views demoted to links.

Static approval artifact, no JS. Writes wall-board.html next to this file.

Usage:
    python3 _scripts/world_metros/mocks/build_wall_board.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import build_geo_shape_mock as gm  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ASSETS = os.path.join(REPO, "is", "building", "world-metros", "assets")

ROSTER = ["shanghai", "tokyo", "seoul", "hong kong", "singapore", "delhi",
          "moscow", "london", "paris", "nyc", "mexico city", "cairo"]
LIVE = {"seoul", "tokyo", "paris"}

CELL_W, CELL_H = 296, 238   # wall cell; silhouette area above the name strip
SIL_PAD = 12

INK = "#17171c"

SEOUL_WHY = [
    "<b>why it’s here:</b> the densest reach of any metro on earth. The green "
    "Line 2 loop orbits the core while seven siblings lace a city of ten "
    "million into one grid.",
    "Full underground cell coverage, heated winter seats, and a circle line so "
    "central that “inside Line 2” is shorthand for downtown.",
]


def load_meta():
    return json.load(open(os.path.join(ASSETS, "meta.json")))


def load_shape(city):
    return json.load(open(os.path.join(ASSETS, f"{city}-shape.json")))


def wall_scale(meta):
    """Shared px-per-km: the largest live network fits the silhouette area."""
    inner_w, inner_h = CELL_W - 2 * SIL_PAD, CELL_H - 2 * SIL_PAD
    s = 1e9
    for city in LIVE:
        c = meta["cities"][city]
        s = min(s, inner_w / c["w_km"], inner_h / c["h_km"])
    return s


def silhouette_cell(city, meta, s):
    c = meta["cities"][city]
    shape = load_shape(city)
    w_px, h_px = shape["w_km"] * s, shape["h_km"] * s
    ox = (CELL_W - w_px) / 2
    oy = (CELL_H - h_px) / 2
    parts = [f'<svg viewBox="0 0 {CELL_W} {CELL_H}" '
             f'xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">']
    parts.append(f'<g fill="none" stroke="{INK}" stroke-width="1.8" '
                 f'stroke-linecap="round" stroke-linejoin="round">')
    for line in shape["lines"]:
        for path in line["paths"]:
            pts = " ".join(f"{ox + x * s:.1f},{oy + y * s:.1f}"
                           for x, y in gm.chaikin(path, 1))
            parts.append(f'<polyline points="{pts}"/>')
    parts.append("</g></svg>")
    return (f'<div class="cell live">{"".join(parts)}'
            f'<div class="cname">{city}</div>'
            f'<div class="cnum">furthest stations {c["span_km"]:.0f} km</div></div>')


def placeholder_cell(city):
    return (f'<div class="cell soon"><div class="soonbox">'
            f'<div class="cname">{city}</div>'
            f'<div class="cnum">soon</div></div></div>')


def dossier_figure():
    """Seoul medium figure in the round-2 geo dress (reuses the bake-off
    machinery; water comes from the /tmp cache or is re-fetched)."""
    net = gm.load_network_with_k("seoul")
    x0, y0, x1, y1 = gm.net_bbox(net)
    bb = (x0 - gm.PAD_KM, y0 - gm.PAD_KM, x1 + gm.PAD_KM, y1 + gm.PAD_KM)
    k = net["k"]
    geo = (-bb[3] / 110.57, bb[0] / (111.32 * k),
           -bb[1] / 110.57, bb[2] / (111.32 * k))
    raw = gm.fetch_water("seoul", geo)
    polys, coast = gm.extract_water(raw, k, bb)
    cw, cl, strokes = gm.close_coastline(coast, bb)
    svg, s = gm.svg_map(net, polys, cw, cl, strokes, 470, 408)
    bar = 10 * s
    return svg, bar


def dossier_section(meta):
    c = meta["cities"]["seoul"]
    chips = "".join(
        f'<i style="background:{l["color"]}">{l["ref"]}</i>'
        for l in c["lines"])
    facts = "".join(
        f'<div><span class="dt">{dt}</span><span class="dd">{dd}</span></div>'
        for dt, dd in [
            ("opened", "1974"),
            ("lines drawn", f'{len(c["lines"])} <span class="ev">(2–9 · L1 scope: Method)</span>'),
            ("stations plotted", str(c["stations"])),
            ("furthest-stations span", f'{c["span_km"]:.0f} km <span class="ev">computed</span>'),
            ("reported route-km", '<span class="ev">pipeline · dated at build</span>'),
            ("annual ridership", '<span class="ev">pipeline · dated at build</span>'),
        ])
    why = "".join(f"<p>{p}</p>" for p in SEOUL_WHY)
    svg, bar = dossier_figure()
    return f"""
<div class="seclabel">CITY DOSSIER · THE DWELL SURFACE · SEOUL SHOWN</div>
<div class="dossier">
  <div class="dcontent">
    <div class="cityname">SEOUL<small>SEOUL METROPOLITAN SUBWAY</small></div>
    <div class="why">{why}</div>
    <div class="facts">{facts}</div>
    <div class="palette">{chips}</div>
    <div class="dlinks"><span>the map riders see ↗</span>
      <span>the familiar diagram ↗</span><span>open the interactive map ↗</span>
      <span class="dim">compare with… ↗</span></div>
  </div>
  <div class="dfigure">
    <div class="figframe">{svg}
      <div class="figscale"><span class="bar" style="width:{bar:.0f}px"></span><span>10 km</span></div>
    </div>
    <div class="figcap">true shape, one of three demoted map views · the map is
    a figure here, not the hero</div>
  </div>
</div>"""


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
.seclabel { padding:16px 22px 8px; font-family:'DM Mono',monospace;
            font-size:10px; letter-spacing:.2em; color:#0052a4; }
.wall { display:grid; grid-template-columns:repeat(4, 1fr); gap:12px;
        padding:4px 22px 6px; }
.cell { background:#fff; border:1px solid #d8d8d2; position:relative;
        height:%(ch)spx; padding-bottom:34px; overflow:hidden; }
.cell .cname { position:absolute; left:10px; bottom:18px; font-size:11px;
               font-weight:800; letter-spacing:.14em; text-transform:uppercase; }
.cell .cnum { position:absolute; left:10px; bottom:6px;
              font-family:'DM Mono',monospace; font-size:8px; color:#8a8a85;
              letter-spacing:.05em; }
.cell.soon { background:#fbfbf9; }
.cell.soon .soonbox { position:absolute; inset:0; display:flex;
                      flex-direction:column; align-items:center;
                      justify-content:center; gap:4px; }
.cell.soon .cname { position:static; color:#b9b9b2; }
.cell.soon .cnum { position:static; color:#cfcfc8; }
.wallnote { display:flex; align-items:center; gap:10px; padding:6px 22px 14px;
            font-family:'DM Mono',monospace; font-size:9px; color:#8a8a85; }
.wallnote .bar { height:3px; background:#17171c; display:inline-block;
                 border-radius:2px; }
.dossier { display:flex; gap:14px; padding:4px 22px 18px; }
.dcontent { flex:1.15; background:#fff; border:1px solid #d8d8d2;
            padding:20px 20px 16px; }
.cityname { font-size:27px; font-weight:800; letter-spacing:.04em; }
.cityname small { display:block; font-size:9.5px; letter-spacing:.18em;
                  color:#0052a4; margin-top:5px; font-weight:600; }
.why { margin-top:14px; font-size:12px; line-height:1.65; color:#3c3c38;
       max-width:52ch; }
.why b { color:#d96629; font-weight:700; }
.why p + p { margin-top:8px; }
.facts { margin-top:16px; border-top:1px solid #d8d8d2;
         font-family:'DM Mono',monospace; }
.facts > div { display:flex; justify-content:space-between; gap:10px;
               align-items:baseline; padding:7px 0;
               border-bottom:1px solid #f7f7f4; font-size:11px; }
.facts .dt { color:#8a8a85; }
.facts .dd { text-align:right; font-weight:500; }
.facts .ev { color:#b9b9b2; font-size:9px; }
.palette { margin-top:14px; display:flex; gap:5px; flex-wrap:wrap; }
.palette i { font-style:normal; font-size:9.5px; color:#fff; padding:2px 0;
             min-width:22px; text-align:center; border-radius:999px;
             font-weight:700; }
.dlinks { margin-top:16px; display:flex; gap:14px; flex-wrap:wrap;
          font-size:10.5px; font-weight:600; color:#0052a4;
          letter-spacing:.04em; }
.dlinks .dim { color:#8a8a85; }
.dfigure { flex:1; display:flex; flex-direction:column; }
.figframe { background:#fff; border:1px solid #d8d8d2; position:relative;
            height:410px; }
.figscale { position:absolute; bottom:8px; left:10px; display:flex;
            align-items:center; gap:7px; font-size:8.5px; color:#8a8a85;
            font-family:'DM Mono',monospace; }
.figscale .bar { height:3px; background:#17171c; display:inline-block;
                 border-radius:2px; }
.figcap { margin-top:7px; font-family:'DM Mono',monospace; font-size:8.5px;
          color:#8a8a85; line-height:1.5; letter-spacing:.03em; }
footer { display:flex; justify-content:space-between; padding:9px 22px;
         border-top:1px solid #d8d8d2; font-family:'DM Mono',monospace;
         font-size:9px; color:#8a8a85; background:#fff; }
""" % {"ch": CELL_H + 34}


def main():
    meta = load_meta()
    s = wall_scale(meta)
    cells = []
    for city in ROSTER:
        if city in LIVE:
            cells.append(silhouette_cell(city, meta, s))
        else:
            cells.append(placeholder_cell(city))
    bar = 10 * s

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>world-metros mock — atlas-page wall</title>
<style>{CSS}</style></head><body><div class="board">
<header><div class="wordmark">WORLD METROS <em>ATLAS</em></div>
<span class="mockbadge">ATLAS-PAGE MOCK · D15 WALL · APPROVAL ARTIFACT</span></header>
<div class="intro"><b>the hero flip (D15):</b> the landing is the thesis, not a
map canvas. Every network drawn at one true scale, north-up; three render real
today, nine arrive after the gate. Click-through is the dossier, where content
leads and the map is a figure.</div>
<div class="seclabel">THE WALL · TWELVE NETWORKS · ONE SCALE · NORTH-UP</div>
<div class="wall">{"".join(cells)}</div>
<div class="wallnote"><span class="bar" style="width:{bar:.0f}px"></span>
<span>10 km · same scale in every cell · geography not aligned · shapes only</span></div>
{dossier_section(meta)}
<footer><span>geometry + water © OpenStreetMap contributors · ODbL · {gm.SNAPSHOT_NOTE}</span>
<span>made by ajin.im</span></footer>
</div></body></html>"""
    out = os.path.join(HERE, "wall-board.html")
    with open(out, "w") as fh:
        fh.write(html)
    print(f"wrote {out}  ({os.path.getsize(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
