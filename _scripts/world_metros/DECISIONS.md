# DECISIONS — World Metros Atlas (append-only, dated)

Status legend: **RATIFIED** (owner said yes) · **PROPOSED** (agent recommendation,
owner ratification pending) · **STANDING** (inherited from repo/global rules).

## 2026-06-11

**D0 · Project origin — RATIFIED (implicitly, by continuation).**
Idea: Ajin, 2026-06-11 ("interactive maps + basic info of the world's top metro
systems in one easy view, only if nothing good exists"). Claude deep-research run
(102 agents, 20 sources, 23/25 claims verified) found the niche open: closest
competitors Metro Bits (curiosity DNA, but sprawling, no interactive maps),
metrolinemap.com (per-city utility, no rankings/comparison), Transit Explorer
(exhaustive research DB, licensing excludes reuse). Codex then produced the
"World Metros Interactive Atlas" plan (in-session only; **no files/commits ever
landed on disk** — verified by repo/branch/filesystem sweep 2026-06-11). That plan
is the structural reference for this doc set.

**D1 · Codex plan adopted as reference, not contract — RATIFIED 2026-06-11.**
Keep: one-URL four-view shape, same-scale Compare invariants, five computed ranking
lenses, scope-freeze discipline, licensing posture, approval gates, soft-launch norms.
Trim: see D2, D5–D7. Judge for all trims: the original brief — a *simple* curiosity
site, not a transit-data product.

**D2 · Kill the practical-traveller layer for v1 — RATIFIED 2026-06-11.**
"First ride" / "Using It" / integration matrices / accessibility & cleanliness
evidence are out. Why: (a) it's the crowded travel-utility space the deep-research
explicitly said not to compete in; (b) fares/payment facts drive the 30/90/180-day
freshness treadmill — permanent maintenance for a curiosity site; (c) it was ~4 of the
5 sections of the Codex information model, i.e. most of the project's weight, serving
a user need nobody stated. Replacement: a compact profile card (opened · km · stations
· lines · ridership · 2–3 curated facts), all dated + sourced.

**D3 · Roster: 12 systems = Codex 10 + Moscow + Hong Kong — RATIFIED 2026-06-11.**
Codex 10: Shanghai, Tokyo, Seoul, Singapore, Delhi, London, Paris, NYC, Mexico City,
Cairo. Add Moscow (palace stations, Soviet metro tradition, top-3 busiest — its absence
is the most glaring gap a curious reader would hit) and Hong Kong (the
efficiency/farebox benchmark, Octopus). Keep Beijing OUT (Shanghai covers the
China-mega category) but give it a "why not" entry on Method. 12 over 10 because the
per-city marginal cost is low (uniform data source, all validate GOOD) and it frees the
site from false top-10 precision. Alternatives if owner insists on 10: drop Cairo
(loses the only Africa rep) or Singapore (HK overlaps its category).

**D4 · Geometry source: OSM via subway-validator CDN — RATIFIED (verified, standing).**
All 13 candidate cities validate GOOD on `cdn.organicmaps.app/subway/` (checked
2026-06-11); per-city GeoJSON is drawable as-is with real line colours. ODbL
attribution required. End-to-end proof render (Seoul 2–9 vs Paris, one shared scale)
succeeded same day — see `proof_same_scale.py`.

**D5 · Reported length/ridership: shown and rankable as a labelled almanac table —
RATIFIED 2026-06-11 (amends Codex).** Codex banned ranking reported figures outright; but "most
extensive" is literally what the owner asked for. Resolution: the five computed lenses
stay the only *computed* rankings; reported route-km + annual ridership appear in a
clearly-labelled "reported figures, as-of dates vary by source" table. Honest and
useful beats pure.

**D6 · Process trims — RATIFIED 2026-06-11.** No Makefile (repo grain is `_scripts/*/ *.py` +
untracked `publish.sh`); no 3-browser Playwright matrix (repo norm: verify at
375/768/1280 + manual pass); no field-level `evidence_status` enum (every fact carries
`source + as_of`; missing renders Unknown); no freshness SLA tiers (annual scripted
refresh).

**D7 · Design: "Electric Cartography" as working direction — RATIFIED 2026-06-11
(as working direction; final look still judged at the mock gate, D8).** Palette + luminous-geometry character per the Codex session (its "approved"
status lives only in that session; re-confirm at the mock-board gate). Bespoke tier:
own art, anchors only (way home, palette sympathy, DM Mono labels). Network lines keep
real OSM colours.

**D8 · Gates before any frontend — STANDING.** Mock boards (real Seoul+Paris data) →
owner approval → Seoul/Paris coded prototype → second approval → scale to roster.
Matches the repo's draft-review-before-publish norm.

**D9 · Forks ratified; mock boards built — RATIFIED 2026-06-11.**
Owner confirmed all three open forks as recommended ("i confirm ur rec"): scope trim
(D2/D5/D6), roster of 12 (D3), Electric Cartography to the mock gate (D7). The three
approval boards (desktop Explore, desktop Compare/Shape pair, mobile Explore) were
built the same day from real Seoul + Paris OSM geometry — `mocks/build_mock_boards.py`
generates them into `mocks/`. Current gate: owner verdict on the boards (D8 gate 1).

**D10 · Design pivot: official-map idiom on white — RATIFIED 2026-06-11 (owner-directed).**
At gate 1 the owner rejected the dark Electric Cartography boards in favour of
"the map the city made for itself": white background, the colour language of the
maps riders actually see. Licensing reality (DATA-CONTRACT.md): official schematic
ARTWORK cannot be embedded (TfL verified-enforced; the major operators hold the
same posture), so the resolution is idiom-not-artwork — our OSM geometry drawn in
the official visual language (white ground, real operator line colours, bold solid
strokes, white-fill/ink-ring station dots, line-select greys the rest like the
metro apps), plus a "the map riders see" link to the operator's official diagram
on every city card, plus a Method note telling the licensing story. Supersedes
D7's palette; D7's "lines keep real OSM colours" survives. Boards rebuilt the same
day (`mocks/`); gate 1 verdict on the round-2 boards pending.

**D11 · Familiar-diagram layer — RATIFIED 2026-06-11 (proposed and ratified same day).**
Owner: the familiar rider map was an integral expectation, and its impossibility was
surfaced too late (a research-table line and a docs rule, never as "you will not see
the Tube map on this site"). Acknowledged; memory written
(feedback_surface_constraint_consequences). Substantive re-answer — three legal grades:
(1) official ARTWORK: blocked for verified-enforced operators (TfL; MTA/RATP/Tokyo/
Moscow hold the same posture); possible per-city exceptions worth an audit (Seoul
KOGL, CDMX, Delhi GoI — unverified); (2) CC BY-SA Commons RECREATIONS in the official
idiom: verified available for Seoul (Seoul_Metropolitan_Subway_network_map.svg,
CC BY-SA 4.0) and even London (the sameboat tube-style map, used on 100+ Wikipedia
pages) — the realistic route to "the familiar map" as a first-class feature;
(3) our true-geometry renders (built; powers Shape). Proposed product change: Explore
gets TWO map modes per city — "Diagram" (default: the familiar schematic; Commons
recreation, or official file where a permissive license is verified;every city gets a
license-ledger entry + attribution) and "True shape" (ours). Shape comparison stays
ours. Pending owner ratification; if ratified, first step is a per-city diagram
sourcing audit (12 cities: file, author, license, currency vs the 2026 network).
*Ratification (2026-06-11):* owner approved via the diagram-mode mock
(`mocks/diagram-desktop.html`), the interactivity spike
(`mocks/diagram-interactive.html`), and by launching the D8-gate-2 prototype build
with diagram mode in scope. The sourcing audit D11 named as its first step is done
(DIAGRAM-LEDGER.md — all 12 cities have a verified-license file + fallback).

**D12 · Coded-prototype scope (D8 gate 2) — RATIFIED 2026-06-11 (owner-launched).**
The gate-2 prototype is a real page at `/is/building/world-metros/`, soft-launched
from day 1 (noindex meta; the sitemap builder auto-skips noindex pages; no
`/is/building` hub card; no home-teaser line; `publish.sh` untouched). Vanilla
HTML/CSS/JS, no framework; official-map-idiom chrome per the round-2 boards (D10).
Scope:
- **Three cities live** — Seoul, Paris, Tokyo. The other 9 roster chips render
  disabled with a "soon" tooltip. Tokyo joins as the deliberate representative of
  the pan-zoom-only diagram class (DIAGRAM-LEDGER): same pan/zoom, a plain "labels
  not tappable on this diagram" note, no fake affordances.
- **Explore** — two modes per D11, DIAGRAM default: inline Commons SVG driven by
  viewBox (pan/zoom/pinch + station-label tap where interactive-ready; tap shows a
  station chip with a "data card in next stage" placeholder). TRUE SHAPE: our OSM
  geometry, emitted at build time as simplified per-city JSON
  (`_scripts/world_metros/build_page_geometry.py` — raw CDN GeoJSON is never
  shipped); line-select greys the rest, station dots, scale bar.
- **Shape** — Seoul × Paris side-by-side at one shared px-per-km, north-up, synced
  zoom, "geography not aligned — shapes only" note, per-panel span readouts.
- **Rankings / Method** — honest in-progress stubs; keyboard-reachable tabs.
- **Attribution** — per-city diagram credit verbatim from DIAGRAM-LEDGER in the
  footer while that city's diagram shows; "geometry © OpenStreetMap contributors
  (ODbL)" always; Seoul card carries the ledger's "diagram dated 2023, future lines
  as then planned" currency note.
- **Weight** — per-city assets lazy-load on city switch; only Seoul loads initially.
- **Scope notes** — Tokyo True Shape draws Tokyo Metro + Toei refs only;
  through-running truncation stays a pipeline-stage matter (like Seoul L1, which
  keeps lines 2–9 here as in the mocks). Full snapshot/refresh discipline
  (committed dated `data/` dir) also lands at pipeline stage; the committed
  per-city JSON, stamped with its OSM as-of date, is the prototype's dated artifact.
- **Stop at the gate** — no scaling to the remaining 9 cities until owner approval
  of the live prototype.

**D13 · Consistent geographic dress for True Shape — PROPOSED 2026-06-11 (owner
question at gate 2).**
Owner, on seeing the live prototype: the Commons diagrams are a style patchwork
(Tokyo's recreation is quasi-geographic; Seoul/Paris are pure schematics), and a
single consistent style like the Tokyo map would be better; less sure the diagram
layer should stay. Substantive answer: per-city geographic-style diagrams cannot
be sourced (don't exist for most cities; same patchwork + license ledger again),
but OUR true geometry can wear a uniform geographic dress: OSM water polygons +
coastline (bay closed against the frame; islands punched out) + ghosted
out-of-scope rail, identical machinery for all 12 cities, one ODbL line for the
whole thing. Evidence: `mocks/build_geo_shape_mock.py` →
`mocks/geo-shape-desktop.html` (Seoul / Tokyo / Paris; the Han, Tokyo Bay and the
Seine all render; built same day). Proposed product change if ratified (option B
of the gate discussion): the geo-dressed True Shape becomes Explore's default and
the site's consistent visual center; the Commons diagram mode stays as the
per-city "the map riders see" exhibit (it remains the only name-bearing view
until a label layer exists — dropping it entirely, option C, would leave the site
with no readable station names). Implementation notes for scaling: fetch
Overpass full geometry (bbox-clipped `out geom` breaks river multipolygon
assembly), clip rings locally (Sutherland-Hodgman); one outer ring per SVG path
(nested-outer data quirks cancel to white under a shared evenodd path); closed
coastline loops: negative shoelace in the y-down projection = island; Paris RER
is a separate validator network file (affects the ghost layer's reach there).
Pending owner pick: A (keep as shipped) / B (this) / C (drop diagrams).

**D14 · Map bake-off spike — RATIFIED 2026-06-11 (owner: "bake-off"; verdict
resolves D13).**
At the gate the owner judged the round-1 geo dress clumsy outside Tokyo and
asked whether to build the rest of the page first or settle the map first.
Settled: map first, as a timeboxed bake-off. Evidence built same day,
`mocks/bakeoff-board.html` (`mocks/build_bakeoff_board.py`) — per city
(Seoul/Tokyo/Paris) three candidates side by side:
1. *Polished geographic* (ours): round-2 polish on the geo dress — Chaikin
   smoothing, per-line white casing, recessive ghost rail, smoothed water
   (`build_geo_shape_mock.py`, regenerated board committed).
2. *Consistent schematic*: octolinear (LOOM, Uni Freiburg, GPL-3 tools; output
   SVGs unencumbered, input stays ODbL). Evidence cells use their global-demo
   render (basemap hidden; scope wider than ours, styling theirs). The LOCAL
   pipeline is fully prepped: `mocks/loom_convert.py` parses the validator
   YAMLs' station-ordered itineraries, batch-resolves stop coords via Overpass,
   and emits verified line-graph GeoJSON for all three cities
   (326/271/281 stops); `docker build` of the toolchain is ready but blocked on
   Docker Desktop's admin prompt on this machine (one password click, then
   `topo | loom | octi | transitmap -l` per city, seconds each).
3. *The familiar diagram* (the shipped prototype's Commons recreations) as the
   patchwork reference.
Caveats recorded on the board: candidates 1 and 2 both lack station-name labels
today (the diagrams remain the only name-bearing view); the schematic's station
clustering relies on `topo` name-merging of per-line OSM stop nodes. Owner
verdict on the board picks the Explore direction; Shape keeps true geometry
regardless.

## 2026-06-12

**D15 · Hero flip: atlas-page IA, map demoted from hero to figure — RATIFIED
2026-06-12 (owner verdict on the D14 board; pick: silhouette wall).**
Owner on the bake-off: all three candidates usable but none is the polished
main visual they imagined; willing to reconsider the UI — map less prominent,
other content the hero, maps small/sparing, possibly an embedded map if legal.
Assessment: the imagined polish is operator/Apple-grade designed cartography
(copyright-walled or a large design investment); but our geometry already
reads as finished at SMALL sizes (the same-scale-poster genre is minimalist
silhouettes). Proposal:
- **Landing hero = same-scale silhouette wall** — all 12 networks as small
  dark true-shape silhouettes, one shared px-per-km, north-up, name + one
  number each. The site's thesis in one screen; built directly from the
  existing shape JSONs.
- **City dossier** as the dwell surface: why-stories, dated facts, almanac,
  line-palette strip; a medium map as a *figure* (round-2 geo dress works at
  that size), expandable on demand.
- **Demotions, not deletions**: the interactive Explore canvas and the Commons
  diagram become per-city secondary views (the diagram stays the name-bearing
  "map riders see" exhibit, D11 obligation kept); the synced pair view becomes
  "compare any two" reached from dossiers; Rankings rows carry tiny
  silhouettes.
- **Embeds** (owner asked): legal via Google embed API or Leaflet + tile
  provider with attribution (raw osm.org tiles policy-discouraged), but
  generic-by-construction; at most a small "locate it" element in a dossier,
  never a hero.
Alternatives offered: rankings-first (table as front page) or dossier-first
(no thesis image). Recommendation: silhouette wall. If ratified, next step is
a landing-board mock with the 3 live cities real + 9 placeholders (D8 gate
discipline: no roster scale-up before prototype approval). Resolves D13 by
superseding the "Explore default" question: in this IA the diagram/true-shape
toggle lives one level down, where patchwork inconsistency stops mattering.
*Ratification (2026-06-12):* owner picked the silhouette wall ("wall").
Next gate artifact: the landing-board mock (wall + one example dossier).

**D16 · Gallery + Duel IA; familiar diagrams promoted to the visual language —
PROPOSED 2026-06-12 (owner verdict on the D15 wall board: rejected as ugly).**
Signal across four visual rounds (dark boards rejected at D10; geographic dress
judged clumsy at D14; octolinear merely usable; silhouette wall rejected at the
D15 gate): the owner's eye consistently holds only on the real, designed
diagrams. Decision follows the signal: stop generating the hero visual.
- **Visual language = the familiar Commons diagrams in uniform frames.** The
  patchwork objection resolves by the site's own design rule (consistent
  chrome, free content): identical card frames, the diagram as the artwork.
  As compared artifacts, per-city style differences are content, not mess.
  Ledger caveats stop binding: tap-ability and currency notes matter less for
  exhibits (the already-built interactive viewer opens from the card).
- **Engagement core = head-to-head + rankings** (the owner's reweighting:
  "fun and engaging" comparison matters more than map polish). Mechanics
  ratified for build: the DUEL (tale-of-the-tape: paired bars per lens +
  almanac fact rows + plain verdict lines + the same-scale silhouette pair
  demoted to one "true size" row; stable per-pair URLs), SUPERLATIVE CHIPS
  (1-2 computed awards per city on its gallery card, linking into rankings),
  PODIUM STORIES (each lens: top-3 podium + spread strip + one surprising
  fact; sortable almanac below). Deferred to v2: reveal-on-tap guessing.
  Rejected: brackets/tournaments (gimmick at n=12).
- **IA**: landing = the 12-card diagram gallery + "compare any two" entry;
  duel pages; Rankings = lens podiums + almanac; Method unchanged. The wall
  (D15) is dead as a landing; the geo dress and octolinear pipeline are
  shelved, kept in mocks/.
Next gate artifact if ratified: gallery + SEOUL-vs-PARIS duel mock board.

**D17 · Hard pivot: METRO CARDS, working name "metro match" — RATIFIED
2026-06-12 (owner verdict on the D16 board gate: pivot. D16 is not ratified;
its atlas IA dies, its mechanics survive inside the cards).**
Owner, on the D16 gallery + duel board: without satisfying map visuals,
archive the project (or at least the current vision), or pivot hard; floated
stat cards in the Pokémon / baseball-card genre plus a match game. Assessment
agreed and the owner confirmed ("pivot"): the card reframe is the first one
that DISSOLVES the map-hero problem instead of fighting it. A hero-sized map
promises cartographic polish we cannot license or afford (the D10 to D15
record); a trading card never makes that promise. Card art is a stamp-sized
window inside a designed frame, the frame is entirely ours to design, and D15
already recorded that our geometry reads as finished at small sizes.
- **Draft North-Star (replaces BUILD-SPEC's if the mock gate passes):** a
  collectible card deck for the world's defining metro systems. Every city is
  one designed stat card; honest dated data is the content; comparison is the
  game. Two modes share the same card object: the BATTLE (pick a stat off
  your card, beat the opponent's; the D16 duel mechanics reskinned) and a
  DAILY guess ("which plots more stations?"), which consciously un-defers
  D16's deferred reveal-on-tap guessing under the new vision.
- **What survives the pivot:** the five computed lenses become the stat
  block; meta.json / shape JSONs become card art; DIAGRAM-LEDGER files become
  "the map riders see" exhibits (card back or detail view); the duel becomes
  the battle; the honest-data DNA becomes the joke itself: trading cards with
  footnotes, every stat dated and sourced. The data contracts, scope rules
  and licensing posture are unchanged.
- **Trade-dress rule:** our own card idiom in the official-map language
  (white card, hairline rules, line-colour strip, DM Mono stats, transit-blue
  accent). No Pokémon / Top Trumps trade dress.
- **Open forks, judged at the mock gate:** (a) card art: true-shape
  silhouette vs diagram window, decided by eye on the mock; (b) game depth:
  battle-only vs battle + daily; (c) naming stays the owner's call ("metro
  match" is the working title).
- **Premise gate before any spec rewrite:** ONE static mock board: a 3-card
  fan (Seoul, Paris, Tokyo), the art fork shown side by side, one battle
  frame, one card back. If the cards do not delight at mock scale, archive
  with confidence (registry to paused/archived) having spent one artifact to
  find out. BUILD-SPEC.md is deliberately NOT rewritten until that gate
  passes; D17 carries the draft North-Star until then.

**D18 · Card v2: game-first front; the map leaves the front — RATIFIED
2026-06-12 (owner-directed at the D17 card-mock gate; v2 board verdict
pending).**
Owner on the round-1 cards: not sure the map belongs on the front at all
(lots of interesting stats could live there instead); the design should be
more polished and minimal, like a modern board-game card, optimized for our
specific game and content rather than the baseball/Pokémon lineage; maybe
the familiar map belongs on the BACK; and the project should really pivot,
not ship a half-measure reactionary fix. Acknowledged: round 1 assembled
atlas parts inside a card frame (silhouette art window + stat rows = the
atlas in miniature). Round 2 designs from the game outward:
- **The stat block IS the play surface.** The battle decision is "which of
  my stats is strong?", so every row carries a deck-rank chip (1ST filled,
  others hollow) and a normalized strength track, computed across the live
  deck (full 12 at pipeline; the card footnote names the basis). Win
  directions defined per stat: opened = earlier wins (seniority); all other
  lenses = larger wins.
- **Front for play, back for lore.** Front: city name + epithet (the
  sprawl / the mesh / the two crews), line pills carrying the real refs in
  the operators' colours (the identity device, rendered purely from data),
  six stat rows (opened, lines, stations, span computed live; route-km and
  ridership ride as pipeline rows with empty tracks), provenance footnote.
  NO map, no art window. Back: the city's familiar diagram full-bleed with
  a name band, the flavor line, and the ledger-verbatim credit (the D11
  "map riders see" obligation moves here). The uniform deck back
  (pinstripes) remains the game-hidden state.
- Gate artifact: `mocks/card-game-board.html` (three v2 fronts, the flip
  exhibit front/back/deck-back, the battle restaged on v2, daily strip
  kept). Round-1 board stays in mocks/ for the record.

**D19 · Premise PASSED; dark ground — RATIFIED 2026-06-12 (owner verdict on
the D18 v2 board: "i like it", with one directed amendment: a black or other
dark background might be better; ground treatment fork pending at the D19
board).**
The D17 premise kill test is passed: the archive branch is dead, and the
commissioned follow-through lands with this entry (BUILD-SPEC.md rewritten
around the D17 North-Star + D18 card grammar; README first paragraph
updated). The amendment opens one visual fork, deliberately built as an
exhibit rather than argued in prose ("background" can mean the card face or
the table it sits on):
- **A · round-2 reference:** white card on the light ground (as approved).
- **B · white card, dark table:** cards stay paper-white objects; the page
  ground goes near-black. The physical-cards-on-a-table read.
- **C · dark card, dark table (recommendation):** the card face itself goes
  ink-dark; the operators' line colours and the rank chips do the lighting.
  The premium game-card read, and the strongest setting for the pills.
Palette stays in the board's own ink family (cool near-black, not the
site's warm house dark): ground `#0f0f12`, card `#1b1b21`, hairlines
`#2e2e36`, light text `#f2f2ee`, transit-blue fills unchanged, light-blue
text accents on dark. Official-map idiom elements carry over (DM Mono data
labels, hairline rules, real line colours); D10's white-ground rule was an
atlas-era rule about maps, and the cards are a different object.
Gate artifact: `mocks/card-dark-board.html` (the three-way ground fork on
swatches, then the fan / flip / battle restaged in the recommended dark
treatment). Owner pick A / B / C settles the ground before the live-page
rebuild; naming ("metro match", working) stays open.
*Resolution (2026-06-12):* owner picked **C** ("i meant c"): dark card, dark
table. The ground is settled.

**D20 · Stat-list review + row-design variants — RATIFIED 2026-06-12
(owner-directed at the D19 pick: confirm the comparison items are optimal,
content AND design; big letters, legible, strong brand identity, board-game
card look; multiple mock versions welcomed).**
- **Content (PROPOSED, owner to confirm): swap `lines` for `density`.**
  The current six (opened, lines, stations, span, route-km, ridership) carry
  three size-correlated stats; big systems would sweep them, which is poor
  Top-Trumps balance. `lines` is also already ON the card: the pills carry
  every ref, so the row spends a slot restating the most visible device.
  `density` (stations per km² of network extent; bbox basis in mocks, hull
  basis at pipeline, defined on Method) is computed from data we already
  hold, is orthogonal to size, and gives Paris its epithet stat: the mesh
  becomes playable. Proposed six: **opened · stations · span · density ·
  route-km · ridership**. Live-deck winner spread improves (Seoul: stations
  + span; Paris: opened + density; full deck projects route-km/ridership to
  the Shanghai class and opened to London: five-plus distinct winners across
  six stats). Line count stays visible via the pills and the lore back.
- **Design: three stat-presentation variants, all in treatment C,** judged
  by eye on one board (`mocks/card-row-variants-board.html`), each shown as
  the full three-city fan. Shared across variants: bigger name (20px),
  bigger pills, the C palette, provenance foot. The variants differ ONLY in
  how the six stats present:
  - **V1 · BIG LEDGER** — six rows, jumbo numerals (19px), rank tag + label
    left, value right; the strength tracks are dropped (the rank tag alone
    carries relative strength). Maximum legibility.
  - **V2 · STAT TILES** — a 2×3 grid of tiles, value on top, label under,
    rank chip in the corner. The board-game player-mat look.
  - **V3 · HERO STAT** — the city's signature stat blown up as the card's
    hero number (epithet-aligned: Seoul span, Paris density; Tokyo shows the
    variant's honest weakness: no crown in the live deck, hero falls back to
    its best rank), five compact rows below.
- Gate: owner picks V1 / V2 / V3 (or elements to merge) AND confirms or
  vetoes the lines→density swap. Then the live-page rebuild starts.
*Revision (2026-06-12, board r2/r3):* owner flagged the label hierarchy
(stats big, headers small and hard to read; bring a UX/game-asset designer
eye). Type pass applied: stat labels lead each row in bold near-white sans
(11.5px; you pick a stat by its name), city name 28px, jumbo values kept.
A designer-critique agent then reviewed the screenshots; adopted: Paris/Tokyo
pill compaction above 12 lines (every ref kept, no overflow hiding), V2 rank
chip to tile bottom-right, dashed treatment so pending rows read as slots not
broken data, quieter deck number. Rejected: re-dimming labels (contradicts
the owner's flag; game hierarchy wants stat names scannable first).
