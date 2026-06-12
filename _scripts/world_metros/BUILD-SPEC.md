# BUILD-SPEC — Metro Match (v2 contract, supersedes the atlas; name ratified D21)

This is the product/acceptance contract for the D17 card pivot, written after
the premise gate passed (D19: owner "i like it" on the D18 v2 board). The v1
atlas contract lives in this file's git history; its data discipline carries
over unchanged. The original user brief stays the fixed judge, reweighted by
the owner at D16: *fun and engaging comparison of interesting metro systems,
in an easy-to-get view*. The four map-hero rounds (D10–D15) established what
this site will NOT be: a cartography product.

## North-Star (D17, ratified; named Metro Match at D21)

A collectible card deck for the world's defining metro systems. Every city is
one designed stat card; honest dated data is the content; comparison is the
game. Trading cards with footnotes.

## Surfaces (one URL)

1. **THE DECK** — the landing: all 18 cards (D23's ranked 16 + Osaka and
   Istanbul at D27, superseding D3's twelve), collection grid locked to
   1/2/3 columns (D27). Cards flip: **front for play, back for lore** (D18).
2. **THE BATTLE** — vs cpu, Top-Trumps loop: see your card, pick a stat, beat
   the hidden opponent card; first to 3. Stable per-pair URLs survive from
   D16's duel mechanics.
3. **THE DAILY** — one guess a day ("which plots more stations?"), streak in
   localStorage. Consciously un-defers D16's reveal-on-tap guessing.
4. **METHOD** — scope rules, definitions, sources, as-of dates, licences,
   win directions, and the diagram licensing story. Method is method: no
   roster editorial (the per-city "why it's in" rationale was cut at the
   owner's D23 revision; it reaches visitors as lore-back facts instead).

## Card grammar (D18, ratified)

- **Front (play side):** city name + epithet (the sprawl / the mesh / the two
  crews / …), deck number `NN/16` in roster order (D23), line pills carrying the
  real refs in the operators' colours (the identity device, rendered purely
  from OSM data; compact above 12 lines) with a line-count + scope tag beside
  them ("8 lines · 2–9 shown": pills never silently claim completeness), six
  stat rows in the **V1 big-ledger presentation** (D20: bold near-white stat
  label leading each row, jumbo mono value right, deck-rank chip 1ST filled /
  others hollow; no strength tracks), and a provenance footnote naming the
  snapshot and the rank basis. NO map on the front.
- **Back (lore side):** the city's familiar Commons diagram full-bleed
  (DIAGRAM-LEDGER file, attribution verbatim, currency caveats where the
  ledger flags them), name band, one flavor line, and 2-3 curated "why it's
  interesting" facts (the D2 profile-card content; evergreen, no
  traveller-utility layer). The D11 "map riders see"
  obligation lives here.
- **Deck back:** uniform pinstripes of every line colour in the deck under
  the wordmark band; serves as the opponent's hidden card in the battle.
- **Ground:** treatment C (D19, picked): ink-dark card `#1b1b21` on
  near-black table `#0f0f12`; the line colours do the lighting.
- **Trade dress:** our own card idiom in the official-map language (DM Mono
  data labels, hairline rules, transit-blue accent). No Pokémon / Top Trumps
  trade dress. No official map artwork anywhere.

## Stats (the six rows; definitions are the product)

| stat | basis | wins |
|---|---|---|
| opened | earliest regular passenger service within declared scope (operator histories, dated) | earlier |
| density | stations per km² of network extent (bbox in mocks, hull at pipeline) | more |
| stations | station complexes plotted from the frozen snapshot | more |
| span | furthest-stations geodesic distance, computed | more |
| route-km | reported, dated, sourced (almanac grade) | more |
| ridership | reported annual, dated, sourced (almanac grade) | more |

The lines→density swap is D20-ratified (the pills + a header count tag
carry line identity; density restores winner spread and makes the mesh
playable). Ranks and track positions are computed across the full deck of
16 at pipeline stage (the mocks footnote "live deck of 3" until then); win
directions are fixed above and explained on Method. Interchange share remains a candidate
seventh stat if the pipeline resolves it cleanly per the lens definition.
Missing evidence renders **Unknown** and excludes that stat from battles for
that card; never shown as zero.

## Explicitly OUT (do not creep back without a DECISIONS entry)

- The practical-traveller layer (D2) — unchanged.
- **Aggregate scores.** Rank chips are per-stat; no card carries an overall
  power number, no "best metro".
- Brackets / tournaments (rejected at D16; n=12).
- Accounts, multiplayer, backend anything. Static site; the streak is
  localStorage.
- Official schematic artwork (licensing posture unchanged, DATA-CONTRACT.md)
  and the maps-as-hero IA (D10–D15, judged and closed).

## Approval gates (in order)

1. **D19 ground pick** — DONE (C: dark card, dark table) + **D20** — DONE
   (V1 big ledger; density swap ratified).
2. **Live-page rebuild** of `/is/building/world-metros/` as DECK + BATTLE +
   DAILY + METHOD with the three live cities real, nine cards "soon" —
   BUILT 2026-06-12 (D21; `build_metro_cards.py`). Owner verdict on the
   live page is the open gate.
3. **Roster scale-up** to all 16, then 18 (D23 + D27) with frozen scope rules under
   rider-scope B (D21; Seoul L1 is the hard one), the dual audit for the
   four D23 newcomers (OSM validator + DIAGRAM-LEDGER stanzas), per-line
   opened-year sourcing, full-deck ranks, lore backs per DIAGRAM-LEDGER,
   and the D24 themed stat sets (dated almanac snapshots, annual refresh).
   Naming is settled (Metro Match, D21). **BUILT 2026-06-12** (D25 scope
   freezes + D26 build record); the owner verdict on the gate-3 page is
   the open gate.

## Soft-launch conditions (repo norm, unchanged)

`noindex` meta · not in sitemap · no `/is/building` hub card · no home-teaser
line · site-wide `/analytics.js` loads as on every page. Lifting any of these
is an owner call after gate 3.

## Acceptance checklist

- Verified at 375 / 768 / 1280 (repo CSS rule); battle and daily fully
  keyboard-playable; `prefers-reduced-motion` respected (card flips degrade
  to instant swaps).
- Per-card lore-back diagrams lazy-load (they are the heavy assets); the deck
  grid ships light. Raw OSM GeoJSON never ships.
- ODbL attribution visible on every surface; per-diagram credit rendered with
  the lore back, verbatim from DIAGRAM-LEDGER.
- Every displayed stat resolves to `source + as_of` (Method shows the table;
  card footnotes name snapshot + rank basis).
- Build stays a deterministic `_scripts/world_metros/build_*.py` run over
  committed dated snapshots (network only in the refresh step).
