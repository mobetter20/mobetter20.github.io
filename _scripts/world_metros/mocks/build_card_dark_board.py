#!/usr/bin/env python3
"""Metro-cards D19 ground board (dark fork, judged by eye).

Owner verdict on the D18 v2 board: "i like it", with one amendment: a black
or other dark background might be better. "Background" can mean the table or
the card face, so this board builds both readings on ground swatches:

  1. THE GROUND FORK: the same Seoul card three ways.
       A · round-2 reference: white card, light ground.
       B · white card, dark table (cards stay paper objects).
       C · dark card, dark table (recommendation: the card face goes
           ink-dark; the operators' line colours do the lighting).
  2. THE FAN, DARK: the three fronts in treatment C.
  3. THE FLIP, DARK: front / lore back (familiar diagram, credited) /
     pinstripe deck back, all in C.
  4. THE BATTLE, DARK: restaged in C (span picked, Seoul takes the round).

Static approval artifact, no JS. Same data discipline as the v2 board
(committed meta.json; ranks across the live deck of three; opened years
from operator histories). Nothing is fetched.
Writes card-dark-board.html next to this file.

Usage:
    python3 _scripts/world_metros/mocks/build_card_dark_board.py
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ASSETS = os.path.join(REPO, "is", "building", "world-metros", "assets")
ASSET_HREF = "../../../is/building/metro-match/assets"

LIVE = ("seoul", "paris", "tokyo")
DECK_NO = {"tokyo": "02", "seoul": "03", "paris": "09"}
SYSTEM = {
    "seoul": "Seoul Metropolitan Subway",
    "paris": "Métro de Paris",
    "tokyo": "Tokyo Metro + Toei",
}
OPENED = {"seoul": 1974, "paris": 1900, "tokyo": 1927}
EPITHET = {"seoul": "the sprawl", "paris": "the mesh", "tokyo": "the two crews"}
FLAVOR = {
    "seoul": "58 km between its furthest stations, the deck’s longest reach.",
    "paris": "1.1 stations per square km, the deck’s tightest grid.",
    "tokyo": "Thirteen lines, two operators, one grid.",
}
LINES_EV = {"seoul": " (2–9)"}

SEOUL_CREDIT = ("“Seoul Metropolitan Subway network map” by Satellizer, "
                "Wikimedia Commons, CC BY-SA 4.0")

ORDINAL = {1: "1st", 2: "2nd", 3: "3rd"}


def load_meta():
    return json.load(open(os.path.join(ASSETS, "meta.json")))


def stat_values(meta):
    c = meta["cities"]
    return [
        ("opened", {k: OPENED[k] for k in LIVE},
         {k: -OPENED[k] for k in LIVE}, lambda k, v: str(v)),
        ("lines", {k: len(c[k]["lines"]) for k in LIVE},
         {k: len(c[k]["lines"]) for k in LIVE},
         lambda k, v: f'{v}{LINES_EV.get(k, "")}'),
        ("stations", {k: c[k]["stations"] for k in LIVE},
         {k: c[k]["stations"] for k in LIVE}, lambda k, v: str(v)),
        ("span", {k: c[k]["span_km"] for k in LIVE},
         {k: c[k]["span_km"] for k in LIVE}, lambda k, v: f"{v:.1f} km"),
    ]


def stat_block(meta, city, highlight=None):
    rows = []
    for label, values, strength, fmt in stat_values(meta):
        sts = sorted(strength.values(), reverse=True)
        rank = sts.index(strength[city]) + 1
        smin, smax = min(sts), max(sts)
        pct = 50.0 if smax == smin else 100.0 * (strength[city] - smin) / (smax - smin)
        chip_cls = "rk rk1" if rank == 1 else "rk"
        hot = " hot" if highlight == label else ""
        rows.append(
            f'<div class="grow{hot}">'
            f'<span class="{chip_cls}">{ORDINAL[rank]}</span>'
            f'<span class="gl">{label}</span>'
            f'<span class="track"><i style="left:{pct:.0f}%"></i></span>'
            f'<span class="gv">{fmt(city, values[city])}</span></div>')
    for label in ("route-km", "ridership"):
        rows.append(
            f'<div class="grow pipe">'
            f'<span class="rk rkp">···</span>'
            f'<span class="gl">{label}</span>'
            f'<span class="track"></span>'
            f'<span class="gv gvp">pipeline · dated</span></div>')
    return "".join(rows)


def pills(meta, city):
    segs = "".join(f'<i style="background:{l["color"]}">{l["ref"]}</i>'
                   for l in meta["cities"][city]["lines"])
    return f'<div class="pills">{segs}</div>'


def card_front(meta, city, theme, highlight=None):
    return (f'<div class="mcard {theme}">'
            f'<div class="mtop"><div><div class="mname">{city}</div>'
            f'<div class="mepi">{EPITHET[city]}</div></div>'
            f'<div class="mno">{DECK_NO[city]}/12</div></div>'
            f'{pills(meta, city)}'
            f'<div class="gblock">{stat_block(meta, city, highlight)}</div>'
            f'<div class="mfoot">data: OSM snapshot {meta["as_of"]} · ODbL · '
            f'ranks: live deck of {len(LIVE)}</div></div>')


def card_lore_back(meta, city, theme):
    return (f'<div class="mcard mlore {theme}">'
            f'<div class="loreart"><img src="{ASSET_HREF}/{city}-diagram.svg" '
            f'alt="{city} metro diagram, Wikimedia Commons recreation"></div>'
            f'<div class="loreband"><div class="mname">{city}</div>'
            f'<div class="loresys">{SYSTEM[city]}</div>'
            f'<div class="loreflavor">{FLAVOR[city]}</div>'
            f'<div class="lorecredit">{SEOUL_CREDIT}</div></div></div>')


def card_deck_back(meta, theme):
    colours = [l["color"] for city in LIVE for l in meta["cities"][city]["lines"]]
    stripes = "".join(f'<i style="background:{c}"></i>' for c in colours)
    return (f'<div class="mcard mback {theme}">'
            f'<div class="pinstripes">{stripes}</div>'
            f'<div class="backband"><div class="backmark">METRO MATCH</div>'
            f'<div class="backsub">twelve systems · one deck</div></div></div>')


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
.cell { display:flex; flex-direction:column; gap:9px; align-items:center; }
.cap { font-family:'DM Mono',monospace; font-size:8.5px; color:#8a8a85;
       letter-spacing:.1em; text-align:center; max-width:300px;
       line-height:1.5; }
.cap b { color:#e8e8e3; font-weight:700; }
.sw { padding:26px 24px; border-radius:8px; border:1px solid #26262c;
      display:flex; justify-content:center; }
.swL { background:#e8e8e3; }
.swD { background:#0f0f12; }

.mcard { width:270px; height:392px; border-radius:12px; padding:16px 14px 11px;
         display:flex; flex-direction:column; flex:none; overflow:hidden;
         position:relative; }
.mtop { display:flex; justify-content:space-between; align-items:flex-start;
        gap:8px; }
.mname { font-size:17px; font-weight:800; letter-spacing:.1em;
         text-transform:uppercase; }
.mepi { font-family:'DM Mono',monospace; font-size:8px; letter-spacing:.22em;
        text-transform:uppercase; margin-top:4px; }
.mno { font-family:'DM Mono',monospace; font-size:9px; color:#8a8a85;
       padding-top:3px; }
.pills { display:flex; flex-wrap:wrap; gap:4px; margin-top:13px;
         min-height:16px; }
.pills i { font-style:normal; font-family:'DM Mono',monospace; font-size:8px;
           font-weight:500; color:#fff; padding:2px 6px; border-radius:999px;
           letter-spacing:.02em; }
.gblock { margin-top:14px; }
.grow { display:grid; grid-template-columns:32px 1fr 56px 64px; gap:8px;
        align-items:center; padding:11px 1px; }
.rk { font-family:'DM Mono',monospace; font-size:6.5px; letter-spacing:.08em;
      text-transform:uppercase; text-align:center; border-radius:999px;
      padding:2px 0; }
.rk1 { background:#0052a4; border-color:#0052a4 !important; color:#fff !important;
       font-weight:500; }
.gl { font-family:'DM Mono',monospace; font-size:7.5px; letter-spacing:.1em;
      color:#8a8a85; text-transform:uppercase; }
.track { position:relative; height:2px; border-radius:1px; }
.track i { position:absolute; top:50%; width:6px; height:6px;
           border-radius:50%; transform:translate(-3px,-50%); }
.gv { font-family:'DM Mono',monospace; font-size:10.5px; font-weight:500;
      text-align:right; white-space:nowrap; }
.gvp { font-size:7px; font-weight:400; }
.mfoot { margin-top:auto; font-family:'DM Mono',monospace; font-size:6.5px;
         line-height:1.5; padding-top:8px; }

/* light card (round-2 reference) */
.tL { background:#fff; border:1px solid #d8d8d2;
      box-shadow:0 2px 10px rgba(20,20,28,.13); color:#17171c; }
.tL .mepi { color:#0052a4; }
.tL .gblock { border-top:1px solid #d8d8d2; }
.tL .grow { border-bottom:1px solid #f0f0ec; }
.tL .rk { border:1px solid #c9c9c2; color:#8a8a85; }
.tL .rkp { border-style:dashed; color:#c9c9c2; }
.tL .track { background:#e4e4de; }
.tL .track i { background:#17171c; }
.tL .gvp { color:#b9b9b2; }
.tL .grow.pipe .gl { color:#c9c9c2; }
.tL .grow.hot { background:#0052a414; box-shadow:inset 2px 0 0 #0052a4;
                border-radius:2px; }
.tL .grow.hot .gl { color:#0052a4; }
.tL .mfoot { color:#b9b9b2; }

/* dark card (treatment C) */
.tD { background:#1b1b21; border:1px solid #32323a;
      box-shadow:0 4px 16px rgba(0,0,0,.55); color:#f2f2ee; }
.tD .mepi { color:#7fb0e8; }
.tD .gblock { border-top:1px solid #32323a; }
.tD .grow { border-bottom:1px solid #232329; }
.tD .rk { border:1px solid #43434c; color:#9a9a94; }
.tD .rkp { border-style:dashed; border-color:#3a3a42; color:#55555e; }
.tD .track { background:#2e2e36; }
.tD .track i { background:#e8e8e3; }
.tD .gvp { color:#55555e; }
.tD .grow.pipe .gl { color:#4a4a52; }
.tD .grow.hot { background:#0052a44d; box-shadow:inset 2px 0 0 #5b9bd5;
                border-radius:2px; }
.tD .grow.hot .gl { color:#9cc4ea; }
.tD .mfoot { color:#5e5e66; }

.mlore { padding:0; }
.loreart { height:236px; overflow:hidden; position:relative; }
.loreart img { position:absolute; inset:-20%; width:140%; height:140%;
               object-fit:cover; }
.loreband { padding:12px 14px 10px; display:flex; flex-direction:column;
            flex:1; }
.tD .loreband { border-top:1px solid #32323a; }
.loresys { font-family:'DM Mono',monospace; font-size:7px;
           letter-spacing:.14em; text-transform:uppercase; margin-top:4px; }
.tD .loresys { color:#7fb0e8; }
.loreflavor { font-size:9.5px; line-height:1.45; margin-top:9px; }
.tD .loreflavor { color:#b9b9b4; }
.lorecredit { margin-top:auto; font-family:'DM Mono',monospace;
              font-size:6.5px; line-height:1.5; }
.tD .lorecredit { color:#5e5e66; }

.mback { padding:0; }
.pinstripes { position:absolute; inset:10px; border-radius:8px;
              overflow:hidden; display:flex; }
.pinstripes i { flex:1; }
.backband { position:absolute; left:0; right:0; top:50%;
            transform:translateY(-50%); padding:14px 0; text-align:center; }
.tD .backband { background:#1b1b21; border-top:1px solid #32323a;
                border-bottom:1px solid #32323a; }
.backmark { font-size:14px; font-weight:800; letter-spacing:.3em; }
.tD .backmark { color:#f2f2ee; }
.backsub { font-family:'DM Mono',monospace; font-size:8px; color:#8a8a85;
           margin-top:5px; letter-spacing:.12em; }

.battle { display:flex; gap:22px; justify-content:center; align-items:center;
          padding:6px 22px 10px; }
.bcenter { width:206px; text-align:center; flex:none; }
.bround { font-family:'DM Mono',monospace; font-size:8.5px; color:#8a8a85;
          letter-spacing:.16em; }
.bcall { font-size:14px; font-weight:800; letter-spacing:.06em; margin-top:8px;
         color:#f2f2ee; }
.bnums { font-family:'DM Mono',monospace; font-size:10px; margin-top:6px;
         color:#c9c9c4; }
.bscore { font-family:'DM Mono',monospace; font-size:8.5px; color:#8a8a85;
          margin-top:10px; }

.daily { display:flex; align-items:center; gap:12px; margin:8px 22px 4px;
         padding:11px 16px; background:#15151a; border:1px solid #26262c; }
.dpill { font-size:10px; font-weight:800; letter-spacing:.14em;
         border:1px solid #e8e8e3; color:#e8e8e3; padding:4px 12px;
         border-radius:999px; text-transform:uppercase; }
.dvs { font-family:'DM Mono',monospace; font-size:9px; color:#8a8a85; }
.dtext { margin-left:8px; font-size:11px; color:#8a8a85; line-height:1.5; }
.dtext b { color:#e8e8e3; font-weight:600; }

footer { display:flex; justify-content:space-between; gap:20px;
         padding:9px 22px; border-top:1px solid #26262c; margin-top:16px;
         font-family:'DM Mono',monospace; font-size:9px; color:#8a8a85;
         background:#15151a; }
"""


def main():
    meta = load_meta()

    fork = (f'<div class="cell"><div class="sw swL">'
            f'{card_front(meta, "seoul", "tL")}</div>'
            f'<div class="cap"><b>A · round-2 reference</b><br>white card, '
            f'light ground</div></div>'
            f'<div class="cell"><div class="sw swD">'
            f'{card_front(meta, "seoul", "tL")}</div>'
            f'<div class="cap"><b>B · white card, dark table</b><br>cards stay '
            f'paper objects on a dark page</div></div>'
            f'<div class="cell"><div class="sw swD">'
            f'{card_front(meta, "seoul", "tD")}</div>'
            f'<div class="cap"><b>C · dark card, dark table (rec)</b><br>the '
            f'card face goes ink-dark; the line colours do the lighting</div>'
            f'</div>')

    fan = "".join(card_front(meta, c, "tD") for c in ("seoul", "paris", "tokyo"))

    flip = (f'<div class="cell">{card_front(meta, "seoul", "tD")}'
            f'<div class="cap"><b>the front</b><br>play side, treatment C</div>'
            f'</div>'
            f'<div class="cell">{card_lore_back(meta, "seoul", "tD")}'
            f'<div class="cap"><b>the flip side</b><br>the familiar map stays '
            f'an artwork window, credited</div></div>'
            f'<div class="cell">{card_deck_back(meta, "tD")}'
            f'<div class="cap"><b>the deck back</b><br>the opponent’s hidden '
            f'card</div></div>')

    battle = (f'{card_front(meta, "seoul", "tD", highlight="span")}'
              f'<div class="bcenter"><div class="bround">ROUND 3 · YOU PICKED '
              f'SPAN</div><div class="bcall">SEOUL TAKES THE ROUND</div>'
              f'<div class="bnums">57.7 km vs 24.1 km</div>'
              f'<div class="bscore">you 2 · cpu 1 · first to 3</div></div>'
              f'{card_front(meta, "paris", "tD", highlight="span")}')

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>world-metros mock: metro cards, dark ground fork</title>
<style>{CSS}</style></head><body><div class="board">
<header><div class="wordmark">WORLD METROS <em>ATLAS</em></div>
<span class="mockbadge">DARK GROUND FORK · D19 · APPROVAL ARTIFACT</span></header>
<div class="intro"><b>the D19 question:</b> the v2 card passed; would a dark
ground serve it better? "Background" can mean the table or the card face, so
both readings are built. B keeps the card paper-white on a dark table; C
turns the card itself ink-dark and lets the operators' line colours do the
lighting. A is the round-2 reference. Everything below the fork applies C,
the recommendation.</div>
<div class="seclabel">THE GROUND FORK · SEOUL THREE WAYS · JUDGE BY EYE</div>
<div class="row">{fork}</div>
<div class="seclabel">THE FAN, DARK · TREATMENT C</div>
<div class="row">{fan}</div>
<div class="seclabel">THE FLIP, DARK · FRONT FOR PLAY, BACK FOR LORE</div>
<div class="row">{flip}</div>
<div class="seclabel">THE BATTLE, DARK · RESTAGED</div>
<div class="battle">{battle}</div>
<div class="daily"><span class="dpill">cairo</span><span class="dvs">vs</span>
<span class="dpill">singapore</span><span class="dtext"><b>the daily:</b>
which plots more stations? One guess a day, keep the streak.</span></div>
<footer><span>stats © OpenStreetMap contributors · ODbL · OSM snapshot
{meta["as_of"]} · ranks and tracks: live deck of three, full deck at pipeline
· lore-side diagram credited on card · opened years: operator histories,
dated sourcing at pipeline</span>
<span>made by ajin.im</span></footer>
</div></body></html>"""
    out = os.path.join(HERE, "card-dark-board.html")
    with open(out, "w") as fh:
        fh.write(html)
    print(f"wrote {out}  ({os.path.getsize(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
