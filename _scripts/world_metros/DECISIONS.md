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
