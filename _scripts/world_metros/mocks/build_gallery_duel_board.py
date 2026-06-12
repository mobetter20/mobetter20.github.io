#!/usr/bin/env python3
"""Gallery + Duel approval board (the D16 direction, gate artifact).

Two sections on one static board:

  1. THE GALLERY: the landing. Twelve diagram cards in uniform frames,
     roster order; the familiar Commons diagrams are the artwork. Seoul,
     Tokyo and Paris render real (embedded from the live prototype's
     assets, attribution verbatim from DIAGRAM-LEDGER.md, one computed
     superlative chip each); the other nine are labeled placeholders
     (D8 discipline: no roster scale-up before the gate).
  2. THE DUEL, SEOUL vs PARIS: the engagement core. Both diagrams small,
     framed and attributed up top, then the tale-of-the-tape: paired bars
     tipping toward the larger value, a plain verdict line per row, the
     reported figures held as dated pipeline placeholders, and the
     same-scale silhouette pair demoted to one "true size" row.

Static approval artifact, no JS. Numbers come from the prototype's
committed meta.json / shape JSONs; nothing is fetched.
Writes gallery-duel-board.html next to this file.

Usage:
    python3 _scripts/world_metros/mocks/build_gallery_duel_board.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import build_geo_shape_mock as gm  # noqa: E402  (chaikin only; no fetches)

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ASSETS = os.path.join(REPO, "is", "building", "world-metros", "assets")
ASSET_HREF = "../../../is/building/metro-match/assets"

ROSTER = ["shanghai", "tokyo", "seoul", "hong kong", "singapore", "delhi",
          "moscow", "london", "paris", "nyc", "mexico city", "cairo"]
LIVE = {"seoul", "tokyo", "paris"}

INK = "#17171c"
OPENED = {"seoul": 1974, "paris": 1900}   # earliest regular passenger service
NOW = 2026

# Attribution strings VERBATIM from DIAGRAM-LEDGER.md (per-city stanzas).
ATTRIB = {
    "seoul": "“Seoul Metropolitan Subway network map” by Satellizer, "
             "Wikimedia Commons, CC BY-SA 4.0",
    "tokyo": "“Tokyo Subway Linemap” by Yveltal, Wikimedia Commons, CC BY-SA 4.0",
    "paris": "“Carte Métro de Paris” by Rigil, Wikimedia Commons, CC BY 3.0",
}

# Placeholder feet: the chosen file's license, from the DIAGRAM-LEDGER summary.
LEDGER_LICENSE = {
    "shanghai": "CC BY-SA 4.0", "hong kong": "public domain",
    "singapore": "CC BY-SA 3.0", "delhi": "CC BY-SA 4.0",
    "moscow": "CC BY-SA 4.0", "london": "CC BY-SA 4.0",
    "nyc": "CC BY-SA 3.0", "mexico city": "CC BY-SA 4.0", "cairo": "CC0",
}


def load_meta():
    return json.load(open(os.path.join(ASSETS, "meta.json")))


def load_shape(city):
    return json.load(open(os.path.join(ASSETS, f"{city}-shape.json")))


def superlative_chips(meta):
    """One computed award per live city, from meta.json alone."""
    c = meta["cities"]
    chips = {}
    spans = {k: v["span_km"] for k, v in c.items()}
    longest = max(spans, key=spans.get)
    chips[longest] = f"longest span · {spans[longest]:.0f} km"
    chips["tokyo"] = f"{len(c['tokyo']['lines'])} lines · two operators"
    dens = {k: v["stations"] / (v["w_km"] * v["h_km"]) for k, v in c.items()}
    tightest = max(dens, key=dens.get)
    chips[tightest] = f"tightest mesh · {dens[tightest]:.1f} stations per km²"
    return chips


def gallery_card(city, chips):
    if city in LIVE:
        return (f'<div class="card live">'
                f'<div class="chead"><span class="cname">{city}</span>'
                f'<span class="chip">{chips[city]}</span></div>'
                f'<div class="art"><img src="{ASSET_HREF}/{city}-diagram.svg" '
                f'alt="{city} metro diagram, Wikimedia Commons recreation"></div>'
                f'<div class="cfoot">{ATTRIB[city]}</div></div>')
    return (f'<div class="card soon">'
            f'<div class="chead"><span class="cname">{city}</span></div>'
            f'<div class="art"><span class="soonmark">soon</span></div>'
            f'<div class="cfoot">sourced in ledger · {LEDGER_LICENSE[city]}</div>'
            f'</div>')


def duel_frame(city):
    return (f'<div class="dframe">'
            f'<div class="dhead">{city}</div>'
            f'<div class="dart"><img src="{ASSET_HREF}/{city}-diagram.svg" '
            f'alt="{city} metro diagram, Wikimedia Commons recreation"></div>'
            f'<div class="dcredit">{ATTRIB[city]}</div></div>')


def bar_pair(lv, rv):
    """Paired bar cells, longer bar toward the larger value; leader in ink."""
    top = max(lv, rv)
    wl, wr = 300 * lv / top, 300 * rv / top
    cl = INK if lv >= rv else "#b9b9b2"
    cr = INK if rv >= lv else "#b9b9b2"
    return (f'<div class="tbar tbarl"><span style="width:{wl:.0f}px;'
            f'background:{cl}"></span></div>',
            f'<div class="tbar tbarr"><span style="width:{wr:.0f}px;'
            f'background:{cr}"></span></div>')


def tape_row(label, left, right, lv=None, rv=None, verdict="", note="",
             lev="", muted=False):
    if lv is None:
        bl = br = '<div class="tbar"></div>'
        vcls, lcls = "tver tmut", "tval pv"
    else:
        bl, br = bar_pair(lv, rv)
        vcls, lcls = "tver", "tval"
    notes = f'<div class="tnote">{note}</div>' if note else ""
    levs = f'<div class="vev">{lev}</div>' if lev else ""
    return (f'<div class="trow">'
            f'<div class="{lcls} tl">{left}{levs}</div>{bl}'
            f'<div class="tcenter"><div class="tlab">{label}</div>'
            f'<div class="{vcls}">{verdict}</div>{notes}</div>'
            f'{br}<div class="{lcls} tr">{right}</div></div>')


def silhouette(city, s):
    """True-shape ink silhouette at the shared px-per-km (no stations)."""
    shape = load_shape(city)
    w, h = shape["w_km"] * s, shape["h_km"] * s
    parts = [f'<svg width="{w:.0f}" height="{h:.0f}" '
             f'viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">',
             f'<g fill="none" stroke="{INK}" stroke-width="1.8" '
             f'stroke-linecap="round" stroke-linejoin="round">']
    for line in shape["lines"]:
        for path in line["paths"]:
            pts = " ".join(f"{x * s:.1f},{y * s:.1f}"
                           for x, y in gm.chaikin(path, 1))
            parts.append(f'<polyline points="{pts}"/>')
    parts.append("</g></svg>")
    return "".join(parts)


def true_size_row(meta, s):
    seoul, paris = silhouette("seoul", s), silhouette("paris", s)
    bar = 10 * s
    return (f'<div class="tsrow">'
            f'<div class="tshalf">{seoul}<div class="tsname">seoul</div></div>'
            f'<div class="tcenter tsc"><div class="tlab">TRUE SIZE</div>'
            f'<div class="tver">the diagrams above equalize the two networks; '
            f'the ground does not.</div>'
            f'<div class="tsscale"><span class="bar" '
            f'style="width:{bar:.0f}px"></span><span>10 km</span></div>'
            f'<div class="tnote">one shared scale · north-up · geography not '
            f'aligned · shapes only</div></div>'
            f'<div class="tshalf">{paris}<div class="tsname">paris</div></div>'
            f'</div>')


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
.gallery { display:grid; grid-template-columns:repeat(3, 1fr); gap:12px;
           padding:4px 22px 6px; }
.card { background:#fff; border:1px solid #d8d8d2; display:flex;
        flex-direction:column; }
.chead { display:flex; justify-content:space-between; align-items:center;
         gap:8px; padding:8px 10px; border-bottom:1px solid #d8d8d2;
         min-height:33px; }
.cname { font-size:11px; font-weight:800; letter-spacing:.14em;
         text-transform:uppercase; }
.chip { font-family:'DM Mono',monospace; font-size:7.5px; letter-spacing:.07em;
        color:#0052a4; border:1px solid #0052a466; border-radius:999px;
        padding:2px 7px; white-space:nowrap; text-transform:uppercase; }
.art { height:272px; display:flex; align-items:center; justify-content:center;
       overflow:hidden; }
.art img { width:100%; height:100%; object-fit:contain; padding:8px; }
.card.soon .art { background:#fbfbf9; }
.soonmark { font-family:'DM Mono',monospace; font-size:10px; color:#cfcfc8;
            letter-spacing:.24em; }
.cfoot { border-top:1px solid #d8d8d2; padding:5px 10px;
         font-family:'DM Mono',monospace; font-size:7.5px; color:#b9b9b2;
         line-height:1.45; min-height:32px; }
.card.soon .cfoot { color:#d4d4ce; }
.gnote { display:flex; align-items:center; gap:10px; padding:6px 22px 2px;
         font-family:'DM Mono',monospace; font-size:9px; color:#8a8a85; }
.compare { display:flex; align-items:center; gap:12px; margin:12px 22px 4px;
           padding:11px 16px; background:#fff; border:1px solid #d8d8d2; }
.cpill { font-size:10px; font-weight:800; letter-spacing:.14em;
         border:1px solid #17171c; padding:4px 12px; border-radius:999px;
         text-transform:uppercase; }
.cvs { font-family:'DM Mono',monospace; font-size:9px; color:#8a8a85; }
.ctext { margin-left:8px; font-size:11px; color:#8a8a85; line-height:1.5; }
.ctext b { color:#17171c; font-weight:600; }
.duel { display:flex; gap:14px; padding:4px 22px 0; align-items:stretch; }
.dframe { flex:1; background:#fff; border:1px solid #d8d8d2; display:flex;
          flex-direction:column; min-width:0; }
.dhead { padding:8px 12px; font-size:12px; font-weight:800;
         letter-spacing:.18em; text-transform:uppercase;
         border-bottom:1px solid #d8d8d2; }
.dart { height:238px; display:flex; align-items:center; justify-content:center;
        overflow:hidden; }
.dart img { width:100%; height:100%; object-fit:contain; padding:8px; }
.dcredit { border-top:1px solid #d8d8d2; padding:5px 12px;
           font-family:'DM Mono',monospace; font-size:7.5px; color:#b9b9b2;
           line-height:1.45; }
.vsbadge { align-self:center; width:36px; height:36px; border-radius:50%;
           border:1px solid #17171c; background:#fff; display:flex;
           align-items:center; justify-content:center;
           font-family:'DM Mono',monospace; font-size:10px; font-weight:500;
           flex:none; }
.tape { background:#fff; border:1px solid #d8d8d2; margin:14px 22px 0; }
.trow { display:grid; grid-template-columns:150px 1fr 250px 1fr 150px;
        align-items:center; padding:10px 16px;
        border-bottom:1px solid #f0f0ec; }
.tval { font-family:'DM Mono',monospace; font-size:13px; font-weight:500; }
.tval.tl { text-align:left; }
.tval.tr { text-align:right; }
.tval.pv { font-size:9px; color:#b9b9b2; font-weight:400; }
.vev { font-family:'DM Mono',monospace; font-size:7.5px; color:#b9b9b2;
       margin-top:3px; }
.tbar { display:flex; align-items:center; min-height:6px; }
.tbar span { height:6px; border-radius:2px; display:inline-block; }
.tbarl { justify-content:flex-end; padding-right:14px; }
.tbarr { justify-content:flex-start; padding-left:14px; }
.tcenter { text-align:center; padding:0 6px; }
.tlab { font-family:'DM Mono',monospace; font-size:8.5px; letter-spacing:.16em;
        color:#8a8a85; text-transform:uppercase; }
.tver { font-size:10.5px; font-weight:600; margin-top:3px; line-height:1.45; }
.tver.tmut { color:#8a8a85; font-weight:400; }
.tnote { font-family:'DM Mono',monospace; font-size:7.5px; color:#b9b9b2;
         margin-top:3px; letter-spacing:.04em; }
.tsrow { display:flex; align-items:center; border-top:1px solid #d8d8d2;
         padding:18px 16px; }
.tshalf { flex:1; display:flex; flex-direction:column; align-items:center;
          gap:8px; min-width:0; }
.tsname { font-family:'DM Mono',monospace; font-size:9px; color:#8a8a85;
          letter-spacing:.2em; }
.tcenter.tsc { width:250px; flex:none; }
.tsscale { display:flex; align-items:center; justify-content:center; gap:7px;
           margin-top:9px; font-size:8.5px; color:#8a8a85;
           font-family:'DM Mono',monospace; }
.tsscale .bar { height:3px; background:#17171c; display:inline-block;
                border-radius:2px; }
footer { display:flex; justify-content:space-between; gap:20px;
         padding:9px 22px; border-top:1px solid #d8d8d2; margin-top:16px;
         font-family:'DM Mono',monospace; font-size:9px; color:#8a8a85;
         background:#fff; }
"""


def main():
    meta = load_meta()
    chips = superlative_chips(meta)
    cards = "".join(gallery_card(city, chips) for city in ROSTER)
    s_m, p_m = meta["cities"]["seoul"], meta["cities"]["paris"]

    rows = [
        tape_row("opened", str(OPENED["seoul"]), str(OPENED["paris"]),
                 lv=NOW - OPENED["seoul"], rv=NOW - OPENED["paris"],
                 verdict=f"Paris opened {OPENED['seoul'] - OPENED['paris']} "
                         "years earlier.",
                 note="bars: years in service"),
        tape_row("lines drawn", str(len(s_m["lines"])), str(len(p_m["lines"])),
                 lv=len(s_m["lines"]), rv=len(p_m["lines"]),
                 verdict=f"Paris draws "
                         f"{len(p_m['lines']) / len(s_m['lines']):g}x "
                         "the lines.",
                 lev="lines 2–9 · L1 scope: Method"),
        tape_row("stations plotted", str(s_m["stations"]), str(p_m["stations"]),
                 lv=s_m["stations"], rv=p_m["stations"],
                 verdict=f"Seoul plots {s_m['stations'] - p_m['stations']} "
                         "more stations."),
        tape_row("furthest-stations span",
                 f"{s_m['span_km']:.1f} km", f"{p_m['span_km']:.1f} km",
                 lv=s_m["span_km"], rv=p_m["span_km"],
                 verdict=f"Seoul’s span is "
                         f"{s_m['span_km'] / p_m['span_km']:.1f}x Paris."),
        tape_row("reported route-km",
                 "pipeline · dated at build", "pipeline · dated at build",
                 verdict="reported figure: arrives with the pipeline, "
                         "dated and sourced.", muted=True),
        tape_row("annual ridership",
                 "pipeline · dated at build", "pipeline · dated at build",
                 verdict="almanac fact: reported, never a computed lens.",
                 muted=True),
    ]

    # Shared px-per-km for the true-size pair: Seoul (the larger) sets it.
    ts_scale = 240 / max(s_m["h_km"], p_m["h_km"])

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>world-metros mock: gallery + duel board</title>
<style>{CSS}</style></head><body><div class="board">
<header><div class="wordmark">WORLD METROS <em>ATLAS</em></div>
<span class="mockbadge">GALLERY + DUEL MOCK · D16 · APPROVAL ARTIFACT</span></header>
<div class="intro"><b>the D16 turn:</b> stop generating the hero visual. The
familiar diagrams, the maps riders actually use, become the site’s visual
language in uniform card frames: consistency from the chrome, not the maps.
The engagement core moves to head-to-head comparison. Three cards render real
today; nine arrive after the gate.</div>
<div class="seclabel">THE GALLERY · LANDING · TWELVE DIAGRAMS · UNIFORM FRAMES</div>
<div class="gallery">{cards}</div>
<div class="gnote">three real today (seoul · tokyo · paris) · nine after the
gate · every city has a license-verified file in the ledger · chips computed
from the live datasets</div>
<div class="compare"><span class="cpill">seoul</span><span class="cvs">vs</span>
<span class="cpill">paris</span><span class="ctext"><b>compare any two:</b>
pick a card, pick a challenger. Every pair gets its own duel page. Seoul vs
Paris worked below.</span></div>
<div class="seclabel">THE DUEL · SEOUL VS PARIS · TALE OF THE TAPE</div>
<div class="duel">{duel_frame("seoul")}<div class="vsbadge">VS</div>
{duel_frame("paris")}</div>
<div class="tape">{"".join(rows)}{true_size_row(meta, ts_scale)}</div>
<footer><span>geometry + computed figures © OpenStreetMap contributors · ODbL ·
OSM snapshot {meta["as_of"]} · diagrams Wikimedia Commons, credited per card</span>
<span>made by ajin.im</span></footer>
</div></body></html>"""
    out = os.path.join(HERE, "gallery-duel-board.html")
    with open(out, "w") as fh:
        fh.write(html)
    print(f"wrote {out}  ({os.path.getsize(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
