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

- D11 RATIFIED 2026-06-11: owner approved the familiar-diagram layer via the
  diagram mock + interactivity spike and by launching the gate-2 build. D12
  records the prototype scope (three cities: Seoul, Paris, Tokyo; diagram +
  true-shape modes; Seoul×Paris shape pair; stubs for Rankings/Method).

## Current gate — owner verdict on the live coded prototype (D8 gate 2),
## now bundled with the D13 consistency fork (A / B / C)

Bake-off verdict landed (2026-06-12): all three candidates usable, none is
hero-grade; owner wants the UI reconsidered with the map demoted. **D15
(PROPOSED)** records the atlas-page proposal: same-scale silhouette wall as
the landing hero, city dossiers as the dwell surface, maps as figures,
Explore canvas + Commons diagram demoted to per-city secondary views,
embeds at most a small "locate it" element. Owner pick pending:
wall (rec) · rankings-first · dossier-first. If wall: next step is the
landing-board mock (3 real cities + 9 placeholders; no roster scale-up
before the D8 prototype approval). Earlier bake-off context: board at
`mocks/bakeoff-board.html` (D14); octolinear local pipeline stays prepped
(`mocks/loom_convert.py`) should the schematic ever be wanted as a dossier
figure.

The coded prototype is BUILT (this session, branch
`claude/confident-margulis-10e030`): real page at `/is/building/world-metros/`
(https://ajin.im/is/building/world-metros/ once merged), soft-launch state
(noindex; the sitemap builder auto-skips noindex pages; no hub card; no teaser),
official-map idiom per the round-2 boards, scope per D12. Verified: 375/768/1280,
keyboard tabs + map keys, station tap (Seoul Hongik / Paris Bastille), Tokyo
degraded treatment, shared px-per-km identical across the Shape pair, sync zoom,
lazy-load (only meta.json + the Seoul diagram at boot), zero console errors.
Geometry: `build_page_geometry.py` emits per-city JSON (Seoul 48 KB / Paris 19 KB
/ Tokyo 22 KB + meta 1.5 KB); Tokyo merges the validator's pre-split
`tokyo` + `tokyo_-_toei` networks, refs filtered to Metro+Toei, the `Al`
through-service excluded.

## Next exact action (after prototype approval)

Scale to the remaining 9 roster cities (D3): per-city diagram assets per
DIAGRAM-LEDGER, per-city True Shape JSON with frozen scope rules
(DATA-CONTRACT — Seoul L1 is the hard one), Rankings + Method built for real.

## Blockers

None. (Seoul L1 scope rule is deliberately deferred to the pipeline stage,
DATA-CONTRACT.md — the prototype keeps the mocks' lines 2–9 scope.)
