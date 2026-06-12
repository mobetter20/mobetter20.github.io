#!/usr/bin/env python3
"""Metro Match page generator (gate-3 + D27 state: the full deck of 18).

Generates is/building/world-metros/index.html: THE DECK (18 cards in the
owner's D23+D27 ranked order, all live with flip-to-lore backs, three switchable
stat themes per D24), THE BATTLE (vs cpu, pick-a-stat, first to 3, ties are
dead heats), THE DAILY (one guess a day, streak in localStorage) and METHOD
(scopes, definitions, sources, licences).

Design state baked in:
  - D18 card grammar: game-first front, familiar diagram on the lore back,
    pinstripe deck back as the game-hidden state.
  - D19 treatment C: ink-dark card #1b1b21 on near-black table #0f0f12.
  - D20 V1 big ledger: bold near-white stat label leading each row, jumbo
    mono value right, deck-rank chip; density on the hull basis now that the
    pipeline landed.
  - D21 name Metro Match; scope rider-B, frozen per city at D25.
  - D23+D27 roster: 18 cards in the owner's ranked order (Osaka, Istanbul appended).
  - D24/D28/D31 themes: SCALE / CHARACTER stat sets switched at deck level
    (display names; the data-set keys stay play/almanac). CHARACTER = base
    fare, driverless, transfer stations, biggest hub, new lines. Battle and
    daily run on the SCALE six only (full coverage there).

Inputs (both committed, both offline):
  assets/meta.json                  geometry snapshot (build_page_geometry.py)
  _scripts/world_metros/almanac.json  researched dated figures (hand-curated)

style.css and app.js are hand-maintained siblings; only index.html is
generated. Diagram attributions are VERBATIM from DIAGRAM-LEDGER.md.

Usage:
    python3 _scripts/world_metros/build_metro_cards.py
"""

import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PAGE = os.path.join(REPO, "is", "building", "world-metros")
ASSETS = os.path.join(PAGE, "assets")

# Deck order = the owner's ranked curation (D23) + Osaka, Istanbul appended
# at 17/18 (D27: deck grows to eighteen, the bench picks promoted).
ROSTER = ["tokyo", "seoul", "singapore", "hong kong", "paris", "shanghai",
          "beijing", "london", "nyc", "madrid", "moscow", "copenhagen",
          "delhi", "guangzhou", "mexico city", "cairo", "osaka", "istanbul"]

# URL-safe / filename-safe key per city (battle hashes, DOM ids, assets).
SLUG = {c: c.replace(" ", "-") for c in ROSTER}

# Lore-back diagram asset extension (Guangzhou's only current, clean-license
# Commons map is a raster; see its DIAGRAM-LEDGER stanza).
DIAGRAM_EXT = {"guangzhou": "png"}


def diagram_file(city):
    return f"{SLUG[city]}-diagram.{DIAGRAM_EXT.get(city, 'svg')}"

DISPLAY = {"nyc": "new york"}  # card face shows the city, not the acronym

SYSTEM = {
    "tokyo": "Tokyo Metro + Toei Subway",
    "seoul": "Seoul Metropolitan Subway",
    "singapore": "Singapore MRT",
    "hong kong": "MTR",
    "paris": "Métro de Paris",
    "shanghai": "Shanghai Metro",
    "beijing": "Beijing Subway",
    "london": "London Underground",
    "nyc": "New York City Subway",
    "madrid": "Metro de Madrid",
    "moscow": "Moscow Metro",
    "copenhagen": "Copenhagen Metro",
    "delhi": "Delhi Metro",
    "guangzhou": "Guangzhou Metro",
    "mexico city": "Metro de la Ciudad de México",
    "cairo": "Cairo Metro",
    "osaka": "Osaka Metro",
    "istanbul": "Metro Istanbul",
}

EPITHET = {
    "tokyo": "the two crews",
    "seoul": "the sprawl",
    "singapore": "the clockwork",
    "hong kong": "the farebox",
    "paris": "the mesh",
    "shanghai": "the giant",
    "beijing": "the heavyweight",
    "london": "the original",
    "nyc": "the all-nighter",
    "madrid": "the dark horse",
    "moscow": "the palace",
    "copenhagen": "the robot",
    "delhi": "the speedrun",
    "guangzhou": "the workhorse",
    "mexico city": "the icons",
    "cairo": "the pioneer",
    "osaka": "the merchant",
    "istanbul": "the crossing",
}

# The scope half of the card subtitle: plain words for what the card
# COUNTS. Exclusions are not abbreviated here ("X out" read as jargon,
# owner flag 2026-06-12); Method's scope table carries them in sentences.
SCOPE_TAG = {
    "tokyo": "Metro + Toei",
    "seoul": "capital region network",
    "singapore": "MRT only",
    "hong kong": "MTR heavy rail only",
    "paris": "full Métro",
    "shanghai": "metro lines only",
    "beijing": "full mapped network",
    "london": "Underground only",
    "nyc": "subway only",
    "madrid": "Metro only",
    "moscow": "metro + MCC ring",
    "copenhagen": "metro M1-M4",
    "delhi": "DMRC + airport line",
    "guangzhou": "metro + Guangfo + APM",
    "mexico city": "STC metro",
    "cairo": "metro lines 1-3",
    "osaka": "Osaka Metro only",
    "istanbul": "metro M-lines only",
}

FLAVOR = {}    # filled from content.json (assert checks all of ROSTER)
FACTS = {}     # two curated facts per lore back (D22 trim)
CREDIT = {}    # VERBATIM from DIAGRAM-LEDGER.md
CAVEAT = {}    # currency caveats where the ledger flags them
FX_DATE = ""   # the single dated FX snapshot for BASE FARE (D28), from almanac


def load_content():
    """Lore content lives in content.json beside this script so the data
    pass and the template stay separately reviewable."""
    global FLAVOR, FACTS, CREDIT, CAVEAT
    with open(os.path.join(HERE, "content.json")) as fh:
        c = json.load(fh)
    FLAVOR = c["flavor"]
    FACTS = c["facts"]
    CREDIT = c["credit"]
    CAVEAT = c["caveat"]
    for city in ROSTER:
        assert city in FLAVOR, f"missing flavor: {city}"
        assert city in FACTS and 2 <= len(FACTS[city]) <= 3, f"facts: {city}"
        assert city in CREDIT, f"missing credit: {city}"


DECK_WORD = "eighteen"

ORDINAL = {n: f"{n}{'th' if 10 < n % 100 < 14 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
           for n in range(1, 19)}


def load_meta():
    with open(os.path.join(ASSETS, "meta.json")) as fh:
        return json.load(fh)


def load_almanac():
    with open(os.path.join(HERE, "almanac.json")) as fh:
        return json.load(fh)


def fmt_density(v):
    return f"{v:.3f}" if v < 0.1 else f"{v:.2f}"


def fmt_riders(m):
    return f"{m / 1000:.2f}<small> B/yr</small>" if m >= 1000 else f"{m:.0f}<small> M/yr</small>"


def fmt_km(v):
    return f"{v:,.0f}<small> km</small>"


def fmt_usd(v):
    return f"${v:.2f}"


def stat_table(meta, alm):
    """Every stat row, across the two D28 sets. Each stat: key, set
    ('play' | 'almanac'), label, win direction, values, display strings,
    ranks (competition ranking over the cities that carry the stat).
    Both sets are full-coverage across the 18 cards (asserted)."""
    c = meta["cities"]
    a = alm["cities"]

    def density(k):
        return c[k]["stations"] / c[k]["hull_km2"]

    stats = [
        # PLAY: the ratified six (battle + daily run here)
        dict(key="opened", set="play", label="opened", win="low",
             values={k: a[k]["opened"]["year"] for k in ROSTER},
             disp={k: str(a[k]["opened"]["year"]) for k in ROSTER}),
        dict(key="stations", set="play", label="stations", win="high",
             values={k: c[k]["stations"] for k in ROSTER},
             disp={k: str(c[k]["stations"]) for k in ROSTER}),
        dict(key="span", set="play", label="span", win="high",
             values={k: c[k]["span_km"] for k in ROSTER},
             disp={k: f'{c[k]["span_km"]:.1f}<small> km</small>' for k in ROSTER}),
        dict(key="density", set="play", label="density", win="high",
             values={k: round(density(k), 4) for k in ROSTER},
             disp={k: f'{fmt_density(density(k))}<small> st/km²</small>' for k in ROSTER}),
        dict(key="routekm", set="play", label="route-km", win="high",
             values={k: a[k]["route_km"]["value"] for k in ROSTER},
             disp={k: fmt_km(a[k]["route_km"]["value"]) for k in ROSTER}),
        dict(key="ridership", set="play", label="ridership", win="high",
             values={k: a[k]["ridership"]["annual_m"] for k in ROSTER},
             disp={k: fmt_riders(a[k]["ridership"]["annual_m"]) for k in ROSTER}),
        # CHARACTER (D28 + D31): base fare (uniform-FX USD), driverless
        # (GoA3+), transfer stations (interchange share), biggest hub (most
        # counted lines at one complex, computed D31 from the same snapshot),
        # new lines (growth since 2016). The redundant "newest line" was
        # dropped at D31 (owner swap); biggest hub took its slot. Internal
        # key "interchange" kept for the data-stat hook; label is the owner's.
        dict(key="fare", set="almanac", label="base fare", win="low",
             values={k: a[k]["fare_usd"]["value"] for k in ROSTER},
             disp={k: fmt_usd(a[k]["fare_usd"]["value"]) for k in ROSTER}),
        dict(key="driverless", set="almanac", label="driverless", win="high",
             values={k: a[k]["driverless"]["value"] for k in ROSTER},
             disp={k: f'{a[k]["driverless"]["value"]}<small> lines</small>' for k in ROSTER}),
        dict(key="interchange", set="almanac", label="transfer", win="high",
             values={k: c[k]["interchange_pct"] for k in ROSTER},
             disp={k: f'{c[k]["interchange_pct"]}<small> %</small>' for k in ROSTER}),
        dict(key="biggest_hub", set="almanac", label="biggest hub", win="high",
             values={k: c[k]["biggest_hub"] for k in ROSTER},
             disp={k: f'{c[k]["biggest_hub"]}<small> lines</small>' for k in ROSTER}),
        # growth, computed from the per-line opened years (low-freshness, no
        # construction-pipeline guesswork): lines opened since 2016.
        dict(key="newlines", set="almanac", label="new lines", win="high",
             values={k: sum(1 for l in a[k]["lines_opened"]["lines"]
                            if l["year"] >= 2016) for k in ROSTER},
             disp={k: f'{sum(1 for l in a[k]["lines_opened"]["lines"] if l["year"] >= 2016)}'
                      f'<small> since &rsquo;16</small>' for k in ROSTER}),
    ]
    for s in stats:
        vals = {k: v for k, v in s["values"].items() if v is not None}
        order = sorted(vals.values(), reverse=(s["win"] == "high"))
        s["ranks"] = {k: (order.index(v) + 1 if v is not None else None)
                      for k, v in s["values"].items()}
        s["basis"] = len(vals)
        assert s["basis"] == len(ROSTER), f"{s['set']} stat {s['key']} not full"
    return stats


def scope_line(meta, city):
    """The core line: count + scope. Rides as the card's subtitle, under the
    name (D-note 4 / owner restructure), so the band needs no tag."""
    lines = meta["cities"][city]["lines"]
    noun = "services" if city == "nyc" else "lines"
    return f"{len(lines)} {noun} · {SCOPE_TAG[city]}"


def identity_html(meta, city):
    """The line-colour band, every card (owner call: one consistent
    treatment). The count + scope is the card subtitle now; the readable
    line names live on the lore-back diagram."""
    lines = meta["cities"][city]["lines"]
    stripes = "".join(f'<i style="background:{l["color"]}"></i>' for l in lines)
    return (f'<div class="cband" role="img" aria-label="{len(lines)} line '
            f'colours, named on the lore side">{stripes}</div>')


def card_foot(meta):
    return (f'<div class="cfoot">data: OSM snapshot {meta["as_of"]} (ODbL) + '
            f'dated almanac · base fare at {FX_DATE} FX · ranks '
            f'across the deck of {len(ROSTER)}</div>')


def chip(rank):
    cls = "crk crk1" if rank == 1 else "crk"
    return f'<span class="{cls}">{ORDINAL[rank]}</span>'


def ledger_html(stats, city, sset, battle=False):
    rows = []
    for s in stats:
        if s["set"] != sset:
            continue
        if s["values"][city] is None:
            continue
        rank, val = s["ranks"][city], s["disp"][city]
        inner = (f'{chip(rank)}<span class="clab">{s["label"]}</span>'
                 f'<span class="cval">{val}</span>')
        if battle:
            rows.append(f'<button type="button" class="crow" '
                        f'data-stat="{s["key"]}">{inner}</button>')
        else:
            rows.append(f'<div class="crow" data-stat="{s["key"]}">{inner}</div>')
    return f'<div class="cledger cl-{sset}" data-set="{sset}">{"".join(rows)}</div>'


def card_front(meta, stats, city, battle=False, deck=False):
    """The play side. deck=True carries both stat sets (SCALE + CHARACTER,
    D28/D31); battle cards carry SCALE only (buttons for the you-card, plain
    rows for cpu)."""
    deck_no = f"{ROSTER.index(city) + 1:02d}"
    if deck:
        ledgers = "".join(ledger_html(stats, city, s)
                          for s in ("play", "almanac"))
    else:
        ledgers = ledger_html(stats, city, "play", battle=battle)
    return (f'<article class="card cfront" '
            f'aria-label="{DISPLAY.get(city, city)}, {scope_line(meta, city)}, '
            f'card {deck_no} of {len(ROSTER)}">'
            f'<div class="chead"><div class="cid">'
            f'<div class="cname">{DISPLAY.get(city, city)}</div></div>'
            f'<div class="cno">{deck_no}/{len(ROSTER)}</div></div>'
            f'<div class="csub">{scope_line(meta, city)}</div>'
            f'{identity_html(meta, city)}'
            f'{ledgers}'
            f'{card_foot(meta)}</article>')


def card_back(city):
    """The lore side: the familiar diagram, credited, plus the curated facts."""
    facts = "".join(f'<div class="lfact">{f}</div>' for f in FACTS[city])
    credit = CREDIT[city]
    caveat = (f'<div class="lcaveat">{CAVEAT[city]}</div>'
              if city in CAVEAT else "")
    return (f'<article class="card cback" aria-label="{DISPLAY.get(city, city)} lore side">'
            f'<div class="lart"><img data-src="assets/{diagram_file(city)}" '
            f'alt="{html.escape(SYSTEM[city])} network diagram, a Wikimedia Commons '
            f'recreation of the map riders see"></div>'
            f'<div class="lband"><div class="lname">{DISPLAY.get(city, city)}</div>'
            f'<div class="lsys">{EPITHET[city]}</div>'
            f'<div class="lflavor">{FLAVOR[city]}</div>'
            f'<div class="lfacts">{facts}</div>'
            f'<div class="lcredit">{credit}{caveat}</div></div></article>')


def card_deck_back(meta):
    """The uniform pinstripe back: every line colour in the deck (BUILD-SPEC),
    the opponent's hidden card in the battle."""
    colours = [l["color"] for city in ROSTER
               for l in meta["cities"][city]["lines"]]
    stripes = "".join(f'<i style="background:{c}"></i>' for c in colours)
    return (f'<div class="card cdeckback" role="img" '
            f'aria-label="Face-down card: the Metro Match deck back">'
            f'<div class="pinstripes">{stripes}</div>'
            f'<div class="backband"><div class="backmark">METRO MATCH</div>'
            f'<div class="backsub">{DECK_WORD} systems · one deck</div></div></div>')


def deck_grid(meta, stats):
    cells = []
    for city in ROSTER:
        slug = SLUG[city]
        cells.append(
            f'<div class="cardunit">'
            f'<div class="flipbox" data-city="{slug}">'
            f'<div class="flipinner">'
            f'<div class="face">{card_front(meta, stats, city, deck=True)}</div>'
            f'<div class="face backface" aria-hidden="true">{card_back(city)}</div>'
            f'</div></div>'
            f'<button type="button" class="flipbtn" data-city="{slug}" '
            f'aria-pressed="false">FLIP · LORE SIDE</button>'
            f'</div>')
    return "".join(cells)


def theme_switch():
    # Two pills, SCALE | CHARACTER (D31 names; replaces PLAY | ALMANAC). The
    # data-set keys stay play/almanac (app.js + style.css switch on them);
    # only the visible labels change. Method carries the definitions + FX date.
    return (
        '<div class="themebar" role="group" aria-label="Stat set">'
        '<span class="themecap">STATS</span>'
        '<button type="button" class="themebtn" data-set="play" aria-pressed="true">SCALE</button>'
        '<button type="button" class="themebtn" data-set="almanac" aria-pressed="false">CHARACTER</button>'
        '</div>')


def battle_panel(meta, stats):
    you = "".join(
        f'<div class="bcardwrap" id="you-{SLUG[c]}" hidden>{card_front(meta, stats, c, battle=True)}</div>'
        for c in ROSTER)
    cpu = "".join(
        f'<div class="bcardwrap" id="cpu-{SLUG[c]}" hidden>{card_front(meta, stats, c)}</div>'
        for c in ROSTER)
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
        <div class="bfine">pick the stat you think beats the hidden card ·
        a dead heat scores nobody</div>
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
        <div class="dq" id="d-q"></div>
        <div class="dchoices" id="d-duel">
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
        <div class="dmc" id="d-mc" hidden>
          <div class="dpills dmcband" id="d-mc-band" aria-hidden="true"></div>
          <div class="dopts" role="group" aria-label="Pick the right number">
            <button type="button" class="dopt"><span class="doptval"></span></button>
            <button type="button" class="dopt"><span class="doptval"></span></button>
            <button type="button" class="dopt"><span class="doptval"></span></button>
            <button type="button" class="dopt"><span class="doptval"></span></button>
          </div>
        </div>
        <div class="dverdict" id="d-verdict" tabindex="-1" aria-live="polite" hidden></div>
        <div class="dstreak" id="d-streak"></div>
        <div class="dnote">the question rotates daily · the streak lives in
        this browser</div>
      </div>
    </div>"""


def method_scope_rows():
    rows = {
        "tokyo": "Tokyo Metro + Toei only; through-running truncated at the "
                 "scope boundary (the familiar Tokyo Subway map stops there).",
        "seoul": "The full capital-region network the familiar map draws, "
                 "incl. Line 1's long Korail corridors, the K-lines, GTX-A, "
                 "AREX, the light metros, Incheon 1-2 and Sinbundang (whose "
                 "validator export is empty, so it rides from a committed "
                 "OpenStreetMap supplement, fetched 2026-06-12).",
        "singapore": "MRT lines only; the LRT feeders are a distinct product "
                     "on the LTA map.",
        "hong kong": "MTR heavy rail incl. the Airport Express and the "
                     "Disneyland Resort line; Light Rail is the map's "
                     "district inset, not the metro.",
        "paris": "Métro 1-14 plus 3bis and 7bis; RER excluded (it is not "
                 "the Métro map).",
        "shanghai": "Metro lines 1-18 plus the Pujiang line; the maglev is "
                    "a separate product even on the official map.",
        "beijing": "The operator's full mapped network: 19 numbered lines, "
                   "the named suburban lines, S1, Xijiao and both airport "
                   "expresses; Batong rides as Line 1 and Daxing as Line 4, "
                   "as the map draws them.",
        "london": "Underground's 11 lines only; the Elizabeth line, "
                  "Overground and DLR are distinct products in the Tube "
                  "map's own grammar.",
        "nyc": "Subway services only; rush-hour diamond variants fold into "
               "their base service, the three S shuttles ride as one pill, "
               "and Staten Island Railway and PATH are separate systems.",
        "madrid": "Metro de Madrid lines 1-12 plus the Ramal; Metro Ligero "
                  "is its own product on the map.",
        "moscow": "Metro lines incl. the MCC ring (the map's line 14); the "
                  "D-branded MCD diameters are commuter rail, excluded.",
        "copenhagen": "Metro M1-M4 only; S-tog is a distinct product.",
        "delhi": "The DMRC network incl. the Airport Express; Rapid Metro "
                 "Gurgaon and the Aqua line are separate concessions.",
        "guangzhou": "Guangzhou Metro incl. the Guangfo through-line and "
                     "the APM; Foshan Metro's own lines and the trams are "
                     "distinct systems.",
        "mexico city": "The STC Metro's 12 lines; Tren Ligero and the "
                       "Suburbano are separate systems.",
        "cairo": "Metro lines 1-3; the LRT and the monorail are separate "
                 "systems.",
        "osaka": "Osaka Metro's nine lines incl. the New Tram (a coequal "
                 "line on the map); the JR Loop and the Osaka Monorail are "
                 "distinct products. Midosuji's through-run to Minoo-kayano "
                 "is drawn continuous, so it stays; Kintetsu and Hankyu "
                 "through-running truncates at the boundary.",
        "istanbul": "The branded Metro Istanbul M-lines (M1A and M1B fold "
                    "to M1). Marmaray is TCDD commuter rail, excluded like "
                    "Moscow's MCD; the funiculars and trams are separate "
                    "feeder products.",
    }
    return "".join(f'<tr><td>{DISPLAY.get(c, c)}</td><td>{rows[c]}</td></tr>'
                   for c in ROSTER)


def short_host(url):
    host = url.split("//")[-1].split("/")[0]
    return host.removeprefix("www.")


def src_link(entry):
    if not entry or not entry.get("source"):
        return ""
    return (f'<a href="{html.escape(entry["source"])}" rel="noopener">'
            f'{short_host(entry["source"])}</a>')


def almanac_table(alm):
    rows = []
    for c in ROSTER:
        a = alm["cities"][c]
        rk, rd = a["route_km"], a["ridership"]
        rows.append(
            f'<tr><td>{DISPLAY.get(c, c)}</td>'
            f'<td>{rk["value"]:,.0f} km <span class="asof">as of {html.escape(str(rk["as_of"]))}</span> {src_link(rk)}</td>'
            f'<td>{rd["annual_m"]:,.0f} M <span class="asof">{html.escape(str(rd["year"]))}</span> {src_link(rd)}</td></tr>')
    return "".join(rows)


def theme_table(alm, fields):
    """fields: [(almanac key, label, unit)]"""
    rows = []
    for c in ROSTER:
        a = alm["cities"][c]
        cells = []
        for key, unit in fields:
            e = a.get(key)
            if not e or e.get("value") is None:
                cells.append("<td>no published figure</td>")
            else:
                asof = e.get("as_of") or e.get("year") or ""
                cells.append(f'<td>{e["value"]:g}{unit} '
                             f'<span class="asof">{html.escape(str(asof))}</span> '
                             f'{src_link(e)}</td>')
        rows.append(f'<tr><td>{DISPLAY.get(c, c)}</td>{"".join(cells)}</tr>')
    return "".join(rows)


def method_panel(meta, alm, stats):
    credits = "".join(f'<p class="credit">{CREDIT[c]}'
                      + (f' <span class="asof">({CAVEAT[c]})</span>' if c in CAVEAT else "")
                      + '</p>'
                      for c in ROSTER)
    alm_table = theme_table(alm, [("fare_usd", " USD"), ("driverless", " lines")])
    return f"""
    <div class="method">
      <h2>The game</h2>
      <p><b>The battle.</b> You hold a card face up; the cpu holds one face
      down. Pick the stat you think wins; the cards compare, and the round
      goes to the better number. First to three rounds takes the match. A
      dead heat scores nobody. The battle runs on the SCALE set.</p>
      <p><b>The daily.</b> One question a day, one guess, and a streak that
      lives in your browser. Some days it is a head-to-head between two
      close systems (never a blowout); some days you pick the right number
      from four, where the wrong three are other cities&rsquo; real
      figures. Nothing leaves the page.</p>
      <p><b>Win directions are fixed.</b> Opened and base fare win smaller;
      everything else wins larger.</p>

      <h2>SCALE: the six</h2>
      <table>
        <tr><th>stat</th><th>what it measures</th><th>wins</th></tr>
        <tr><td>opened</td><td>earliest regular passenger service within the
        card&rsquo;s declared scope, the system&rsquo;s own dating, from
        operator histories</td><td>earlier</td></tr>
        <tr><td>stations</td><td>station complexes counted from the frozen
        snapshot: named stations, same-name platforms merged within 350 m,
        interchanges counted once</td><td>more</td></tr>
        <tr><td>span</td><td>the furthest-stations distance: the geodesic
        between the two stations farthest apart</td><td>more</td></tr>
        <tr><td>density</td><td>stations per square km of network extent,
        the convex hull of the counted stations</td><td>more</td></tr>
        <tr><td>route-km</td><td>reported route length, dated and sourced
        (almanac grade)</td><td>more</td></tr>
        <tr><td>ridership</td><td>reported annual rides, dated and sourced
        (almanac grade)</td><td>more</td></tr>
      </table>

      <h2>CHARACTER: the five</h2>
      <p>A second switchable set. Every figure is dated; sources are in the
      almanac file in the site&rsquo;s public repo.</p>
      <table>
        <tr><th>stat</th><th>what it measures</th><th>wins</th></tr>
        <tr><td>base fare</td><td>the adult single minimum fare, converted to
        USD at one dated FX snapshot ({alm["fx"]["date"]}) for every card, so
        the row compares on one rate; check the operator for today&rsquo;s
        fare</td><td>cheaper</td></tr>
        <tr><td>driverless</td><td>count of GoA3+ lines (driverless, attended
        or not) within the card&rsquo;s declared scope, from Wikipedia&rsquo;s
        driverless-train-systems list</td><td>more</td></tr>
        <tr><td>transfer</td><td>share of the card&rsquo;s station
        complexes served by two or more counted lines, computed from our
        own snapshot</td><td>more</td></tr>
        <tr><td>biggest hub</td><td>the most counted lines that meet at a
        single station complex, computed from the same snapshot</td>
        <td>more</td></tr>
        <tr><td>new lines</td><td>lines that opened in the last decade (since
        2016), counted from the per-line opening years</td><td>more</td></tr>
      </table>
      <p>Transfer and biggest hub are both computed from the same
      snapshot as the other geometry stats. New York reads high on both
      because its lettered and numbered services share track through most
      stations, so a single complex counts many services. The cut stats
      (peak headway, service hours, farebox recovery) were dropped for want
      of one comparable, current source across the deck.</p>

      <h2>Scope: what each card counts</h2>
      <p>Each card declares its scope as <b>the network its city&rsquo;s own
      familiar map draws as coequal metro lines</b>: the rider&rsquo;s
      network, not one operator&rsquo;s books. Modes the map itself marks as
      distinct products (commuter overlays, trams, feeders, people-movers)
      stay out. Frozen per city 2026-06-12 (D25):</p>
      <table class="scopes">{method_scope_rows()}</table>

      <h2>Sources and dates</h2>
      <p>Geometry, station counts, span and density: OpenStreetMap via the
      subway preprocessor CDN, snapshot {meta["as_of"]}, ODbL. The page is
      built offline from committed snapshots; raw GeoJSON never ships.</p>
      <p>Opened years: operator histories, per-line, dated (sources in the
      almanac file in the site&rsquo;s public repo). Reported figures:</p>
      <table class="almtable">
        <tr><th>city</th><th>route-km</th><th>annual rides</th></tr>
        {almanac_table(alm)}
      </table>
      <details><summary>character set: figures and sources</summary>
      <table class="almtable">
        <tr><th>city</th><th>base fare (USD, {alm["fx"]["date"]} FX)</th><th>driverless (GoA3+)</th></tr>
        {alm_table}
      </table>
      <p class="credit">Interchange is computed from the same snapshot as the
      other geometry stats; its per-city value is in the deck data and on each
      card. Driverless counts are from the driverless-train-systems list at the
      revision named in the rows.</p></details>

      <h2>The diagrams on the backs</h2>
      <p>The lore side of each card carries the diagram riders actually see,
      as a Wikimedia Commons recreation, credited on the card:</p>
      {credits}
      <p>Official schematic artwork appears nowhere on this site: the major
      operators enforce copyright on their map artwork, so the
      long-maintained Commons recreations are the legal route to the
      familiar map. Every back&rsquo;s file and licence was verified on its
      Commons page before it shipped.</p>
    </div>"""


def data_json(meta, stats):
    cities = {}
    # battle + daily are bound to the SCALE set (D28/D31; key "play")
    play = [s for s in stats if s["set"] == "play"]
    for c in ROSTER:
        slug = SLUG[c]
        cities[slug] = {
            "name": DISPLAY.get(c, c),
            "values": {s["key"]: s["values"][c] for s in play},
            "disp": {s["key"]: s["disp"][c].replace("<small>", "").replace("</small>", "")
                     for s in play},
            "lines": meta["cities"][c]["lines"],
        }
    slugs = [SLUG[c] for c in ROSTER]
    pairs = [[slugs[i], slugs[j]] for i in range(len(slugs))
             for j in range(i + 1, len(slugs))]
    payload = {
        "asOf": meta["as_of"],
        "live": slugs,
        "statOrder": [s["key"] for s in play],
        "stats": {s["key"]: {"win": s["win"]} for s in play},
        "cities": cities,
        "pairs": pairs,
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
    global FX_DATE
    load_content()
    meta = load_meta()
    alm = load_almanac()
    FX_DATE = alm["fx"]["date"]
    for c in ROSTER:
        assert c in meta["cities"], f"meta.json missing {c}"
        assert c in alm["cities"], f"almanac.json missing {c}"
        assert "interchange_pct" in meta["cities"][c], f"no interchange for {c}"
        assert os.path.exists(os.path.join(ASSETS, diagram_file(c))), \
            f"missing diagram asset for {c}"
    stats = stat_table(meta, alm)

    html_out = f"""<!DOCTYPE html>
<!-- GENERATED FILE - DO NOT EDIT. Built by _scripts/world_metros/build_metro_cards.py; edit the script and re-run. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><!-- soft launch: unlisted until the owner verdict gate -->
<meta name="theme-color" content="#0f0f12">
<title>Metro Match</title>
<meta name="description" content="A collectible card deck for the world's defining metro systems. Eighteen cities, honest dated stats in two sets (scale and character), a battle and a daily guess. Trading cards with footnotes.">
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
    <span class="livebadge">DECK OF 18</span>
  </header>

  <main>

    <section id="panel-deck" role="tabpanel" aria-labelledby="tab-deck">
      <p class="intro">Stat cards for the world&rsquo;s great metro systems,
      every number dated and sourced. <b>Flip a card for the lore; pick a
      stat and beat the cpu; one guess a day in the daily.</b></p>
      {theme_switch()}
      <div class="deckgrid" id="deckgrid" data-set="play">{deck_grid(meta, stats)}</div>
    </section>

    <section id="panel-battle" role="tabpanel" aria-labelledby="tab-battle" hidden>
      {battle_panel(meta, stats)}
    </section>

    <section id="panel-daily" role="tabpanel" aria-labelledby="tab-daily" hidden>
      {daily_panel()}
    </section>

    <section id="panel-method" role="tabpanel" aria-labelledby="tab-method" hidden>
      {method_panel(meta, alm, stats)}
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
        fh.write(html_out)
    print(f"wrote {out}  ({os.path.getsize(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
