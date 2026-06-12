#!/usr/bin/env python3
"""Pill-density board (D27 design round). Two candidates for how a card shows
its line identities at mega-network counts, judged by eye in the preview
(open in Arc, no screenshots):

  C1 - AS-IS, FIXED: multi-row pills under the name, the line/scope tag always
       visible below them, the card grows to fit. This is exactly what ships
       now (reuses the real card_front), so the board shows the true cost.
  C2 - ADAPTIVE BAND: cards over ~16 lines render their line colours as one
       thin multi-stripe band (the deck-back motif) plus the count/scope tag;
       the refs themselves move to the lore-back diagram. Cards at or under 16
       keep pills exactly as today (Tokyo unchanged).

Shown on Tokyo (13, the unchanged reference), Seoul (24, wide Korean refs) and
Beijing (27, the true worst case). Owner judges; neither candidate is locked.

    python3 _scripts/world_metros/mocks/build_pill_density_board.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WM = os.path.dirname(HERE)
sys.path.insert(0, WM)
import build_metro_cards as bmc  # noqa: E402

BAND_THRESHOLD = 16
# Tokyo (13, reference, keeps pills) then the seam + extremes by line count:
# Guangzhou 19, NYC 23, Seoul 24, Beijing 27 all band in C2 (over 16).
CITIES = ["tokyo", "guangzhou", "nyc", "seoul", "beijing"]


def band_front(meta, stats, city):
    """C2 variant. Over the threshold: pills become a thin colour band + tag.
    At or under it: identical to C1 (the real card_front)."""
    lines = meta["cities"][city]["lines"]
    if len(lines) <= BAND_THRESHOLD:
        return bmc.card_front(meta, stats, city, deck=True)
    deck_no = "%02d" % (bmc.ROSTER.index(city) + 1)
    stripes = "".join('<i style="background:%s"></i>' % l["color"] for l in lines)
    # count computed from len(lines); "lines on the map side" is exact (the
    # lore back is the diagram, which labels lines its own way, not our refs).
    tag = "%d lines &middot; %s &middot; lines on the map side" % (
        len(lines), bmc.SCOPE_TAG[city])
    ledgers = "".join(bmc.ledger_html(stats, city, s)
                      for s in ("play", "almanac"))
    name = bmc.DISPLAY.get(city, city)
    return ('<article class="card cfront">'
            '<div class="chead"><div class="cid">'
            '<div class="cname">%s</div>'
            '<div class="cepi">%s</div></div>'
            '<div class="cno">%s/18</div></div>'
            '<div class="pdband" aria-label="line colours">%s</div>'
            '<div class="ctag">%s</div>'
            '%s%s</article>') % (name, bmc.EPITHET[city], deck_no,
                                 stripes, tag, ledgers, bmc.card_foot(meta))


def cell(label, front_html):
    return ('<div class="pdcell"><div class="pdcap">%s</div>'
            '<div class="pdcard">%s</div></div>') % (label, front_html)


def main():
    meta = bmc.load_meta()
    bmc.load_content()
    stats = bmc.stat_table(meta, bmc.load_almanac())

    def row(title, note, builder, dset):
        cells = "".join(
            cell("%s &middot; %d lines" % (bmc.DISPLAY.get(c, c).upper(),
                                           len(meta["cities"][c]["lines"])),
                 builder(c))
            for c in CITIES)
        return ('<section class="pdrow"><h2>%s</h2><p class="pdnote">%s</p>'
                '<div class="pdgrid" data-set="%s">%s</div></section>'
                % (title, note, dset, cells))

    c1 = row("C1 &middot; AS-IS, FIXED (pill density)",
             "Every ref kept as a readable pill; the line/scope tag sits on "
             "its own line below and is never occluded. The card grows to fit: "
             "Tokyo stays compact, Seoul and Beijing grow taller (the card has "
             "been 486px min since gate 3's six rows, well past the old 420px). "
             "This is what ships today.",
             lambda c: bmc.card_front(meta, stats, c, deck=True), "play")
    c2 = row("C2 &middot; ADAPTIVE BAND (pill density)",
             "Over ~16 lines the refs collapse to one thin colour band (the "
             "deck-back motif) plus the count and scope; the readable refs live "
             "on the lore-back diagram instead. Cards at or under 16 keep pills "
             "exactly as today, so Tokyo is identical to C1. Seoul and Beijing "
             "come back to the compact height.",
             lambda c: band_front(meta, stats, c), "play")
    almanac = row("ALMANAC SET (the void treatment, D28)",
                  "The second stat set is three rows where PLAY is six: base "
                  "fare, driverless, interchange. To avoid leaving a void below, "
                  "the three rows are grown so they fill the same height the six "
                  "would. Shown here on the same cards; judge whether the taller "
                  "rows read well or want a different treatment.",
                  lambda c: bmc.card_front(meta, stats, c, deck=True), "almanac")

    html = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Metro Match &middot; pill-density board (D27)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/is/building/metro-match/style.css">
<style>
  body { padding: 0 22px 60px; }
  .pdhead { max-width: 760px; margin: 26px auto 8px; }
  .pdhead h1 { font-size: 16px; font-weight: 800; letter-spacing: .22em; color: var(--text); }
  .pdhead h1 em { font-style: normal; color: var(--lblue); }
  .pdhead p { font-size: 13px; color: var(--soft); line-height: 1.65; margin-top: 10px; max-width: 720px; }
  .pdrow { max-width: 1000px; margin: 38px auto 0; }
  .pdrow h2 { font-family: var(--mono); font-size: 12px; letter-spacing: .16em; color: var(--lblue); text-transform: uppercase; }
  .pdnote { font-size: 12px; color: var(--soft); line-height: 1.6; margin: 8px 0 0; max-width: 760px; }
  .pdgrid { display: flex; flex-wrap: wrap; gap: 30px 26px; padding: 22px 0 8px; align-items: start; }
  .pdcell { display: flex; flex-direction: column; gap: 9px; align-items: center; }
  .pdcap { font-family: var(--mono); font-size: 10px; letter-spacing: .14em; color: var(--grey); }
  .pdcard { width: 270px; }
  /* the board shows whichever set its row declares */
  .pdcard .cledger { display: none; }
  .pdgrid[data-set="play"] .cledger[data-set="play"],
  .pdgrid[data-set="almanac"] .cledger[data-set="almanac"] { display: block; }
  /* C2 adaptive band: a thin strip of the line colours, deck-back motif */
  .pdband { display: flex; gap: 0; height: 16px; border-radius: 8px; overflow: hidden; margin-top: 13px; }
  .pdband i { flex: 1; }
</style>
</head><body>
  <div class="pdhead">
    <h1>METRO <em>MATCH</em> &middot; PILL-DENSITY + ALMANAC BOARD</h1>
    <p>Two things to judge by eye, Tokyo (13 lines) the unchanged reference in
    every row. First, the pill treatment for mega-networks: C1 keeps every ref
    as a pill (cards grow), C2 collapses over-16 cards to a colour band. The
    occlusion bug fix ships regardless and is already live. Second, the new
    ALMANAC set's three-row layout (D28) and whether its void-fill reads well.</p>
  </div>
  %s
  %s
  %s
</body></html>
""" % (c1, c2, almanac)

    out = os.path.join(HERE, "pill-density-board.html")
    with open(out, "w") as fh:
        fh.write(html)
    print("wrote %s (%.0f KB)" % (out, os.path.getsize(out) / 1024))


if __name__ == "__main__":
    main()
