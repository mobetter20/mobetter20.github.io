# BUILD-SPEC — World Metros Atlas (v1, trimmed)

This is the product/acceptance contract. It descends from the Codex plan of 2026-06-11
("World Metros Interactive Atlas") with deliberate trims recorded in DECISIONS.md (D2, D5–D7).
The original user brief is the fixed judge: *"fill my curiosity about interesting metro
systems in an easy-to-get view — not a complicated site with info scattered around."*

## North-Star (draft — owner to ratify)

A fast visual atlas for exploring the world's defining metro systems: compare their
physical forms at a true shared scale, see why each one is interesting, and rank them
only where a ranking can be honestly defined — without pretending there is one
objective best.

## Views (one URL, four tabs)

1. **Explore** — one city at a time: interactive pan/zoom map drawn from OSM geometry
   (real line colours), plus a compact profile card:
   opened year · reported route-km (dated) · stations · lines · reported annual
   ridership (dated) · 2–3 curated "why it's interesting" facts.
2. **Compare / Shape** — the signature view. All systems at one north-up
   pixels-per-kilometre scale. Pair mode with synchronized zoom; overlay translates
   network centres only (never rotates/resizes/warps); inline note that geography is
   not aligned.
3. **Rankings** — the five computed lenses (defined in DATA-CONTRACT.md), each with a
   one-paragraph "why this is rankable" explanation, **plus** a clearly-labelled
   "reported figures" almanac table (route-km, annual ridership) shown as dated,
   sourced facts — labelled by source basis, never blended with computed lenses.
4. **Method** — scope rules, definitions, sources, data as-of dates, licences, and a
   short **"why not X"** section (Beijing, Madrid, Istanbul, …) — absence is content.

## Explicitly OUT of v1 (do not let these creep back without a DECISIONS entry)

- The practical-traveller layer: fares / "first ride" / payment / open-loop gates /
  registration / planner languages / disruption info / integration matrices /
  accessibility evidence / cleanliness evidence. (D2: it's the crowded travel-utility
  space, and it drives a freshness treadmill a curiosity site doesn't owe.)
- Freshness SLA machinery (30/90/180-day tiers, auto-eviction from Compare).
  Replacement: every fact carries `source + as_of`; refresh is a scripted annual pass.
- Route planning, live positions, street basemap, official schematic reproduction.
- Aggregate scores of any kind. No "best metro" number.

## Design direction

**Official-map idiom** (owner-directed 2026-06-11, supersedes Electric Cartography
— see DECISIONS D10): white paper ground, the operators' real line colours (OSM
`stroke`), bold solid strokes, white-fill/ink-ring station dots; selecting a line
greys the rest of the network (the metro-app convention). Chrome: clean sans for
UI, DM Mono for data/provenance labels, transit-blue accent `#0052a4`, city chips
as pills, active tab underlined like a route line. The site dresses like the
artifact it describes. Official map ARTWORK is never embedded (licensing,
DATA-CONTRACT.md); every city card carries **"the map riders see →"** linking to
the operator's official diagram, and Method tells the licensing story. Bespoke
tier: own art, anchors only (way home, palette sympathy, DM Mono labels).

## Approval gates (in order)

1. **Mock boards** — desktop Explore, desktop Compare/Shape (pair), mobile Explore,
   built with real Seoul+Paris geometry. Owner approval recorded in DECISIONS.md.
2. **Coded prototype** — Seoul Explore + Seoul/Paris Shape pair. Second approval.
3. Scale to the full roster only after both.

## Soft-launch conditions (repo norm, chronogrid precedent)

`noindex` meta · not in sitemap · no `/is/building` hub card · no home-teaser line.
Site-wide `/analytics.js` loads as on every page (do not fight the site default).

## Acceptance checklist (v1)

- Verified at 375 / 768 / 1280 widths (repo CSS rule); keyboard reachable tabs +
  city switcher; `prefers-reduced-motion` respected (no glow pulse).
- Per-city geometry lazy-loaded; initial payload stays light (overview index +
  first city only). Raw OSM GeoJSON is simplified at build time, never shipped raw.
- ODbL attribution line for OSM data visible on every view; no official schematic
  imagery anywhere; UITP linked as background reading only, figures not republished.
- Every displayed fact resolves to `source + as_of` (visible on Method, hover or
  footnote elsewhere).
- Build is a deterministic `_scripts/world_metros/build_*.py` run over committed,
  dated data snapshots (network access only in the refresh step, never the build).
