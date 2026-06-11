# STATUS — World Metros Atlas

_Last updated: 2026-06-11 (Claude session, branch `claude/world-metros-mocks`)._

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

## Current gate — owner verdict on (a) round-2 boards and (b) the D11 familiar-diagram proposal

All three forks were ratified 2026-06-11 (D9). The first board round (Electric
Cartography, dark) was rejected by the owner at the gate; direction pivoted to
the **official-map idiom on white** (D10) and the three boards were rebuilt the
same day: `mocks/explore-desktop.html`, `mocks/shape-desktop.html`,
`mocks/explore-mobile.html` (generator: `mocks/build_mock_boards.py`, real
Seoul + Paris geometry).

## Next exact action (after board approval)

Build the coded Seoul Explore + Seoul/Paris Shape prototype (D8 gate 2) in the
approved direction: real interactivity (pan/zoom, line select, pair sync), still
only two cities, no scaling to the roster until the second approval.

## Blockers

None. (Seoul L1 scope rule is deliberately deferred to the pipeline stage,
DATA-CONTRACT.md — it does not block the mock boards.)
