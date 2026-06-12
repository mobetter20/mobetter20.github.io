#!/usr/bin/env python3
"""Emit the Metro Match deck's per-city geometry stats (gate-3 pipeline).

This is the REFRESH step (network access): it pulls per-city GeoJSON from the
OSM subway-validator CDN into a /tmp cache and emits the committed, dated
assets/meta.json snapshot for all 16 deck cities. build_metro_cards.py (the
BUILD step) then runs offline over that snapshot. Raw CDN GeoJSON is never
shipped or committed (BUILD-SPEC).

Scope rules are the D25 freezes (rider-scope B, ratified D21): each card
claims the network its city's familiar map draws as coequal metro lines;
modes the map marks as distinct products (commuter-rail overlays, trams,
feeders, airport people-movers) stay out. Per-city ref sets below implement
those freezes; DECISIONS.md D25 and the page's Method tab record the prose.

Per D20 (pipeline basis): density moves from bbox to CONVEX HULL of the
plotted stations; span is exact (computed over hull vertices).

Customer-facing line identities: service variants sharing a ref are unioned;
REF_FOLD merges refs that are one identity on the rider map (e.g. Beijing
Batong into Line 1, NYC <6> into 6); REF_DISPLAY relabels pills to the form
the rider map uses where the raw OSM ref is unwieldy.

Station counting (gate-3 fix): the validator GeoJSON carries both named
station nodes and unnamed per-service stop points, and the unnamed share
varies wildly by city (NYC plotted 2.9x its official count, Copenhagen
1.6x), which would bias the stations and density stats. The pipeline now
counts NAMED points only, scoped to within 90 m of an in-scope line vertex,
then merges same-named points within 350 m single-linkage into one station
complex. Cross-line transfers sharing a name count once; same-named but
distant stations (NYC's many "86 St"s) stay distinct.

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

# Deck keys match build_metro_cards.py ROSTER.
CITY_CONFIG = {
    "tokyo": {
        # Tokyo Metro + Toei only; JR refs and the Al through-service excluded
        # (the familiar Tokyo Subway map stops at the subway proper).
        "slugs": ["tokyo", "tokyo_-_toei"],
        "refs": {"G", "M", "H", "T", "C", "Y", "Z", "N", "F",
                 "A", "I", "S", "E"},
        "order": ["G", "M", "H", "T", "C", "Y", "Z", "N", "F",
                  "A", "I", "S", "E"],
        "outlier_km": 35,
    },
    "seoul": {
        # The full capital-region network the familiar map draws, incl. the
        # L1 through-running corridors and Incheon 1/2. Sinbundang is in the
        # declared scope but its validator export is empty (snapshot gap,
        # noted on Method). The suspended Incheon airport maglev stays out.
        "slugs": ["seoul", "incheon"],
        "refs": {str(i) for i in range(1, 10)} | {
            "경의·중앙", "수인·분당", "경춘", "경강", "서해", "공항철도",
            "GTX-A", "W", "Silim", "U", "E", "김포 골드라인", "인천1", "I2"},
        "display": {"경의·중앙": "경의중앙", "수인·분당": "수인분당",
                    "공항철도": "공항", "김포 골드라인": "김포",
                    "Silim": "신림", "W": "우이신설", "U": "의정부",
                    "E": "에버라인", "I2": "인천2"},
        "order": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "GTX-A",
                  "공항철도", "경의·중앙", "경춘", "수인·분당", "경강", "서해",
                  "W", "Silim", "U", "E", "김포 골드라인", "인천1", "I2"],
        "outlier_km": 250,
    },
    "singapore": {
        # MRT only; LRT feeders and airport people-movers excluded.
        "slugs": ["singapore"],
        "refs": {"NSL", "EWL", "NEL", "CCL", "DTL", "TEL"},
        "order": ["NSL", "EWL", "NEL", "CCL", "DTL", "TEL"],
        "outlier_km": 60,
    },
    "hong kong": {
        # MTR heavy rail incl. Airport Express and Disneyland Resort line;
        # Light Rail excluded (district feeder inset on the map).
        "slugs": ["hong_kong"],
        "refs": {"EAL", "ISL", "KTL", "SIL", "TCL", "TKL", "TML", "TWL",
                 "DRL", "AEL"},
        "order": ["ISL", "TWL", "KTL", "TKL", "EAL", "TML", "TCL", "SIL",
                  "DRL", "AEL"],
        "outlier_km": 60,
    },
    "paris": {
        # Metro proper; RER and the airport people-movers excluded.
        "slugs": ["paris"],
        "refs": {"1", "2", "3", "3bis", "4", "5", "6", "7", "7bis",
                 "8", "9", "10", "11", "12", "13", "14"},
        "outlier_km": 16,
    },
    "shanghai": {
        # Lines 1-18 + Pujiang; the maglev is a distinct product on the map.
        "slugs": ["shanghai"],
        "refs": {str(i) for i in range(1, 19)} | {"浦江"},
        "outlier_km": 120,
    },
    "beijing": {
        # The operator's full mapped network. Batong rides as Line 1 and
        # Daxing as Line 4 (one identity each on the map); the named
        # suburban lines, both airport expresses, S1 and Xijiao are all
        # coequal members of the official map.
        "slugs": ["beijing"],
        "refs": {str(i) for i in range(1, 20)} | {
            "1E", "4S", "27", "25N", "25S", "24;L2", "S1;26", "L1",
            "Daxing Airport", "西郊"},
        "fold": {"1E": "1", "4S": "4"},
        "display": {"27": "昌平", "25N": "房山", "25S": "燕房",
                    "24;L2": "亦庄", "S1;26": "S1", "L1": "首都机场",
                    "Daxing Airport": "大兴机场"},
        "order": [str(i) for i in range(1, 20)] + [
            "27", "25N", "25S", "24;L2", "S1;26", "西郊", "L1",
            "Daxing Airport"],
        "outlier_km": 120,
    },
    "london": {
        # Underground only. Elizabeth line, Overground lines and DLR are
        # distinct products in the Tube map's own grammar.
        "slugs": ["london"],
        "refs": {"Bakerloo", "Central", "Circle", "District",
                 "Hammersmith & City", "Jubilee", "Metropolitan",
                 "Northern", "Piccadilly", "Victoria", "Waterloo & City"},
        "display": {"Bakerloo": "BAK", "Central": "CEN", "Circle": "CIR",
                    "District": "DIS", "Hammersmith & City": "H&C",
                    "Jubilee": "JUB", "Metropolitan": "MET",
                    "Northern": "NOR", "Piccadilly": "PIC",
                    "Victoria": "VIC", "Waterloo & City": "W&C"},
        "order": ["Bakerloo", "Central", "Circle", "District",
                  "Hammersmith & City", "Jubilee", "Metropolitan",
                  "Northern", "Piccadilly", "Victoria", "Waterloo & City"],
        "outlier_km": 70,
    },
    "nyc": {
        # Subway services only (SIR/PATH are separate networks already).
        # Rush-hour express variants fold into their base identity; the
        # three S shuttles ride as one S pill, as the map labels them.
        "slugs": ["new_york_city"],
        "refs": {"1", "2", "3", "4", "5", "6", "7", "A", "B", "C", "D",
                 "E", "F", "G", "J", "L", "M", "N", "Q", "R", "S", "W",
                 "Z", "<6>", "<7>", "<F>"},
        "fold": {"<6>": "6", "<7>": "7", "<F>": "F"},
        "order": ["1", "2", "3", "4", "5", "6", "7", "A", "C", "E", "B",
                  "D", "F", "M", "G", "J", "Z", "L", "N", "Q", "R", "W",
                  "S"],
        "outlier_km": 60,
    },
    "madrid": {
        # Metro de Madrid proper; Metro Ligero is a distinct product.
        "slugs": ["madrid"],
        "refs": {f"L{i}" for i in range(1, 13)} | {"R"},
        "display": {**{f"L{i}": str(i) for i in range(1, 13)}},
        "order": [f"L{i}" for i in range(1, 13)] + ["R"],
        "outlier_km": 60,
    },
    "moscow": {
        # Metro incl. the MCC (the map's coequal line 14); the MCD
        # diameters are a distinct D-branded product. The Filyovskaya
        # branch rides as line 4.
        "slugs": ["moscow"],
        "refs": {str(i) for i in range(1, 13)} | {"14", "15", "16",
                                                  "4А", "8А"},
        "fold": {"4А": "4"},
        "display": {"8А": "8A"},
        "order": [str(i) for i in range(1, 13)] + ["8А", "14", "15", "16"],
        "outlier_km": 90,
    },
    "copenhagen": {
        # Metro M1-M4 only; S-tog and Lokaltog are distinct products.
        "slugs": ["copenhagen"],
        "refs": {"M1", "M2", "M3", "M4"},
        "order": ["M1", "M2", "M3", "M4"],
        "outlier_km": 60,
    },
    "delhi": {
        # DMRC network incl. the Airport Express; Rapid Metro Gurgaon is a
        # separate concession. The Blue branch rides as the Blue line.
        "slugs": ["delhi"],
        "refs": {str(i) for i in range(1, 10)} | {"AEx"},
        "fold": {"4": "3"},
        "display": {"AEx": "AE"},
        "order": [str(i) for i in range(1, 10)] + ["AEx"],
        "outlier_km": 80,
    },
    "guangzhou": {
        # Guangzhou Metro network incl. Guangfo and the APM; Foshan's own
        # lines, the trams and the Qingyuan maglev are out of scope.
        "slugs": ["guangzhou"],
        "refs": {str(i) for i in range(1, 15)} | {"18", "21", "22",
                                                  "GF", "APM"},
        "display": {"GF": "广佛"},
        "order": [str(i) for i in range(1, 15)] + ["18", "21", "22",
                                                   "GF", "APM"],
        "outlier_km": 120,
    },
    "mexico city": {
        # STC Metro's 12 lines; Tren Ligero and Suburbano are distinct.
        "slugs": ["mexico_city"],
        "refs": {str(i) for i in range(1, 10)} | {"12", "A", "B"},
        "order": [str(i) for i in range(1, 10)] + ["A", "B", "12"],
        "outlier_km": 60,
    },
    "cairo": {
        # Metro lines 1-3; the LRT and the monorail are distinct systems.
        "slugs": ["cairo"],
        "refs": {"1", "2", "3"},
        "order": ["1", "2", "3"],
        "outlier_km": 80,
    },
}


def fetch_city(slug):
    cache = f"/tmp/wm_{slug}.geojson"
    if not os.path.exists(cache):
        req = urllib.request.Request(CDN + f"{slug}.geojson",
                                     headers={"User-Agent": "world-metros-card-build"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        with open(cache, "wb") as fh:
            fh.write(data)
    return json.load(open(cache))


def project_pt(lon, lat, k):
    return lon * 111.32 * k, -lat * 110.57


def load_network(cfg):
    """-> dict(lines={identity: {color, pts}}, stations=[(x,y)])"""
    refs = cfg["refs"]
    fold = cfg.get("fold", {})
    lines, pts = [], []
    for slug in cfg["slugs"]:
        gj = fetch_city(slug)
        lines += [f for f in gj["features"]
                  if f["geometry"]["type"] == "LineString"
                  and f["properties"].get("ref") in refs]
        pts += [(f["geometry"]["coordinates"], f["properties"].get("name"))
                for f in gj["features"]
                if f["geometry"]["type"] == "Point"]
    if not lines:
        raise SystemExit(f"no lines matched refs for slugs {cfg['slugs']}")
    lat0 = sum(c[1] for f in lines for c in f["geometry"]["coordinates"]) / \
        sum(len(f["geometry"]["coordinates"]) for f in lines)
    k = math.cos(math.radians(lat0))

    segs = []
    for f in lines:
        p = f["properties"]
        ident = fold.get(p["ref"], p["ref"])
        proj = [project_pt(lon, lat, k) for lon, lat in f["geometry"]["coordinates"]]
        segs.append((ident, p.get("stroke", "#888"), proj))

    # outlier guard: drop stray fragments far from the network's median
    # centroid (kept generous; the ref filter does the real scoping)
    cxs = sorted(sum(x for x, _ in s[2]) / len(s[2]) for s in segs)
    cys = sorted(sum(y for _, y in s[2]) / len(s[2]) for s in segs)
    mx, my = cxs[len(cxs) // 2], cys[len(cys) // 2]
    segs = [s for s in segs
            if math.hypot(sum(x for x, _ in s[2]) / len(s[2]) - mx,
                          sum(y for _, y in s[2]) / len(s[2]) - my)
            < cfg["outlier_km"]]

    by_line = {}
    for ident, color, proj in segs:
        entry = by_line.setdefault(ident, {"color": color, "pts": []})
        entry["pts"] += proj

    # named station points within 90 m of a scoped vertex
    grid = {}
    for ident in by_line:
        for x, y in by_line[ident]["pts"]:
            grid.setdefault((int(x), int(y)), []).append((x, y))
    scoped = []
    for coords, name in pts:
        x, y = project_pt(coords[0], coords[1], k)
        gx, gy = int(x), int(y)
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
            scoped.append((x, y, name.strip() if name else None))

    def cluster(group, linkage):
        clusters = []
        for p in group:
            hits = [cl for cl in clusters
                    if any((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
                           < linkage ** 2 for q in cl)]
            if hits:
                hits[0].append(p)
                for other in hits[1:]:
                    hits[0].extend(other)
                    clusters.remove(other)
            else:
                clusters.append([p])
        return [(sum(q[0] for q in cl) / len(cl),
                 sum(q[1] for q in cl) / len(cl)) for cl in clusters]

    # complex merge: same name within 350 m single-linkage counts once
    by_name = {}
    for x, y, name in scoped:
        if name:
            by_name.setdefault(name, []).append((x, y))
    stations = []
    for name, group in by_name.items():
        stations.extend(cluster(group, 0.35))
    return {"lines": by_line, "stations": stations}


def convex_hull(points):
    """Andrew's monotone chain; returns hull vertices counter-clockwise."""
    pts = sorted(set(points))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) > 1 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) > 1 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def hull_area(hull):
    if len(hull) < 3:
        return 0.0
    s = 0.0
    for i in range(len(hull)):
        x1, y1 = hull[i]
        x2, y2 = hull[(i + 1) % len(hull)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def span_km(stations):
    """Exact furthest pair: the extreme pair lies on the convex hull."""
    hull = convex_hull(stations)
    best = 0.0
    for i in range(len(hull)):
        for j in range(i + 1, len(hull)):
            d = (hull[i][0] - hull[j][0]) ** 2 + (hull[i][1] - hull[j][1]) ** 2
            if d > best:
                best = d
    return math.sqrt(best)


def ref_sort_key(ref):
    return (0, len(ref), ref) if ref.isdigit() else (1, len(ref), ref)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=datetime.date.today().isoformat())
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    note = ("GENERATED by _scripts/world_metros/build_page_geometry.py - "
            "DO NOT EDIT by hand")
    meta = {
        "_generated": note,
        "as_of": args.as_of,
        "source": "OSM via cdn.organicmaps.app/subway (ODbL)",
        "basis": {"density": "stations per km2 of the convex hull of "
                             "plotted stations",
                  "span": "furthest plotted stations, geodesic"},
        "cities": {},
    }
    for city, cfg in CITY_CONFIG.items():
        net = load_network(cfg)
        stations = net["stations"]
        hull = convex_hull(stations)
        area = hull_area(hull)
        span = span_km(stations)
        order = cfg.get("order")
        idents = list(net["lines"])
        idents.sort(key=(lambda r: (order.index(r) if r in order else 99,
                                    ref_sort_key(r))) if order
                    else ref_sort_key)
        display = cfg.get("display", {})
        xs = [x for l in net["lines"].values() for x, _ in l["pts"]]
        ys = [y for l in net["lines"].values() for _, y in l["pts"]]
        meta["cities"][city] = {
            "stations": len(stations),
            "span_km": round(span, 1),
            "hull_km2": round(area, 1),
            "w_km": round(max(xs) - min(xs), 1),
            "h_km": round(max(ys) - min(ys), 1),
            "lines": [{"ref": display.get(r, r),
                       "color": net["lines"][r]["color"]} for r in idents],
        }
        print(f"{city:13s} {len(stations):4d} stations  span {span:6.1f} km  "
              f"hull {area:8.1f} km2  {len(idents):2d} lines")

    meta_path = os.path.join(OUT_DIR, "meta.json")
    with open(meta_path, "w") as fh:
        json.dump(meta, fh, separators=(",", ":"), ensure_ascii=False)
    print(f"wrote {os.path.relpath(meta_path, REPO)}  "
          f"({os.path.getsize(meta_path) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
