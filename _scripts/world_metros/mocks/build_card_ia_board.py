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
# The proposed post-dedup lore copy. Rule: a fact or flavor line never
# restates a number the card shows as a stat (or its subtitle count, or a
# deck-rank claim); the stories stay, the numbers live in the ledgers.
# Cities absent here keep their current line unchanged.

NEW_FLAVOR = {
    "tokyo": "Run so tightly that a five-minute delay comes with a certificate.",
    "seoul": "One network from the mountains north of the city to the Yellow Sea coast.",
    "singapore": "Spotless, sealed and air-conditioned from gate to gate.",
    "paris": "Almost nowhere in Paris is more than a few minutes&rsquo; walk from a M&eacute;tro entrance.",
    "shanghai": "The whole system is younger than many of its riders.",
    "beijing": "Ring lines inside ring lines, tracking the city&rsquo;s ring roads outward.",
    "london": "Still called the Tube, after the shape of its deep tunnels.",
    "madrid": "Dug fast and cheap, by a method other cities came to copy.",
    "moscow": "Trains so frequent the platform clock counts up from the last one, not down to the next.",
    "copenhagen": "The trains drive themselves; the staff ride along with everyone else.",
    "delhi": "Built at a pace no metro had managed before, and it pays its own way.",
    "guangzhou": "New lines open here almost every year; the printed maps can barely keep up.",
    "mexico city": "Trains ride on rubber tires, quieter and softer than steel.",
    "cairo": "Africa&rsquo;s first metro, and still its hardest-working.",
    "istanbul": "A metro on two continents, with the Bosphorus in between.",
}

NEW_FACTS = {  # only the changed slots; None = keep current
    "tokyo": [None, "G is for Ginza: the letter marks Asia&rsquo;s first metro line."],
    "paris": ["Built for the World&rsquo;s Fair; Line 1 still runs the route it opened with.", None],
    "shanghai": [None, "The newest lines run with no driver aboard at all."],
    "beijing": ["China&rsquo;s first subway, built as a Cold War defence project; Zhou Enlai rode the first train.", None],
    "nyc": [None, "The ornate original City Hall station survives as a ghost stop the 6 train still loops through."],
    "madrid": [None, "Chamber&iacute; station, bypassed in the 1960s, survives as a time-capsule museum of the original metro."],
    "copenhagen": ["With no cab up front, the front-window seats are the most fought-over on the train.", None],
    "mexico city": ["Every station has its own pictogram, designed so riders could navigate without reading.", None],
    "cairo": ["Line 2 runs beneath the Nile itself, through twin tunnels bored under the riverbed.", None],
    "osaka": ["Midosuji&rsquo;s first stations were built like vaults, with high arched ceilings and chandeliers.", None],
    "istanbul": [None, "Istanbul has run an underground railway since 1875: the two-stop T&uuml;nel funicular."],
}


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

EDITS = [
    # (city, item, old, new, why)
    ("tokyo", "flavor", "Thirteen lines, two operators, one grid.",
     NEW_FLAVOR["tokyo"],
     "the subtitle already counts the lines; the delay certificate is the better story"),
    ("tokyo", "fact 2", "G is for Ginza: Asia&rsquo;s first metro line, opened 1927.",
     NEW_FACTS["tokyo"][1], "drop the year; OPENED carries 1927"),
    ("seoul", "flavor", "146 km between its furthest stations, the deck&rsquo;s longest reach.",
     NEW_FLAVOR["seoul"], "SPAN and its 1ST chip carry both the number and the claim"),
    ("singapore", "flavor", "Six lines, four of them driverless, none older than 1987.",
     NEW_FLAVOR["singapore"],
     "must change in any candidate: it contradicts DRIVERLESS 6 and restates the count and OPENED"),
    ("paris", "flavor", "1.35 stations per square km, the deck&rsquo;s tightest grid.",
     NEW_FLAVOR["paris"], "DENSITY carries the number; the walk claim is the lived version"),
    ("paris", "fact 1", "Opened for the 1900 World&rsquo;s Fair; Line 1 still runs the route it opened with.",
     NEW_FACTS["paris"][0], "drop the year; OPENED carries 1900"),
    ("shanghai", "flavor", "From first train to 800 route-km inside three decades.",
     NEW_FLAVOR["shanghai"], "ROUTE-KM carries the number; the age story stays"),
    ("shanghai", "fact 2", "Five lines run driverless, about 169 km of unattended metro.",
     NEW_FACTS["shanghai"][1],
     "must change in any candidate: the fact says 5 where the stat says 7"),
    ("beijing", "flavor", "909 route-km under one operator, the deck&rsquo;s biggest single system.",
     NEW_FLAVOR["beijing"], "ROUTE-KM carries the number; the ring structure is the better story"),
    ("beijing", "fact 1", "China&rsquo;s first subway, built as a Cold War defence project; Zhou Enlai rode the first train in 1969.",
     NEW_FACTS["beijing"][0], "drop the year; OPENED carries 1969"),
    ("london", "flavor", "Underground since 1863, before anyone else tried.",
     NEW_FLAVOR["london"], "OPENED and its 1ST chip say it; the Tube name is the lore"),
    ("nyc", "fact 2", "Its 472 stations are the most of any single-operator metro in the world.",
     NEW_FACTS["nyc"][1],
     "472 fights the plotted 504 on the same card; City Hall is the richer story"),
    ("madrid", "flavor", "172 km of new metro in sixteen years, Europe&rsquo;s great expansion.",
     NEW_FLAVOR["madrid"], "fact 1 tells the expansion in full; the method story replaces it"),
    ("madrid", "fact 2", "Chamber&iacute; station, bypassed in the 1960s, survives as a time-capsule museum of the 1919 metro.",
     NEW_FACTS["madrid"][1], "drop the year; OPENED carries 1919"),
    ("moscow", "flavor", "Marble, mosaics and a train every 90 seconds.",
     NEW_FLAVOR["moscow"],
     "fact 1 owns the palaces, fact 2 owns the record; the count-up clock is its own story"),
    ("copenhagen", "flavor", "Four lines, zero drivers, all night.",
     NEW_FLAVOR["copenhagen"], "the subtitle counts the lines; fact 2 owns the all-night claim"),
    ("copenhagen", "fact 1", "Every train has run driverless since the first one in 2002.",
     NEW_FACTS["copenhagen"][0],
     "&ldquo;every train&rdquo; is DRIVERLESS 4-of-4 and 2002 is OPENED; the front-window seats are the story"),
    ("delhi", "flavor", "374 route-km in barely two decades, and it pays its own way.",
     NEW_FLAVOR["delhi"], "ROUTE-KM carries the number; pace and farebox pride stay"),
    ("guangzhou", "flavor", "From a 5 km starter line in 1997 to 780 km today.",
     NEW_FLAVOR["guangzhou"], "OPENED and ROUTE-KM carry both numbers; growth stays as the story"),
    ("mexico city", "flavor", "A pictogram for every station, a 5-peso fare for every ride.",
     NEW_FLAVOR["mexico city"],
     "the peso figure is BASE FARE&rsquo;s local value; pictograms already lead fact 1; rubber tires are the unused signature"),
    ("mexico city", "fact 1", "Every station has its own pictogram, a 1969 design for navigating without reading.",
     NEW_FACTS["mexico city"][0], "drop the year; OPENED carries 1969"),
    ("cairo", "flavor", "Africa&rsquo;s first metro, opened 1987, still its workhorse.",
     NEW_FLAVOR["cairo"], "drop the year; OPENED carries 1987"),
    ("cairo", "fact 1", "Africa&rsquo;s and the Middle East&rsquo;s first metro, opened 1987.",
     NEW_FACTS["cairo"][0],
     "it repeated the flavor and the stat; the Nile tunnels are a new story"),
    ("osaka", "fact 1", "The Midosuji Line opened in 1933 as Japan&rsquo;s first municipally run subway.",
     NEW_FACTS["osaka"][0],
     "the flavor already says oldest municipal and OPENED carries 1933; the vault stations are new"),
    ("istanbul", "flavor", "A metro on two continents, and one of the world&rsquo;s fastest-growing.",
     NEW_FLAVOR["istanbul"],
     "&ldquo;fastest-growing&rdquo; reads against the shown 4th on NEW SINCE &rsquo;16; the continents stay here"),
    ("istanbul", "fact 2", "Its lines run on both the European and Asian sides of the Bosphorus.",
     NEW_FACTS["istanbul"][1],
     "the flavor owns the continents now; the 1875 T&uuml;nel is the deeper cut"),
]


# --------------------------------------------------------------------- board

def candidate_section(cid, title, oneliner, note, inner):
    return (f'<section class="iasec ia-{cid}" id="ia-{cid}">'
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
            + cell("BACK (deduped copy)", back_html(c, flavor, facts), "play")
            + '</div></div>')
    names_menu = """
    <div class="ianames">
      <div class="ianamecap">SET-NAME MENU (A only; B and C need no names in the UI)</div>
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
        "a", "KEEP + RENAME &middot; three views, honest names",
        "Two front sets and the flip stay; PLAY / ALMANAC become SCALE / CHARACTER "
        "(menu below); the bar gains a binding whisper; each ledger carries its set "
        "caption so a scrolled deck still says which set is showing.",
        "Smallest change. The toggle and the deck-wide scan of the second set both "
        "survive; the cost is that the card keeps a hidden state, and the lore "
        "dedup must police both fronts forever.",
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
        "b", "TWO SURFACES &middot; front for play, back for lore",
        "The front toggle dies. The five character stats move to the lore back as a "
        "compact figure strip (small ordinals; 1st keeps the blue chip); the front is "
        "the six play stats the battle and the daily actually use.",
        "A card has two sides; this uses exactly two. The set-name problem "
        "dissolves (no toggle to label), and numbers and stories share one surface, "
        "so the dedup division (figures carry numbers, facts carry stories) polices "
        "itself. Costs: no deck-wide scan of the second set (Method keeps the full "
        "table), figure ranks demote to small ordinals, and the diagram window narrows on long-copy backs (Mexico City, the wordiest, drops to ~112px; the alternative lever is letting the flip box size to the taller face, which grows those cards instead).",
        "".join(b_groups))

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
        "c", "NO MODES &middot; everything on the face",
        "Both sets render at once: the six as the big ledger, the five as a "
        "fine-print strip above the foot. Nothing toggles; the deck has no hidden "
        "state at all.",
        "Maximum discoverability (a visitor who never finds a toggle still sees "
        "everything) and the second set stays deck-scannable. Costs: the V1 "
        "big-ledger calm dies into an 11-figure face, every card grows, and the "
        "strip rides into the battle arena too.",
        "".join(c_groups))

    # ---- exhibit: before/after on the worst collision (B vehicle)
    old_mc = back_html("mexico city", bmc.FLAVOR["mexico city"],
                       bmc.FACTS["mexico city"], strip_html(stats, "mexico city"))
    nf, nfa = new_copy("mexico city")
    new_mc = back_html("mexico city", nf, nfa, strip_html(stats, "mexico city"))
    exhibit = (
        '<section class="iasec"><h2>THE DEDUP, BEFORE AND AFTER &middot; the worst collision</h2>'
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
        f'stats, the subtitle count and the rank chips: <b>{n_fix} collisions</b> '
        f'(three of them outright contradictions) and <b>{n_keep} deliberate '
        f'keeps</b> where a number near a stat is doing real story work. Hong Kong '
        f'is the model back: zero collisions, and its 1910 fact exists to explain a '
        f'stat rather than restate it.</p>'
        '<table class="iatable iaoverlap"><tr><th>card</th><th>where</th><th>the line</th>'
        '<th>collides with</th><th>class</th><th>note</th></tr>'
        + "".join(rows) + '</table></section>')

    # ---- edit list
    eitems = []
    for city, item, old, new, why in EDITS:
        eitems.append(
            f'<div class="iaedit"><div class="iaeh">{bmc.DISPLAY.get(city, city).upper()}'
            f' &middot; {item}</div>'
            f'<div class="iaeold"><span>OLD</span>{old}</div>'
            f'<div class="iaenew"><span>NEW</span>{new}</div>'
            f'<div class="iaewhy">{why}</div></div>')
    edits_sec = (
        '<section class="iasec"><h2>THE EDIT LIST &middot; 26 edits across 17 cards '
        '(Hong Kong untouched)</h2>'
        '<p class="ianote"><b>The list is the same under A, B and C</b>: every '
        'candidate keeps all eleven numbers somewhere on the card, so a fact that '
        'restates one is redundant in every IA. What changes is where the collision '
        'sits: under A the restated number hides behind a toggle; under B the figure '
        'sits beside the fact (the strip becomes the number, the fact becomes its '
        'caption); under C everything shares the face. Nothing below is applied '
        'yet; these ship with whichever candidate wins.</p>'
        '<p class="ianote"><b>Watch-items for the pending second-set menu</b> (a '
        'separate session is researching candidates): Guangzhou&rsquo;s 160 km/h '
        'fact vs a possible top-speed stat; Moscow&rsquo;s 80-second record vs a '
        'headway stat; the New York flavor and Copenhagen fact 2 vs an hours stat; '
        'Osaka&rsquo;s &ldquo;driverless since 1981&rdquo; wording vs its source '
        'dating GoA4 to 1991. Re-run this dedup pass against the final set before '
        'it ships.</p>'
        f'<div class="iaedits">{"".join(eitems)}</div></section>')

    # ---- tradeoffs + rec
    trade = """
    <section class="iasec"><h2>TRADEOFFS + RECOMMENDATION</h2>
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
    <div class="iarec">
      <div class="iarecl">RECOMMENDATION</div>
      <p><b>B &middot; two surfaces.</b> It answers all three flags at once: three
      views become a card&rsquo;s natural two; the disliked set names stop existing
      rather than getting better; and the overlap stops being a policing problem
      because the figures and the facts share the lore surface (the strip carries
      the numbers, the facts carry the stories). It also restores the ratified D18
      grammar, front for play, back for lore: the battle and the daily never used
      the second set, so it was always lore wearing a play costume. The honest
      costs sit above: the deck-wide fare scan moves to Method, the figure ranks
      shrink to ordinals, and the diagram window pays for the strip (178px down
      to ~125px on the Seoul back; ~112px on wordy Mexico City; judge those
      two backs above). Fallback if that scan or the bigger diagram matters
      more: <b>A with SCALE &middot; CHARACTER</b>.</p>
      <p class="iaverdict"><b>Your verdict:</b> pick A (plus a name pair), B, or C.
      The dedup edit list ships with any of them; then the pick gets built into the
      live page and Method and re-verified. The deck-of-18 ship gate (push / PR /
      merge) stays the separate yes already pending in STATUS.</p>
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
    <p>Your flag: the card has three views (play front, almanac front via the
    deck toggle, lore-back flip) and they may not be the intuitive shape; the
    almanac figures and the lore copy sometimes say the same thing. This board
    answers both: three IA candidates on real cards (Seoul the busy case, Tokyo
    the reference), then the full 18-card overlap map and the dedup edit list
    that ships with whichever candidate wins. Nothing is applied to the live
    page yet.</p>
  </div>
  {baseline}
  {sec_a}
  {sec_b}
  {sec_c}
  {exhibit}
  {overlap_sec}
  {edits_sec}
  {trade}
</body></html>
"""
    out = os.path.join(HERE, "card-ia-board.html")
    with open(out, "w") as fh:
        fh.write(page)
    print(f"wrote {out} ({os.path.getsize(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
