#!/usr/bin/env python3
"""Geo-dressed True Shape mock — evidence for the gate-2 consistency fork.

Owner question (2026-06-11, at the live-prototype gate): the chosen Commons
diagrams are a style patchwork across cities (Tokyo's is quasi-geographic,
Seoul/Paris are pure schematics); could OUR true-geometry mode wear a
consistent geographic dress (like the official Tokyo map) across all cities?

This board is the visual proof for that fork (option B in the gate discussion):
Seoul / Tokyo / Paris true OSM geometry over

  - water polygons (natural=water / riverbank) from Overpass, pale fill;
  - coastline closed against the panel edge (OSM convention: water on the
    RIGHT of the way direction) -> Tokyo Bay as a filled region; falls back
    to a shoreline stroke if assembly fails;
  - ghosted out-of-scope rail from the same network GeoJSONs (JR around the
    Tokyo subway, Korail/L1 corridors around Seoul lines 2-9, RER/trams
    around the Paris Métro) — the texture the official maps use.

Static approval artifact, no JS, per-city fit (Explore framing, not the
same-scale Shape invariant). Writes geo-shape-desktop.html next to this file.
Everything drawn is OSM/ODbL — one license line covers the whole dress.

Usage:
    python3 _scripts/world_metros/mocks/build_geo_shape_mock.py
"""

import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import build_page_geometry as bpg  # fetch_city, project_pt, rdp, CITY_CONFIG

OVERPASS_ENDPOINTS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]
SNAPSHOT_NOTE = "OSM snapshot 2026-06-11"
PAD_KM = 3.0           # render bbox = network bbox + this pad; water clips to it
MIN_WATER_KM2 = 0.08   # drop ponds

P = {
    "paper": "#f7f7f4", "panel": "#ffffff", "line": "#d8d8d2",
    "ink": "#17171c", "grey": "#8a8a85", "faint": "#b9b9b2",
    "accent": "#0052a4", "red": "#d96629",
    "water": "#d9e8f1", "coast": "#c2d8e6", "ghost": "#e4e4df",
}

CITY_LABELS = {
    "seoul": ("SEOUL", "lines 2–9 · ghost: Korail + suburban lines · Han from OSM water"),
    "tokyo": ("TOKYO", "Tokyo Metro + Toei · ghost: JR lines · bay closed from coastline"),
    "paris": ("PARIS", "Métro 1–14 · Seine from OSM water · ghost: airport shuttles only (RER is a separate network file)"),
}


# ------------------------------------------------------------------ network

def load_network_with_k(city):
    """Like bpg.load_network but exposes the projection constant and the
    OUT-OF-SCOPE LineStrings (the ghost-rail layer), so the water layer and
    the ghosts can be projected into the same km plane as the network."""
    cfg = bpg.CITY_CONFIG[city]
    refs = cfg["refs"]
    lines, ghosts, pts = [], [], []
    for slug in cfg["slugs"]:
        gj = bpg.fetch_city(slug)
        for f in gj["features"]:
            if f["geometry"]["type"] == "LineString":
                (lines if f["properties"].get("ref") in refs else ghosts).append(f)
            elif f["geometry"]["type"] == "Point":
                pts.append(f["geometry"]["coordinates"])
    lat0 = sum(c[1] for f in lines for c in f["geometry"]["coordinates"]) / \
        sum(len(f["geometry"]["coordinates"]) for f in lines)
    k = math.cos(math.radians(lat0))

    def proj_feature(f, eps):
        coords = [bpg.project_pt(lon, lat, k) for lon, lat in f["geometry"]["coordinates"]]
        return bpg.rdp(coords, eps)

    segs = [(f["properties"].get("ref"), f["properties"].get("stroke", "#888"),
             proj_feature(f, 0.05)) for f in lines]

    # outlier guard (same as the page build)
    cxs = sorted(sum(x for x, _ in s[2]) / len(s[2]) for s in segs)
    cys = sorted(sum(y for _, y in s[2]) / len(s[2]) for s in segs)
    mx, my = cxs[len(cxs) // 2], cys[len(cys) // 2]
    segs = [s for s in segs
            if math.hypot(sum(x for x, _ in s[2]) / len(s[2]) - mx,
                          sum(y for _, y in s[2]) / len(s[2]) - my) < cfg["outlier_km"]]

    # stations near scoped vertices (same matching as the page build)
    grid = {}
    for _, _, ps in segs:
        for x, y in ps:
            grid.setdefault((int(x), int(y)), []).append((x, y))
    stations = []
    for lon, lat in pts:
        x, y = bpg.project_pt(lon, lat, k)
        gx, gy = int(x), int(y)
        if any((vx - x) ** 2 + (vy - y) ** 2 < 0.09 ** 2
               for cx in (gx - 1, gx, gx + 1) for cy in (gy - 1, gy, gy + 1)
               for vx, vy in grid.get((cx, cy), ())):
            stations.append((x, y))
    seen, uniq = set(), []
    for x, y in stations:
        key = (round(x / 0.06), round(y / 0.06))
        if key not in seen:
            seen.add(key)
            uniq.append((x, y))

    ghost_segs = [proj_feature(f, 0.08) for f in ghosts]
    ghost_refs = sorted({str(f["properties"].get("ref")) for f in ghosts})
    return {"segs": segs, "stations": uniq, "ghosts": ghost_segs,
            "ghost_refs": ghost_refs, "k": k}


def net_bbox(net):
    xs = [p[0] for _, _, ps in net["segs"] for p in ps]
    ys = [p[1] for _, _, ps in net["segs"] for p in ps]
    return min(xs), min(ys), max(xs), max(ys)


# -------------------------------------------------------------------- water

def fetch_water(city, geo_bbox):
    """Overpass: water polygons + riverbank ways + coastline in bbox.
    geo_bbox = (south, west, north, east). Cached in /tmp; serialized calls.
    Geometry is fetched UNCLIPPED (no bbox on `out geom`): clipped relation
    members leave gaps that break ring assembly, and the big rivers are
    exactly the geometry we want. We clip rings ourselves at render time."""
    cache = f"/tmp/{city}-water-full.json"
    if os.path.exists(cache):
        return json.load(open(cache))
    s, w, n, e = geo_bbox
    bbox = f"({s:.4f},{w:.4f},{n:.4f},{e:.4f})"
    q = (f'[out:json][timeout:150];('
         f'way["natural"="water"](if: length() > 1200){bbox};'
         f'relation["natural"="water"]{bbox};'
         f'way["waterway"="riverbank"]{bbox};'
         f'way["natural"="coastline"]{bbox};'
         f');out geom;')
    data = urllib.parse.urlencode({"data": q}).encode()
    for attempt in range(1, 5):
        endpoint = OVERPASS_ENDPOINTS[(attempt - 1) % len(OVERPASS_ENDPOINTS)]
        try:
            req = urllib.request.Request(
                endpoint, data=data,
                headers={"User-Agent": "world-metros-atlas-mock (ajin.im)"})
            with urllib.request.urlopen(req, timeout=180) as resp:
                payload = resp.read()
            out = json.loads(payload)
            with open(cache, "w") as fh:
                json.dump(out, fh)
            return out
        except Exception as err:  # noqa: BLE001 — 429/timeout: back off, retry
            print(f"  overpass attempt {attempt} ({endpoint.split('/')[2]}) "
                  f"for {city}: {err}; backing off")
            time.sleep(45 * attempt)
    raise RuntimeError(f"overpass failed for {city}")


def way_coords(el):
    """Geometry list of an element from `out geom`, split at null gaps."""
    runs, cur = [], []
    for g in el.get("geometry") or []:
        if g is None:
            if len(cur) > 1:
                runs.append(cur)
            cur = []
        else:
            cur.append((g["lon"], g["lat"]))
    if len(cur) > 1:
        runs.append(cur)
    return runs


def stitch(chains, tol=1e-6):
    """Join open chains end-to-end (either orientation) until no merge applies."""
    chains = [c[:] for c in chains if len(c) > 1]
    merged = True
    while merged:
        merged = False
        for i in range(len(chains)):
            if merged:
                break
            for j in range(i + 1, len(chains)):
                a, b = chains[i], chains[j]
                if a is None or b is None:
                    continue
                close = lambda p, q: abs(p[0] - q[0]) < tol and abs(p[1] - q[1]) < tol
                if close(a[-1], b[0]):
                    chains[i] = a + b[1:]
                elif close(a[-1], b[-1]):
                    chains[i] = a + b[-2::-1]
                elif close(a[0], b[-1]):
                    chains[i] = b + a[1:]
                elif close(a[0], b[0]):
                    chains[i] = b[::-1] + a[1:]
                else:
                    continue
                chains[j] = None
                merged = True
                break
        chains = [c for c in chains if c is not None]
    return chains


def ring_area(ring):
    """Shoelace, km² on projected coords (sign: + = counter-clockwise)."""
    a = 0.0
    for i in range(len(ring) - 1):
        a += ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1]
    return a / 2.0


def sutherland_hodgman(ring, bb):
    """Clip a polygon ring to the bbox (convex). Returns the clipped ring
    (possibly empty). Ring need not repeat its first point."""
    x0, y0, x1, y1 = bb
    edges = (
        lambda p: p[0] >= x0, lambda p, q, t: (x0, p[1] + (q[1] - p[1]) * t),
        lambda p: p[0] <= x1, lambda p, q, t: (x1, p[1] + (q[1] - p[1]) * t),
        lambda p: p[1] >= y0, lambda p, q, t: (p[0] + (q[0] - p[0]) * t, y0),
        lambda p: p[1] <= y1, lambda p, q, t: (p[0] + (q[0] - p[0]) * t, y1),
    )
    params = (
        lambda p, q: (x0 - p[0]) / (q[0] - p[0]) if q[0] != p[0] else 0.0,
        lambda p, q: (x1 - p[0]) / (q[0] - p[0]) if q[0] != p[0] else 0.0,
        lambda p, q: (y0 - p[1]) / (q[1] - p[1]) if q[1] != p[1] else 0.0,
        lambda p, q: (y1 - p[1]) / (q[1] - p[1]) if q[1] != p[1] else 0.0,
    )
    pts = ring[:-1] if ring and ring[0] == ring[-1] else ring[:]
    for i in range(4):
        inside, isect = edges[2 * i], edges[2 * i + 1]
        tfun = params[i]
        out = []
        for j in range(len(pts)):
            p, q = pts[j], pts[(j + 1) % len(pts)]
            pin, qin = inside(p), inside(q)
            if pin:
                out.append(p)
                if not qin:
                    out.append(isect(p, q, tfun(p, q)))
            elif qin:
                out.append(isect(p, q, tfun(p, q)))
        pts = out
        if not pts:
            return []
    return pts + [pts[0]]


def closed(ring, tol=1e-6):
    return len(ring) > 3 and abs(ring[0][0] - ring[-1][0]) < tol \
        and abs(ring[0][1] - ring[-1][1]) < tol


def point_in_ring(p, ring):
    """Ray-cast point-in-polygon."""
    x, y = p
    inside = False
    for i in range(len(ring) - 1):
        (x1, y1), (x2, y2) = ring[i], ring[i + 1]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) / (y2 - y1) * (x2 - x1):
            inside = not inside
    return inside


def extract_water(raw, k, bb):
    """-> (polys, coast_chains): polys = list of [outer, hole, hole...] —
    exactly ONE outer ring per poly (multiple outers of a relation are split
    into separate polys; nested-outer data quirks would cancel to white under
    a shared evenodd path), holes assigned to their containing outer by
    point-in-polygon. All rings km-projected and clipped to the render bbox;
    coast chains km, OSM direction preserved (water on the right of travel)."""
    proj = lambda run: [bpg.project_pt(lon, lat, k) for lon, lat in run]

    def finish(ring, min_km2):
        """project -> clip -> area-filter -> simplify"""
        r = sutherland_hodgman(proj(ring), bb)
        if len(r) > 3 and abs(ring_area(r)) >= min_km2:
            return bpg.rdp(r, 0.03)
        return None

    polys, coast = [], []
    for el in raw.get("elements", []):
        tags = el.get("tags", {})
        if el["type"] == "way" and tags.get("natural") == "coastline":
            for run in way_coords(el):
                coast.append(proj(run))
        elif el["type"] == "way":
            for run in way_coords(el):
                if closed(run):
                    r = finish(run, MIN_WATER_KM2)
                    if r:
                        polys.append([r])
        elif el["type"] == "relation":
            outers, inners = [], []
            for m in el.get("members", []):
                if m.get("type") != "way":
                    continue
                runs, cur = [], []
                for g in m.get("geometry") or []:
                    if g is None:
                        if len(cur) > 1:
                            runs.append(cur)
                        cur = []
                    else:
                        cur.append((g["lon"], g["lat"]))
                if len(cur) > 1:
                    runs.append(cur)
                (outers if m.get("role") != "inner" else inners).extend(runs)
            rings = [r for r in (finish(ring, MIN_WATER_KM2)
                                 for ring in stitch(outers) if closed(ring)) if r]
            if rings:
                holes = [r for r in (finish(ring, 0.02)
                                     for ring in stitch(inners) if closed(ring)) if r]
                for outer in rings:
                    mine = [hh for hh in holes if point_in_ring(hh[0], outer)]
                    polys.append([outer] + mine)
    coast = [bpg.rdp(c, 0.03) for c in stitch(coast)]
    return polys, coast


# ------------------------------------------------- coastline -> bay polygons

def clip_chain(points, bb):
    """Clip a polyline to bbox (x0,y0,x1,y1); -> list of in-box chains whose
    cut endpoints lie exactly on the border."""
    x0, y0, x1, y1 = bb
    inside = lambda p: x0 <= p[0] <= x1 and y0 <= p[1] <= y1

    def cut(p, q):
        """Intersections of segment p->q with the box border, ordered p->q."""
        hits = []
        dx, dy = q[0] - p[0], q[1] - p[1]
        for t_num, t_den, coord in (
                (x0 - p[0], dx, "x"), (x1 - p[0], dx, "x"),
                (y0 - p[1], dy, "y"), (y1 - p[1], dy, "y")):
            if t_den == 0:
                continue
            t = t_num / t_den
            if 0 <= t <= 1:
                pt = (p[0] + dx * t, p[1] + dy * t)
                if x0 - 1e-9 <= pt[0] <= x1 + 1e-9 and y0 - 1e-9 <= pt[1] <= y1 + 1e-9:
                    hits.append((t, (min(max(pt[0], x0), x1), min(max(pt[1], y0), y1))))
        return [pt for _, pt in sorted(hits)]

    chains, cur = [], []
    for i in range(len(points)):
        p = points[i]
        if inside(p):
            cur.append(p)
        if i + 1 < len(points):
            q = points[i + 1]
            a, b = inside(p), inside(q)
            if a != b:
                hits = cut(p, q)
                if hits:
                    if a:  # exiting
                        cur.append(hits[0])
                        if len(cur) > 1:
                            chains.append(cur)
                        cur = []
                    else:  # entering
                        cur = [hits[-1]]
            elif not a and not b:
                hits = cut(p, q)
                if len(hits) >= 2:  # crosses through the box
                    chains.append([hits[0], hits[-1]])
    if len(cur) > 1:
        chains.append(cur)
    return chains


def border_pos(p, bb):
    """Clockwise arc-length of a border point (screen coords, y down):
    top L->R, right T->B, bottom R->L, left B->T."""
    x0, y0, x1, y1 = bb
    w, h = x1 - x0, y1 - y0
    eps = 1e-6
    if abs(p[1] - y0) < eps:
        return p[0] - x0
    if abs(p[0] - x1) < eps:
        return w + (p[1] - y0)
    if abs(p[1] - y1) < eps:
        return w + h + (x1 - p[0])
    if abs(p[0] - x0) < eps:
        return w + h + w + (y1 - p[1])
    return None


def walk_border(a, b, bb):
    """Border points (corners) strictly between a and b, walking CLOCKWISE
    from a to b (water stays on the right of coastline direction)."""
    x0, y0, x1, y1 = bb
    w, h = x1 - x0, y1 - y0
    per = 2 * (w + h)
    pa, pb = border_pos(a, bb), border_pos(b, bb)
    if pa is None or pb is None:
        return []
    corners = [(w, (x1, y0)), (w + h, (x1, y1)), (w + h + w, (x0, y1)), (per, (x0, y0))]
    out, d = [], (pb - pa) % per
    for cpos, cpt in corners:
        cd = (cpos - pa) % per
        if 0 < cd < d:
            out.append((cd, cpt))
    return [pt for _, pt in sorted(out)]


def close_coastline(chains, bb):
    """Closed coastline loops pass through (orientation decides island vs
    enclosed water: in our y-down projected coords an island, walked with
    water on the right, has NEGATIVE shoelace). Open chains are clipped to
    the bbox and closed clockwise along its border into water polygons.
    Chains whose clipped endpoints don't land on the border (OSM data gaps)
    are excluded from closure and returned for stroking.
    Returns (water_rings, land_rings, stroke_chains)."""
    water, land, open_chains = [], [], []
    for c in chains:
        if closed(c):
            (land if ring_area(c) < 0 else water).append(
                sutherland_hodgman(c, bb) or c)
        else:
            open_chains.extend(clip_chain(c, bb))
    open_chains = [c for c in open_chains if len(c) > 1]
    water = [w for w in water if len(w) > 3]
    land = [l for l in land if len(l) > 3]
    if not open_chains:
        return water, land, []

    closable, strokes = [], []
    for c in open_chains:
        if border_pos(c[0], bb) is not None and border_pos(c[-1], bb) is not None:
            closable.append(c)
        else:
            strokes.append(c)

    starts = {}
    for c in closable:
        starts.setdefault(round(border_pos(c[0], bb), 6), c)

    per = 2 * ((bb[2] - bb[0]) + (bb[3] - bb[1]))
    used, rings = set(), []
    for c in closable:
        if id(c) in used:
            continue
        ring, cur, guard = [], c, 0
        while id(cur) not in used and guard < len(closable) + 1:
            used.add(id(cur))
            ring.extend(cur)
            guard += 1
            end_pos = border_pos(cur[-1], bb)
            # next chain start = nearest clockwise along the border
            best, best_d = None, None
            for spos, cand in starts.items():
                d = (spos - end_pos) % per
                if d == 0 and cand is cur and len(closable) == 1:
                    d = per  # single chain closes all the way around
                if id(cand) in used and cand is not c:
                    continue
                if cand is c and d == 0:
                    continue
                if best is None or d < best_d:
                    best, best_d = cand, d
            if best is None:
                break
            ring.extend(walk_border(cur[-1], best[0], bb))
            if best is c:
                break
            cur = best
        if len(ring) > 2:
            ring.append(ring[0])
            rings.append(ring)
    return water + rings, land, strokes


# --------------------------------------------------------------------- svg

def svg_panel(city, net, water_polys, coast_water, coast_land, coast_strokes,
              w, h):
    x0, y0, x1, y1 = net_bbox(net)
    bb = (x0 - PAD_KM, y0 - PAD_KM, x1 + PAD_KM, y1 + PAD_KM)
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    s = min(w / bw, h / bh)
    ox = (w - bw * s) / 2 - bb[0] * s
    oy = (h - bh * s) / 2 - bb[1] * s
    pt = lambda p: f"{ox + p[0] * s:.1f},{oy + p[1] * s:.1f}"

    def path_d(rings):
        return " ".join("M " + " L ".join(pt(p) for p in ring) + " Z"
                        for ring in rings if len(ring) > 2)

    out = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
           f'width="100%" height="100%" preserveAspectRatio="xMidYMid meet">']
    # 1. bay/sea regions closed from coastline
    if coast_water:
        out.append(f'<path d="{path_d(coast_water)}" fill="{P["water"]}" stroke="none"/>')
    # 2. islands back on top of the bay
    if coast_land:
        out.append(f'<path d="{path_d(coast_land)}" fill="{P["panel"]}" stroke="none"/>')
    # 3. rivers/lakes (one outer + its holes per path; the same-colour stroke
    #    keeps thin rivers like the Seine visible at panel scale)
    for rings in water_polys:
        out.append(f'<path d="{path_d(rings)}" fill="{P["water"]}" '
                   f'fill-rule="evenodd" stroke="{P["water"]}" stroke-width="1.2"/>')
    # 4. shoreline fragments that couldn't join the closure (data gaps)
    for c in coast_strokes:
        d = " ".join(pt(p) for p in c)
        out.append(f'<polyline points="{d}" fill="none" stroke="{P["coast"]}" '
                   f'stroke-width="1.6"/>')
    # 5. ghost rail
    out.append(f'<g stroke="{P["ghost"]}" fill="none" stroke-width="1.5" '
               f'stroke-linecap="round" stroke-linejoin="round">')
    for ps in net["ghosts"]:
        out.append(f'<polyline points="{" ".join(pt(p) for p in ps)}"/>')
    out.append('</g>')
    # 6. the network in official colours
    for _, color, ps in net["segs"]:
        out.append(f'<polyline points="{" ".join(pt(p) for p in ps)}" fill="none" '
                   f'stroke="{color}" stroke-width="2.8" stroke-linecap="round" '
                   f'stroke-linejoin="round"/>')
    # 7. stations
    out.append(f'<g fill="{P["panel"]}" stroke="{P["ink"]}" stroke-width="0.8" '
               f'opacity="0.92">')
    for x, y in net["stations"]:
        out.append(f'<circle cx="{ox + x * s:.1f}" cy="{oy + y * s:.1f}" r="1.1"/>')
    out.append('</g>')
    out.append('</svg>')
    label, sub = CITY_LABELS[city]
    bar = 10 * s
    return f"""
<div class="panel">
  <div class="plabel">{label}</div>
  <div class="psub">{sub}</div>
  {"".join(out)}
  <div class="scale"><span class="bar" style="width:{bar:.0f}px"></span><span>10 km</span></div>
</div>"""


CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap');
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#e8e8e3; color:%(ink)s; display:flex; align-items:center;
       justify-content:center; min-height:100vh;
       font-family:-apple-system,'Helvetica Neue','Segoe UI',Arial,sans-serif; }
.board { width:1280px; background:%(paper)s; outline:1px solid %(line)s;
         box-shadow:0 1px 14px rgba(20,20,28,.10); display:flex;
         flex-direction:column; }
header { display:flex; align-items:baseline; gap:20px; padding:14px 22px 11px;
         border-bottom:1px solid %(line)s; background:%(panel)s; }
.wordmark { font-size:15px; font-weight:700; letter-spacing:.24em; }
.wordmark em { font-style:normal; color:%(accent)s; }
.mockbadge { margin-left:auto; font-family:'DM Mono',monospace; font-size:9px;
             letter-spacing:.14em; color:%(red)s; border:1px solid %(red)s66;
             padding:3px 7px; border-radius:2px; background:%(panel)s;
             white-space:nowrap; }
.intro { padding:9px 22px; font-size:11px; color:%(grey)s; background:%(panel)s;
         border-bottom:1px solid %(line)s; line-height:1.5; }
.intro b { color:%(ink)s; font-weight:600; }
main { display:flex; gap:0; padding:14px; }
.panel { flex:1; position:relative; background:%(panel)s; border:1px solid %(line)s;
         height:680px; min-width:0; overflow:hidden; }
.panel + .panel { margin-left:14px; }
.plabel { position:absolute; top:10px; left:12px; font-size:10px;
          letter-spacing:.18em; font-weight:700; z-index:2;
          background:rgba(255,255,255,.88); padding:4px 7px; border-radius:3px; }
.psub { position:absolute; top:32px; left:12px; font-size:9px; color:%(grey)s;
        z-index:2; background:rgba(255,255,255,.88); padding:2px 7px;
        border-radius:3px; max-width:80%%; }
.scale { position:absolute; bottom:10px; left:12px; display:flex;
         align-items:center; gap:8px; font-size:9px; color:%(grey)s; z-index:2;
         font-family:'DM Mono',monospace; }
.scale .bar { height:3px; background:%(ink)s; display:inline-block;
              border-radius:2px; }
footer { display:flex; justify-content:space-between; padding:9px 22px;
         border-top:1px solid %(line)s; font-family:'DM Mono',monospace;
         font-size:9px; color:%(grey)s; background:%(panel)s; }
""" % P


def main():
    panels = []
    for city in ("seoul", "tokyo", "paris"):
        print(f"== {city}")
        net = load_network_with_k(city)
        print(f"  ghost refs: {net['ghost_refs'][:14]}{' …' if len(net['ghost_refs']) > 14 else ''}"
              f" ({len(net['ghosts'])} ways)")
        x0, y0, x1, y1 = net_bbox(net)
        bb = (x0 - PAD_KM, y0 - PAD_KM, x1 + PAD_KM, y1 + PAD_KM)
        k = net["k"]
        # km bbox -> geo (south, west, north, east); y = -lat*110.57
        geo = (-bb[3] / 110.57, bb[0] / (111.32 * k),
               -bb[1] / 110.57, bb[2] / (111.32 * k))
        raw = fetch_water(city, geo)
        polys, coast = extract_water(raw, k, bb)
        cw, cl, strokes = close_coastline(coast, bb)
        print(f"  water polys: {len(polys)} · coastline chains: {len(coast)} "
              f"-> closed water rings: {len(cw)}, islands: {len(cl)}, "
              f"stroke fragments: {len(strokes)}")
        panels.append(svg_panel(city, net, polys, cw, cl, strokes, 405, 680))
        time.sleep(8)  # be polite to Overpass between cities

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>world-metros mock — geo-dressed true shape</title>
<style>{CSS}</style></head><body><div class="board">
<header><div class="wordmark">WORLD METROS <em>ATLAS</em></div>
<span class="mockbadge">GEO-SHAPE MOCK · FORK-B EVIDENCE · NOT THE PRODUCT</span></header>
<div class="intro"><b>the consistency question:</b> our true OSM geometry dressed
with OSM water + ghosted out-of-scope rail — one style we control, applied
identically to every city (per-city fit here; the Shape tab keeps its same-scale
invariant). Diagrams would remain as the per-city “the map riders see” exhibit.</div>
<main>{"".join(panels)}</main>
<footer><span>geometry + water © OpenStreetMap contributors · ODbL · {SNAPSHOT_NOTE}</span>
<span>made by ajin.im</span></footer>
</div></body></html>"""
    out = os.path.join(HERE, "geo-shape-desktop.html")
    with open(out, "w") as fh:
        fh.write(html)
    print(f"wrote {out}  ({os.path.getsize(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
