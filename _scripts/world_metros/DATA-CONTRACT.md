# DATA-CONTRACT — World Metros Atlas

## Geometry source of truth (verified 2026-06-11)

**OSM via the subway preprocessor/validator CDN** — per-city GeoJSON, regenerated
~hourly from OSM `route=subway` relations:

- Index: `https://cdn.organicmaps.app/subway/` (321/325 networks validating clean)
- Per city: `https://cdn.organicmaps.app/subway/<slug>.geojson` (also `.yaml` with richer
  station/transfer detail)
- Format: `FeatureCollection` of `LineString` (props: `ref`, `name`, `stroke` = line
  colour) + `Point` stations. Drawable as-is.
- Pipeline: github.com/organicmaps/subways (Apache-2.0). Data: **ODbL** — attribution
  required ("© OpenStreetMap contributors, ODbL"); a derivative database must stay open.

Audit results, all candidates **GOOD** (raw GeoJSON size; build will simplify):

| city | slug | raw size |
|---|---|---|
| Shanghai | `shanghai` | 813 KB |
| Tokyo | `tokyo` | 925 KB |
| Seoul | `seoul` | 3.45 MB (capital-region net incl. through-running — see scope) |
| Singapore | `singapore` | 333 KB |
| Delhi | `delhi` | 330 KB |
| London | `london` | 2.65 MB |
| Paris | `paris` | 451 KB |
| New York | `new_york_city` | 1.58 MB (PATH/SIR/JFK are separate networks — pre-split for us) |
| Mexico City | `mexico_city` | 269 KB |
| Cairo | `cairo` | 176 KB |
| Moscow | `moscow` | 1.13 MB (proposed add, D3) |
| Hong Kong | `hong_kong` | 1.05 MB (proposed add, D3) |
| Beijing | `beijing` | 688 KB (proposed "why not" entry, D3) |

Re-verify any time: `python3 _scripts/world_metros/audit_osm_sources.py`.

## Refresh / freeze discipline

`refresh` (future script) fetches dated snapshots into a committed `data/` dir with
timestamps + checksums; `build` runs offline and deterministically over snapshots.
Facts carry `value · unit · source · as_of`. Missing evidence renders **Unknown**,
never "No" or zero. No SLA tiers (D6) — annual scripted refresh.

## System scopes (freeze before extraction; each gets a Method entry)

- Shanghai Metro — exclude maglev.
- Tokyo — Tokyo Metro + Toei only; truncate through-running at scope boundary.
- Seoul — **OPEN QUESTION (the hard one):** OSM network spans ~148 km north–south;
  `ref=1` alone carries ~26 Korail through-service variants (Cheonan/Incheon/Soyosan).
  "Lines 1–9 at marketed extents" (Codex) would still include ~200 km of Korail
  corridor. Candidate rule: lines 1–9 truncated to Seoul-Metro-operated sections;
  decide at pipeline stage with data in hand, record in DECISIONS.
- Singapore MRT — exclude LRT.
- Delhi Metro — as is.
- London Underground — exclude Elizabeth line.
- Paris Métro — 1–14 + 3bis/7bis; exclude RER. (Note: stray `LISA` ref and one outlier
  segment in raw data — build-step QA filters by known refs + bbox sanity.)
- NYC Subway — `new_york_city` network only (PATH, Staten Island, JFK already separate).
- Mexico City Metro — as is.
- Cairo Metro — exclude LRT + monorail.
- Moscow Metro — exclude Central Circle (MCC) + Diameters (MCD) if added.
- Hong Kong MTR — exclude light rail + Airport Express? (freeze before extraction).

Route variants: many service patterns share a `ref` (Seoul L1: 26). For Shape
rendering, union segments per ref. For counted lenses, count **customer-facing line
identities**, not variants.

## The five computed ranking lenses (from frozen snapshots; definitions are the product)

1. **Furthest-stations span** — max geodesic distance between two station complexes.
2. **Station complexes** — official identities; interchanges counted once.
3. **Customer-facing lines** — primary-map identities, excluding service variants.
4. **Interchange share** — complexes served by ≥2 counted lines ÷ all complexes.
5. **Opening chronology** — earliest regular passenger service within declared scope.

Anything whose definition can't be resolved cleanly becomes `profile_only` and leaves
Rankings. Reported route-km and annual ridership are **profile facts** (dated, sourced,
shown in the almanac table) — never computed lenses (D5).

## Licensing exclusions (hard rules, verified in deep research 2026-06-11)

- **No official schematic maps** — TfL enforces copyright via an exclusive licensing
  partner; generalize the posture to all operators. We render our own geometry.
- **No Transit Explorer data** — public-website use is explicitly commercial;
  redistribution forbidden at any tier.
- **No UITP republication** — link as background research only.
- Stats sources: operator reports + live-checked Wikipedia (cite revision date).
  Note: a prior research pass's scraped Wikipedia figures failed adversarial
  verification — always re-pull from the live table, never reuse cached numbers.
