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

## Current gate — owner verdict on the round-2 mock boards (D8 gate 1)

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
