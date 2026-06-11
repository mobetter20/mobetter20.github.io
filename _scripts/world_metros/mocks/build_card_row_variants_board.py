#!/usr/bin/env python3
"""Metro-cards D20 board: stat-list confirm + three row-design variants.

Owner picked treatment C at D19, then asked to confirm the comparison items
(content and design): big letters, legible, strong brand identity, a real
board-game card look, multiple versions welcome.

  0. THE STAT LIST: was / proposed / why (D20 content proposal: swap
     `lines` for `density`; the pills already carry line count; winner
     spread improves; Paris's mesh becomes playable).
  1. V1 · BIG LEDGER: six rows, jumbo numerals, rank tag + label left,
     value right, no tracks. Maximum legibility.
  2. V2 · STAT TILES: a 2x3 player-mat grid, value on top, label under,
     rank chip in the corner.
  3. V3 · HERO STAT: the city's signature stat blown up (epithet-aligned),
     five compact rows below. Tokyo shows the variant's honest weakness:
     no crown in the live deck of three.

All variants share treatment C (D19), a bigger name (20px), bigger pills,
and the provenance foot. Static, no JS, nothing fetched; stats from the
committed meta.json (density = stations / bbox km², hull basis at pipeline).
Writes card-row-variants-board.html next to this file.

Usage:
    python3 _scripts/world_metros/mocks/build_card_row_variants_board.py
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ASSETS = os.path.join(REPO, "is", "building", "world-metros", "assets")

LIVE = ("seoul", "paris", "tokyo")
DECK_NO = {"tokyo": "02", "seoul": "03", "paris": "09"}
OPENED = {"seoul": 1974, "paris": 1900, "tokyo": 1927}
EPITHET = {"seoul": "the sprawl", "paris": "the mesh", "tokyo": "the two crews"}
HERO_STAT = {"seoul": "span", "paris": "density", "tokyo": "opened"}

ORDINAL = {1: "1st", 2: "2nd", 3: "3rd"}


def load_meta():
    return json.load(open(os.path.join(ASSETS, "meta.json")))


def stat_defs(meta):
    """The PROPOSED six (D20). value, unit, strength (higher = stronger)."""
    c = meta["cities"]

    def dens(k):
        d = c[k]
        return d["stations"] / (d["w_km"] * d["h_km"])

    return [
        ("opened", {k: str(OPENED[k]) for k in LIVE}, "",
         {k: -OPENED[k] for k in LIVE}),
        ("stations", {k: str(c[k]["stations"]) for k in LIVE}, "",
         {k: c[k]["stations"] for k in LIVE}),
        ("span", {k: f'{c[k]["span_km"]:.1f}' for k in LIVE}, "km",
         {k: c[k]["span_km"] for k in LIVE}),
        ("density", {k: f"{dens(k):.2f}" for k in LIVE}, "st/km²",
         {k: dens(k) for k in LIVE}),
    ]


def ranks_for(meta, city):
    out = {}
    for key, values, unit, strength in stat_defs(meta):
        sts = sorted(strength.values(), reverse=True)
        out[key] = (ORDINAL[sts.index(strength[city]) + 1],
                    values[city], unit,
                    sts.index(strength[city]) + 1)
    return out


def pills(meta, city):
    lines = meta["cities"][city]["lines"]
    segs = "".join(f'<i style="background:{l["color"]}">{l["ref"]}</i>'
                   for l in lines)
    compact = " compact" if len(lines) > 12 else ""
    return f'<div class="pills{compact}">{segs}</div>'


def head(meta, city):
    return (f'<div class="mtop"><div><div class="mname">{city}</div>'
            f'<div class="mepi">{EPITHET[city]}</div></div>'
            f'<div class="mno">{DECK_NO[city]}/12</div></div>'
            f'{pills(meta, city)}')


def foot(meta):
    return (f'<div class="mfoot">data: OSM snapshot {meta["as_of"]} · ODbL · '
            f'ranks: live deck of {len(LIVE)} · density: bbox basis</div>')


def chip(rank_ord, rank_n, extra=""):
    cls = "rk rk1" if rank_n == 1 else "rk"
    return f'<span class="{cls}{extra}">{rank_ord}</span>'


def card_v1(meta, city):
    r = ranks_for(meta, city)
    rows = []
    for key in ("opened", "stations", "span", "density"):
        o, v, u, n = r[key]
        unit = f"<small> {u}</small>" if u else ""
        rows.append(f'<div class="v1row">{chip(o, n)}'
                    f'<span class="v1lab">{key}</span>'
                    f'<span class="v1val">{v}{unit}</span></div>')
    for key in ("route-km", "ridership"):
        rows.append(f'<div class="v1row pipe"><span class="rk rkp">···</span>'
                    f'<span class="v1lab">{key}</span>'
                    f'<span class="v1pipe">pipeline · dated</span></div>')
    return (f'<div class="mcard">{head(meta, city)}'
            f'<div class="v1block">{"".join(rows)}</div>{foot(meta)}</div>')


def card_v2(meta, city):
    r = ranks_for(meta, city)
    tiles = []
    for key in ("opened", "stations", "span", "density"):
        o, v, u, n = r[key]
        unit = f"<small> {u}</small>" if u else ""
        tiles.append(f'<div class="tile">{chip(o, n, " tchip")}'
                     f'<div class="tval">{v}{unit}</div>'
                     f'<div class="tlab">{key}</div></div>')
    for key in ("route-km", "ridership"):
        tiles.append(f'<div class="tile pipe">'
                     f'<span class="rk rkp tchip">···</span>'
                     f'<div class="tval tvp">soon</div>'
                     f'<div class="tlab">{key}</div></div>')
    return (f'<div class="mcard">{head(meta, city)}'
            f'<div class="tiles">{"".join(tiles)}</div>{foot(meta)}</div>')


def card_v3(meta, city):
    r = ranks_for(meta, city)
    hk = HERO_STAT[city]
    ho, hv, hu, hn = r[hk]
    hunit = f"<small> {hu}</small>" if hu else ""
    hero = (f'<div class="hero">{chip(ho, hn, " hchip")}'
            f'<div class="hval">{hv}{hunit}</div>'
            f'<div class="hlab">{hk}</div></div>')
    rows = []
    for key in ("opened", "stations", "span", "density"):
        if key == hk:
            continue
        o, v, u, n = r[key]
        unit = f" {u}" if u else ""
        rows.append(f'<div class="v3row">{chip(o, n)}'
                    f'<span class="v3lab">{key}</span>'
                    f'<span class="v3val">{v}{unit}</span></div>')
    for key in ("route-km", "ridership"):
        rows.append(f'<div class="v3row pipe"><span class="rk rkp">···</span>'
                    f'<span class="v3lab">{key}</span>'
                    f'<span class="v3pipe">pipeline · dated</span></div>')
    return (f'<div class="mcard">{head(meta, city)}{hero}'
            f'<div class="v3block">{"".join(rows)}</div>{foot(meta)}</div>')


CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap');
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#0a0a0d; color:#e8e8e3; display:flex; align-items:flex-start;
       justify-content:center; min-height:100vh; padding:24px 0;
       font-family:-apple-system,'Helvetica Neue','Segoe UI',Arial,sans-serif; }
.board { width:1280px; background:#131318; outline:1px solid #26262c;
         box-shadow:0 1px 18px rgba(0,0,0,.6); }
header { display:flex; align-items:baseline; gap:20px; padding:14px 22px 11px;
         border-bottom:1px solid #26262c; background:#15151a; }
.wordmark { font-size:15px; font-weight:700; letter-spacing:.24em;
            color:#f2f2ee; }
.wordmark em { font-style:normal; color:#7fb0e8; }
.mockbadge { margin-left:auto; font-family:'DM Mono',monospace; font-size:9px;
             letter-spacing:.14em; color:#e08040; border:1px solid #e0804066;
             padding:3px 7px; border-radius:2px; white-space:nowrap; }
.intro { padding:9px 22px; font-size:11px; color:#8a8a85; background:#15151a;
         border-bottom:1px solid #26262c; line-height:1.5; }
.intro b { color:#e8e8e3; font-weight:600; }
.seclabel { padding:16px 22px 10px; font-family:'DM Mono',monospace;
            font-size:10px; letter-spacing:.2em; color:#7fb0e8; }
.row { display:flex; gap:26px; justify-content:center; align-items:flex-start;
       padding:6px 22px 10px; }
.cap { font-family:'DM Mono',monospace; font-size:8.5px; color:#8a8a85;
       letter-spacing:.1em; text-align:center; line-height:1.6;
       padding:0 22px 6px; }
.cap b { color:#e8e8e3; font-weight:700; }

.statlist { display:flex; gap:26px; margin:4px 22px 6px; padding:13px 18px;
            background:#15151a; border:1px solid #26262c; font-size:11px;
            line-height:1.6; }
.statlist .col { flex:1; }
.statlist .k { font-family:'DM Mono',monospace; font-size:8px;
               letter-spacing:.18em; color:#7fb0e8; text-transform:uppercase;
               display:block; margin-bottom:4px; }
.statlist .was { color:#8a8a85; }
.statlist .now { color:#e8e8e3; font-weight:600; }
.statlist .why { color:#8a8a85; font-size:10.5px; }
.statlist .out { text-decoration:line-through; color:#55555e; }
.statlist .in { color:#7fb0e8; font-weight:700; }

.mcard { width:270px; height:420px; border-radius:12px; padding:16px 14px 11px;
         display:flex; flex-direction:column; flex:none; overflow:hidden;
         position:relative; background:#1b1b21; border:1px solid #32323a;
         box-shadow:0 4px 16px rgba(0,0,0,.55); color:#f2f2ee; }
.mtop { display:flex; justify-content:space-between; align-items:flex-start;
        gap:8px; }
.mname { font-size:28px; font-weight:800; letter-spacing:.04em;
         text-transform:uppercase; }
.mepi { font-family:'DM Mono',monospace; font-size:9.5px; letter-spacing:.22em;
        color:#7fb0e8; text-transform:uppercase; margin-top:4px; }
.mno { font-family:'DM Mono',monospace; font-size:9px; color:#6a6a72;
       padding-top:6px; }
.pills { display:flex; flex-wrap:wrap; gap:4px; margin-top:12px;
         min-height:18px; }
.pills i { font-style:normal; font-family:'DM Mono',monospace; font-size:9.5px;
           font-weight:500; color:#fff; padding:3px 8px; border-radius:999px;
           letter-spacing:.02em; }
.pills.compact { gap:3px; }
.pills.compact i { font-size:8px; padding:2px 5.5px; }
.rk { font-family:'DM Mono',monospace; font-size:7.5px; letter-spacing:.08em;
      text-transform:uppercase; text-align:center; border-radius:999px;
      padding:3px 0; width:38px; border:1px solid #43434c; color:#9a9a94;
      flex:none; }
.rk1 { background:#0052a4; border-color:#0052a4; color:#fff; font-weight:500; }
.rkp { border-style:dashed; border-color:#3a3a42; color:#55555e; }
.mfoot { margin-top:auto; font-family:'DM Mono',monospace; font-size:6.5px;
         color:#5e5e66; line-height:1.5; padding-top:8px; }

/* V1 big ledger */
.v1block { margin-top:13px; border-top:1px solid #32323a; }
.v1row { display:flex; align-items:center; gap:10px; padding:10px 1px;
         border-bottom:1px solid #232329; }
.v1lab { font-size:11.5px; font-weight:700; letter-spacing:.05em;
         color:#e3e3de; text-transform:uppercase; }
.v1val { margin-left:auto; font-family:'DM Mono',monospace; font-size:20px;
         font-weight:500; letter-spacing:-.01em; white-space:nowrap; }
.v1val small { font-size:9px; color:#8a8a85; letter-spacing:.06em; }
.v1pipe { margin-left:auto; font-family:'DM Mono',monospace; font-size:7px;
          color:#55555e; }
.v1row.pipe .v1lab { color:#6a6a72; }
.v1row.pipe { border-bottom-style:dashed; border-bottom-color:#2c2c34; }

/* V2 stat tiles */
.tiles { margin-top:13px; display:grid; grid-template-columns:1fr 1fr;
         gap:8px; }
.tile { position:relative; background:#1f1f26; border:1px solid #2c2c34;
        border-radius:8px; padding:12px 10px 9px; }
.tile .tchip { position:absolute; bottom:8px; right:8px; width:30px;
               font-size:6.5px; padding:2px 0; }
.tval { font-family:'DM Mono',monospace; font-size:20px; font-weight:500;
        margin-top:2px; white-space:nowrap; }
.tval small { font-size:8.5px; color:#8a8a85; letter-spacing:.06em; }
.tval.tvp { color:#55555e; font-size:12px; }
.tlab { font-size:9.5px; font-weight:700; letter-spacing:.06em;
        color:#e3e3de; text-transform:uppercase; margin-top:5px; }
.tile.pipe { border-style:dashed; background:transparent; }
.tile.pipe .tlab { color:#6a6a72; }

/* V3 hero stat */
.hero { margin-top:13px; border:1px solid #32323a; border-radius:8px;
        background:#1f1f26; padding:13px 12px 11px; position:relative; }
.hero .hchip { position:absolute; top:9px; right:9px; }
.hval { font-family:'DM Mono',monospace; font-size:34px; font-weight:500;
        letter-spacing:-.02em; line-height:1; }
.hval small { font-size:11px; color:#8a8a85; letter-spacing:.06em; }
.hlab { font-size:10.5px; font-weight:700; letter-spacing:.08em;
        color:#e3e3de; text-transform:uppercase; margin-top:7px; }
.v3block { margin-top:9px; }
.v3row { display:flex; align-items:center; gap:10px; padding:8.5px 1px;
         border-bottom:1px solid #232329; }
.v3lab { font-size:10px; font-weight:700; letter-spacing:.05em;
         color:#e3e3de; text-transform:uppercase; }
.v3val { margin-left:auto; font-family:'DM Mono',monospace; font-size:13px;
         font-weight:500; white-space:nowrap; }
.v3pipe { margin-left:auto; font-family:'DM Mono',monospace; font-size:7px;
          color:#55555e; }
.v3row.pipe .v3lab { color:#6a6a72; }
.v3row.pipe { border-bottom-style:dashed; border-bottom-color:#2c2c34; }

footer { display:flex; justify-content:space-between; gap:20px;
         padding:9px 22px; border-top:1px solid #26262c; margin-top:16px;
         font-family:'DM Mono',monospace; font-size:9px; color:#8a8a85;
         background:#15151a; }
"""


def main():
    meta = load_meta()

    statlist = (
        '<div class="statlist">'
        '<div class="col"><span class="k">was</span><span class="was">'
        'opened · <span class="out">lines</span> · stations · span · '
        'route-km · ridership</span></div>'
        '<div class="col"><span class="k">proposed (D20)</span>'
        '<span class="now">opened · stations · span · '
        '<span class="in">density</span> · route-km · ridership</span></div>'
        '<div class="col" style="flex:1.6"><span class="k">why</span>'
        '<span class="why">three size stats let big systems sweep; the pills '
        'already show every line, so the row restated the card’s most visible '
        'device. Density is computed from data in hand, restores winner '
        'spread, and makes Paris’s mesh playable.</span></div></div>')

    v1 = "".join(card_v1(meta, c) for c in LIVE)
    v2 = "".join(card_v2(meta, c) for c in LIVE)
    v3 = "".join(card_v3(meta, c) for c in LIVE)

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>world-metros mock: card stat variants (D20)</title>
<style>{CSS}</style></head><body><div class="board">
<header><div class="wordmark">WORLD METROS <em>ATLAS</em></div>
<span class="mockbadge">STAT VARIANTS · D20 · APPROVAL ARTIFACT</span></header>
<div class="intro"><b>the D20 question (board r2):</b> label hierarchy fixed
after owner flag: stat names now lead each row in bold near-white (you pick a
stat by its name; it cannot be the quietest thing on the card). Ground C is
settled; are the
comparison items optimal, and how should they present? One content proposal
(the strip below) and three presentations of the same card, big letters
first. Pick a variant or name elements to merge; confirm or veto the stat
swap.</div>
<div class="seclabel">THE STAT LIST · ONE SWAP PROPOSED</div>
{statlist}
<div class="seclabel">V1 · BIG LEDGER · JUMBO NUMERALS, NO TRACKS</div>
<div class="row">{v1}</div>
<div class="cap"><b>V1</b> maximum legibility · the rank tag alone carries
relative strength · quietest of the three</div>
<div class="seclabel">V2 · STAT TILES · THE PLAYER-MAT GRID</div>
<div class="row">{v2}</div>
<div class="cap"><b>V2</b> most board-game · tiles give every stat equal
weight · pipeline tiles read as empty slots waiting to fill</div>
<div class="seclabel">V3 · HERO STAT · THE SIGNATURE NUMBER</div>
<div class="row">{v3}</div>
<div class="cap"><b>V3</b> strongest per-card identity (epithet-aligned hero)
· honest weakness shown: Tokyo holds no crown in the live deck of three, so
its hero falls back to its best rank</div>
<footer><span>stats © OpenStreetMap contributors · ODbL · OSM snapshot
{meta["as_of"]} · ranks: live deck of three, full deck at pipeline · density:
bbox basis in mocks, hull basis at pipeline · opened years: operator
histories, dated sourcing at pipeline</span>
<span>made by ajin.im</span></footer>
</div></body></html>"""
    out = os.path.join(HERE, "card-row-variants-board.html")
    with open(out, "w") as fh:
        fh.write(html)
    print(f"wrote {out}  ({os.path.getsize(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
