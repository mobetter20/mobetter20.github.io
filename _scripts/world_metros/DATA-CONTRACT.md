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
| Beijing | `beijing` | 688 KB (D3 "why not" → IN the deck at D23) |
| Madrid | `madrid` | 429 KB (D23 newcomer; audited GOOD 2026-06-12) |
| Copenhagen | `copenhagen` | 582 KB (D23 newcomer; audited GOOD 2026-06-12) |
| Guangzhou | `guangzhou` | 1.58 MB (D23 newcomer; audited GOOD 2026-06-12; file carries Foshan + trams, scoped out by ref) |
| Osaka | `osaka` | 540 pts (D27 newcomer; audited GOOD 2026-06-12; file carries JR Loop `O` + Osaka Monorail `OM`, scoped out by ref; `osaka_-_rapit` airport express is its own network) |
| Istanbul | `istanbul` | 624 pts (D27 newcomer; audited GOOD 2026-06-12; file carries Marmaray `B1` + funicular `F3`, scoped out by ref) |

Re-verify any time: `python3 _scripts/world_metros/audit_osm_sources.py`.

**Audit note 2026-06-12 (gate-3 re-run):** all 16 deck cities GOOD except
**Paris, which showed ERRORS on that day's validator run** (it was GOOD
2026-06-11; the validator regenerates hourly from OSM, so status
fluctuates). Its GeoJSON still serves and the gate-3 extraction matched
the committed 2026-06-11 numbers (16 lines; station delta only from the
new complex-merge rule), so the snapshot shipped. Re-check on the next
refresh.

Seoul-area supplementary networks: the capital-region scope (D25) also
draws `incheon` (Incheon 1-2). `seoul_-_neotrans` (Sinbundang) exists on
the validator but its GeoJSON export is **empty**: a snapshot gap recorded
in D25 and on Method. `incheon_-_airport` (the suspended airport maglev)
stays out.

## Refresh / freeze discipline

`refresh` (future script) fetches dated snapshots into a committed `data/` dir with
timestamps + checksums; `build` runs offline and deterministically over snapshots.
Facts carry `value · unit · source · as_of`. Missing evidence renders **Unknown**,
never "No" or zero. No SLA tiers (D6) — annual scripted refresh.

## System scopes (FROZEN 2026-06-12, D25; rider-scope B operationalized)

The rule: a card claims the city's metro network **as its familiar map draws
it as coequal metro lines**; modes the map itself marks as distinct products
(commuter overlays, trams, feeders, people-movers) stay out. Implemented as
per-city ref sets in `build_page_geometry.py`; prose on the page's Method tab.

- Tokyo — Metro + Toei only (13 lines); JR refs and the `Al` through-service
  excluded. Through-running truncates at the scope boundary, because the
  familiar Tokyo Subway map stops there.
- Seoul — **FROZEN: the full capital-region network the familiar map draws**,
  incl. Line 1's whole through-running corridor (the map draws it as one
  line), the Korail K-lines, GTX-A, AREX, the light metros, Incheon 1-2,
  and Sinbundang. The L1 open question closes on the map-draws-it test.
  Sinbundang's validator export (`seoul_-_neotrans`) is empty, so it rides
  as a committed Overpass supplement (`data/seoul-sinbundang.geojson`,
  ODbL, ref 신분당, fetched 2026-06-12; D27 Seoul-first completion). 24
  line identities, the full familiar map. Reported figures cover the whole
  declared scope.
- Osaka — **FROZEN: Osaka Metro's nine lines** (M, T, Y, C, S, K, N, I,
  P) incl. the New Tram (Nanko Port Town, P, a coequal line on the Osaka
  Metro map). The JR Loop (`O`) and the Osaka Monorail (`OM`) in the same
  file are distinct products; `osaka_-_rapit` (Nankai airport) is its own
  network. Midosuji's through-run to Minoo-kayano (Kita-Osaka Kyuko) is
  drawn continuous on the Osaka Metro map (rider-scope B), so the `M` ref
  keeps it; through-running onto Kintetsu/Hankyu sits under other refs and
  drops out.
- Istanbul — **FROZEN: the branded Metro Istanbul M-lines** (M1A/M1B
  folded to M1, M2 through M11): ten line identities. **Marmaray (`B1`,
  TCDD commuter rail) is excluded**, like Moscow's MCD and London's
  Elizabeth line; the funiculars (F-lines) and trams are distinct feeder
  products. This is the one D27 scope call flagged for owner confirmation
  at the gate (the familiar Istanbul rapid-transit map does draw Marmaray
  coequal, so an owner could pull it in).
- Singapore — MRT only (6 lines); LRT feeders out.
- Hong Kong — MTR heavy rail incl. Airport Express + Disneyland Resort line
  (10 lines); Light Rail out (district inset, not the metro map's network).
  The AEL question closes as INCLUDE: the MTR map draws it coequal.
- Paris — Métro 1-14 + 3bis/7bis; RER out; CDGVAL/Orlyval out (not on the
  Métro map). Outlier guard still drops the stray fragment.
- Shanghai — lines 1-18 + Pujiang (19); maglev out (distinct product even
  on the official map).
- Beijing — the operator's full mapped network (27 identities incl. both
  airport expresses, S1, Xijiao, the named suburban lines); Batong folds
  into Line 1 and Daxing into Line 4 as the map draws them. Snapshot gap:
  the Yizhuang T1 tram is on the operator's map but absent from the
  validator export; reported route-km (909) includes it.
- London — Underground only (11 lines); Elizabeth, Overground, DLR out
  (distinct products in the Tube map's own grammar).
- NYC — subway services only (23 pills); `<6>`/`<7>`/`<F>` fold into their
  base identities; the three S shuttles ride as one; SIR/PATH separate.
- Madrid — Metro 1-12 + Ramal (13); Metro Ligero out.
- Moscow — metro + MCC (16 identities; the map's coequal line 14, so the
  old exclude-MCC note is superseded); MCD diameters out (D-branded
  commuter product); 4А folds into 4; monorail closed and absent.
- Copenhagen — M1-M4 only; S-tog and Lokaltog out.
- Delhi — DMRC + Airport Express (9 identities); the Blue branch folds into
  Blue; Rapid Metro Gurgaon and the Aqua line out (separate concessions).
- Guangzhou — GZ metro + Guangfo + APM (19); Foshan's own lines (F2/F3),
  all trams, and the stray Qingyuan maglev out.
- Mexico City — STC Metro's 12 lines; Tren Ligero and Suburbano out.
- Cairo — metro 1-3; LRT and monorail out.

Route variants: many service patterns share a `ref` (Seoul L1: 87 at the
gate-3 snapshot). Segments union per ref; counted lenses count
**customer-facing line identities** (ref folds above), not variants.

Station counting (gate-3 definition): named station points within 90 m of
an in-scope line vertex; same-named points merge within 350 m
single-linkage into one complex (interchanges count once); unnamed
per-service stop points are ignored (their share varies wildly by city and
was biasing counts; NYC plotted 2.9x its official count under the old 60 m
grid rule).

## The computed ranking lenses (from frozen snapshots; definitions are the product)

_Updated at the gate-3 sweep: the SCALE face ships six stats (opened,
stations, span, density, route-km, ridership). Density replaced
customer-facing lines at D20; route-km and ridership are almanac-grade
reported figures (D5/D26), never computed lenses._

1. **Furthest-stations span** — max geodesic distance between two station complexes.
2. **Station complexes** — official identities; interchanges counted once.
3. **Network density** (D20, replaces customer-facing lines): station complexes per km2 of the convex hull; line identities ride the cards as band metadata only.
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
