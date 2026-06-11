# STATUS — World Metros Atlas

_Last updated: 2026-06-11 (Claude session, branch `claude/confident-margulis-10e030`)._

## Done

- Deep research (2026-06-11): niche verified open; data/licensing landscape mapped.
- Codex plan received (in-session only — produced **no files/commits**; verified).
- Critical assessment of the plan → trimmed v1 contract (BUILD-SPEC.md, D1–D7).
- Data audit: all 13 candidate cities GOOD on the OSM subway validator; per-city
  GeoJSON confirmed drawable (real line colours); sizes recorded (DATA-CONTRACT.md).
- End-to-end proof: same-scale Seoul (lines 2–9) vs Paris SVG render from raw CDN
  GeoJSON (`proof_same_scale.py`). Seoul's through-running scope problem quantified
  (~148 km bbox; L1 = 26 service variants).
- This doc set + registry stanza (`world-metros-atlas` in `~/projects.md`).
- Forks ratified (D9); mock boards round 1 built (Electric Cartography), rejected
  at gate; round 2 rebuilt in the official-map idiom (D10) with fixes: RDP
  closed-ring handling (Line 2 loop), outlier-aware station filtering, Paris
  stray-fragment guard.

- D11 mock built: `mocks/diagram-desktop.html` — Explore in DIAGRAM mode with the
  real Commons Seoul map (Satellizer, CC BY-SA 4.0, bilingual, marks 2026 openings)
  embedded at `mocks/assets/seoul-diagram.svg`, mode toggle + attribution in place.

- Interactivity spike PROVEN on the Commons diagram (`mocks/diagram-interactive.html`):
  viewBox pan/zoom/pinch + station-label tap (1,847 real text nodes; verified live —
  zoomTo/tap on "Hongik University"). Caveat: tap-ability requires real <text> nodes;
  the 12-city diagram audit must grade each file's structure, not just its license.

- D11 per-city diagram sourcing audit done: `DIAGRAM-LEDGER.md` — all 12 roster
  cities have a chosen file + fallback; every license verified on the actual Commons
  page data/wikitext (catch: the "official" CDMX iconographic upload is deletion-
  nominated over Wyman icon IP — excluded), every structure grade verified by
  downloading + counting nodes (working-map lineages keep real `<text>`; the
  print-faithful Shanghai/Tokyo/NYC recreations are outlined → pan-zoom-only).
  Official-artwork checks: Seoul KOGL Type 3 (ND, static-only), CDMX LGACDMX
  (third-party-IP carve-out), DMRC (no open license). No city at no-good-option;
  Delhi flagged weakest (2020 base, four named missing openings).

- Coded prototype (D8 gate 2) BUILT and soft-launched 2026-06-11 at
  https://ajin.im/is/building/world-metros/ (PR #145: Explore diagram +
  true-shape, Seoul-Paris Shape pair, noindex/unlisted; full verification
  record in this file's git history). Map-direction mocks followed: bake-off
  D14 (PR #147), wall D15 (PR #149, rejected at gate).

- D11 RATIFIED 2026-06-11: owner approved the familiar-diagram layer via the
  diagram mock + interactivity spike and by launching the gate-2 build. D12
  records the prototype scope (three cities: Seoul, Paris, Tokyo; diagram +
  true-shape modes; Seoul×Paris shape pair; stubs for Rankings/Method).

## Current gate — owner verdict on the D16 Gallery + Duel proposal

The D15 wall board was REJECTED at its gate (owner: ugly). **D16 (PROPOSED)**
follows the four-round visual signal: the familiar Commons diagrams become the
site's visual language (uniform gallery frames; consistency from chrome, not
maps), and the engagement core shifts to head-to-head comparison: duel pages
with a tale-of-the-tape (paired lens bars, verdict lines, the same-scale pair
demoted to one "true size" row), superlative chips on gallery cards, podium
stories per ranking lens. Owner pick pending; if ratified, next gate artifact
is the gallery + SEOUL-vs-PARIS duel mock board. Prior boards stay in mocks/
for the record (wall-board.html, bakeoff-board.html, geo-shape-desktop.html).

## Next exact action (after D16 ratification)

Build the gallery + duel mock board (12 diagram cards with 3 real, one full
SEOUL vs PARIS duel with tale-of-the-tape). After that gate: rebuild the live
page into the Gallery + Duel IA, then scale to the remaining 9 roster cities
(D3) with frozen scope rules (DATA-CONTRACT — Seoul L1 is the hard one),
diagram assets per DIAGRAM-LEDGER, Rankings podiums + almanac for real.

## Blockers

None. (Seoul L1 scope rule is deliberately deferred to the pipeline stage,
DATA-CONTRACT.md — the prototype keeps the mocks' lines 2–9 scope.)
