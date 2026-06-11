#!/usr/bin/env python3
"""Validator-YAML -> line-graph converter for the bake-off's octolinear leg.

The subway-validator CDN publishes per-network YAML with station-ORDERED
itineraries per route (the topology our drawable GeoJSON lacks) but no
coordinates; station coords are batch-resolved from their OSM node ids via
Overpass (cached in /tmp). Output: a neutral graph dict
    {nodes: {nid: {name, lat, lon}}, edges: {(a, b): set(refs)}}
which the LOOM-format serializer (added once the toolchain probe lands)
turns into the tool's input. Stdlib only (the YAML subset is parsed by
indentation; no pyyaml dependency).
"""

import json
import math
import os
import re
import time
import urllib.parse
import urllib.request

OVERPASS_ENDPOINTS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]

CITY_YAMLS = {
    "seoul": ["seoul"],
    "tokyo": ["tokyo", "tokyo_-_toei"],
    "paris": ["paris"],
}
CITY_REFS = {
    "seoul": {str(i) for i in range(2, 10)},
    "tokyo": {"G", "M", "H", "T", "C", "Y", "Z", "N", "F", "A", "I", "S", "E"},
    "paris": {"1", "2", "3", "3bis", "4", "5", "6", "7", "7bis",
              "8", "9", "10", "11", "12", "13", "14"},
}
# official line colours from our shape JSONs (meta.json carries them too);
# read at convert time so the schematic uses the same palette as candidate 1
META_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "..", "..", "is", "building", "world-metros", "assets",
                         "meta.json")

STOP_RE = re.compile(r"^\s+-\s+'?(.+?)'?\s*\((n\d+)\)\s*$")


def parse_routes(yaml_path, want_refs):
    """-> {ref: [ [ (name, node_id), ... ] itinerary, ... ]} for wanted refs.
    Parses the validator YAML's `routes:` section by indentation."""
    routes = {}
    ref = None
    in_routes = False
    in_itins = False
    cur_itin = None

    for line in open(yaml_path, encoding="utf-8"):
        if line.startswith("routes:"):
            in_routes = True
            continue
        if in_routes and line and not line[0].isspace() and not line.startswith("routes"):
            break  # left the routes block
        if not in_routes:
            continue

        m = re.match(r"^\s{4}ref:\s*(\S+)\s*$", line)
        if m:
            ref = m.group(1)
            in_itins = False
            continue
        if re.match(r"^\s{4}itineraries:\s*$", line):
            in_itins = ref is not None and ref in want_refs
            continue
        if in_itins:
            if re.match(r"^\s{6}\S.*:\s*$", line):  # 'r123784:' itinerary head
                cur_itin = []
                routes.setdefault(ref, []).append(cur_itin)
                continue
            m = STOP_RE.match(line)
            if m and cur_itin is not None:
                cur_itin.append((m.group(1), m.group(2)))
            elif line.strip() and not line.startswith(" " * 6):
                in_itins = False
    return routes


def resolve_coords(city, node_ids):
    """Batch-resolve OSM node ids -> {nid: (lat, lon)} via Overpass, cached."""
    cache = f"/tmp/{city}-stop-nodes.json"
    if os.path.exists(cache):
        got = json.load(open(cache))
    else:
        ids = ",".join(sorted(nid[1:] for nid in node_ids))
        q = f"[out:json][timeout:90];node(id:{ids});out;"
        data = urllib.parse.urlencode({"data": q}).encode()
        got = None
        for attempt in range(1, 5):
            endpoint = OVERPASS_ENDPOINTS[(attempt - 1) % len(OVERPASS_ENDPOINTS)]
            try:
                req = urllib.request.Request(
                    endpoint, data=data,
                    headers={"User-Agent": "world-metros-atlas-mock (ajin.im)"})
                with urllib.request.urlopen(req, timeout=120) as resp:
                    got = json.loads(resp.read())
                break
            except Exception as err:  # noqa: BLE001
                print(f"  overpass nodes attempt {attempt} ({endpoint.split('/')[2]}): "
                      f"{err}; backing off")
                time.sleep(30 * attempt)
        if got is None:
            raise RuntimeError(f"node resolve failed for {city}")
        with open(cache, "w") as fh:
            json.dump(got, fh)
    return {f"n{el['id']}": (el["lat"], el["lon"])
            for el in got.get("elements", []) if el["type"] == "node"}


def build_graph(city):
    """-> {nodes: {nid: {name, lat, lon}}, edges: {(a,b)sorted: set(refs)},
          colors: {ref: '#hex'}}"""
    here = os.path.dirname(os.path.abspath(__file__))
    refs = CITY_REFS[city]
    routes = {}
    for slug in CITY_YAMLS[city]:
        path = f"/tmp/{slug}.yaml"
        if not os.path.exists(path):
            raise SystemExit(f"missing {path} — fetch the validator YAML first")
        for ref, itins in parse_routes(path, refs).items():
            routes.setdefault(ref, []).extend(itins)

    names, ids = {}, set()
    edges = {}
    for ref, itins in routes.items():
        for itin in itins:
            for name, nid in itin:
                names[nid] = name
                ids.add(nid)
            for (na, a), (nb, b) in zip(itin, itin[1:]):
                if a == b:
                    continue
                key = (a, b) if a < b else (b, a)
                edges.setdefault(key, set()).add(ref)

    coords = resolve_coords(city, ids)
    missing = ids - set(coords)
    if missing:
        print(f"  {city}: {len(missing)} stop nodes unresolved (dropped)")
    nodes = {nid: {"name": names[nid], "lat": coords[nid][0], "lon": coords[nid][1]}
             for nid in ids if nid in coords}
    edges = {k: v for k, v in edges.items() if k[0] in nodes and k[1] in nodes}

    colors = {}
    meta_file = os.path.normpath(META_PATH)
    if os.path.exists(meta_file):
        meta = json.load(open(meta_file))
        for l in meta["cities"].get(city, {}).get("lines", []):
            colors[l["ref"]] = l["color"]

    print(f"  {city}: {len(nodes)} stops, {len(edges)} edges, "
          f"{len(routes)} lines ({', '.join(sorted(routes, key=lambda r: (len(r), r)))})")
    return {"nodes": nodes, "edges": edges, "colors": colors}


def to_loom_geojson(graph):
    """Serialize the neutral graph to LOOM's line-graph GeoJSON (verified
    against shared/linegraph/LineGraph.cpp readFromGeoJson): Points carry
    station_id/station_label; LineStrings carry from/to + a `lines` array of
    {id, label, color}. Stations sit exactly on edge endpoints, so no orphan
    snapping is needed; `topo` then merges shared corridors and clusters
    same-name stations (per-line OSM stop nodes) into interchange nodes."""
    feats = []
    for nid, n in graph["nodes"].items():
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [n["lon"], n["lat"]]},
            "properties": {"id": nid, "station_id": nid,
                           "station_label": n["name"]},
        })
    for (a, b), refs in graph["edges"].items():
        na, nb = graph["nodes"][a], graph["nodes"][b]
        feats.append({
            "type": "Feature",
            "geometry": {"type": "LineString",
                         "coordinates": [[na["lon"], na["lat"]],
                                         [nb["lon"], nb["lat"]]]},
            "properties": {"id": f"e_{a}_{b}", "from": a, "to": b,
                           "lines": [{"id": ref, "label": ref,
                                      "color": graph["colors"].get(ref, "888888").lstrip("#")}
                                     for ref in sorted(refs)]},
        })
    return {"type": "FeatureCollection", "features": feats}


if __name__ == "__main__":
    for city in CITY_YAMLS:
        print(f"== {city}")
        g = build_graph(city)
        out = f"/tmp/{city}-linegraph.json"
        with open(out, "w") as fh:
            json.dump(to_loom_geojson(g), fh, ensure_ascii=False)
        print(f"  wrote {out} ({os.path.getsize(out) / 1024:.0f} KB)")
