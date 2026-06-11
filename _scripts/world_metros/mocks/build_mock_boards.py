#!/usr/bin/env python3
"""Generate the three mock approval boards in the official-map idiom (D8 gate 1, round 2).

Owner direction 2026-06-11 (supersedes Electric Cartography, see DECISIONS D10):
white background, official line colours, the visual language of the maps riders
actually see. Official map ARTWORK cannot be embedded (verified licensing wall,
DATA-CONTRACT.md), so the boards draw our own OSM geometry in that idiom and give
each city a "the map riders see" link to the operator's official diagram.

Real Seoul + Paris geometry from the OSM subway-validator CDN (cached in /tmp),
simplified (RDP with closed-ring handling) and rendered as inline SVG in three
static HTML boards in this directory:

  explore-desktop.html   1280x800   Explore view, Seoul
  shape-desktop.html     1280x800   Compare/Shape pair, Seoul vs Paris, one scale
  explore-mobile.html     375x760   Explore view, Seoul, mobile

Boards are design artifacts, not the product: no JS, no interactivity, every
number on them computed from the snapshot or independently true.
"""

import json
import math
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CDN = "https://cdn.organicmaps.app/subway/"
SNAPSHOT_NOTE = "OSM snapshot 2026-06-11"

P = {
    "paper": "#f7f7f4",    # board background
    "panel": "#ffffff",    # map/card sheets
    "line": "#d8d8d2",     # hairline borders
    "ink": "#17171c",      # primary text
    "grey": "#8a8a85",     # secondary text
    "faint": "#b9b9b2",    # tertiary/meta text
    "dim": "#dcdcd8",      # greyed-out network lines (line-select idiom)
    "accent": "#0052a4",   # transit blue (chrome accent)
    "red": "#d96629",      # badge + "why" label
    "grid": "#ecece6",     # km grid on Shape view
}

SEOUL_REFS = {str(i) for i in range(2, 10)}
PARIS_REFS = {"1", "2", "3", "3bis", "4", "5", "6", "7", "7bis",
              "8", "9", "10", "11", "12", "13", "14"}


# ---------------------------------------------------------------- geometry

def fetch_city(slug):
    cache = f"/tmp/{slug}.geojson"
    if not os.path.exists(cache):
        req = urllib.request.Request(CDN + f"{slug}.geojson",
                                     headers={"User-Agent": "world-metros-atlas-mocks"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        with open(cache, "wb") as fh:
            fh.write(data)
    return json.load(open(cache))


def project_pt(lon, lat, k):
    return lon * 111.32 * k, -lat * 110.57


def rdp(points, eps):
    """Iterative Ramer-Douglas-Peucker, km units."""
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    # closed rings (loop lines): the start-end chord is zero-length, so every
    # interior distance is 0 and the ring would collapse — anchor the farthest
    # vertex from the start and simplify the two halves separately
    if math.hypot(points[0][0] - points[-1][0], points[0][1] - points[-1][1]) < eps:
        mid = max(range(1, len(points) - 1),
                  key=lambda i: (points[i][0] - points[0][0]) ** 2 +
                                (points[i][1] - points[0][1]) ** 2)
        keep[mid] = True
        stack = [(0, mid), (mid, len(points) - 1)]
    else:
        stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = points[a]
        bx, by = points[b]
        dx, dy = bx - ax, by - ay
        norm = math.hypot(dx, dy) or 1e-12
        dmax, idx = -1.0, -1
        for i in range(a + 1, b):
            px, py = points[i]
            d = abs(dx * (ay - py) - dy * (ax - px)) / norm
            if d > dmax:
                dmax, idx = d, i
        if dmax > eps:
            keep[idx] = True
            stack.append((a, idx))
            stack.append((idx, b))
    return [p for p, k in zip(points, keep) if k]


def load_network(slug, refs, eps=0.05, outlier_km=35):
    """-> dict(segs=[(ref, color, [(x,y)km])], stations=[(x,y)], refs=sorted)"""
    gj = fetch_city(slug)
    lines = [f for f in gj["features"] if f["geometry"]["type"] == "LineString"
             and f["properties"].get("ref") in refs]
    pts = [f["geometry"]["coordinates"] for f in gj["features"]
           if f["geometry"]["type"] == "Point"]
    lat0 = sum(c[1] for f in lines for c in f["geometry"]["coordinates"]) / \
        sum(len(f["geometry"]["coordinates"]) for f in lines)
    k = math.cos(math.radians(lat0))

    segs = []
    for f in lines:
        p = f["properties"]
        proj = [project_pt(lon, lat, k) for lon, lat in f["geometry"]["coordinates"]]
        segs.append((p.get("ref"), p.get("stroke", "#888"), proj))

    # outlier guard (e.g. one stray Paris fragment far from the network)
    cxs = sorted(sum(x for x, _ in s[2]) / len(s[2]) for s in segs)
    cys = sorted(sum(y for _, y in s[2]) / len(s[2]) for s in segs)
    mx, my = cxs[len(cxs) // 2], cys[len(cys) // 2]
    segs = [s for s in segs
            if math.hypot(sum(x for x, _ in s[2]) / len(s[2]) - mx,
                          sum(y for _, y in s[2]) / len(s[2]) - my) < outlier_km]

    # vertices for station matching come from KEPT segs only, so stations near
    # a dropped outlier fragment can't leak into counts or the span
    raw_vertices = [pt for _, _, ps in segs for pt in ps]

    # stations: project all Points, keep those within 90 m of a scoped vertex
    grid = {}
    for x, y in raw_vertices:
        grid.setdefault((int(x // 1), int(y // 1)), []).append((x, y))
    stations = []
    for coords in pts:
        x, y = project_pt(coords[0], coords[1], k)
        gx, gy = int(x // 1), int(y // 1)
        near = False
        for cx in (gx - 1, gx, gx + 1):
            for cy in (gy - 1, gy, gy + 1):
                for vx, vy in grid.get((cx, cy), ()):
                    if (vx - x) ** 2 + (vy - y) ** 2 < 0.09 ** 2:
                        near = True
                        break
                if near:
                    break
            if near:
                break
        if near:
            stations.append((x, y))
    # dedupe stations on a 60 m grid (entrances/platforms collapse)
    seen, uniq = set(), []
    for x, y in stations:
        key = (round(x / 0.06), round(y / 0.06))
        if key not in seen:
            seen.add(key)
            uniq.append((x, y))

    return {
        "segs": [(r, c, rdp(p, eps)) for r, c, p in segs],
        "stations": uniq,
        "refs": sorted({s[0] for s in segs}, key=lambda r: (len(r), r)),
    }


def bbox(net):
    xs = [p[0] for _, _, ps in net["segs"] for p in ps]
    ys = [p[1] for _, _, ps in net["segs"] for p in ps]
    return min(xs), min(ys), max(xs), max(ys)


def span_km(stations):
    best = 0.0
    pts = stations[::2] if len(stations) > 600 else stations
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d = (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2
            if d > best:
                best = d
    return math.sqrt(best)


# ---------------------------------------------------------------- svg

def svg_network(net, w, h, px_per_km=None, pad=26, highlight=None, station_r=1.35,
                grid_km=10, grid_on=False, stations_on=True, station_op=0.92):
    """Official-map idiom: solid official colours on white; line-select greys
    the rest (the metro-app convention) instead of fading opacity."""
    x0, y0, x1, y1 = bbox(net)
    bw, bh = x1 - x0, y1 - y0
    s = px_per_km or min((w - 2 * pad) / bw, (h - 2 * pad) / bh)
    ox = (w - bw * s) / 2 - x0 * s
    oy = (h - bh * s) / 2 - y0 * s

    out = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
           f'width="100%" height="100%" preserveAspectRatio="xMidYMid meet">']
    if grid_on:
        g = grid_km * s
        out.append(f'<g stroke="{P["grid"]}" stroke-width="1">')
        x = ox % g
        while x < w:
            out.append(f'<line x1="{x:.0f}" y1="0" x2="{x:.0f}" y2="{h}"/>')
            x += g
        y = oy % g
        while y < h:
            out.append(f'<line x1="0" y1="{y:.0f}" x2="{w}" y2="{y:.0f}"/>')
            y += g
        out.append('</g>')

    dim = highlight is not None
    for ref, color, ps in net["segs"]:
        if ref == highlight:
            continue
        d = " ".join(f"{ox + x * s:.1f},{oy + y * s:.1f}" for x, y in ps)
        stroke = P["dim"] if dim else color
        out.append(f'<polyline points="{d}" fill="none" stroke="{stroke}" '
                   f'stroke-width="3.0" stroke-linecap="round" '
                   f'stroke-linejoin="round"/>')
    if highlight is not None:
        for ref, color, ps in net["segs"]:
            if ref != highlight:
                continue
            d = " ".join(f"{ox + x * s:.1f},{oy + y * s:.1f}" for x, y in ps)
            out.append(f'<polyline points="{d}" fill="none" stroke="{color}" '
                       f'stroke-width="3.8" stroke-linecap="round" '
                       f'stroke-linejoin="round"/>')
    if stations_on:
        out.append(f'<g fill="{P["panel"]}" stroke="{P["ink"]}" '
                   f'stroke-width="0.95" opacity="{station_op}">')
        for x, y in net["stations"]:
            out.append(f'<circle cx="{ox + x * s:.1f}" cy="{oy + y * s:.1f}" r="{station_r}"/>')
        out.append('</g>')
    out.append('</svg>')
    return "".join(out), s


def scalebar(px_per_km, km=10):
    w = px_per_km * km
    return (f'<div class="scalebar"><span class="bar" style="width:{w:.0f}px"></span>'
            f'<span>{km} km</span></div>')


# ---------------------------------------------------------------- html chrome

CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #e8e8e3; color: %(ink)s; display: flex; align-items: center;
       justify-content: center; min-height: 100vh;
       font-family: -apple-system, 'Helvetica Neue', 'Segoe UI', Arial, sans-serif; }
.mono { font-family: 'DM Mono', ui-monospace, monospace; }
.board { width: %(bw)spx; height: %(bh)spx; background: %(paper)s; position: relative;
         display: flex; flex-direction: column; overflow: hidden;
         outline: 1px solid %(line)s; box-shadow: 0 1px 14px rgba(20,20,28,0.10); }
.mockbadge { font-family: 'DM Mono', ui-monospace, monospace; font-size: 9px;
             letter-spacing: 0.14em; color: %(red)s; border: 1px solid %(red)s66;
             padding: 3px 7px; border-radius: 2px; background: %(panel)s;
             white-space: nowrap; margin-left: 20px; }
header { display: flex; align-items: baseline; gap: 26px; flex: none;
         padding: 16px 22px 12px; border-bottom: 1px solid %(line)s;
         background: %(panel)s; }
.wordmark { font-size: 15px; font-weight: 700; letter-spacing: 0.24em; }
.wordmark em { font-style: normal; color: %(accent)s; }
nav { display: flex; gap: 22px; margin-left: auto; font-size: 11px;
      letter-spacing: 0.16em; font-weight: 600; }
nav span { color: %(grey)s; padding-bottom: 4px; }
nav .on { color: %(ink)s; border-bottom: 3px solid %(accent)s; }
.m { height: auto; min-height: %(bh)spx; }
.m header { flex-wrap: wrap; row-gap: 7px; padding: 12px 14px 9px; }
.m .wordmark { font-size: 13px; letter-spacing: 0.2em; }
.m .mockbadge { margin-left: auto; font-size: 8px; }
.m nav { order: 3; margin-left: 0; width: 100%%%%; gap: 16px; font-size: 10px; }
.m .citystrip { padding: 8px 14px; }
.citystrip { display: flex; gap: 7px; padding: 10px 22px; flex: none;
             border-bottom: 1px solid %(line)s; flex-wrap: nowrap;
             overflow: hidden; background: %(panel)s; }
.citystrip span { font-size: 10.5px; letter-spacing: 0.04em; color: %(grey)s;
                  border: 1px solid %(line)s; padding: 3px 9px;
                  border-radius: 999px; white-space: nowrap; background: %(panel)s; }
.citystrip .on { color: %(panel)s; background: %(ink)s; border-color: %(ink)s;
                 font-weight: 600; }
main { flex: 1; display: flex; min-height: 0; }
.mappanel { flex: 1; position: relative; background: %(panel)s; margin: 14px;
            border: 1px solid %(line)s; min-width: 0; }
.mappanel .label { position: absolute; top: 10px; left: 12px; font-size: 10px;
                   letter-spacing: 0.18em; font-weight: 700; color: %(ink)s;
                   z-index: 2; }
.mappanel .sub { position: absolute; top: 26px; left: 12px; font-size: 9.5px;
                 color: %(grey)s; z-index: 2; }
.scalebar { position: absolute; bottom: 10px; left: 12px; display: flex;
            align-items: center; gap: 8px; font-size: 9px; color: %(grey)s;
            z-index: 2; font-family: 'DM Mono', ui-monospace, monospace; }
.scalebar .bar { height: 3px; background: %(ink)s; display: inline-block;
                 border-radius: 2px; }
.modetoggle { position: absolute; top: 10px; right: 10px; display: flex; gap: 0;
              z-index: 2; border: 1px solid %(line)s; border-radius: 3px;
              overflow: hidden; }
.modetoggle span { font-size: 9px; letter-spacing: 0.12em; font-weight: 600;
                   color: %(grey)s; padding: 5px 11px; background: %(panel)s; }
.modetoggle .on { color: %(panel)s; background: %(accent)s; }
.diagram { position: absolute; inset: 0; width: 100%%%%; height: 100%%%%;
           object-fit: contain; padding: 40px 12px 12px; }
.maptools { position: absolute; top: 10px; right: 10px; display: flex;
            flex-direction: column; gap: 5px; z-index: 2; }
.maptools span { width: 24px; height: 24px; border: 1px solid %(line)s;
                 color: %(grey)s; display: flex; align-items: center;
                 justify-content: center; font-size: 13px; background: %(panel)s;
                 border-radius: 3px; }
aside { width: 336px; margin: 14px 14px 14px 0; border: 1px solid %(line)s;
        background: %(panel)s; padding: 18px 18px 14px; display: flex;
        flex-direction: column; }
.cityname { font-size: 27px; font-weight: 800; letter-spacing: 0.04em; }
.cityname small { display: block; font-size: 9.5px; letter-spacing: 0.18em;
                  color: %(accent)s; margin-top: 5px; font-weight: 600; }
.facts { margin-top: 16px; border-top: 1px solid %(line)s;
         font-family: 'DM Mono', ui-monospace, monospace; }
.facts div { display: flex; justify-content: space-between; gap: 10px;
             align-items: baseline; padding: 7px 0;
             border-bottom: 1px solid %(paper)s; font-size: 11px; }
.facts dt { color: %(grey)s; }
.facts dd { text-align: right; font-weight: 500; }
.facts .ev { color: %(faint)s; font-size: 9px; }
.facts a { color: %(accent)s; text-decoration: none; font-weight: 500; }
.why { margin-top: 14px; font-size: 11.5px; line-height: 1.6; color: #3c3c38; }
.why b { color: %(red)s; font-weight: 700; }
.why p + p { margin-top: 8px; }
.lines { margin-top: auto; padding-top: 12px; display: flex; gap: 5px;
         flex-wrap: wrap; }
.lines i { font-style: normal; font-size: 9.5px; color: #fff; padding: 2px 0;
           width: 20px; text-align: center; border-radius: 999px;
           font-weight: 700; }
footer { display: flex; justify-content: space-between; padding: 9px 22px;
         border-top: 1px solid %(line)s; font-size: 9px; color: %(grey)s;
         letter-spacing: 0.05em; flex: none; background: %(panel)s;
         font-family: 'DM Mono', ui-monospace, monospace; }
.pairbar { display: flex; align-items: center; gap: 14px; padding: 10px 22px;
           font-size: 11px; letter-spacing: 0.1em; flex: none; font-weight: 700;
           border-bottom: 1px solid %(line)s; background: %(panel)s; }
.pairbar .vs { color: %(red)s; font-size: 13px; }
.pairbar .note { color: %(grey)s; margin-left: 8px; letter-spacing: 0.02em;
                 font-weight: 400; font-style: italic; font-size: 10px; }
.pairbar .ctl { margin-left: auto; display: flex; gap: 8px; }
.pairbar .ctl span { border: 1px solid %(line)s; padding: 3px 10px;
                     color: %(grey)s; font-size: 9px; letter-spacing: 0.12em;
                     border-radius: 3px; font-weight: 600; }
.pairbar .ctl .on { color: %(panel)s; background: %(accent)s;
                    border-color: %(accent)s; }
""" % dict(P, bw="%(bw)s", bh="%(bh)s")


def chrome(active, mock_no, total="3"):
    tabs = "".join(
        f'<span class="{ "on" if t == active else "" }">{t}</span>'
        for t in ("EXPLORE", "SHAPE", "RANKINGS", "METHOD"))
    return (f'<header><div class="wordmark">WORLD METROS <em>ATLAS</em></div>'
            f'<nav>{tabs}</nav>'
            f'<span class="mockbadge">MOCK BOARD {mock_no}/{total} · APPROVAL ARTIFACT</span>'
            f'</header>')


CITIES = ["shanghai", "tokyo", "seoul", "hong kong", "singapore", "delhi",
          "moscow", "london", "paris", "nyc", "mexico city", "cairo"]


def citystrip(active="seoul"):
    return ('<div class="citystrip">' +
            "".join(f'<span class="{ "on" if c == active else "" }">{c}</span>'
                    for c in CITIES) + '</div>')


def footer_html():
    return (f'<footer><span>geometry © OpenStreetMap contributors · ODbL · '
            f'{SNAPSHOT_NOTE}</span><span>made by ajin.im</span></footer>')


def write_board(name, body, bw, bh, cls="board"):
    html = (f'<!doctype html><html><head><meta charset="utf-8">'
            f'<title>world-metros mock — {name}</title>'
            f'<style>{CSS % dict(bw=bw, bh=bh)}</style></head>'
            f'<body><div class="{cls}">{body}</div></body></html>')
    path = os.path.join(HERE, name)
    with open(path, "w") as fh:
        fh.write(html)
    print(f"wrote {name}  ({os.path.getsize(path)/1024:.0f} KB)")


# ---------------------------------------------------------------- boards

def seoul_card(seoul, span):
    line_chips = "".join(
        f'<i style="background:{c}">{r}</i>'
        for r, c in sorted({(r, c) for r, c, _ in seoul["segs"]},
                           key=lambda t: t[0]))
    return f"""
<aside>
  <div class="cityname">SEOUL<small>SEOUL METROPOLITAN SUBWAY</small></div>
  <div class="facts">
    <div><dt>opened</dt><dd>1974</dd></div>
    <div><dt>lines drawn</dt><dd>{len(seoul['refs'])} <span class="ev">(2–9 · L1 scope: Method)</span></dd></div>
    <div><dt>stations plotted</dt><dd>{len(seoul['stations'])}</dd></div>
    <div><dt>furthest-stations span</dt><dd>{span:.0f} km <span class="ev">computed</span></dd></div>
    <div><dt>reported route-km</dt><dd><span class="ev">pipeline · dated at build</span></dd></div>
    <div><dt>annual ridership</dt><dd><span class="ev">pipeline · dated at build</span></dd></div>
    <div><dt>the map riders see</dt><dd><a href="https://www.seoulmetro.co.kr">official map ↗</a></dd></div>
  </div>
  <div class="why">
    <p><b>why it's here</b> — the densest reach of any metro on earth: the green
    Line 2 loop orbits the core while seven siblings lace a city of ten million
    into one grid.</p>
    <p>Full underground cell coverage, heated winter seats, and a circle line so
    central that "inside Line 2" is shorthand for downtown.</p>
  </div>
  <div class="lines">{line_chips}</div>
</aside>"""


def main():
    seoul = load_network("seoul", SEOUL_REFS)
    paris = load_network("paris", PARIS_REFS, outlier_km=16)
    seoul_span = span_km(seoul["stations"])
    paris_span = span_km(paris["stations"])

    # ---- board 1: desktop explore (1280x800)
    map_w, map_h = 880, 622
    svg, s1 = svg_network(seoul, map_w, map_h)
    body = (chrome("EXPLORE", "1") + citystrip() +
            '<main><div class="mappanel">'
            '<div class="label">SEOUL · TRUE GEOMETRY · NORTH-UP</div>'
            '<div class="sub">8 lines in their official colours · true geometry</div>'
            '<div class="maptools"><span>+</span><span>−</span><span>⌖</span></div>'
            + svg + scalebar(s1) + '</div>'
            + seoul_card(seoul, seoul_span) + '</main>' + footer_html())
    write_board("explore-desktop.html", body, 1280, 800)

    # ---- board 2: desktop shape pair (1280x800), one shared px/km
    pw, ph = 601, 580
    sx0, sy0, sx1, sy1 = bbox(seoul)
    px0, py0, px1, py1 = bbox(paris)
    shared = min((pw - 52) / max(sx1 - sx0, px1 - px0),
                 (ph - 52) / max(sy1 - sy0, py1 - py0))
    svg_s, _ = svg_network(seoul, pw, ph, px_per_km=shared, stations_on=False,
                           grid_on=True)
    svg_p, _ = svg_network(paris, pw, ph, px_per_km=shared, stations_on=False,
                           grid_on=True)
    body = (chrome("SHAPE", "2") +
            '<div class="pairbar"><span>SEOUL</span><span class="vs">×</span>'
            '<span>PARIS</span>'
            '<span class="note">one scale · north-up · geography not aligned — shapes only</span>'
            '<div class="ctl"><span class="on">SYNC ZOOM</span><span>OVERLAY</span>'
            '<span>SWAP</span></div></div>'
            '<main>'
            f'<div class="mappanel"><div class="label">SEOUL · LINES 2–9</div>'
            f'<div class="sub">furthest stations {seoul_span:.0f} km · 8 lines</div>{svg_s}'
            f'{scalebar(shared)}</div>'
            f'<div class="mappanel"><div class="label">PARIS · MÉTRO 1–14</div>'
            f'<div class="sub">furthest stations {paris_span:.0f} km · 16 lines</div>{svg_p}'
            f'{scalebar(shared)}</div>'
            '</main>' + footer_html())
    write_board("shape-desktop.html", body, 1280, 800)

    # ---- board 4: desktop explore, DIAGRAM mode (D11 — the familiar map)
    dcard = seoul_card(seoul, seoul_span).replace(
        '<div><dt>the map riders see</dt>',
        '<div><dt>diagram source</dt><dd><a href="https://commons.wikimedia.org/wiki/'
        'File:Seoul_Metropolitan_Subway_network_map.svg">Commons · CC BY-SA 4.0</a></dd></div>'
        '<div><dt>the map riders see</dt>')
    dfooter = footer_html().replace(
        '<footer><span>geometry',
        '<footer><span>diagram: Satellizer / Wikimedia Commons (CC BY-SA 4.0) · geometry')
    body = (chrome("EXPLORE", "4", total="4") + citystrip() +
            '<main><div class="mappanel">'
            '<div class="label">SEOUL · DIAGRAM — THE FAMILIAR MAP</div>'
            '<div class="sub">community recreation in the official idiom · bilingual · marks 2026 openings</div>'
            '<div class="modetoggle"><span class="on">DIAGRAM</span><span>TRUE SHAPE</span></div>'
            '<img class="diagram" src="assets/seoul-diagram.svg" alt="Seoul Metropolitan Subway diagram">'
            '</div>' + dcard + '</main>' + dfooter)
    write_board("diagram-desktop.html", body, 1280, 800)

    # ---- board 3: mobile explore (375x760, natural height)
    msvg, s3 = svg_network(seoul, 347, 330, highlight="2", station_r=1.0, pad=18,
                           station_op=0.85)
    mcard = seoul_card(seoul, seoul_span).replace(
        '<aside>', '<aside style="width:auto;margin:0 14px 14px;">')
    body = (chrome("EXPLORE", "3") + citystrip() +
            '<div class="mappanel" style="flex:none;height:330px;margin:14px;">'
            '<div class="label">SEOUL</div>'
            '<div class="sub">line 2 selected</div>'
            + msvg + scalebar(s3, km=20) + '</div>'
            + mcard + footer_html())
    write_board("explore-mobile.html", body, 375, 760, cls="board m")


if __name__ == "__main__":
    main()
