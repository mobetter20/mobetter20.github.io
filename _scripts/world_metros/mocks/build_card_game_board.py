#!/usr/bin/env python3
"""Metro-cards v2 approval board (D18: game-first front, map to the back).

Round 2 of the D17 premise kill test, designed from the game outward
(owner verdict on round 1: no map on the front, more stats, polished and
minimal like a modern board-game card, the familiar map maybe on the back).

  1. THE CARD, GAME-FIRST: three v2 fronts (Seoul, Paris, Tokyo). No map.
     Name + epithet, line pills with the real refs in the operators'
     colours, and the play surface: six stat rows, each with a deck-rank
     chip (1ST filled) and a normalized strength track. Four stats computed
     live; route-km and ridership ride as pipeline rows with empty tracks.
  2. THE FLIP: front for play, back for lore. The Seoul back carries the
     familiar diagram full-bleed with a name band, flavor line and the
     ledger-verbatim credit; the uniform pinstripe deck back stays the
     game-hidden state.
  3. THE BATTLE: restaged on v2 cards (span picked, Seoul takes the round).
  4. THE DAILY: the second-mode affordance strip, unchanged role.

Static approval artifact, no JS. Stats from the committed meta.json; ranks
and tracks computed across the live deck of three (full 12 at pipeline);
opened years from operator histories. Nothing is fetched.
Writes card-game-board.html next to this file.

Usage:
    python3 _scripts/world_metros/mocks/build_card_game_board.py
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ASSETS = os.path.join(REPO, "is", "building", "world-metros", "assets")
ASSET_HREF = "../../../is/building/world-metros/assets"

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

# Attribution VERBATIM from DIAGRAM-LEDGER.md (the lore back shows Seoul).
SEOUL_CREDIT = ("“Seoul Metropolitan Subway network map” by Satellizer, "
                "Wikimedia Commons, CC BY-SA 4.0")

ORDINAL = {1: "1st", 2: "2nd", 3: "3rd"}


def load_meta():
    return json.load(open(os.path.join(ASSETS, "meta.json")))


def stat_values(meta):
    """Per-stat values + strength (higher = stronger) for the live deck.
    Win directions per D18: opened = earlier wins; everything else = larger."""
    c = meta["cities"]
    stats = []
    stats.append(("opened", {k: OPENED[k] for k in LIVE},
                  {k: -OPENED[k] for k in LIVE},
                  lambda k, v: str(v)))
    stats.append(("lines", {k: len(c[k]["lines"]) for k in LIVE},
                  {k: len(c[k]["lines"]) for k in LIVE},
                  lambda k, v: f'{v}{LINES_EV.get(k, "")}'))
    stats.append(("stations", {k: c[k]["stations"] for k in LIVE},
                  {k: c[k]["stations"] for k in LIVE},
                  lambda k, v: str(v)))
    stats.append(("span", {k: c[k]["span_km"] for k in LIVE},
                  {k: c[k]["span_km"] for k in LIVE},
                  lambda k, v: f"{v:.1f} km"))
    return stats


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


def card_front(meta, city, highlight=None):
    return (f'<div class="mcard">'
            f'<div class="mtop"><div><div class="mname">{city}</div>'
            f'<div class="mepi">{EPITHET[city]}</div></div>'
            f'<div class="mno">{DECK_NO[city]}/12</div></div>'
            f'{pills(meta, city)}'
            f'<div class="gblock">{stat_block(meta, city, highlight)}</div>'
            f'<div class="mfoot">data: OSM snapshot {meta["as_of"]} · ODbL · '
            f'ranks: live deck of {len(LIVE)}</div></div>')


def card_lore_back(meta, city):
    return (f'<div class="mcard mlore">'
            f'<div class="loreart"><img src="{ASSET_HREF}/{city}-diagram.svg" '
            f'alt="{city} metro diagram, Wikimedia Commons recreation"></div>'
            f'<div class="loreband"><div class="mname">{city}</div>'
            f'<div class="loresys">{SYSTEM[city]}</div>'
            f'<div class="loreflavor">{FLAVOR[city]}</div>'
            f'<div class="lorecredit">{SEOUL_CREDIT}</div></div></div>')


def card_deck_back(meta):
    colours = [l["color"] for city in LIVE for l in meta["cities"][city]["lines"]]
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
.row { display:flex; gap:26px; justify-content:center; align-items:flex-start;
       padding:6px 22px 10px; }
.cell { display:flex; flex-direction:column; gap:8px; align-items:center; }
.cap { font-family:'DM Mono',monospace; font-size:8.5px; color:#8a8a85;
       letter-spacing:.1em; text-align:center; max-width:270px;
       line-height:1.5; }
.cap b { color:#17171c; font-weight:700; }

.mcard { width:270px; height:392px; background:#fff; border:1px solid #d8d8d2;
         border-radius:12px; box-shadow:0 2px 10px rgba(20,20,28,.13);
         padding:16px 14px 11px; display:flex; flex-direction:column;
         flex:none; overflow:hidden; position:relative; }
.mtop { display:flex; justify-content:space-between; align-items:flex-start;
        gap:8px; }
.mname { font-size:17px; font-weight:800; letter-spacing:.1em;
         text-transform:uppercase; }
.mepi { font-family:'DM Mono',monospace; font-size:8px; letter-spacing:.22em;
        color:#0052a4; text-transform:uppercase; margin-top:4px; }
.mno { font-family:'DM Mono',monospace; font-size:9px; color:#8a8a85;
       padding-top:3px; }
.pills { display:flex; flex-wrap:wrap; gap:4px; margin-top:13px;
         min-height:16px; }
.pills i { font-style:normal; font-family:'DM Mono',monospace; font-size:8px;
           font-weight:500; color:#fff; padding:2px 6px; border-radius:999px;
           letter-spacing:.02em; }
.gblock { margin-top:14px; border-top:1px solid #d8d8d2; }
.grow { display:grid; grid-template-columns:32px 1fr 56px 64px; gap:8px;
        align-items:center; padding:11px 1px;
        border-bottom:1px solid #f0f0ec; }
.rk { font-family:'DM Mono',monospace; font-size:6.5px; letter-spacing:.08em;
      text-transform:uppercase; text-align:center; border-radius:999px;
      padding:2px 0; border:1px solid #c9c9c2; color:#8a8a85; }
.rk1 { background:#0052a4; border-color:#0052a4; color:#fff; font-weight:500; }
.rkp { border-style:dashed; color:#c9c9c2; }
.gl { font-family:'DM Mono',monospace; font-size:7.5px; letter-spacing:.1em;
      color:#8a8a85; text-transform:uppercase; }
.track { position:relative; height:2px; background:#e4e4de; border-radius:1px; }
.track i { position:absolute; top:50%; width:6px; height:6px;
           border-radius:50%; background:#17171c;
           transform:translate(-3px,-50%); }
.gv { font-family:'DM Mono',monospace; font-size:10.5px; font-weight:500;
      text-align:right; white-space:nowrap; }
.gvp { font-size:7px; color:#b9b9b2; font-weight:400; }
.grow.pipe .gl { color:#c9c9c2; }
.grow.hot { background:#0052a414; box-shadow:inset 2px 0 0 #0052a4;
            border-radius:2px; }
.grow.hot .gl { color:#0052a4; }
.mfoot { margin-top:auto; font-family:'DM Mono',monospace; font-size:6.5px;
         color:#b9b9b2; line-height:1.5; padding-top:8px; }

.mlore { padding:0; }
.loreart { height:236px; overflow:hidden; position:relative; }
.loreart img { position:absolute; inset:-20%; width:140%; height:140%;
               object-fit:cover; }
.loreband { border-top:1px solid #d8d8d2; padding:12px 14px 10px;
            display:flex; flex-direction:column; flex:1; }
.loresys { font-family:'DM Mono',monospace; font-size:7px;
           letter-spacing:.14em; color:#0052a4; text-transform:uppercase;
           margin-top:4px; }
.loreflavor { font-size:9.5px; color:#3c3c38; line-height:1.45;
              margin-top:9px; }
.lorecredit { margin-top:auto; font-family:'DM Mono',monospace;
              font-size:6.5px; color:#b9b9b2; line-height:1.5; }

.mback { padding:0; }
.pinstripes { position:absolute; inset:10px; border-radius:8px;
              overflow:hidden; display:flex; }
.pinstripes i { flex:1; }
.backband { position:absolute; left:0; right:0; top:50%;
            transform:translateY(-50%); background:#fff; padding:14px 0;
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
"""


def main():
    meta = load_meta()
    fronts = "".join(card_front(meta, c) for c in ("seoul", "paris", "tokyo"))

    flip = (f'<div class="cell">{card_front(meta, "seoul")}'
            f'<div class="cap"><b>the front</b><br>play side: ranks + tracks, '
            f'no map</div></div>'
            f'<div class="cell">{card_lore_back(meta, "seoul")}'
            f'<div class="cap"><b>the flip side</b><br>lore: the familiar map, '
            f'full-bleed, credited</div></div>'
            f'<div class="cell">{card_deck_back(meta)}'
            f'<div class="cap"><b>the deck back</b><br>the opponent’s hidden '
            f'card in the battle</div></div>')

    battle = (f'{card_front(meta, "seoul", highlight="furthest span")}'
              f'<div class="bcenter"><div class="bround">ROUND 3 · YOU PICKED '
              f'SPAN</div><div class="bcall">SEOUL TAKES THE ROUND</div>'
              f'<div class="bnums">57.7 km vs 24.1 km</div>'
              f'<div class="bscore">you 2 · cpu 1 · first to 3</div></div>'
              f'{card_front(meta, "paris", highlight="furthest span")}')

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>world-metros mock: metro cards v2, game-first</title>
<style>{CSS}</style></head><body><div class="board">
<header><div class="wordmark">WORLD METROS <em>ATLAS</em></div>
<span class="mockbadge">METRO CARDS V2 · D18 · APPROVAL ARTIFACT</span></header>
<div class="intro"><b>the D18 correction:</b> round 1 was the atlas in a card
costume. Round 2 designs from the game outward: the stat block is the play
surface (a rank chip and a strength track on every row, so a strong stat is
visible before you pick it), the line pills are the identity, the map leaves
the front entirely and becomes the lore on the flip side. Polished, minimal,
ours.</div>
<div class="seclabel">THE CARD, GAME-FIRST · THREE FRONTS · NO MAP ON THE FRONT</div>
<div class="row">{fronts}</div>
<div class="seclabel">THE FLIP · FRONT FOR PLAY, BACK FOR LORE</div>
<div class="row">{flip}</div>
<div class="seclabel">THE BATTLE · RESTAGED ON V2</div>
<div class="battle">{battle}</div>
<div class="daily"><span class="dpill">cairo</span><span class="dvs">vs</span>
<span class="dpill">singapore</span><span class="dtext"><b>the daily:</b>
which plots more stations? One guess a day, keep the streak. Mode fork for
this gate: battle only, or battle + daily.</span></div>
<footer><span>stats © OpenStreetMap contributors · ODbL · OSM snapshot
{meta["as_of"]} · ranks and tracks: live deck of three, full deck at pipeline
· lore-side diagram credited on card · opened years: operator histories,
dated sourcing at pipeline</span>
<span>made by ajin.im</span></footer>
</div></body></html>"""
    out = os.path.join(HERE, "card-game-board.html")
    with open(out, "w") as fh:
        fh.write(html)
    print(f"wrote {out}  ({os.path.getsize(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
