# STATUS — World Metros Atlas

_Last updated: 2026-06-11 (Claude session, branch `claude/world-metros-scaffold`)._

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

## Current gate — owner (Ajin) ratification of three forks

1. **Scope trim (D2, D5, D6):** kill the practical-traveller layer; almanac table for
   reported figures; lighter process. → recommendation: yes.
2. **Roster (D3):** 12 = Codex 10 + Moscow + Hong Kong, Beijing as "why not" entry.
   → recommendation: yes; owner may prefer strict 10.
3. **Design (D7):** proceed to mock boards in Electric Cartography. → recommendation: yes.

## Next exact action (after ratification)

Build the three mock approval boards with **real Seoul + Paris geometry** in the
Electric Cartography direction: desktop Explore, desktop Compare/Shape (pair),
mobile Explore (375px). Static HTML/SVG, no frontend framework yet. Stop for
approval; record the verdict in DECISIONS.md.

## Blockers

None. (Seoul L1 scope rule is deliberately deferred to the pipeline stage,
DATA-CONTRACT.md — it does not block the mock boards.)
