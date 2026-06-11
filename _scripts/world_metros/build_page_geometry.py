#!/usr/bin/env python3
"""Emit the prototype's per-city True Shape geometry (D12, D8 gate 2).

Ports the projection / RDP (closed-ring aware) / outlier-guard / station-match
logic from mocks/build_mock_boards.py and writes simplified per-city JSON into
the page's asset dir — raw CDN GeoJSON is never shipped (BUILD-SPEC).

Outputs (is/building/world-metros/assets/):
  meta.json          tiny boot payload: per-city stats + line chips (all cities)
  <city>-shape.json  lazy-loaded path data for True Shape / Shape views

Prototype-stage caveat (recorded in D12): geometry is fetched from
cdn.organicmaps.app into a /tmp cache like the mock generator; the committed,
dated JSON output is the prototype's snapshot artifact. The full refresh/build
split over a committed data/ dir lands at pipeline stage.

City scopes (DATA-CONTRACT):
  seoul  lines 2–9 (L1 scope rule deferred to pipeline stage)
  paris  Métro 1–14 + 3bis/7bis (RER excluded; outlier guard drops the stray)
  tokyo  Tokyo Metro + Toei only. The validator pre-splits Toei into its own
         network (tokyo_-_toei.geojson, like NYC's PATH/SIR); the main tokyo
         file carries Tokyo Metro plus JR refs (J*), which the ref filter
         excludes. Toei's 'Al' Airport Ltd Exp through-service (Narita–Haneda
         over Keisei/Keikyu tracks) is excluded per the through-running rule.

Usage:
    python3 _scripts/world_metros/build_page_geometry.py [--as-of YYYY-MM-DD]
"""

import argparse
import datetime
import json
import math
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT_DIR = os.path.join(REPO, "is", "building", "world-metros", "assets")
CDN = "https://cdn.organicmaps.app/subway/"

CITY_CONFIG = {
    "seoul": {
        "slugs": ["seoul"],
        "refs": {str(i) for i in range(2, 10)},
        "outlier_km": 35,
    },
    "paris": {
        "slugs": ["paris"],
        "refs": {"1", "2", "3", "3bis", "4", "5", "6", "7", "7bis",
                 "8", "9", "10", "11", "12", "13", "14"},
        "outlier_km": 16,
    },
    "tokyo": {
        "slugs": ["tokyo", "tokyo_-_toei"],
        "refs": {"G", "M", "H", "T", "C", "Y", "Z", "N", "F",
                 "A", "I", "S", "E"},
        "outlier_km": 35,
    },
}


def fetch_city(slug):
    cache = f"/tmp/{slug}.geojson"
    if not os.path.exists(cache):
        req = urllib.request.Request(CDN + f"{slug}.geojson",
                                     headers={"User-Agent": "world-metros-atlas-build"})
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


def load_network(slugs, refs, eps=0.05, outlier_km=35):
    """-> dict(segs=[(ref, color, [(x,y)km])], stations=[(x,y)])"""
    lines, pts = [], []
    for slug in slugs:
        gj = fetch_city(slug)
        lines += [f for f in gj["features"] if f["geometry"]["type"] == "LineString"
                  and f["properties"].get("ref") in refs]
        pts += [f["geometry"]["coordinates"] for f in gj["features"]
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

    return {"segs": [(r, c, rdp(p, eps)) for r, c, p in segs], "stations": uniq}


def span_km(stations):
    best = 0.0
    pts = stations[::2] if len(stations) > 600 else stations
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d = (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2
            if d > best:
                best = d
    return math.sqrt(best)


def ref_sort_key(ref):
    return (len(ref), ref) if ref.isdigit() else (99, ref)


def city_payload(net):
    """Rebase to the bbox origin, round to ~1 m, group polylines by line."""
    xs = [p[0] for _, _, ps in net["segs"] for p in ps]
    ys = [p[1] for _, _, ps in net["segs"] for p in ps]
    x0, y0 = min(xs), min(ys)
    w, h = max(xs) - x0, max(ys) - y0

    by_line = {}
    for ref, color, ps in net["segs"]:
        entry = by_line.setdefault(ref, {"ref": ref, "color": color, "paths": []})
        entry["paths"].append([[round(x - x0, 3), round(y - y0, 3)] for x, y in ps])
    lines = [by_line[r] for r in sorted(by_line, key=ref_sort_key)]

    stations = sorted([round(x - x0, 3), round(y - y0, 3)]
                      for x, y in net["stations"])
    return {
        "w_km": round(w, 3),
        "h_km": round(h, 3),
        "lines": lines,
        "stations": stations,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=datetime.date.today().isoformat())
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    note = ("GENERATED by _scripts/world_metros/build_page_geometry.py — "
            "DO NOT EDIT by hand")
    meta = {
        "_generated": note,
        "as_of": args.as_of,
        "source": "OSM via cdn.organicmaps.app/subway (ODbL)",
        "cities": {},
    }
    for city, cfg in CITY_CONFIG.items():
        net = load_network(cfg["slugs"], cfg["refs"], outlier_km=cfg["outlier_km"])
        payload = city_payload(net)
        span = span_km(net["stations"])
        meta["cities"][city] = {
            "stations": len(payload["stations"]),
            "span_km": round(span, 1),
            "w_km": payload["w_km"],
            "h_km": payload["h_km"],
            "lines": [{"ref": l["ref"], "color": l["color"]}
                      for l in payload["lines"]],
        }
        shape = {"_generated": note, "as_of": args.as_of, "city": city, **payload}
        path = os.path.join(OUT_DIR, f"{city}-shape.json")
        with open(path, "w") as fh:
            json.dump(shape, fh, separators=(",", ":"), ensure_ascii=True)
        print(f"wrote {os.path.relpath(path, REPO)}  "
              f"({os.path.getsize(path) / 1024:.0f} KB, "
              f"{len(payload['lines'])} lines, {len(payload['stations'])} stations, "
              f"span {span:.0f} km)")

    meta_path = os.path.join(OUT_DIR, "meta.json")
    with open(meta_path, "w") as fh:
        json.dump(meta, fh, separators=(",", ":"), ensure_ascii=True)
    print(f"wrote {os.path.relpath(meta_path, REPO)}  "
          f"({os.path.getsize(meta_path) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
