#!/usr/bin/env python3
"""Metro-cards approval board (the D17 pivot, premise kill test).

Four exhibits on one static board:

  1. THE FAN: three of the twelve cards (Seoul, Paris, Tokyo) at full
     anatomy: city name + deck number, the line-colour strip (the operators'
     own palette), an ink true-shape art window, one ability with a flavor
     line, the four-stat block, and the provenance footnote (the joke made
     literal: trading cards with footnotes).
  2. THE ART FORK: the Seoul card twice, silhouette window (A) vs diagram
     window (B, Commons recreation, credited on-card). Judged by eye.
  3. THE BATTLE: Top-Trumps moment, Seoul vs Paris with SPAN picked and the
     winner called; the card back (working-title wordmark over the deck's
     line-colour pinstripes) shown beside it.
  4. THE DAILY: the second-mode affordance hint (one guess a day, streak).

Static approval artifact, no JS. Stats come from the prototype's committed
meta.json / shape JSONs; opened years from operator histories (dated sourcing
lands with the pipeline). Nothing is fetched.
Writes card-fan-board.html next to this file.

Usage:
    python3 _scripts/world_metros/mocks/build_card_fan_board.py
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

INK = "#17171c"

# Deck numbers follow roster order (D3): shanghai 01 .. cairo 12.
DECK_NO = {"tokyo": "02", "seoul": "03", "paris": "09"}
SYSTEM = {
    "seoul": "Seoul Metropolitan Subway",
    "paris": "Métro de Paris",
    "tokyo": "Tokyo Metro + Toei",
}
OPENED = {"seoul": 1974, "paris": 1900, "tokyo": 1927}
LINES_EV = {"seoul": " (2–9)"}

ABILITY = {
    "seoul": ("sprawl",
              "58 km between its furthest stations, the deck’s longest reach."),
    "paris": ("mesh",
              "1.1 stations per square km, the deck’s tightest grid."),
    "tokyo": ("two crews",
              "Thirteen lines, two operators, one grid."),
}

# Attribution VERBATIM from DIAGRAM-LEDGER.md (variant B shows Seoul).
SEOUL_CREDIT = ("art: “Seoul Metropolitan Subway network map” by Satellizer, "
                "Wikimedia Commons, CC BY-SA 4.0")
PROVENANCE = "data: OSM snapshot {as_of} · ODbL"

ART_W, ART_H = 234, 158   # inner art window
SIL_PAD = 10


def load_meta():
    return json.load(open(os.path.join(ASSETS, "meta.json")))


def load_shape(city):
    return json.load(open(os.path.join(ASSETS, f"{city}-shape.json")))


def colour_strip(meta, city):
    segs = "".join(f'<i style="background:{l["color"]}"></i>'
                   for l in meta["cities"][city]["lines"])
    return f'<div class="cstrip">{segs}</div>'


def silhouette_art(city):
    """Per-card fit (cards are portraits; comparison stays a stat)."""
    shape = load_shape(city)
    s = min((ART_W - 2 * SIL_PAD) / shape["w_km"],
            (ART_H - 2 * SIL_PAD) / shape["h_km"])
    w_px, h_px = shape["w_km"] * s, shape["h_km"] * s
    ox, oy = (ART_W - w_px) / 2, (ART_H - h_px) / 2
    parts = [f'<svg viewBox="0 0 {ART_W} {ART_H}" width="100%" height="100%" '
             f'xmlns="http://www.w3.org/2000/svg">',
             f'<g fill="none" stroke="{INK}" stroke-width="1.5" '
             f'stroke-linecap="round" stroke-linejoin="round">']
    for line in shape["lines"]:
        for path in line["paths"]:
            pts = " ".join(f"{ox + x * s:.1f},{oy + y * s:.1f}"
                           for x, y in gm.chaikin(path, 1))
            parts.append(f'<polyline points="{pts}"/>')
    parts.append("</g></svg>")
    return "".join(parts)


def diagram_art(city):
    return (f'<img src="{ASSET_HREF}/{city}-diagram.svg" '
            f'alt="{city} metro diagram window, Wikimedia Commons recreation">')


def stat_rows(meta, city, highlight=None):
    c = meta["cities"][city]
    rows = [
        ("opened", str(OPENED[city])),
        ("lines drawn", f'{len(c["lines"])}{LINES_EV.get(city, "")}'),
        ("stations plotted", str(c["stations"])),
        ("furthest span", f'{c["span_km"]:.1f} km'),
    ]
    out = []
    for label, val in rows:
        cls = " hot" if highlight == label else ""
        out.append(f'<div class="srow{cls}"><span class="sl">{label}</span>'
                   f'<span class="sv">{val}</span></div>')
    return "".join(out)


def card(meta, city, art="silhouette", highlight=None, credit=False):
    aname, aflavor = ABILITY[city]
    artwork = diagram_art(city) if art == "diagram" else silhouette_art(city)
    foot = PROVENANCE.format(as_of=meta["as_of"])
    if credit:
        foot = f"{SEOUL_CREDIT}<br>{foot}"
    return (f'<div class="mcard">'
            f'<div class="mtop"><div><div class="mname">{city}</div>'
            f'<div class="msys">{SYSTEM[city]}</div></div>'
            f'<div class="mno">{DECK_NO[city]}/12</div></div>'
            f'{colour_strip(meta, city)}'
            f'<div class="mart">{artwork}</div>'
            f'<div class="mability"><span class="apill">{aname}</span>'
            f'<span class="aflavor">{aflavor}</span></div>'
            f'<div class="mstats">{stat_rows(meta, city, highlight)}</div>'
            f'<div class="mfoot">{foot}</div></div>')


def card_back(meta):
    """The back: deck pinstripes in the live cities' line colours under a
    white wordmark band. Working title on it; naming stays open."""
    colours = [l["color"] for city in ("seoul", "tokyo", "paris")
               for l in meta["cities"][city]["lines"]]
    stripes = "".join(f'<i style="background:{c}"></i>' for c in colours)
    return (f'<div class="mcard mback"><div class="pinstripes">{stripes}</div>'
            f'<div class="backband"><div class="backmark">METRO MATCH</div>'
            f'<div class="backsub">twelve systems · one deck</div></div></div>')


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
.seclabel { padding:16px 22px 10px; font-family:'DM Mono',monospace;
            font-size:10px; letter-spacing:.2em; color:#0052a4; }

.fan { display:flex; gap:26px; justify-content:center; padding:6px 22px 10px; }
.forkrow { display:flex; gap:26px; justify-content:center; align-items:flex-start;
           padding:6px 22px 10px; }
.forkcell { display:flex; flex-direction:column; gap:8px; align-items:center; }
.forkcap { font-family:'DM Mono',monospace; font-size:8.5px; color:#8a8a85;
           letter-spacing:.1em; text-align:center; max-width:270px;
           line-height:1.5; }
.forkcap b { color:#17171c; font-weight:700; }

.mcard { width:270px; height:392px; background:#fff; border:1px solid #d8d8d2;
         border-radius:12px; box-shadow:0 2px 10px rgba(20,20,28,.13);
         padding:12px 12px 9px; display:flex; flex-direction:column;
         flex:none; overflow:hidden; }
.mtop { display:flex; justify-content:space-between; align-items:flex-start;
        gap:8px; }
.mname { font-size:16px; font-weight:800; letter-spacing:.1em;
         text-transform:uppercase; }
.msys { font-family:'DM Mono',monospace; font-size:7px; letter-spacing:.14em;
        color:#0052a4; text-transform:uppercase; margin-top:3px; }
.mno { font-family:'DM Mono',monospace; font-size:9px; color:#8a8a85;
       padding-top:2px; }
.cstrip { display:flex; height:5px; border-radius:2px; overflow:hidden;
          margin-top:8px; }
.cstrip i { flex:1; }
.mart { height:%(arth)spx; margin-top:9px; border:1px solid #e4e4de;
        border-radius:6px; background:#fcfcfa; overflow:hidden; display:flex;
        align-items:center; justify-content:center; }
.mart img { width:100%%; height:100%%; object-fit:cover; }
.mability { display:flex; align-items:baseline; gap:7px; margin-top:9px;
            min-height:30px; }
.apill { font-family:'DM Mono',monospace; font-size:7.5px; letter-spacing:.1em;
         color:#0052a4; border:1px solid #0052a466; border-radius:999px;
         padding:2px 8px; text-transform:uppercase; white-space:nowrap; }
.aflavor { font-size:9.5px; color:#3c3c38; line-height:1.4; }
.mstats { margin-top:8px; border-top:1px solid #d8d8d2; }
.srow { display:flex; justify-content:space-between; align-items:baseline;
        padding:4.5px 2px; border-bottom:1px solid #f0f0ec;
        font-family:'DM Mono',monospace; }
.srow .sl { font-size:8px; color:#8a8a85; letter-spacing:.08em;
            text-transform:uppercase; }
.srow .sv { font-size:10.5px; font-weight:500; }
.srow.hot { background:#0052a414; box-shadow:inset 2px 0 0 #0052a4;
            padding-left:6px; padding-right:4px; }
.srow.hot .sl { color:#0052a4; }
.mfoot { margin-top:auto; font-family:'DM Mono',monospace; font-size:6.5px;
         color:#b9b9b2; line-height:1.5; padding-top:6px; }

.mback { position:relative; padding:0; }
.pinstripes { position:absolute; inset:10px; border-radius:8px;
              overflow:hidden; display:flex; }
.pinstripes i { flex:1; }
.backband { position:absolute; left:0; right:0; top:50%%;
            transform:translateY(-50%%); background:#fff; padding:14px 0;
            text-align:center; border-top:1px solid #d8d8d2;
            border-bottom:1px solid #d8d8d2; }
.backmark { font-size:14px; font-weight:800; letter-spacing:.3em; }
.backsub { font-family:'DM Mono',monospace; font-size:8px; color:#8a8a85;
           margin-top:5px; letter-spacing:.12em; }

.battle { display:flex; gap:22px; justify-content:center; align-items:center;
          padding:6px 22px 10px; }
.bcenter { width:206px; text-align:center; flex:none; }
.bround { font-family:'DM Mono',monospace; font-size:8.5px; color:#8a8a85;
          letter-spacing:.16em; }
.bcall { font-size:14px; font-weight:800; letter-spacing:.06em; margin-top:8px; }
.bnums { font-family:'DM Mono',monospace; font-size:10px; margin-top:6px; }
.bscore { font-family:'DM Mono',monospace; font-size:8.5px; color:#8a8a85;
          margin-top:10px; }
.backcell { display:flex; flex-direction:column; gap:8px; align-items:center;
            margin-left:18px; }

.daily { display:flex; align-items:center; gap:12px; margin:8px 22px 4px;
         padding:11px 16px; background:#fff; border:1px solid #d8d8d2; }
.dpill { font-size:10px; font-weight:800; letter-spacing:.14em;
         border:1px solid #17171c; padding:4px 12px; border-radius:999px;
         text-transform:uppercase; }
.dvs { font-family:'DM Mono',monospace; font-size:9px; color:#8a8a85; }
.dtext { margin-left:8px; font-size:11px; color:#8a8a85; line-height:1.5; }
.dtext b { color:#17171c; font-weight:600; }

footer { display:flex; justify-content:space-between; gap:20px;
         padding:9px 22px; border-top:1px solid #d8d8d2; margin-top:16px;
         font-family:'DM Mono',monospace; font-size:9px; color:#8a8a85;
         background:#fff; }
""" % {"arth": ART_H}


def main():
    meta = load_meta()
    fan = "".join(card(meta, c) for c in ("seoul", "paris", "tokyo"))

    fork = (f'<div class="forkcell">{card(meta, "seoul")}'
            f'<div class="forkcap"><b>A · true-shape silhouette</b><br>'
            f'ours · uniform across the deck · license-free</div></div>'
            f'<div class="forkcell">{card(meta, "seoul", art="diagram", credit=True)}'
            f'<div class="forkcap"><b>B · diagram window</b><br>'
            f'the familiar map cropped to the window · per-city patchwork · '
            f'credited on the card</div></div>')

    battle = (f'{card(meta, "seoul", highlight="furthest span")}'
              f'<div class="bcenter"><div class="bround">ROUND 3 · YOU PICKED '
              f'SPAN</div><div class="bcall">SEOUL TAKES THE ROUND</div>'
              f'<div class="bnums">57.7 km vs 24.1 km</div>'
              f'<div class="bscore">you 2 · cpu 1 · first to 3</div></div>'
              f'{card(meta, "paris", highlight="furthest span")}'
              f'<div class="backcell">{card_back(meta)}'
              f'<div class="forkcap"><b>the back</b><br>deck pinstripes: every '
              f'line colour in the deck · working title, naming open</div></div>')

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>world-metros mock: metro cards board</title>
<style>{CSS}</style></head><body><div class="board">
<header><div class="wordmark">WORLD METROS <em>ATLAS</em></div>
<span class="mockbadge">METRO CARDS MOCK · D17 · APPROVAL ARTIFACT</span></header>
<div class="intro"><b>the D17 turn:</b> the map was the product; now the card
is. A hero map promises polish we cannot license or afford. A card never makes
that promise: the art is a stamp-sized window, the frame is ours, the data is
the content. Three cards, the art fork, one battle, one back. If these do not
delight at this scale, the project archives with confidence.</div>
<div class="seclabel">THE FAN · THREE OF TWELVE · FULL CARD ANATOMY</div>
<div class="fan">{fan}</div>
<div class="seclabel">THE ART FORK · SEOUL TWICE · JUDGE BY EYE</div>
<div class="forkrow">{fork}</div>
<div class="seclabel">THE BATTLE · PICK A STAT · AND THE BACK</div>
<div class="battle">{battle}</div>
<div class="daily"><span class="dpill">cairo</span><span class="dvs">vs</span>
<span class="dpill">singapore</span><span class="dtext"><b>the daily:</b>
which plots more stations? One guess a day, keep the streak. Mode fork for
this gate: battle only, or battle + daily.</span></div>
<footer><span>stats © OpenStreetMap contributors · ODbL · OSM snapshot
{meta["as_of"]} · diagram window credited on card · opened years: operator
histories, dated sourcing at pipeline</span>
<span>made by ajin.im</span></footer>
</div></body></html>"""
    out = os.path.join(HERE, "card-fan-board.html")
    with open(out, "w") as fh:
        fh.write(html)
    print(f"wrote {out}  ({os.path.getsize(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
