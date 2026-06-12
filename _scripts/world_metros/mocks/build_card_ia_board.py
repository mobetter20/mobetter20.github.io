#!/usr/bin/env python3
"""Card-IA board (D30 round). The owner's flag: the card now has three views
(PLAY front, ALMANAC front toggled at deck level, lore-back flip) and they
may not be intuitive; almanac figures and lore-back facts sometimes overlap.

The board shows, side by side on real cards (Seoul the busy case, Tokyo the
reference):

  TODAY - the three views exactly as they ship, current copy (the baseline).
  A     - KEEP + RENAME: two front sets + flip, honest set names
          (SCALE | CHARACTER mocked; menu of pairs below), set caption on the
          card, battle-binding whisper on the bar.
  B     - TWO SURFACES: the front toggle dies; the five character stats move
          to the lore back as a compact figure strip; front = the six play
          stats only. Two surfaces, one flip.
  C     - NO MODES: both sets on the face, the six as rows + the five as a
          fine-print strip; nothing toggles, everything always visible.

Plus the full 18-city overlap map (lore copy vs shown stats) and the dedup
edit list (old -> new copy, written to ship), which is candidate-invariant:
all three candidates keep all eleven numbers somewhere on the card.

Nothing here touches the live page; the verdict applies the pick.

    python3 _scripts/world_metros/mocks/build_card_ia_board.py
"""

import html as html_mod
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WM = os.path.dirname(HERE)
sys.path.insert(0, WM)
import build_metro_cards as bmc  # noqa: E402

CITIES = ["seoul", "tokyo"]  # busy case + reference (brief: Seoul/Beijing + Tokyo)

# ---------------------------------------------------------------- dedup copy
# ROUND 2 (owner verdict 2026-06-12). The owner's bar for lore copy:
# factually correct, no copyright entanglement, interesting on its own.
# Number restates are TOLERATED under that bar, so the round-1 list of 26
# shrinks to the slim set below: factual must-fixes plus repeat-swaps
# (a back that says the same thing twice wastes one of its two slots).
# Cities absent here keep their current line unchanged.

NEW_FLAVOR = {
    # repeat-swaps: the flavor duplicated one of the facts
    "tokyo": "Run so tightly that a five-minute delay comes with a certificate.",
    "madrid": "Dug fast and cheap, by a method other cities came to copy.",
    "moscow": "Trains so frequent the platform clock counts up from the last one, not down to the next.",
    "mexico city": "Trains ride on rubber tires, quieter and softer than steel.",
    # factual must-fix: all six MRT lines are GoA4 since the NSL/EWL
    # conversions; "four of them" is stale. Minimal edit, structure kept.
    "singapore": "Six lines, every one of them driverless, none older than 1987.",
}

NEW_FACTS = {  # only the changed slots; None = keep current
    # factual must-fixes
    "shanghai": [None, "Seven lines now run driverless, five of them with no staff aboard at all."],
    "osaka": ["Midosuji&rsquo;s first stations were built like vaults, with high arched ceilings and chandeliers.",
              "The New Tram has run as an automated people-mover since 1981."],
    # repeat-swaps: the fact duplicated the flavor line
    "cairo": ["Line 2 runs beneath the Nile itself, through twin tunnels bored under the riverbed.", None],
    "istanbul": [None, "Istanbul has run an underground railway since 1875: the two-stop T&uuml;nel funicular."],
}

# Flagged, owner's call (factually correct, so it may stand as-is): the NYC
# fact "Its 472 stations are the most of any single-operator metro in the
# world" sits on a card whose plotted count reads 504. Optional clarifier:
NYC_OPTIONAL = ("Officially 472 stations, the most of any single-operator "
                "metro in the world.")


def new_copy(city):
    flavor = NEW_FLAVOR.get(city, bmc.FLAVOR[city])
    facts = list(bmc.FACTS[city])
    for i, repl in enumerate(NEW_FACTS.get(city, [])):
        if repl is not None:
            facts[i] = repl
    return flavor, facts


# ------------------------------------------------------------- card variants

STRIP_LABEL = {"fare": "BASE FARE", "driverless": "DRIVERLESS",
               "interchange": "INTERCHANGE", "newlines": "NEW SINCE &rsquo;16",
               "newest": "NEWEST LINE"}


def strip_val(s, city):
    v = s["values"][city]
    if s["key"] == "fare":
        return f"${v:.2f}"
    if s["key"] == "interchange":
        return f"{v}%"
    if s["key"] in ("driverless", "newlines"):
        return f"{v} lines"
    return str(v)


def strip_html(stats, city, front=False):
    """The character stats as a compact figure strip (3+2 cells). Rank rides
    as a small ordinal; 1st keeps the filled-chip blue."""
    cells = []
    for s in stats:
        if s["set"] != "almanac":
            continue
        r = s["ranks"][city]
        rcls = "xr xr1" if r == 1 else "xr"
        cells.append(
            f'<div class="xcell"><span class="xlab">{STRIP_LABEL[s["key"]]}</span>'
            f'<span class="xv">{strip_val(s, city)}<i class="{rcls}">{bmc.ORDINAL[r].lower()}</i></span></div>')
    cls = "xstrip xfront" if front else "xstrip"
    return f'<div class="{cls}">{"".join(cells)}</div>'


def back_html(city, flavor, facts, strip=""):
    """Mirror of bmc.card_back, parameterized for copy + the B figure strip;
    diagrams load eagerly (no app.js on the board). Strip-bearing backs get
    .bfit: pinned to the live flip height (469px, the front drives the box),
    with the diagram window absorbing the squeeze, exactly as the live
    implementation would."""
    facts_html = "".join(f'<div class="lfact">{f}</div>' for f in facts)
    caveat = (f'<div class="lcaveat">{bmc.CAVEAT[city]}</div>'
              if city in bmc.CAVEAT else "")
    name = bmc.DISPLAY.get(city, city)
    cls = "card cback bfit" if strip else "card cback"
    return (f'<article class="{cls}" aria-label="{name} lore side">'
            f'<div class="lart"><img src="/is/building/world-metros/assets/{bmc.diagram_file(city)}" '
            f'alt="{html_mod.escape(bmc.SYSTEM[city])} network diagram"></div>'
            f'<div class="lband"><div class="lname">{name}</div>'
            f'<div class="lsys">{bmc.EPITHET[city]}</div>'
            f'<div class="lflavor">{flavor}</div>'
            f'<div class="lfacts">{facts_html}</div>'
            f'{strip}'
            f'<div class="lcredit">{bmc.CREDIT[city]}{caveat}</div></div></article>')


def c_front(meta, stats, city):
    """Candidate C: the play ledger + the character strip on one face."""
    f = bmc.card_front(meta, stats, city)  # play ledger only
    return f.replace('<div class="cfoot">',
                     strip_html(stats, city, front=True) + '<div class="cfoot">')


def bar(a, b, active, whisper=""):
    btns = "".join(
        f'<button type="button" class="themebtn" aria-pressed='
        f'"{"true" if active == i else "false"}">{n}</button>'
        for i, n in enumerate((a, b)))
    w = f'<span class="themenote">{whisper}</span>' if whisper else ""
    return (f'<div class="themebar iabar"><span class="themecap">STATS</span>'
            f'{btns}{w}</div>')


def cell(cap, inner, dset="play", note=""):
    n = f'<div class="iacellnote">{note}</div>' if note else ""
    return (f'<div class="iacell" data-set="{dset}">'
            f'<div class="iacap">{cap}</div>{inner}{n}</div>')


# ------------------------------------------------------------- overlap table

K_CONTRA, K_RESTATE, K_INTERNAL, K_COUNT, K_KEEP = (
    "contradicts", "restates", "internal", "count", "keep")

OVERLAP = [
    # (city, where, quote, what it hits, class, note)
    ("tokyo", "flavor", "Thirteen lines, two operators, one grid.",
     "the card subtitle (13 lines &middot; Metro + Toei)", K_COUNT,
     "the count is the first thing the front says"),
    ("tokyo", "fact 2", "G is for Ginza: Asia&rsquo;s first metro line, opened 1927.",
     "OPENED 1927 (5th)", K_RESTATE, "the story stays, the year is the stat"),
    ("tokyo", "fact 1", "Tokyo Metro runs nine lines, Toei runs four.",
     "nothing shown as a stat", K_KEEP,
     "the two-crews split is structure, not a stat restate"),
    ("seoul", "flavor", "146 km between its furthest stations, the deck&rsquo;s longest reach.",
     "SPAN 146.1 km and its 1ST chip", K_RESTATE,
     "value and rank claim both sit one ledger row away"),
    ("singapore", "flavor", "Six lines, four of them driverless, none older than 1987.",
     "DRIVERLESS 6 lines", K_CONTRA,
     "stale: all six are GoA4 since the NSL/EWL conversion; also restates the subtitle count and OPENED 1987"),
    ("singapore", "fact 2", "The North East Line opened in 2003 as one of the world&rsquo;s first fully automated heavy metro lines.",
     "DRIVERLESS (story)", K_KEEP, "a first-story; the count stays unstated"),
    ("hong kong", "flavor", "Fares cover the costs and then some&hellip;",
     "no stat (farebox was cut at D28)", K_KEEP, "famous-case lore, sanctioned"),
    ("hong kong", "fact 2", "The East Rail corridor dates to 1910&hellip;",
     "OPENED 1979", K_KEEP,
     "deliberate: explains why the scope holds older track than the system&rsquo;s own dating"),
    ("paris", "flavor", "1.35 stations per square km, the deck&rsquo;s tightest grid.",
     "DENSITY 1.35 and its 1ST chip", K_RESTATE, "the exact value, plus the rank claim"),
    ("paris", "fact 1", "Opened for the 1900 World&rsquo;s Fair&hellip;",
     "OPENED 1900 (2nd)", K_RESTATE, "the Fair stays, the year is the stat"),
    ("shanghai", "flavor", "From first train to 800 route-km inside three decades.",
     "ROUTE-KM 816 km (3rd)", K_RESTATE, "rounds the stat it sits behind"),
    ("shanghai", "fact 2", "Five lines run driverless, about 169 km of unattended metro.",
     "DRIVERLESS 7 lines", K_CONTRA,
     "the fact counts the five GoA4 lines; the stat adds two GoA3 (5 and 17): 5 vs 7 on one card"),
    ("shanghai", "fact 1", "Set a one-day record of 13.39 million rides&hellip;",
     "RIDERSHIP (annual)", K_KEEP, "a dated record, a different grain than the annual stat"),
    ("beijing", "flavor", "909 route-km under one operator, the deck&rsquo;s biggest single system.",
     "ROUTE-KM 909 km (2nd)", K_RESTATE, "exact value plus a rank-flavored claim"),
    ("beijing", "fact 1", "&hellip;Zhou Enlai rode the first train in 1969.",
     "OPENED 1969 (8th)", K_RESTATE, "the year only; the project story stays"),
    ("london", "flavor", "Underground since 1863, before anyone else tried.",
     "OPENED 1863 and its 1ST chip", K_RESTATE, "the chip already says first"),
    ("nyc", "fact 2", "Its 472 stations are the most of any single-operator metro in the world.",
     "STATIONS 504 (2nd)", K_CONTRA,
     "official complexes (472) vs our plotted count (504) fight on one card; the rank chip also reads 2nd"),
    ("nyc", "flavor", "24 hours a day, every day of the year.",
     "no stat (hours were cut at D28)", K_KEEP, "watch-item if an hours stat returns"),
    ("madrid", "flavor", "172 km of new metro in sixteen years, Europe&rsquo;s great expansion.",
     "fact 1 (same story)", K_INTERNAL, "fact 1 carries the same 172 km in full detail"),
    ("madrid", "fact 2", "&hellip;a time-capsule museum of the 1919 metro.",
     "OPENED 1919 (4th)", K_RESTATE, "the year only"),
    ("moscow", "flavor", "Marble, mosaics and a train every 90 seconds.",
     "fact 1 (marble palaces) + fact 2 (80 s)", K_INTERNAL,
     "repeats fact 1&rsquo;s story; 90 s beside fact 2&rsquo;s 80 s reads like a discrepancy"),
    ("moscow", "fact 2", "In 2023 Moscow cut rush-hour intervals to 80 seconds&hellip;",
     "no stat (headway was cut at D28)", K_KEEP, "famous-case lore; watch-item"),
    ("copenhagen", "flavor", "Four lines, zero drivers, all night.",
     "the subtitle count + fact 2", K_COUNT,
     "restates the 4-line count and pre-states fact 2&rsquo;s 24/7"),
    ("copenhagen", "fact 1", "Every train has run driverless since the first one in 2002.",
     "DRIVERLESS 4 of 4 + OPENED 2002", K_RESTATE,
     "&ldquo;every train&rdquo; is the stat&rsquo;s totality; 2002 is the opened stat"),
    ("delhi", "flavor", "374 route-km in barely two decades, and it pays its own way.",
     "ROUTE-KM 374 km (8th)", K_RESTATE, "exact value"),
    ("delhi", "fact 2", "India&rsquo;s first driverless trains entered service on the Magenta Line in 2020.",
     "DRIVERLESS (story)", K_KEEP, "first-story; the count (3) stays unstated"),
    ("guangzhou", "flavor", "From a 5 km starter line in 1997 to 780 km today.",
     "OPENED 1997 + ROUTE-KM 780 km", K_RESTATE, "two stats in one line"),
    ("guangzhou", "fact 1", "Lines 18 and 22 run at 160 km/h&hellip;",
     "no stat (speed)", K_KEEP, "watch-item if the second-set menu adds top speed"),
    ("guangzhou", "fact 2", "The Guangfo line, opened 2010, was China&rsquo;s first intercity metro.",
     "nothing shown as a stat", K_KEEP, "2010 is no stat value here"),
    ("mexico city", "flavor", "A pictogram for every station, a 5-peso fare for every ride.",
     "BASE FARE $0.29 (= MXN 5.00)", K_RESTATE,
     "the peso figure IS the fare stat&rsquo;s local value; pictogram also repeats fact 1"),
    ("mexico city", "fact 1", "Every station has its own pictogram, a 1969 design&hellip;",
     "OPENED 1969 (8th)", K_RESTATE, "the design story stays, the year is the stat"),
    ("cairo", "flavor", "Africa&rsquo;s first metro, opened 1987, still its workhorse.",
     "OPENED 1987 (12th)", K_RESTATE, "the year only"),
    ("cairo", "fact 1", "Africa&rsquo;s and the Middle East&rsquo;s first metro, opened 1987.",
     "the flavor line + OPENED 1987", K_INTERNAL,
     "repeats the flavor nearly verbatim and the stat year with it"),
    ("osaka", "fact 1", "The Midosuji Line opened in 1933 as Japan&rsquo;s first municipally run subway.",
     "the flavor line + OPENED 1933 (6th)", K_INTERNAL,
     "the flavor already says oldest municipal; the year is the stat"),
    ("osaka", "fact 2", "The New Tram has run as a driverless people-mover since 1981.",
     "DRIVERLESS 1 line (story)", K_KEEP,
     "the story behind the figure; check the 1981 wording at apply time (the source dates GoA4 to 1991)"),
    ("istanbul", "flavor", "A metro on two continents, and one of the world&rsquo;s fastest-growing.",
     "NEW SINCE &rsquo;16 5 lines (4th) + fact 2", K_RESTATE,
     "&ldquo;fastest-growing&rdquo; rubs against the shown 4th; two continents repeats fact 2"),
    ("istanbul", "fact 1", "The M5, opened 2017, was Turkey&rsquo;s first driverless metro line.",
     "DRIVERLESS (story)", K_KEEP, "first-story; the count (4) stays unstated"),
    ("istanbul", "fact 2", "Its lines run on both the European and Asian sides of the Bosphorus.",
     "the flavor line", K_INTERNAL, "one of the two carries the continents; the other changes"),
]

KCLASS_LABEL = {
    K_CONTRA: "CONTRADICTS A STAT", K_RESTATE: "RESTATES A STAT",
    K_INTERNAL: "REPEATS ITSELF", K_COUNT: "RESTATES THE SUBTITLE",
    K_KEEP: "KEEP (deliberate)",
}

# ----------------------------------------------------------------- edit list

# The slim list, tiered. (city, item, tier, old, new, why).
SLIM_EDITS = [
    ("singapore", "flavor", "MUST FIX",
     "Six lines, four of them driverless, none older than 1987.",
     NEW_FLAVOR["singapore"],
     "stale: all six MRT lines have run GoA4 since the North South / East West conversions "
     "(2017-18); the card&rsquo;s DRIVERLESS figure says 6. One word changes."),
    ("shanghai", "fact 2", "MUST FIX",
     "Five lines run driverless, about 169 km of unattended metro.",
     NEW_FACTS["shanghai"][1],
     "the card&rsquo;s DRIVERLESS figure counts 7 (five GoA4 plus two attended GoA3 lines); "
     "saying five beside it reads as an error. The new line carries both truths."),
    ("osaka", "fact 2", "MUST FIX",
     "The New Tram has run as a driverless people-mover since 1981.",
     NEW_FACTS["osaka"][1],
     "the source dates full driverless (GoA4) to 1991; the line has been automated since "
     "1981. &ldquo;Automated&rdquo; is the safely true word."),
    ("tokyo", "flavor", "REPEAT SWAP",
     "Thirteen lines, two operators, one grid.",
     NEW_FLAVOR["tokyo"],
     "fact 1 already tells the two-operator story (and the subtitle counts the lines); "
     "the duplicated slot goes to the delay-certificate story instead."),
    ("madrid", "flavor", "REPEAT SWAP",
     "172 km of new metro in sixteen years, Europe&rsquo;s great expansion.",
     NEW_FLAVOR["madrid"],
     "fact 1 tells the same expansion with the same 172 km; the freed slot goes to the "
     "Madrid-method story."),
    ("moscow", "flavor", "REPEAT SWAP",
     "Marble, mosaics and a train every 90 seconds.",
     NEW_FLAVOR["moscow"],
     "fact 1 already owns the marble palaces, and the 90 seconds sits oddly beside "
     "fact 2&rsquo;s 80-second record; the count-up platform clock is its own story."),
    ("mexico city", "flavor", "REPEAT SWAP",
     "A pictogram for every station, a 5-peso fare for every ride.",
     NEW_FLAVOR["mexico city"],
     "fact 1 already owns the pictograms; rubber tires are the unused signature. "
     "(The 5-peso half was fine under your bar; it leaves as a side effect. If you want "
     "the peso line kept instead, say so and only the pictogram half changes.)"),
    ("cairo", "fact 1", "REPEAT SWAP",
     "Africa&rsquo;s and the Middle East&rsquo;s first metro, opened 1987.",
     NEW_FACTS["cairo"][0],
     "it repeats the flavor line nearly verbatim, so the back says Africa&rsquo;s-first "
     "twice; the Nile tunnels are a new story."),
    ("osaka", "fact 1", "REPEAT SWAP",
     "The Midosuji Line opened in 1933 as Japan&rsquo;s first municipally run subway.",
     NEW_FACTS["osaka"][0],
     "the flavor directly above already says Japan&rsquo;s oldest municipal subway; the "
     "vaulted-station story is new."),
    ("istanbul", "fact 2", "REPEAT SWAP",
     "Its lines run on both the European and Asian sides of the Bosphorus.",
     NEW_FACTS["istanbul"][1],
     "the flavor directly above already says a metro on two continents; the 1875 "
     "T&uuml;nel is the deeper cut."),
    ("nyc", "fact 2", "OPTIONAL",
     "Its 472 stations are the most of any single-operator metro in the world.",
     NYC_OPTIONAL,
     "the fact is officially TRUE, so under your bar it may stand; flagged only because "
     "it sits on a card whose plotted STATIONS reads 504 (Method explains the counting "
     "difference). The clarifier keeps the claim and softens the clash. Your call."),
]


# --------------------------------------------------------------------- board

def candidate_section(cid, title, oneliner, note, inner, dead=False):
    cls = f"iasec ia-{cid}" + (" iadead" if dead else "")
    return (f'<section class="{cls}" id="ia-{cid}">'
            f'<h2><span class="iatag">{cid.upper()}</span> {title}</h2>'
            f'<p class="iaone">{oneliner}</p>'
            f'<p class="ianote">{note}</p>{inner}</section>')


def main():
    bmc.load_content()
    meta = bmc.load_meta()
    alm = bmc.load_almanac()
    bmc.FX_DATE = alm["fx"]["date"]
    stats = bmc.stat_table(meta, alm)

    # ---- baseline: the three views today, current copy
    base_cells = []
    base_cells.append(cell(
        "VIEW 1 &middot; PLAY FRONT (default)",
        bar("PLAY", "ALMANAC", 0) + bmc.card_front(meta, stats, "seoul", deck=True),
        "play"))
    base_cells.append(cell(
        "VIEW 2 &middot; ALMANAC FRONT (deck toggle)",
        bar("PLAY", "ALMANAC", 1) + bmc.card_front(meta, stats, "seoul", deck=True),
        "almanac",
        "mid-scroll, nothing on the card says which set is showing"))
    base_cells.append(cell(
        "VIEW 3 &middot; LORE BACK (flip)",
        back_html("seoul", bmc.FLAVOR["seoul"], bmc.FACTS["seoul"]),
        "play",
        "the flavor line restates SPAN 146 km from view 1"))
    baseline = (
        '<section class="iasec ia-base"><h2>TODAY &middot; the three views as they ship</h2>'
        '<p class="ianote">Seoul, current copy. One card, three states: two front sets '
        'switched at deck level under placeholder names, plus the flip. The flags this '
        'round answers: do three views feel intuitive, and the lore copy sometimes '
        'restates the stats.</p>'
        f'<div class="iarow">{"".join(base_cells)}</div></section>')

    # ---- A: keep + rename
    a_groups = []
    for c in CITIES:
        flavor, facts = new_copy(c)
        cn = bmc.DISPLAY.get(c, c).upper()
        a_groups.append(
            f'<div class="iagroup"><div class="iagcap">{cn}</div><div class="iarow">'
            + cell("FRONT &middot; SCALE", bar("SCALE", "CHARACTER", 0,
                   "the battle and the daily play SCALE")
                   + bmc.card_front(meta, stats, c, deck=True), "play")
            + cell("FRONT &middot; CHARACTER", bar("SCALE", "CHARACTER", 1,
                   "the battle and the daily play SCALE")
                   + bmc.card_front(meta, stats, c, deck=True), "almanac")
            + cell("BACK (slim edits applied)", back_html(c, flavor, facts), "play")
            + '</div></div>')
    names_menu = """
    <div class="ianames">
      <div class="ianamecap">SET-NAME MENU &middot; the open pick</div>
      <table class="iatable">
        <tr><th>pair</th><th>for</th><th>against</th></tr>
        <tr><td class="iapick">SCALE &middot; CHARACTER <span class="iarecchip">REC</span></td>
            <td>describes the content of both sets: how big it is, what it is like; already on the table</td>
            <td>opened is age, not scale (a small stretch); both abstract nouns</td></tr>
        <tr><td>CORE &middot; CHARACTER</td>
            <td>CORE says which set the game plays, which is the real asymmetry</td>
            <td>names the role, not the content; CORE echoes the retired theme trio</td></tr>
        <tr><td>SYSTEM &middot; RIDE</td>
            <td>most concrete pair: the network vs what riding it is like</td>
            <td>ridership sits on the SYSTEM side while RIDE names the other; smells of the cut traveller layer</td></tr>
      </table>
    </div>"""
    sec_a = candidate_section(
        "a", "THE STANDING SHAPE &middot; keep the toggle, honest names",
        "Round-2 state: B and C were rejected at the gate (the strips read as "
        "ugly), and the character info stays on the cards, so the toggle stays. "
        "What changes: PLAY / ALMANAC become honest names (menu below, SCALE | "
        "CHARACTER mocked), each ledger carries its set caption so a scrolled "
        "deck still says which set is showing, and the bar whispers which set "
        "the game plays.",
        "Three views remain; the polish makes the third view legible instead of "
        "hidden. If fewer views ever matters more than on-card figures, the one "
        "remaining door is moving the second set off the cards to a Method "
        "table, which reverses D28 and is not recommended.",
        "".join(a_groups) + names_menu)

    # ---- B: two surfaces
    b_groups = []
    for c in CITIES:
        flavor, facts = new_copy(c)
        cn = bmc.DISPLAY.get(c, c).upper()
        b_groups.append(
            f'<div class="iagroup"><div class="iagcap">{cn}</div><div class="iarow">'
            + cell("FRONT &middot; the six play stats (no toggle anywhere)",
                   bmc.card_front(meta, stats, c), "play")
            + cell("BACK &middot; lore + the character figures",
                   back_html(c, flavor, facts, strip_html(stats, c)), "play",
                   "pinned to the live flip height (469px): the strip squeezes the diagram window from 178px to ~125px on Seoul, ~155px on Tokyo; judge that cost here")
            + '</div></div>')
    sec_b = candidate_section(
        "b", "TWO SURFACES &middot; REJECTED at the board gate (2026-06-12)",
        "The front toggle dies. The five character stats move to the lore back as a "
        "compact figure strip (small ordinals; 1st keeps the blue chip); the front is "
        "the six play stats the battle and the daily actually use.",
        "Owner verdict: the figures shoved onto the back ruined the card; the "
        "squeezed diagram window was the visible cost. Kept on the board for the "
        "record, per the mocks convention.",
        "".join(b_groups), dead=True)

    # ---- C: no modes
    c_groups = []
    for c in CITIES:
        flavor, facts = new_copy(c)
        cn = bmc.DISPLAY.get(c, c).upper()
        c_groups.append(
            f'<div class="iagroup"><div class="iagcap">{cn}</div><div class="iarow">'
            + cell("FRONT &middot; six rows + the character strip, always visible",
                   c_front(meta, stats, c), "play",
                   "measured: the face grows 469px to 567px (+98px); the battle arena&rsquo;s fixed 469px slots would retune, and the strip rides into battles too")
            + cell("BACK (deduped copy)", back_html(c, flavor, facts), "play")
            + '</div></div>')
    sec_c = candidate_section(
        "c", "NO MODES &middot; REJECTED at the board gate (2026-06-12)",
        "Both sets render at once: the six as the big ledger, the five as a "
        "fine-print strip above the foot. Nothing toggles; the deck has no hidden "
        "state at all.",
        "Owner verdict: the figures shoved onto the front ruined the card the "
        "same way. Kept for the record.",
        "".join(c_groups), dead=True)

    # ---- exhibit: before/after on the worst collision (B vehicle)
    old_mc = back_html("mexico city", bmc.FLAVOR["mexico city"],
                       bmc.FACTS["mexico city"], strip_html(stats, "mexico city"))
    nf, nfa = new_copy("mexico city")
    new_mc = back_html("mexico city", nf, nfa, strip_html(stats, "mexico city"))
    exhibit = (
        '<section class="iasec iadead"><h2>ROUND-1 EXHIBIT (record) &middot; before/after on the B back</h2>'
        '<p class="ianote">Mexico City on the B back (the adjacency makes it starkest; '
        'the same edits apply under every candidate). Left: today&rsquo;s copy puts '
        'the 5-peso fare in the flavor line while BASE FARE shows the same fare as '
        '$0.29, and fact 1 dates the pictograms to the year OPENED already shows. '
        'Right: the figures keep the numbers, the facts keep the stories.</p>'
        '<div class="iarow">'
        + cell("TODAY&rsquo;S COPY beside the figures", old_mc, "play")
        + cell("AFTER THE EDITS", new_mc, "play")
        + '</div></section>')

    # ---- overlap map
    rows = []
    for city, where, quote, hits, cls, note in OVERLAP:
        rows.append(
            f'<tr class="k-{cls}"><td>{bmc.DISPLAY.get(city, city)}</td>'
            f'<td>{where}</td><td class="iaq">&ldquo;{quote}&rdquo;</td>'
            f'<td>{hits}</td><td><span class="kchip k-{cls}">{KCLASS_LABEL[cls]}</span></td>'
            f'<td>{note}</td></tr>')
    n_fix = sum(1 for *_, cls, _n in OVERLAP if cls != K_KEEP)
    n_keep = sum(1 for *_, cls, _n in OVERLAP if cls == K_KEEP)
    overlap_sec = (
        '<section class="iasec"><h2>THE OVERLAP MAP &middot; all 18 lore backs vs the shown stats</h2>'
        f'<p class="ianote">Every flavor line and fact checked against the eleven '
        f'stats, the subtitle count and the rank chips: <b>{n_fix} overlaps</b> '
        f'found, <b>{n_keep} deliberate keeps</b>. <b>Round-2 bar (your verdict): '
        f'a line is fine if it is factually correct, original, and interesting on '
        f'its own.</b> Under that bar the RESTATES and SUBTITLE rows are tolerated '
        f'and act no further; only the CONTRADICTS rows (factual) and the '
        f'REPEATS-ITSELF rows (a wasted slot) feed the slim edit list above. Hong '
        f'Kong remains the model back: zero overlaps, and its 1910 fact exists to '
        f'explain a stat rather than restate it.</p>'
        '<table class="iatable iaoverlap"><tr><th>card</th><th>where</th><th>the line</th>'
        '<th>collides with</th><th>class</th><th>note</th></tr>'
        + "".join(rows) + '</table></section>')

    # ---- the slim edit list (round 2: readable, tiered)
    eitems = []
    for city, item, tier, old, new, why in SLIM_EDITS:
        tcls = {"MUST FIX": "t-must", "REPEAT SWAP": "t-swap",
                "OPTIONAL": "t-opt"}[tier]
        eitems.append(
            f'<div class="sled"><div class="sledh">'
            f'<span class="sledtier {tcls}">{tier}</span>'
            f'<span class="sledcity">{bmc.DISPLAY.get(city, city)}</span>'
            f'<span class="sleditem">{item}</span></div>'
            f'<div class="sledold">now&nbsp;&nbsp;&ldquo;{old}&rdquo;</div>'
            f'<div class="slednew">new&nbsp;&nbsp;&ldquo;{new}&rdquo;</div>'
            f'<div class="sledwhy">{why}</div></div>')
    edits_sec = (
        '<section class="iasec" id="ia-edits"><h2>THE SLIM EDIT LIST &middot; '
        '3 must-fixes + 7 repeat swaps + 1 your-call</h2>'
        '<p class="ianote"><b>Recalibrated to your bar</b> (factually correct, '
        'no copyright entanglement, interesting on its own). The round-1 list '
        'asked for 26 edits; under the bar, a fact restating a stat number is '
        'fine, so those all drop. What remains: <b>MUST FIX</b> = the line is '
        'factually wrong or fights the card&rsquo;s own figure; <b>REPEAT '
        'SWAP</b> = the back says the same thing twice, so one slot is wasted '
        'and gets a fresh story instead; <b>OPTIONAL</b> = correct as written, '
        'flagged for your call. On copyright: facts themselves are not '
        'copyrightable, every line below is phrased by us and verified against '
        'operator pages or Wikipedia (sources recorded in almanac.json), and no '
        'curated fact collection was copied. The licensed assets on the backs '
        'are the diagrams, credited verbatim. Nothing is applied yet.</p>'
        '<p class="ianote"><b>Watch-items for the pending second-set menu</b> (a '
        'separate session is researching candidates): Guangzhou&rsquo;s 160 km/h '
        'fact vs a possible top-speed stat; Moscow&rsquo;s 80-second record vs a '
        'headway stat; the New York flavor and Copenhagen fact 2 vs an hours '
        'stat. If those stats land, the lines beside them get the same '
        'must-fix/tolerate test.</p>'
        f'<div class="sleds">{"".join(eitems)}</div></section>')

    # ---- tradeoffs (round-1 record) + round-2 state
    trade = """
    <section class="iasec iadead"><h2>ROUND-1 TRADEOFF TABLE (record)</h2>
    <table class="iatable iatrade">
      <tr><th></th><th>A &middot; keep + rename</th><th>B &middot; two surfaces</th><th>C &middot; no modes</th></tr>
      <tr><td>views per card</td><td>3</td><td class="iapick">2</td><td>2</td></tr>
      <tr><td>the toggle</td><td>stays, renamed</td><td class="iapick">dies</td><td>dies</td></tr>
      <tr><td>set names</td><td>owner must pick a pair</td><td class="iapick">none needed in the UI</td><td>none needed</td></tr>
      <tr><td>character stats live</td><td>second front, full rows + chips</td><td>lore back, figure strip</td><td>front fine-print strip</td></tr>
      <tr><td>their rank chips</td><td>full ordinal chips</td><td>small ordinals, 1st in blue</td><td>small ordinals, 1st in blue</td></tr>
      <tr><td>scan the 2nd set across the deck</td><td class="iapick">yes, via the toggle</td><td>no; Method keeps the table</td><td class="iapick">yes, always visible</td></tr>
      <tr><td>back diagram window</td><td>unchanged (178px)</td><td>~112-155px (strip + copy length)</td><td>unchanged (178px)</td></tr>
      <tr><td>front height</td><td>unchanged</td><td class="iapick">unchanged</td><td>+98px on every card, battle arena retunes</td></tr>
      <tr><td>2nd-set growth headroom (menu pending)</td><td class="iapick">rows scale to ~7</td><td>strip fits 4-6 figures</td><td>strip caps ~5</td></tr>
      <tr><td>overlap structure</td><td>edits only; numbers half-hidden</td><td class="iapick">numbers and stories share a surface</td><td>edits only; densest face</td></tr>
      <tr><td>code cost</td><td>S (strings + caption)</td><td>M (front/back restructure, bar removal, Method)</td><td>M (front block + battle variant)</td></tr>
    </table>
    </section>"""

    rec2 = """
    <section class="iasec"><div class="iarec">
      <div class="iarecl">ROUND-2 STATE &middot; WHAT IS LEFT TO PICK</div>
      <p><b>Settled by your verdict:</b> B and C are dead (the strips ruined the
      card), the character set stays on the cards behind the toggle, and number
      restates in the lore are tolerated. The standing shape is the section at
      the top: today&rsquo;s three views with honest names, a set caption on the
      card, and a binding whisper on the bar.</p>
      <p class="iaverdict"><b>Two confirms ship the round:</b> (1) the set-name
      pair, SCALE | CHARACTER recommended, menu above; (2) the slim edit list,
      3 must-fixes + 7 repeat swaps, plus your call on the optional New York
      clarifier. On your yes both build into the live page and Method and get
      re-verified. The deck-of-18 ship gate (push / PR / merge) stays the
      separate yes already pending in STATUS.</p>
    </div></section>"""

    board_css = """
  body { padding: 0 22px 70px; }
  .iahead { max-width: 860px; margin: 28px auto 6px; }
  .iahead h1 { font-size: 16px; font-weight: 800; letter-spacing: .22em; color: var(--text); }
  .iahead h1 em { font-style: normal; color: var(--lblue); }
  .iahead p { font-size: 13px; color: var(--soft); line-height: 1.65; margin-top: 10px; }
  .iasec { max-width: 1180px; margin: 44px auto 0; }
  .iasec h2 { font-family: var(--mono); font-size: 12px; letter-spacing: .16em;
              color: var(--lblue); text-transform: uppercase; }
  .iatag { display: inline-block; background: var(--blue); color: #fff;
           border-radius: 3px; padding: 2px 7px; margin-right: 6px; }
  .iaone { font-size: 13px; color: var(--body); line-height: 1.6; margin: 9px 0 0; max-width: 860px; }
  .ianote { font-size: 12px; color: var(--soft); line-height: 1.6; margin: 7px 0 0; max-width: 860px; }
  .ianote b, .iaone b { color: var(--text); font-weight: 600; }
  .iarow { display: flex; flex-wrap: wrap; gap: 26px; padding: 20px 0 4px; align-items: flex-start; }
  .iagroup { margin-top: 6px; }
  .iagcap { font-family: var(--mono); font-size: 10px; letter-spacing: .22em;
            color: var(--grey); padding-top: 14px; }
  .iacell { width: 270px; display: flex; flex-direction: column; gap: 9px; }
  .iacap { font-family: var(--mono); font-size: 9.5px; letter-spacing: .12em; color: var(--grey); }
  .iacellnote { font-family: var(--mono); font-size: 9px; color: var(--faint); line-height: 1.55; }
  .iabar { padding: 0 0 2px; }
  /* pin one ledger per cell (the live page switches at deck level) */
  .iacell .cledger { display: none; }
  .iacell[data-set="play"] .cledger[data-set="play"],
  .iacell[data-set="almanac"] .cledger[data-set="almanac"] { display: block; }
  /* A: the set caption on the card, so a scrolled deck names its state */
  .ia-a .iacell[data-set="play"] .cledger[data-set="play"]::before { content: "SCALE"; }
  .ia-a .iacell[data-set="almanac"] .cledger[data-set="almanac"]::before { content: "CHARACTER"; }
  .ia-a .iacell .cledger::before {
    display: block; font-family: var(--mono); font-size: 9px;
    letter-spacing: .22em; color: var(--lblue); padding: 8px 1px 0; text-align: right;
  }
  /* the character figure strip (B back, C front) */
  .xstrip { display: flex; flex-wrap: wrap; margin-top: 9px;
            border-top: 1px solid var(--rowline); }
  .xcell { flex: 1 1 33%; min-width: 33%; padding: 6px 2px 5px;
           border-bottom: 1px solid var(--rowline); }
  .xlab { display: block; font-family: var(--mono); font-size: 9px;
          letter-spacing: .04em; color: var(--grey); white-space: nowrap; }
  .xv { display: block; font-family: var(--mono); font-size: 13px;
        color: var(--text); margin-top: 2px; white-space: nowrap; }
  .xv .xr { font-style: normal; font-size: 9px; color: var(--dim); margin-left: 5px; }
  .xv .xr1 { color: var(--lblue); font-weight: 500; }
  .xstrip.xfront { margin-top: 13px; }
  /* B backs at the live flip height: the front (469px) drives the flip box,
     so the back cannot grow; the diagram window absorbs the strip's cost. */
  .cback.bfit { height: 469px; min-height: 469px; }
  .cback.bfit .lart { height: auto; flex: 1 1 auto; min-height: 0; }
  .cback.bfit .lband { flex: 0 0 auto; }
  .xstrip.xfront .xcell { border-bottom: 0; }
  /* names + tables */
  .ianames { margin-top: 18px; }
  .ianamecap { font-family: var(--mono); font-size: 10px; letter-spacing: .16em; color: var(--grey); }
  .iatable { width: 100%; border-collapse: collapse; margin-top: 12px; }
  .iatable th { font-family: var(--mono); font-size: 9px; letter-spacing: .12em;
                color: var(--grey); text-transform: uppercase; text-align: left;
                padding: 6px 12px 6px 0; border-bottom: 1px solid var(--edge); }
  .iatable td { padding: 9px 12px 9px 0; border-bottom: 1px solid #1d1d23;
                vertical-align: top; color: var(--soft); font-size: 12px; line-height: 1.55; }
  .iapick { color: var(--text); font-weight: 600; }
  .iarecchip { font-family: var(--mono); font-size: 9px; letter-spacing: .1em;
               background: var(--blue); color: #fff; border-radius: 3px;
               padding: 2px 6px; margin-left: 7px; vertical-align: 1px; }
  .iaoverlap td:first-child { font-weight: 700; color: var(--body);
               text-transform: uppercase; font-size: 10.5px; white-space: nowrap; }
  .iaq { font-style: italic; color: var(--body); max-width: 300px; }
  .kchip { font-family: var(--mono); font-size: 9px; letter-spacing: .06em;
           border: 1px solid; border-radius: 3px; padding: 2px 6px; white-space: nowrap; }
  .k-contradicts .kchip, .kchip.k-contradicts { color: #e89a9a; border-color: #b85c5c; }
  .kchip.k-restates { color: #e0b97f; border-color: #c89a5a; }
  .kchip.k-internal { color: #d6d68a; border-color: #a8a85c; }
  .kchip.k-count { color: #9cc4ea; border-color: #5b9bd5; }
  .kchip.k-keep { color: var(--grey); border-color: var(--chipedge); }
  /* edit list */
  .iaedits { display: grid; grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
             gap: 16px; margin-top: 18px; }
  .iaedit { border: 1px solid var(--edge); border-radius: 8px; padding: 12px 14px;
            background: var(--chrome2); }
  .iaeh { font-family: var(--mono); font-size: 10px; letter-spacing: .14em; color: var(--lblue); }
  .iaeold, .iaenew { font-size: 12px; line-height: 1.55; margin-top: 8px; color: var(--dim); }
  .iaenew { color: var(--body); }
  .iaeold span, .iaenew span { font-family: var(--mono); font-size: 9px;
            letter-spacing: .12em; margin-right: 7px; color: var(--faint); }
  .iaenew span { color: var(--goodtext); }
  .iaewhy { font-family: var(--mono); font-size: 9px; color: var(--grey);
            line-height: 1.55; margin-top: 7px; }
  /* slim edit list (round 2) */
  .sleds { margin-top: 16px; max-width: 880px; }
  .sled { border-bottom: 1px solid var(--edge); padding: 13px 2px 12px; }
  .sledh { display: flex; align-items: baseline; gap: 10px; }
  .sledtier { font-family: var(--mono); font-size: 9px; letter-spacing: .08em;
              border: 1px solid; border-radius: 3px; padding: 2px 7px; white-space: nowrap; }
  .t-must { color: #e89a9a; border-color: #b85c5c; }
  .t-swap { color: #d6d68a; border-color: #a8a85c; }
  .t-opt  { color: var(--grey); border-color: var(--chipedge); }
  .sledcity { font-size: 13px; font-weight: 700; color: var(--body); text-transform: uppercase; letter-spacing: .05em; }
  .sleditem { font-family: var(--mono); font-size: 10px; color: var(--grey); }
  .sledold { font-size: 13px; color: var(--dim); line-height: 1.55; margin-top: 8px; }
  .slednew { font-size: 13px; color: var(--text); line-height: 1.55; margin-top: 4px; }
  .sledwhy { font-size: 11.5px; color: var(--grey); line-height: 1.55; margin-top: 6px; max-width: 800px; }
  /* rejected round-1 sections: kept for the record, dimmed */
  .iadead { opacity: .55; }
  .iadead h2 { color: var(--grey); }
  .iadead .iatag { background: var(--chipedge); }
  /* rec */
  .iarec { border: 1px solid #7fb0e855; border-radius: 10px; padding: 16px 20px;
           margin-top: 20px; background: var(--chrome2); max-width: 860px; }
  .iarecl { font-family: var(--mono); font-size: 10px; letter-spacing: .22em; color: var(--lblue); }
  .iarec p { font-size: 13px; color: var(--soft); line-height: 1.7; margin-top: 9px; }
  .iarec b { color: var(--text); }
  .iaverdict { border-top: 1px solid var(--edge); padding-top: 11px; }
"""

    page = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Metro Match &middot; card-IA board (D30)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/is/building/world-metros/style.css">
<style>{board_css}</style>
</head><body>
  <div class="iahead">
    <h1>METRO <em>MATCH</em> &middot; CARD-IA BOARD (D30)</h1>
    <p>ROUND 2, your verdict folded in: B and C (figures shoved onto the back
    or front) are rejected as ugly and kept below only as the record; the
    character info stays on the cards; and lore lines are judged by your bar,
    factually correct + no copyright entanglement + interesting on their own.
    What is live on this board: the standing shape (the toggle with honest
    names and small UX polish), the slim edit list it needs (3 must-fixes, 7
    repeat swaps, 1 your-call), and the overlap map as evidence. Nothing is
    applied to the live page yet.</p>
  </div>
  {baseline}
  {sec_a}
  {edits_sec}
  {overlap_sec}
  {sec_b}
  {sec_c}
  {exhibit}
  {trade}
  {rec2}
</body></html>
"""
    out = os.path.join(HERE, "card-ia-board.html")
    with open(out, "w") as fh:
        fh.write(page)
    print(f"wrote {out} ({os.path.getsize(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
