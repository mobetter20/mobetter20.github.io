#!/usr/bin/env python3
"""Metro Match page generator (the D17 card pivot at its D20-resolved state).

Generates is/building/world-metros/index.html: THE DECK (12 cards in roster
order, three live with flip-to-lore backs, nine "soon" slots), THE BATTLE
(vs cpu, pick-a-stat, first to 3), THE DAILY (one guess a day, streak in
localStorage) and METHOD (scopes, definitions, sources, licences, why-not).

Design state baked in:
  - D18 card grammar: game-first front, familiar diagram on the lore back,
    pinstripe deck back as the game-hidden state.
  - D19 treatment C: ink-dark card #1b1b21 on near-black table #0f0f12.
  - D20 V1 big ledger: bold near-white stat label leading each row, jumbo
    mono value right, deck-rank chip; lines swapped for density; line count
    + scope tag beside the pills; 2-3 curated facts on lore backs.
  - D21 name: Metro Match (ratified); scope: rider-scope (B), binds at the
    roster scale-up.

Stats come from the committed assets/meta.json snapshot (never fetched);
diagram attributions are VERBATIM from DIAGRAM-LEDGER.md. style.css and
app.js are hand-maintained siblings; only index.html is generated.

Usage:
    python3 _scripts/world_metros/build_metro_cards.py
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PAGE = os.path.join(REPO, "is", "building", "world-metros")
ASSETS = os.path.join(PAGE, "assets")

# Roster order = deck order (established at the D16 gallery board; Paris 09).
ROSTER = ["shanghai", "tokyo", "seoul", "hong kong", "singapore", "delhi",
          "moscow", "london", "paris", "nyc", "mexico city", "cairo"]
LIVE = ["seoul", "paris", "tokyo"]  # battle/daily availability order

DISPLAY = {"nyc": "new york"}  # card face shows the city, not the acronym

SYSTEM = {
    "seoul": "Seoul Metropolitan Subway",
    "paris": "Métro de Paris",
    "tokyo": "Tokyo Metro + Toei",
}
OPENED = {"seoul": 1974, "paris": 1900, "tokyo": 1927}
EPITHET = {"seoul": "the sprawl", "paris": "the mesh", "tokyo": "the two crews"}

# Line count + scope tag beside the pills (D20 ratified default: pills never
# silently claim completeness).
SCOPE_TAG = {"seoul": "2–9 shown", "paris": "full Métro", "tokyo": "Metro + Toei"}
EXPECTED_LINE_COUNT = {"seoul": 8, "paris": 16, "tokyo": 13}

FLAVOR = {
    "seoul": "58 km between its furthest stations, the deck’s longest reach.",
    "paris": "1.1 stations per square km, the deck’s tightest grid.",
    "tokyo": "Thirteen lines, two operators, one grid.",
}

# 2-3 curated "why it's interesting" facts per lore back (D20 ratified
# default; the D2 profile-card content, evergreen, no traveller-utility).
# Two per back: the scope/through-running point lives on Method, not here.
FACTS = {
    "seoul": [
        "Line 2 is a 48 km loop around the city; trains circle it all day.",
        "Many stations double as underground arcades; a few anchor whole malls.",
    ],
    "paris": [
        "Opened for the 1900 World&rsquo;s Fair; Line 1 still runs the route it opened with.",
        "In central Paris you are rarely more than 500 m from a Métro entrance.",
    ],
    "tokyo": [
        "Two operators share one grid: Tokyo Metro runs nine lines, Toei runs four.",
        "G is for Ginza: Asia&rsquo;s first metro line, opened 1927.",
    ],
}

# Attribution strings VERBATIM from DIAGRAM-LEDGER.md per-city stanzas.
CREDIT = {
    "seoul": "“Seoul Metropolitan Subway network map” by Satellizer, "
             "Wikimedia Commons, CC BY-SA 4.0",
    "tokyo": "“Tokyo Subway Linemap” by Yveltal, Wikimedia Commons, CC BY-SA 4.0",
    "paris": "“Carte Métro de Paris” by Rigil, Wikimedia Commons, CC BY 3.0",
}
# Currency caveats where the ledger flags them.
CAVEAT = {"seoul": "diagram dated 2023, future lines as then planned"}

# The nine pipeline cities: chosen-diagram licence from the DIAGRAM-LEDGER
# summary (each lore back is already sourced and licence-verified).
LEDGER_LICENSE = {
    "shanghai": "CC BY-SA 4.0", "hong kong": "public domain",
    "singapore": "CC BY-SA 3.0", "delhi": "CC BY-SA 4.0",
    "moscow": "CC BY-SA 4.0", "london": "CC BY-SA 4.0",
    "nyc": "CC BY-SA 3.0", "mexico city": "CC BY-SA 4.0", "cairo": "CC0",
}

ORDINAL = {1: "1st", 2: "2nd", 3: "3rd"}


def load_meta():
    with open(os.path.join(ASSETS, "meta.json")) as fh:
        return json.load(fh)


def density(c):
    return c["stations"] / (c["w_km"] * c["h_km"])


def stat_table(meta):
    """The six D20 stats. Four live (value+rank), two pipeline slots.
    win: 'low' = earlier/smaller wins, 'high' = larger wins."""
    c = meta["cities"]
    live = [
        ("opened", "", "low", {k: OPENED[k] for k in LIVE},
         {k: str(OPENED[k]) for k in LIVE}),
        ("stations", "", "high", {k: c[k]["stations"] for k in LIVE},
         {k: str(c[k]["stations"]) for k in LIVE}),
        ("span", "km", "high", {k: c[k]["span_km"] for k in LIVE},
         {k: f'{c[k]["span_km"]:.1f}' for k in LIVE}),
        ("density", "st/km²", "high", {k: density(c[k]) for k in LIVE},
         {k: f"{density(c[k]):.2f}" for k in LIVE}),
    ]
    out = []
    for key, unit, win, values, disp in live:
        ranks = {}
        order = sorted(values.values(), reverse=(win == "high"))
        for k in LIVE:
            ranks[k] = order.index(values[k]) + 1
        out.append({"key": key, "unit": unit, "win": win,
                    "values": values, "disp": disp, "ranks": ranks})
    return out


def pills_html(meta, city):
    lines = meta["cities"][city]["lines"]
    assert len(lines) == EXPECTED_LINE_COUNT[city], \
        f"{city}: {len(lines)} lines in meta.json, expected {EXPECTED_LINE_COUNT[city]}"
    segs = "".join(f'<i style="background:{l["color"]}">{l["ref"]}</i>'
                   for l in lines)
    compact = " compact" if len(lines) > 12 else ""
    tag = f"{len(lines)} lines · {SCOPE_TAG[city]}"
    # tag on its own line below the pills: with 16 refs it would clip if it
    # rode the wrapping pill row.
    return (f'<div class="cpills{compact}">{segs}</div>'
            f'<div class="ctag">{tag}</div>')


def card_foot(meta):
    return (f'<div class="cfoot">data: OSM snapshot {meta["as_of"]} · ODbL · '
            f'ranks: live deck of {len(LIVE)} · density: bbox basis</div>')


def chip(rank):
    cls = "crk crk1" if rank == 1 else "crk"
    return f'<span class="{cls}">{ORDINAL[rank]}</span>'


def card_front(meta, stats, city, battle=False):
    """The play side. battle=True renders the four live rows as buttons."""
    deck_no = f"{ROSTER.index(city) + 1:02d}"
    rows = []
    for s in stats:
        rank, val, unit = s["ranks"][city], s["disp"][city], s["unit"]
        unit_html = f"<small> {unit}</small>" if unit else ""
        inner = (f'{chip(rank)}<span class="clab">{s["key"]}</span>'
                 f'<span class="cval">{val}{unit_html}</span>')
        if battle:
            rows.append(f'<button type="button" class="crow" '
                        f'data-stat="{s["key"]}">{inner}</button>')
        else:
            rows.append(f'<div class="crow" data-stat="{s["key"]}">{inner}</div>')
    # route-km + ridership are hidden until they carry scope-matched, dated
    # figures (D21 owner call: a reported figure has to match the card's
    # declared scope, and Seoul's scope is the open freeze). They return at
    # the roster scale-up; Method still documents them as the six-stat model.
    return (f'<article class="card cfront" '
            f'aria-label="{DISPLAY.get(city, city)}, {EPITHET[city]}, card {deck_no} of 12">'
            f'<div class="chead"><div class="cid">'
            f'<div class="cname">{DISPLAY.get(city, city)}</div>'
            f'<div class="cepi">{EPITHET[city]}</div></div>'
            f'<div class="cno">{deck_no}/12</div></div>'
            f'{pills_html(meta, city)}'
            f'<div class="cledger">{"".join(rows)}</div>'
            f'{card_foot(meta)}</article>')


def card_back(city):
    """The lore side: the familiar diagram, credited, plus the curated facts."""
    facts = "".join(f'<div class="lfact">{f}</div>' for f in FACTS[city])
    credit = CREDIT[city]
    caveat = (f'<div class="lcaveat">{CAVEAT[city]}</div>'
              if city in CAVEAT else "")
    return (f'<article class="card cback" aria-label="{DISPLAY.get(city, city)} lore side">'
            f'<div class="lart"><img data-src="assets/{city}-diagram.svg" '
            f'alt="{SYSTEM[city]} network diagram, a Wikimedia Commons recreation of '
            f'the map riders see"></div>'
            f'<div class="lband"><div class="lname">{DISPLAY.get(city, city)}</div>'
            f'<div class="lsys">{SYSTEM[city]}</div>'
            f'<div class="lflavor">{FLAVOR[city]}</div>'
            f'<div class="lfacts">{facts}</div>'
            f'<div class="lcredit">{credit}{caveat}</div></div></article>')


def card_deck_back(meta, label_id=""):
    """The uniform pinstripe back: the opponent's hidden card in the battle."""
    colours = [l["color"] for city in LIVE for l in meta["cities"][city]["lines"]]
    stripes = "".join(f'<i style="background:{c}"></i>' for c in colours)
    ident = f' id="{label_id}"' if label_id else ""
    return (f'<div class="card cdeckback"{ident} role="img" '
            f'aria-label="Face-down card: the Metro Match deck back">'
            f'<div class="pinstripes">{stripes}</div>'
            f'<div class="backband"><div class="backmark">METRO MATCH</div>'
            f'<div class="backsub">twelve systems · one deck</div></div></div>')


def card_soon(city):
    deck_no = f"{ROSTER.index(city) + 1:02d}"
    name = DISPLAY.get(city, city)
    return (f'<div class="card csoon" aria-label="{name}, card {deck_no} of 12, '
            f'in the pipeline">'
            f'<div class="chead"><div class="cid"><div class="cname">{name}</div>'
            f'</div><div class="cno">{deck_no}/12</div></div>'
            f'<div class="soonmid"><span class="soonchip">SOON</span></div>'
            f'<div class="cfoot">diagram sourced · {LEDGER_LICENSE[city]}</div></div>')


def deck_grid(meta, stats):
    cells = []
    for city in ROSTER:
        if city in LIVE:
            cells.append(
                f'<div class="cardunit">'
                f'<div class="flipbox" data-city="{city}">'
                f'<div class="flipinner">'
                f'<div class="face">{card_front(meta, stats, city)}</div>'
                f'<div class="face backface" aria-hidden="true">{card_back(city)}</div>'
                f'</div></div>'
                f'<button type="button" class="flipbtn" data-city="{city}" '
                f'aria-pressed="false">FLIP · LORE SIDE</button>'
                f'</div>')
        else:
            cells.append(f'<div class="cardunit">{card_soon(city)}'
                         f'<span class="flipbtn ghost" aria-hidden="true">'
                         f'IN THE PIPELINE</span></div>')
    return "".join(cells)


def battle_panel(meta, stats):
    you = "".join(
        f'<div class="bcardwrap" id="you-{c}" hidden>{card_front(meta, stats, c, battle=True)}</div>'
        for c in LIVE)
    cpu = "".join(
        f'<div class="bcardwrap" id="cpu-{c}" hidden>{card_front(meta, stats, c)}</div>'
        for c in LIVE)
    return f"""
    <div class="arena">
      <div class="bcol">
        <div class="bcap">YOU · PICK A STAT</div>
        <div class="bslot" id="you-slot">{you}</div>
      </div>
      <div class="bmid">
        <div class="bround" id="b-round">ROUND 1</div>
        <div class="bprompt" id="b-prompt">pick the stat you think wins</div>
        <div class="bresult" aria-live="polite">
          <div class="bcall" id="b-call" hidden></div>
          <div class="bnums" id="b-nums" hidden></div>
        </div>
        <div class="bscore" id="b-score">you 0 · cpu 0 · first to 3</div>
        <button type="button" class="bnext" id="b-next" hidden>NEXT ROUND</button>
        <button type="button" class="bnext" id="b-again" hidden>PLAY AGAIN</button>
        <div class="bfine">pick the stat you think beats the hidden card</div>
      </div>
      <div class="bcol">
        <div class="bcap">CPU · FACE DOWN</div>
        <div class="bslot bflip" id="cpu-slot">
          <div class="bflipinner" id="cpu-flip">
            <div class="bface">{card_deck_back(meta)}</div>
            <div class="bface bfaceup" id="cpu-front">{cpu}</div>
          </div>
        </div>
      </div>
    </div>"""


def daily_panel():
    return """
    <div class="dailywrap">
      <div class="dailybox">
        <div class="dhead">THE DAILY · <span id="d-date"></span></div>
        <div class="dstat" id="d-stat"></div>
        <div class="dq" id="d-q">Which plots more stations?</div>
        <div class="dchoices">
          <button type="button" class="dchoice" id="d-a">
            <span class="dname"></span>
            <span class="dpills" aria-hidden="true"></span>
            <span class="dmeta">?</span></button>
          <span class="dvs">vs</span>
          <button type="button" class="dchoice" id="d-b">
            <span class="dname"></span>
            <span class="dpills" aria-hidden="true"></span>
            <span class="dmeta">?</span></button>
        </div>
        <div class="dverdict" id="d-verdict" tabindex="-1" aria-live="polite" hidden></div>
        <div class="dstreak" id="d-streak"></div>
        <div class="dnote">one guess a day, and the stat rotates: opened,
        stations, span, density. The streak lives in this browser; counts
        are plotted from the dated OSM snapshot. Live deck of three, the
        pool deepens as cards land.</div>
      </div>
    </div>"""


def method_panel(meta, stats):
    credits = "".join(f'<p class="credit">{CREDIT[c]}</p>' for c in LIVE)
    return f"""
    <div class="method">
      <h2>The game</h2>
      <p><b>The battle.</b> You hold a card face up; the cpu holds one face
      down. Pick the stat you think wins; the cards compare, and the round
      goes to the better number. First to three rounds takes the match.</p>
      <p><b>The daily.</b> One question a day, one guess, and a streak that
      lives in your browser. Nothing leaves the page.</p>
      <p><b>Win directions are fixed.</b> Opened wins earlier; stations,
      span, density, route-km and ridership win larger.</p>

      <h2>The six stats</h2>
      <table>
        <tr><th>stat</th><th>what it measures</th><th>wins</th></tr>
        <tr><td>opened</td><td>earliest regular passenger service within the
        card&rsquo;s declared scope, from operator histories, dated</td>
        <td>earlier</td></tr>
        <tr><td>stations</td><td>station complexes plotted from the frozen
        snapshot; interchanges counted once</td><td>more</td></tr>
        <tr><td>span</td><td>the furthest-stations distance: the geodesic
        between the two stations farthest apart, computed</td><td>more</td></tr>
        <tr><td>density</td><td>stations per square km of network extent;
        bounding-box basis today, convex-hull basis when the pipeline
        lands</td><td>more</td></tr>
        <tr><td>route-km</td><td>reported route length, dated and sourced
        (almanac grade; in the pipeline)</td><td>more</td></tr>
        <tr><td>ridership</td><td>reported annual ridership, dated and
        sourced (almanac grade; in the pipeline)</td><td>more</td></tr>
      </table>
      <p>Ranks are computed across the live deck of {len(LIVE)}; the full
      deck of 12 takes over at the pipeline stage. Missing evidence renders
      <b>Unknown</b>, never zero, and Unknown sits out battles.</p>

      <h2>Scope: what a card counts</h2>
      <p>Each card declares its scope as <b>the network its city&rsquo;s own
      familiar map draws</b>: the rider&rsquo;s network, not one
      operator&rsquo;s books (ratified 2026-06-12; lands fully at the roster
      scale-up).</p>
      <p>Today&rsquo;s three cards: <b>Seoul</b> shows lines 2–9; the full
      Capital Area network, with its long shared-track corridors, is the
      pipeline&rsquo;s hard scope question and gets its entry here when
      frozen. <b>Paris</b> is the Métro proper, lines 1–14 plus 3bis and
      7bis; RER excluded. <b>Tokyo</b> is Tokyo Metro plus Toei,
      through-running truncated at the scope boundary.</p>
      <p>The pills on every card carry a line count and a scope tag, so the
      card never silently claims completeness.</p>

      <h2>Sources and dates</h2>
      <p>Geometry and station counts: OpenStreetMap, via the subway
      preprocessor CDN, snapshot {meta["as_of"]}, ODbL. The page is built
      offline from committed snapshots; raw GeoJSON never ships here.</p>
      <p>Opened years: operator histories; per-line dated sourcing arrives
      with the pipeline. Route-km and annual ridership: reported figures,
      almanac grade; they appear when they can carry a source and an as-of
      date, and until then their rows read <b>pipeline</b>, never zero.</p>

      <h2>The diagrams on the backs</h2>
      <p>The lore side of each card carries the diagram riders actually see,
      as a Wikimedia Commons recreation, credited on the card:</p>
      {credits}
      <p class="credit">Seoul&rsquo;s diagram is dated 2023 and draws future
      lines as then planned.</p>
      <p>Official schematic artwork appears nowhere on this site: the major
      operators enforce copyright on their map artwork, so the
      long-maintained Commons recreations are the legal route to the
      familiar map. The nine pipeline cities are already sourced and
      licence-verified the same way.</p>

      <h2>Why twelve, and why not Beijing</h2>
      <p>The deck is twelve category-defining systems, not a top-N:
      Shanghai, Tokyo, Seoul, Hong Kong, Singapore, Delhi, Moscow, London,
      Paris, New York, Mexico City, Cairo. <b>Beijing stays out
      deliberately</b>: Shanghai holds the China-mega seat, and a deck of
      every mega-system would be a different, duller product. Absence is
      content.</p>
    </div>"""


def data_json(meta, stats):
    cities = {}
    for c in LIVE:
        cities[c] = {
            "name": DISPLAY.get(c, c),
            "no": f"{ROSTER.index(c) + 1:02d}",
            "values": {s["key"]: s["values"][c] for s in stats},
            "disp": {s["key"]: (s["disp"][c] + (f' {s["unit"]}' if s["unit"] else ""))
                     for s in stats},
            "lines": meta["cities"][c]["lines"],
        }
    payload = {
        "asOf": meta["as_of"],
        "live": LIVE,
        "statOrder": [s["key"] for s in stats],
        "stats": {s["key"]: {"win": s["win"]} for s in stats},
        "cities": cities,
        "pairs": [["seoul", "paris"], ["seoul", "tokyo"], ["paris", "tokyo"]],
    }
    return json.dumps(payload, separators=(",", ":"), sort_keys=True,
                      ensure_ascii=False)


FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
           "viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='18' "
           "fill='%231b1b21'/%3E%3Crect x='22' y='18' width='10' height='64' "
           "rx='5' fill='%2300a23f'/%3E%3Crect x='38' y='18' width='10' "
           "height='64' rx='5' fill='%23ffbe00'/%3E%3Crect x='54' y='18' "
           "width='10' height='64' rx='5' fill='%23f62e36'/%3E%3Crect x='70' "
           "y='18' width='10' height='64' rx='5' fill='%230052a4'/%3E%3C/svg%3E")


def main():
    meta = load_meta()
    stats = stat_table(meta)

    # Sanity: every live stat has three distinct values (battle never ties).
    for s in stats:
        vals = list(s["values"].values())
        assert len(set(vals)) == len(vals), f'tie in stat {s["key"]}: {vals}'

    html = f"""<!DOCTYPE html>
<!-- GENERATED FILE - DO NOT EDIT. Built by _scripts/world_metros/build_metro_cards.py; edit the script and re-run. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><!-- soft launch: unlisted until the owner verdict gate -->
<meta name="theme-color" content="#0f0f12">
<title>Metro Match</title>
<meta name="description" content="A collectible card deck for the world's defining metro systems. Twelve cities, six honest stats, a battle and a daily guess. Trading cards with footnotes.">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<script src="/analytics.js" defer></script>
</head>
<body>
<div class="table">

  <header>
    <h1 class="wordmark">METRO <em>MATCH</em></h1>
    <nav role="tablist" aria-label="Views" id="tabs">
      <button type="button" role="tab" id="tab-deck" aria-controls="panel-deck" aria-selected="true">THE DECK</button>
      <button type="button" role="tab" id="tab-battle" aria-controls="panel-battle" aria-selected="false" tabindex="-1">THE BATTLE</button>
      <button type="button" role="tab" id="tab-daily" aria-controls="panel-daily" aria-selected="false" tabindex="-1">THE DAILY</button>
      <button type="button" role="tab" id="tab-method" aria-controls="panel-method" aria-selected="false" tabindex="-1">METHOD</button>
    </nav>
    <span class="livebadge">3 OF 12 LIVE</span>
  </header>

  <main>

    <section id="panel-deck" role="tabpanel" aria-labelledby="tab-deck">
      <p class="intro">A collectible card deck for the world&rsquo;s defining
      metro systems. Every city is one card, honest dated data is the
      content, and comparison is the game: flip a card for its lore side,
      then take the deck into the battle or the daily.
      <b>Trading cards with footnotes.</b></p>
      <div class="deckgrid">{deck_grid(meta, stats)}</div>
    </section>

    <section id="panel-battle" role="tabpanel" aria-labelledby="tab-battle" hidden>
      {battle_panel(meta, stats)}
    </section>

    <section id="panel-daily" role="tabpanel" aria-labelledby="tab-daily" hidden>
      {daily_panel()}
    </section>

    <section id="panel-method" role="tabpanel" aria-labelledby="tab-method" hidden>
      {method_panel(meta, stats)}
    </section>

  </main>

  <footer>
    <span>stats © OpenStreetMap contributors · ODbL · OSM snapshot {meta["as_of"]} · lore diagrams credited on each card</span>
    <a class="made" href="/" target="_self">made by ajin.im</a>
  </footer>

</div>
<script id="mm-data" type="application/json">{data_json(meta, stats)}</script>
<script src="app.js" defer></script>
</body>
</html>
"""
    out = os.path.join(PAGE, "index.html")
    with open(out, "w") as fh:
        fh.write(html)
    print(f"wrote {out}  ({os.path.getsize(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
