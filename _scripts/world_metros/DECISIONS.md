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
*Resolution (2026-06-12):* owner picked **V1 (big ledger)**; the
lines→density swap is confirmed (owner: line info should live somewhere, but
not at stat level, that would be redundant). Ratified defaults for the
rebuild: line count as header metadata beside the pills ("8 lines · 2–9
shown"), a scope tag so pills never silently claim completeness, and 2-3
curated "why it's interesting" facts on the lore back (the D2 profile-card
content finds its home; the traveller-utility layer stays out, D2 holds).
Still open: per-city declared scope (A operator-proper vs B rider-scope, rec
B: each card covers the network its own familiar map draws; owner flagged
Seoul's missing lines), due before roster scale-up, recorded on Method when
decided. Naming ("metro match") still the owner's call before wide ship.
Next gate artifact: the live page rebuilt as the deck.

**D21 · Name and scope ratified; the deck is live — RATIFIED 2026-06-12
(owner picks at the rebuild session's gate check; build landed the same
session).**
- **Name: METRO MATCH** ships (picked over "Metro Cards" and over keeping
  "World Metros"; the URL stays `/is/building/world-metros/`). The title
  tag, header wordmark and pinstripe deck back carry it.
- **Scope: B, rider-scope.** Each card declares the network its city's own
  familiar map draws, not one operator's books. Binds at the roster
  scale-up; this build keeps Seoul at lines 2–9 under the ratified scope
  tag ("8 lines · 2–9 shown"), and Method records the rule plus the Seoul
  L1 freeze question it defers to the pipeline.
- **The rebuild (D20's gate artifact) shipped:** `/is/building/world-metros/`
  is now the card deck. THE DECK: 12 cards in roster order; Seoul, Paris,
  Tokyo live with flip-to-lore backs (ledger diagrams lazy-load on flip,
  attribution verbatim, Seoul currency caveat carried); nine dashed "soon"
  slots naming their verified licences. THE BATTLE: vs cpu, pick a stat off
  the V1 ledger, first to 3, per-pair hash URLs, the pinstripe deck back as
  the hidden card; route-km/ridership sit out as Unknown. THE DAILY: one
  stations guess a day, streak in localStorage. METHOD: game rules, the six
  stat definitions with win directions, scope rules, sources and as-of
  dates, the diagram licensing story, why not Beijing. Generator:
  `_scripts/world_metros/build_metro_cards.py` writes index.html from the
  committed meta.json (style.css and app.js hand-maintained beside it).
  Soft-launch norms kept: noindex, no sitemap entry, no hub card, no home
  teaser; analytics.js loads. Verified at 375/768/1280; battle and daily
  keyboard-playable; prefers-reduced-motion degrades flips to instant
  swaps; console clean; the deck grid ships light (no diagram fetch before
  a flip). Gate: owner verdict on the live page, then roster scale-up
  (BUILD-SPEC gate 3).

**D22 · Live-page polish on owner feedback — RATIFIED 2026-06-12 (owner
verdict on the D21 live page: three fixes directed, two with owner picks).**
The owner judged the live page and flagged, with two questions: the empty
`route-km`/`ridership` rows ("is this data gonna be included?"), the daily
UX ("small and empty screen"; "what kind of quiz?"), and legibility ("why
are some text so small"). Resolutions:
- **Empty rows: hidden until sourced (owner pick).** route-km + ridership
  leave the card face entirely until they carry scope-matched, dated
  figures; the card now shows four clean live stats. They return at the
  roster scale-up (a reported figure must match the card's declared scope,
  and Seoul's scope is the open freeze). Method still documents the
  six-stat model. No playability cost: Unknown stats already sat out
  battles.
- **Daily: the stat rotates (owner pick).** Same one-guess-a-day cadence,
  but the question rotates deterministically across the four live stats
  (opened / stations / span / density), each with its own framing; the
  reveal shows the contested values. The surface was rebuilt: vertically
  centered (top-aligned on mobile), bigger, a "today's stat" chip, line
  pills on each choice card, value-on-reveal. Fixes the marooned-box look.
- **Legibility pass.** Nothing readable now sits below ~9px; the worst
  offenders (the lore-back CC attribution and card footnotes at 6.5px)
  lifted to 9px, the ledger rows given more height, the scope tag moved to
  its own line so 16 Paris refs never clip. This closes the D20 small-text
  flag, which the first build only half-fixed (stat labels big, secondary
  labels still tiny). Lore backs trimmed to two facts each (the spec's
  2–3) to fit the larger type; the through-running scope point lives on
  Method. Re-verified 375/768/1280, keyboard, reduced-motion, console
  clean. Gate unchanged: owner verdict on the revised live page.

**D23 · Roster recurated: the owner's ranked 16 — RATIFIED 2026-06-12
(owner-directed at the D22 page review; picks recorded verbatim from the
session log after a crash-rewind).**
Owner, on the live page: questioned Cairo's seat ("is there a reason we
have cairo versus other metro systems?") and supplied a ranked 15-list
with a one-line reason per city (Tokyo, Seoul, Singapore, Hong Kong,
Paris, Shanghai, Beijing, London, New York, Madrid, Moscow, Copenhagen,
Delhi, Guangzhou-or-Shenzhen, Mexico City). Forks asked and picked:
- **Keep Cairo → deck of 16** (it was D3's only Africa rep, holds the
  ledger's cleanest diagram: CC0, current, tap-ready; "the African
  pioneer, 1987" fits the owner's distinct-model grammar).
- **Guangzhou takes the Pearl River Delta seat** (over Shenzhen).
- **Deck order = the owner's ranking** (Cairo 16th). The D16-era roster
  order dies; deck numbers renumber.
Consequences: D3 is superseded (12 → 16). Beijing's "why not" entry
reverses: Beijing joins as the capital mega-system, and Method's
absence-is-content note now names Shenzhen, Osaka, São Paulo, Istanbul
and Mumbai as the ones outside the deck. The four newcomers (Beijing,
Madrid, Copenhagen, Guangzhou) need BOTH audits at scale-up: the OSM
validator source check (Beijing already GOOD in DATA-CONTRACT's table;
Madrid/Copenhagen/Guangzhou not yet audited) and a DIAGRAM-LEDGER stanza
(none of the four audited). Until then their soon cards read "diagram
audit pending", never claiming a sourced lore back.
Same round, same owner message, all shipped with this entry: masthead
paragraph replaced (owner: "not sure what it is trying to convey"; pick:
premise + verbs: "Stat cards for the world's great metro systems, every
number dated and sourced. Flip a card for the lore; pick a stat and beat
the cpu; one guess a day in the daily."), nav tabs to the sans stack at
12.5px/600 (owner disliked the mono nav font and its legibility), and a
further daily type bump (the iOS-legibility flag: head/stat/meta/verdict
/streak/note all up one step).
*Revision (2026-06-12, owner on the live page):* the "Why sixteen" Method
section is CUT ("is this part even necessary?"), and the absence note
("def not necessary") with it. The per-city rationale was the wrong grain
for the page: it lives here in this entry as working material, and
surfaces for visitors as each card's own lore-back facts at scale-up.
With Beijing in the deck, no absence demands an on-page explanation;
"absence is content" retires with D3's roster. Method ends on the
licensing story.
*Revision 2 (2026-06-12, owner: "to fill up the row, how about 18 cards
instead of 16?"):* measured first: the deck grid was even at 4-col
desktop and 2-col tablet; only the 3-column band (~906-1200px windows)
orphaned one card, and 18 would have evened that band while breaking
full desktop (4-4-4-4-2; only multiples of 12 are even at both). Owner
picked the grid fix over the roster change: **deck stays 16; the grid's
column count is locked to 1 / 2 / 4 and never renders 3 columns**
(style.css media queries replace auto-fit). Verified even rows with no
overflow at 375 / 768 / 1000 / 1280. Bench note, should the deck ever
grow: the owner's picks for two more seats are **Osaka and Istanbul**
(over São Paulo and Mumbai).

**D24 · Themed stat sets ride the scale-up — RATIFIED 2026-06-12 (owner
idea at the D22 review; sequencing pick recorded).**
Owner: "its a shame we dont give other interesting info like frequency
and fare and integration etc. maybe we have different themes of info that
the deck entries changes per the theme?" Pick: **build themes into the
roster scale-up** (not this build, not a separate later phase). Design
note for the scale-up: themes are alternate stat SETS on the same card
object (e.g. service: frequency/hours; money: fares/farebox; integration:
through-running/airport link), switched at deck level. The D2 tension is
real and recorded: fares were cut at D2 over the freshness treadmill;
themes revive such facts as dated almanac snapshots (source + as-of,
annual refresh per D6), never as live utility info. Nothing themed
renders in this build; the generator carries the decision as a comment.

**D25 · Per-city scope freezes (rider-scope B operationalized) · PROPOSED
2026-06-12 (built into the gate-3 page; the owner verdict at the preview
gate ratifies).**
The D21 rider-scope B rule, made operational: a card claims the city's
metro network AS ITS FAMILIAR MAP DRAWS IT as coequal metro lines; modes
the map itself marks as distinct products (commuter overlays, trams,
feeders, people-movers) stay out. The full per-city ref sets live in
DATA-CONTRACT.md (now frozen) and `build_page_geometry.py`; Method
carries the prose. The named hard cases close as follows:
- **Seoul L1 (the long-deferred hard one): IN, whole corridor.** The
  familiar capital map draws Line 1 end to end as one line, so the card
  claims it. Seoul's scope is the full capital-region network incl. the
  Korail K-lines, GTX-A, AREX, light metros and Incheon 1-2 (the owner
  flagged Seoul's missing lines at D20; this answers it). Two snapshot
  gaps, declared rather than papered over: Sinbundang's validator export
  is empty, so plotted counts omit it; same for Beijing's Yizhuang T1
  tram. Declared scope and reported figures include both; Method says so.
- **Guangzhou vs Foshan: Guangfo IN, Foshan-proper OUT.** The Guangfo
  line is drawn coequal on the Guangzhou map and run by the GZ Metro
  group; Foshan's own lines (F2/F3 in the OSM file) are another system.
  APM in; trams out; the stray Qingyuan maglev out.
- **Copenhagen: M1-M4 only.** S-tog is a distinct product.
- **Madrid: Metro 1-12 + Ramal; Metro Ligero OUT** (ML-branded distinct
  product on the official plano).
- **Moscow MCC: IN (supersedes the old exclude note).** The map draws the
  MCC as coequal line 14; the D-branded MCD diameters stay out.
- **Hong Kong Airport Express: IN** (drawn coequal on the MTR map);
  Light Rail out.
- Identity folds so pills match the rider map: Beijing Batong into 1 and
  Daxing into 4; NYC rush diamonds into their base services and the three
  S shuttles as one pill; Moscow 4A into 4; Delhi's Blue branch into Blue.
Also frozen here, the pipeline-stage stat definitions the cards now use:
**stations** = named station points within 90 m of an in-scope vertex,
same-named points merged within 350 m, interchanges once (the old 60 m
point-grid rule inflated unevenly: NYC plotted 2.9x its official count,
Copenhagen 1.6x, which would have biased two stats); **density** moves to
the convex-hull basis (D20's pipeline commitment); **span** is exact over
hull vertices; **opened** = earliest regular passenger service within the
declared scope, the system's own dating (Beijing dates itself 1969;
the public-access-1971 nuance lives in the almanac note).

**D26 · Gate-3 scale-up build: 16 live cards, themes, almanac · PROPOSED
2026-06-12 (the owner verdict on the preview ratifies; this entry is the
build record).**
- **Roster:** all 16 cards live (flip-to-lore, lazy diagrams); the soon
  slots and the "3 OF 16" badge retire. Card canvas grows 420 to 460 px
  so the big pill decks (Beijing 27, Seoul 23) and six core rows share
  the face; the deck grid stays 1/2/4 columns (D23 rev 2).
- **Dual audit done** for the D23 newcomers: Madrid / Copenhagen /
  Guangzhou audited GOOD on the OSM validator (DATA-CONTRACT table);
  DIAGRAM-LEDGER stanzas added for all four with licenses verified on
  the Commons pages and structure graded on the downloaded files
  (Copenhagen interactive-ready 6,719 text nodes; Beijing and Madrid
  pan-zoom-only; Guangzhou raster-only). Guangzhou call recorded in its
  stanza: on the deck's fastest-growing network, the current clean
  raster beats a watermarked personal-style SVG and a 2023-frozen
  official-idiom SVG that would contradict the card's own 19 pills.
  All 13 missing lore-back diagrams downloaded (serialized, long
  backoff per the Wikimedia throttle) and committed to assets/.
- **Themes (D24) ship as CORE / SERVICE / MONEY**, a deck-level switch;
  the cards re-render rows per theme. SERVICE: best headway, service
  day, driverless lines. MONEY: fare from (USD-converted, dated),
  farebox recovery. Every themed figure carries source + as-of on
  Method; a card missing a themed figure drops that row (the D22
  hide-not-Unknown pattern). Integration (the third D24 example) is
  deferred: it lacks three honest, uniformly sourceable numeric stats;
  revisit when it has them.
- **Battle and daily stay on the core six**, where every card carries
  every stat: opened, stations, span, density, and the returning
  route-km + ridership (scope-matched, dated, sourced almanac rows per
  the D22 owner call). Battles can now tie at year/figure grain: a dead
  heat scores nobody and says so. The daily rotates across all six.
- **Almanac:** per-city opened year + per-line opened years, route-km,
  annual ridership, and the theme figures, all researched against live
  pages this session with source + as-of recorded in
  `_scripts/world_metros/almanac.json` (committed). Known soft spots
  recorded there as notes: farebox years vary widely by city (Madrid's
  newest published ratio is 2007); Seoul and Moscow ridership are
  same-year component sums (Seoul's whole capital network has no single
  published total, so it is summed from Korea Railroad Statistics 2024 and
  cross-checks against Seoul Metro's own 2,417.5M for lines 1-8; Moscow is
  metro plus MCC); Tokyo ridership sums the two operators' published
  annual actuals (FY2024).
- **Lore backs:** all 16 carry the ledger diagram (attribution verbatim,
  currency caveats where flagged), one flavor line, two curated facts;
  epithets drafted for the 13 new cards (owner reviews at the gate).
- Method gains the frozen scope table, the theme definitions with win
  directions, and per-figure source tables; it stays method (no roster
  editorial, per the D23 revision).

**D27 · Deck grows to EIGHTEEN; grid capped at 3 columns (1/2/3, never 4)
- RATIFIED 2026-06-12 (owner, design session; supersedes D23 rev 2's
  1/2/4 lock and its "deck stays 16" line).**
_Numbering note: the owner labeled this "D25", but the gate-3 build
session had already appended D25 (per-city scope freezes) and D26 (build
record) as PROPOSED, and DATA-CONTRACT / STATUS / code comments reference
them. Recorded as D27 to keep the log append-only; content is the owner's
verbatim decision._
Owner: "i do not like 2 cards per row visual i think 3 was much better."
18 is even at 3-col and 2-col (and 1-col), so rows fill at every width;
16 only evened at 2-col and 4-col, which forced the 4-col lock the owner
now reverses.
- **Roster += Osaka, Istanbul** as 17/18 (the D23 rev-2 bench note
  pre-picked them over Sao Paulo and Mumbai). Full newcomer pipeline for
  both: OSM validator audit, DIAGRAM-LEDGER stanza, rider-scope-B scope
  freeze (Osaka: Osaka Metro proper, through-running truncated at the
  boundary; Istanbul: the metro/M-lines, with Marmaray and the trams as
  the scope question), almanac + lore backs + epithet. Taken to live this
  session where the audits clear; a card whose audit does not clear stays
  a "diagram audit pending" soon card and the badge counts it out.
- **Grid: 1 / 2 / 3 columns, no 4-col tier.** style.css media tiers:
  1 col base, 2 cols from ~612px, 3 cols from ~906px. Verify by DOM probe
  at 375 / 768 / 1000 / 1280 (1280 now renders 3, not 4).
- **All count strings 16 -> 18:** DECK_WORD "eighteen", deck-back
  "eighteen systems · one deck", livebadge, method "full deck of 18",
  meta description, ORDINAL range, aria labels (auto from len(ROSTER)),
  README / BUILD-SPEC / STATUS counts.
- **PRIORITY (owner): Seoul first.** The owner asked when Seoul's lines
  would be complete. Do the Seoul scope freeze (the L1 / through-running
  rule, DATA-CONTRACT) and the full rider-network re-extraction FIRST,
  not last. (Status entering D27: the D25 freeze already takes Seoul as
  the whole capital network with L1's through-running corridor IN, 23
  line identities extracted; the known gap is Sinbundang, whose OSM
  validator export is empty. D27's Seoul-first work closes or documents
  that gap before the newcomers.)

**D28 · Stat sets recomposed on verified fetchability: PLAY + ALMANAC -
RATIFIED 2026-06-12 (owner, design session; supersedes D24's CORE /
SERVICE / MONEY theme trio and the parts of D26/D27 that described it).**
_Numbering note: the owner labeled this "D26"; D26 (the gate-3 build
record) and D27 (deck of 18) were already appended this session, so it is
recorded as D28 to keep the log append-only. Content is the owner's
verbatim decision, composed from a source-checked menu after flagging
thin themes and unclear labels._
- **Two sets, one toggle: PLAY and ALMANAC.** CORE/SERVICE/MONEY die.
  - PLAY = the ratified six (opened, stations, span, density, route-km,
    ridership, as they source).
  - ALMANAC = base fare + driverless lines + interchange share.
- **Cut from cards entirely:** peak/best headway and service day/hours
  (no comparable source exists; per-operator timetable archaeology), and
  farebox recovery (owner did not pick it; the central comparison table
  is FY2018 Tokyo / 2007 Madrid with ~7 of 18 cities missing). The
  shipped Tokyo farebox 161.55% was an FY2018 figure at false precision;
  nothing like it ships again. Famous individual cases (e.g. Paris
  85-second headways) may surface as lore-back facts where citable. The
  researched headway/hours/farebox figures stay in almanac.json as
  sourced reference, but render nowhere on the cards.
- **ALMANAC definitions (Method records each):**
  - BASE FARE: adult single minimum fare, USD at ONE dated FX rate for
    all cards (owner-ratified); the FX date is named in the card foot and
    Method. Lower wins. 2 decimals.
  - DRIVERLESS: count of GoA3+ lines within the card's declared scope,
    from Wikipedia's driverless-train-systems list (cite revision). More
    wins. Integer; "lines" unit.
  - INTERCHANGE: share of station complexes served by 2+ counted lines,
    computed from our own snapshot (the long-planned 7th lens). More
    wins. Whole percent.
- **Labels (owner flagged clarity), exact:** BASE FARE, DRIVERLESS,
  INTERCHANGE. Switcher: two pills, PLAY | ALMANAC; the fine-print
  trailer leaves the bar (Method carries it).
- **Battle stays bound to the PLAY set** for now; almanac battling is a
  later owner call.
- **Layout fork (judged on the board, not pre-locked):** the three
  ALMANAC rows must not leave the void the owner flagged on sparse cards.
  The almanac view ships with a default fuller-row layout, shown on the
  same board as the pill-density candidates (C1/C2) so both are judged by
  eye together.
- Priority order unchanged: Seoul scope freeze first (done at D25/D27);
  D28 lands with the board round.

**D29 · Pill-density: C2 adaptive band picked; occlusion bug fixed -
RATIFIED 2026-06-12 (owner on the board: "C2 adaptive band seems pretty
good").**
- **Bug fix (unconditional, shipped):** at high pill counts the pills (a
  flex item in a fixed-height column) were shrunk and overflowed the tag
  and ledger. Fixed: `.cpills { flex: none }` plus a front-drives-height
  flip so the card grows, so the line/scope tag is never occluded at any
  count. Verified deck + battle + 375/768/1000/1280.
- **C2 ratified, then made UNIVERSAL:** the refs collapse to one thin
  colour band (the deck-back motif) plus count + scope + "on the map
  side"; the readable line names live on the lore-back diagram. C2 first
  shipped as adaptive (band only over 16 lines, pills below). _Revision
  2026-06-12: the owner rejected the pills/band MIX as inconsistent
  ("either every city pills or density, not mixed; the mix looks bad")
  and the band is now EVERY card._ All-pills was the alternative but
  reintroduces the mega-card density problem this round fixed; all-band
  is uniform and keeps every card at 487px. This retires pills as the
  on-front identity device (D18/D20); line identity now reads on the lore
  diagram for all cards. The BAND_THRESHOLD and the variable-height pill
  machinery are vestigial (all cards uniform now).
- **Board fixes folded in:** seam cities (Guangzhou, NYC) added to the
  judged set; counts render from len(lines) (Seoul reads 24, not the
  stale 23); the band copy is "on the map side" (the lore back is the
  diagram, which labels lines its own way, not our refs).
- **Band made universal (revision, 2026-06-12):** see the C2 bullet above;
  the owner rejected the pills/band mix, so every card now wears the band.
- **Head restructure DONE (2026-06-12, owner took the rec):** the core
  line (count + scope, e.g. "13 lines · Metro + Toei") moves UP to be the
  card subtitle under the city name; the band drops its tag (no repeat, no
  clip); the epithet ("the two crews") moves to the lore back as its blue
  subtitle (replacing the system-name line there; the system name stays in
  the diagram alt + credit). Card min-height retuned 486 -> 469 so the
  shorter head leaves no gap above the foot. Verified play/almanac gap 0,
  battle fit, 375-1280, console clean.
- **Second set grown to FIVE (2026-06-12):** base fare, driverless,
  interchange, plus two computed growth stats (new lines opened since
  2016; newest line year), after the owner asked about update-frequency /
  profitability. Profitability stays out (it is the cut farebox: 7 of 18
  missing, incomparable); the forward construction pipeline stays out
  (freshness trap). A background research chip is out for more candidates.
- **Still open (owner):** the set NAMES (PLAY / ALMANAC are placeholders
  the owner dislikes; proposal on the table is SCALE + CHARACTER, or the
  research-chip menu may reshape the second set first).

**D30 · The daily gets smart: close duels + pick-the-number - RATIFIED
2026-06-12 (owner flag on a giveaway question: "which plots more
stations, Hong Kong vs Shanghai... too easy and obvious; the quiz should
be smarter than this"; forms picked from the owner's own list).**
- **Two question forms, deterministic per day** (date hash picks stat,
  form and contestants):
  - **DUEL**: head-to-head only between CLOSE systems: values within 30
    percent (12 years for opened), never equal, so no blowouts. Pools are
    healthy (23 to 40 eligible pairs per stat across the 18). Example
    dailies: Singapore 243 vs Paris 246 route-km; Moscow 267 vs Delhi 270
    stations; Singapore 1987 vs Istanbul 1989 opened.
  - **PICK**: one city, four candidate values; the wrong three are other
    cities' REAL figures nearest the truth (honest distractors), truth's
    slot hash-placed. Example: "How many stations does SINGAPORE plot?"
    176 / 159 / 195 / 135.
  - Roughly even mix over time (27/33 across a 60-day simulation).
- **The choice cards drop their pills for the colour band** (consistent
  with D29's universal band, and ref text no longer leaks network size;
  with close pairs, stripe count stops correlating with the answer).
- Battle unchanged (the owner: "battle type is fine"). Streak/localStorage
  unchanged; the store gains a mode field (an old same-day save without
  one just lets the player replay once, soft-launch grade).
- Method's daily paragraph documents both forms. Verified by simulating
  14 dated challenges (all duels close, all picks well-formed) plus live
  plays of both forms, 375/1280, console clean.
- _Revision (2026-06-12, owner review of the bank):_ the date hash gained
  an avalanche finalizer. Without it, consecutive dates correlated (the
  same city six pick-days running, exact question repeats a week apart);
  with it the 30-day simulation interleaves cities and forms cleanly.
  The full question space is enumerable: 176 eligible duels + 108 pick
  questions = 284. `mocks/build_daily_bank_board.py` bakes the complete
  bank plus the literal next-120-day schedule for owner review
  (`mocks/daily-bank-board.html`), with its Python selection logic
  parity-checked 30/30 days against the page's real JS. Known property:
  hash collisions can repeat a question within a week or two (one in the
  current 30-day window); a no-repeat window is a possible follow-up.

**D31 · Second set recomposed + named: SCALE / CHARACTER - RATIFIED
2026-06-12 (owner, resolving D29's open naming and the research-chip menu).**
_Numbering note: D30 (the daily revamp) was appended this session, so the
research-chip resolution is D31._
The background research chip from D29 returned a ranked menu (six parallel
agents verified coverage across all 18 cities against live sources). Owner
picks, composed from that menu:
- **Swap, not add (owner): drop `newest line`, add `BIGGEST HUB`.** Newest
  line was redundant growth with new-lines (both cluster the fast-growers at
  2024-25); biggest hub is a NEW computed lens, the most counted lines that
  meet at one station complex. It is free: the per-complex line-sets already
  drive interchange, so `max(len(rs))` is one line in build_page_geometry.py.
  All-18, low-freshness (snapshot-grade), spread 2 (Cairo, Delhi, Mexico
  City, Istanbul) to 9 (NYC), London 6 at King's Cross, Copenhagen 4.
- **Relabel the interchange-share row `transfer stations`** (owner flagged
  bare "interchange 22%" as confusing: the percent hid its denominator). The
  internal stat key stays `interchange`; only the visible label changed.
  Biggest hub is worded as a line COUNT, never a percent, so the two
  connectivity stats never blur. Both read NYC high for the same
  service-sharing reason (Method notes it).
- **Set NAMES: PLAY -> SCALE, ALMANAC -> CHARACTER** (display text only; the
  data-set keys stay play/almanac, so app.js and style.css are untouched).
  CHARACTER (5): base fare, driverless, transfer stations, biggest hub, new
  lines. Battle and daily stay bound to SCALE (the six).
- **Cut after research (do not re-propose):** step-free accessibility (11/18,
  four incompatible definitions), platform screen doors (9-13/18, ten cities
  mid-rollout = freshness trap), rolling stock (no consistent unit across the
  18: cars vs trainsets vs vehicles), average/commercial speed (4/18 publish
  it), busiest single station (10-12/18). Top design speed is comparable but
  mostly measures "has an airport express", so it stays out. Deepest station
  passed (15-17/18, wide spread) but the owner declined it. Women-only-car
  and 24-hour service are lore-fact grade, not stat grade.
- **Data:** biggest_hub computed from the frozen 2026-06-12 snapshot via the
  cached validator GeoJSON (no network, no drift: meta.json gains the one
  field, every other value byte-identical, as_of preserved).
- **Verified:** regenerated, DOM-probed at 375/768/1280 (1/2/3 columns, no
  overflow), toggle switches sets, battle stays SCALE-only (no biggest_hub
  leak), console clean. Open polish: `transfer stations` wraps to two lines
  on the narrow card (contained, no overlap or card growth, the CHARACTER
  rows carry the padding for it); `transfers` is a one-word single-line
  alternative if the owner prefers uniform single-line labels.
- **Ship state:** built on the gate-3 lineage (this branch fast-forwarded
  onto it); the whole gate-3 body (D25-D31) is not yet merged to master, so
  the merge to live is the owner's gate call, not an automatic push.
- _Revision (2026-06-12, owner):_ the card label is **`transfer`** (not
  `transfer stations`), which also resolves the two-line wrap; single line
  at every width. Owner then opened the gate: the whole gate-3 body
  (D25-D31) is squash-merged to master, so the soft-launched deck-of-18 is
  now the live page (noindex/unlisted norms unchanged).

_Numbering note (2026-06-12): this card-IA session ran in PARALLEL with
the session that appended D30 (the daily revamp) and D31 (the second set
recomposed + named SCALE / CHARACTER) and squash-merged them to master
first. This session's three decisions are therefore recorded as D32-D34
(its pre-merge worktree commits and its board artifact carry the original
D30-D32 labels; the board html keeps them as the round's record). Where
they overlap: the SCALE | CHARACTER names were picked independently in
both sessions and agree; D34 supersedes both sessions' toggle (one flip
now cycles the faces); D31's recomposed CHARACTER set (base fare,
driverless, transfer, biggest hub, new lines) is adopted unchanged and
renders on the CHARACTER face._

**D32 · Card-IA round: three candidates + the lore dedup - PROPOSED
2026-06-12 (board built; the owner verdict on the board is the gate).**
Owner flag: the card now has three views (play front, almanac front via
the deck toggle, the lore flip), "not entirely sure if they feel intuitive
and most appropriate", and "info in almanac and map content sometimes
overlap". Board: `mocks/card-ia-board.html`
(`mocks/build_card_ia_board.py`), Seoul the busy case + Tokyo the
reference, baseline TODAY row first:
- **A · KEEP + RENAME:** three views stay; PLAY/ALMANAC become honest
  names (SCALE | CHARACTER mocked; menu with CORE | CHARACTER and
  SYSTEM | RIDE as alternates); plus small toggle UX: a set caption on
  each card (mid-scroll state visibility) and a battle-binding whisper
  on the bar.
- **B · TWO SURFACES (recommendation):** the front toggle dies; the five
  character stats move to the lore back as a compact figure strip (small
  ordinals; 1st keeps the blue chip); the front is the six play stats the
  battle and daily actually use. Restores the D18 grammar (front for
  play, back for lore); the set-name question dissolves. Cost shown
  honestly on the board: pinned to the live flip height (the front
  drives the box at 469px), the diagram window pays for the strip,
  178px down to ~125px (Seoul) / ~155px (Tokyo) / ~112px (Mexico City,
  wordiest); the deck-wide scan of the second set moves to Method's
  table. Alternative lever noted: let the flip box size to the taller
  face instead (cards grow).
- **C · NO MODES:** both sets on one face (six rows + a fine-print
  strip); zero hidden state; measured +98px per card and the battle
  arena's fixed slots would retune.
- **Overlap map, all 18 backs vs the shown stats:** 26 collisions,
  including three outright contradictions (Singapore flavor "four of
  them driverless" vs DRIVERLESS 6 after the NSL/EWL conversions;
  Shanghai fact "five lines driverless" vs stat 7 incl. GoA3; NYC fact
  "472 stations" vs the plotted 504 on the same card), plus 12
  deliberate keeps (Hong Kong's 1910 East Rail fact is the model: it
  explains a stat rather than restating one).
- **Dedup edit list: 26 edits across 17 cards (Hong Kong untouched),
  candidate-invariant** (every candidate keeps all eleven numbers
  somewhere on the card). Listed on the board with replacement copy
  written to ship; NOT applied before the verdict. Watch-items recorded
  for the pending second-set research menu (Guangzhou 160 km/h vs a
  speed stat, Moscow 80 s vs headway, NYC/Copenhagen 24/7 vs hours,
  Osaka's 1981-vs-1991 driverless dating): re-run the dedup pass against
  the final set composition before it ships.
Gate: owner picks A (plus a name pair) / B / C; the pick and the edit
list then build into the live page and Method and re-verify. The
deck-of-18 ship gate (push/PR/merge) stays the separate pending yes.
*Resolution (2026-06-12, owner on the board):* **B and C REJECTED** ("the
ui change u showed me with base fare and driverless etc shoved into
either front or the back were all ugly and ui wise it basically ruined
it"); the character info is "interesting and good to have", so it stays
on the cards and the toggle survives. Three views acknowledged as not
ideal but stand as the shape, pending A's polish (honest names + set
caption + binding whisper; name pair still the owner's pick). **The lore
bar restated by the owner:** facts are fine as long as they are
factually correct, carry no copyright entanglement, and earn their keep
by being interesting; number restates are TOLERATED. The round-1 26-edit
dedup therefore shrinks to the SLIM LIST: 3 must-fixes (Singapore
"four driverless" is stale, all six MRT lines are GoA4 now; Shanghai
"five lines driverless" vs the shown 7; Osaka "driverless since 1981" vs
the source dating GoA4 to 1991, fixed with "automated"), 7 repeat-swaps
(a back saying the same thing twice wastes a slot: Tokyo, Madrid,
Moscow, Mexico City flavors; Cairo, Osaka fact 1; Istanbul fact 2), and
1 optional NYC clarifier (officially-true 472 beside the plotted 504,
owner's call). The owner also flagged the round-1 edit-list presentation
as hard to read; the board was rebuilt in place (round 2): A reframed as
the standing shape, the slim list in a full-width readable form with the
copyright note (facts not copyrightable, phrasing ours, sources in
almanac.json, no curated collection copied), B/C/exhibit/tradeoff kept
as dimmed round-1 records. Open to close the round: the set-name pair
(SCALE | CHARACTER recommended) and a yes on the slim list.
*Resolution 2 (2026-06-12, owner: "by copy i meants doesnt feel too
written. i think ur recs are fine") - D32 RATIFIED AND SHIPPED.* The
"copyright" concern was copywriting, not law: lore must not feel too
WRITTEN (the repo's plain-not-poetic rule applied to the cards). Recs
approved as-is. Shipped the same session, with a plain-pass over the
new lines (Tokyo / Madrid / Moscow flavors, Cairo / Osaka facts
simplified; e.g. "Run so tightly that..." became "Trains run to the
minute;..."):
- content.json: the 11 slim edits applied (incl. the NYC clarifier,
  taken per the rec).
- Set names SCALE | CHARACTER live: theme bar relabeled (internal keys
  stay play/almanac), binding whisper "the battle and the daily play
  SCALE" added, deck-only set captions via style.css ::before (battle
  cards are SCALE-bound, no caption), flip button's flipped label
  PLAY SIDE -> STAT SIDE (app.js).
- Method: "SCALE: the six", "CHARACTER: the five" with the previously
  missing new-lines and newest-line definitions added (a D29 gap), the
  battle binding line, details summary, meta description all renamed.
- Verified: toggle/captions/whisper by DOM probe, all 18 lore backs
  unclipped, 375/768/1280 at 1/2/3 columns with no overflow, console
  clean. Board restamped as the round's record. The card-IA round is
  closed; the deck-of-18 ship gate remains the separate pending yes.

**D33 · URL moves to /is/building/metro-match/ - RATIFIED 2026-06-12
(owner: "it should not be world metro in URL but metro match. Check
with me before publish"; supersedes D21's "the URL stays" note).**
The page directory moved wholesale (index.html, style.css, app.js,
assets/) to `is/building/metro-match/`; a noindex meta-refresh stub
(house redirect pattern, canonical to the new URL) sits at the old
`world-metros` path, since that URL has been live soft-launched since
2026-06-11. Functional path updates: `build_metro_cards.py` PAGE,
`build_page_geometry.py` OUT_DIR, the two living mock boards' absolute
style/asset links (regenerated); living docs (README, BUILD-SPEC,
DIAGRAM-LEDGER, repo CLAUDE.md) updated. Internal names deliberately
stay: the `_scripts/world_metros/` dev dir, the `world-metros-atlas`
registry stanza, and historical URLs inside past DECISIONS/STATUS
entries (history is history). The registry stanza gains the new URL at
ship time. Per the owner's note, NOTHING IS PUBLISHED: the move is
committed on the branch and rides the same single ship gate (owner
check before push/PR/merge).

**D34 · One flip cycles three faces: SCALE -> CHARACTER -> MAP -
RATIFIED 2026-06-12 (owner: "might be better to maybe jsut have three
flips... jus flip let it go through three faces one by obe"; supersedes
the D32 standing shape and the toggle the parallel session reaffirmed at D31; amends D18's two-side grammar).**
The deck-level SCALE | CHARACTER toggle dies; the card flip is the whole
interaction. Each flip is a real 180-degree turn: rotation accumulates
and app.js mounts the next face into whichever slot is hidden before the
turn (two physical slots, a stash parks the third card), so the cycle
reads as one continuous gesture. Implementation notes:
- Generator: deck cards render TWO single-ledger fronts (scale,
  character; each keeps its D32 set caption) plus the map side in a
  hidden stash; `theme_switch()` deleted; intro reads "Each card has
  three faces: scale, character, the map. Flip to cycle them."
- app.js: cycling flip with height locked at first interaction (the box
  freezes at the front height, 489px, so the shorter map card cannot
  collapse it); diagrams still lazy-load, now on the map turn; the flip
  button names the NEXT face (FLIP - CHARACTER / MAP / SCALE) and stays
  the keyboard path; aria-hidden tracks the visible slot.
- style.css: f-a / f-b slot grammar (f-b pre-rotated), .locked absolute
  faces, .facestash hidden; the old deckgrid[data-set] switching CSS
  removed (each face carries one ledger); themebar CSS retained only
  because the round-record mocks reference it.
- Battle and daily untouched (SCALE-bound; battle cards carry no
  caption); Method's "second face" wording updated; reduced-motion
  still degrades to instant swaps (the transition is the only motion).
- Verified by DOM probe: full cycle x2 incl. wrap, height locked at 489
  through all faces, captions per face, lazy diagram on the map turn,
  battle round resolves, daily intact, 375/768/1280 at 1/2/3 columns
  with no overflow, console clean.
Ship note, same message: the owner said "u can put it on metromatch.
but dont list on building page yet. i will be testing": publish
authorized (push/PR/merge), soft-launch norms STAY (noindex, no
sitemap, no /is/building hub card, no home teaser) while the owner
tests live.

**D35 · Header polish: one frame, no badge, wordmark is the way back -
RATIFIED 2026-06-12 (owner flagged the badge, the dead wordmark and the
horizontal misalignment; picked the recommended slate: B + cut + #deck).**
- **Alignment (option B):** the header content moves into an `.hframe`
  that mirrors main's column exactly (max-width 1240, same side padding),
  so the chrome and the content share one frame at every width (measured:
  wordmark x equals the masthead text edge at 1990 and 1280). The
  masthead paragraph centers over the centered deck, joining the one axis
  every other surface already uses (deck, battle, daily, method); it was
  the page's only left-anchored stray.
- **DECK OF 18 badge CUT:** it was the soft-launch progress badge ("3 OF
  16 LIVE"); with the full deck live it repeated what the masthead and
  every card number already say. Styles pruned.
- **Wordmark clickable:** METRO MATCH links to #deck (an in-page anchor:
  exempt from the analytics.js new-tab retarget, handled by the existing
  hash router), so the logo acts as the app's way back to the deck from
  battle / daily / method. The way home to ajin.im stays the footer
  colophon, per the bespoke-tier rule.
- Verified by DOM probe: frame alignment at 1990/1280, intro-grid axis
  delta 0, wordmark click returns battle to deck, nav wrap at 375, no
  overflow at 375/768/1280, console clean.
