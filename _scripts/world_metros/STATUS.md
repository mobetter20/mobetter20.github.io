# STATUS — Metro Match (was World Metros Atlas)

_Last updated: 2026-06-12 (Claude session, branch `claude/exciting-shaw-1ae32b`)._

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

- D16 gate artifact built (2026-06-12, owner-commissioned while D16 sat
  PROPOSED): `mocks/gallery-duel-board.html` (`mocks/build_gallery_duel_board.py`).
  The 12-card diagram gallery in uniform frames (Seoul/Tokyo/Paris real:
  embedded Commons diagrams, ledger-verbatim attribution, one computed
  superlative chip each from meta.json; nine labeled "soon" with their ledger
  license), a "compare any two" strip, and the SEOUL vs PARIS duel: framed +
  attributed diagram pair, tale-of-the-tape (opened year, lines drawn, stations
  plotted, furthest-stations span: paired bars tipping toward the larger value
  plus a plain verdict line per row; reported route-km and annual ridership as
  "pipeline · dated at build" placeholders), and the same-scale silhouette pair
  demoted to one "true size" row. Numbers from the prototype's committed
  meta.json/shape JSONs; no fetches; no JS.

- D16 judged at its gate (2026-06-12): not ratified. Owner, on the board:
  without satisfying map visuals, archive the project (or the current vision)
  or pivot hard; floated stat cards + a match game. Owner confirmed the pivot
  ("pivot") over archive. Recorded as **D17 (RATIFIED): METRO CARDS**, working
  name "metro match": every city one designed stat card, comparison as the
  game (battle + daily guess), our own card idiom, no Pokémon/Top Trumps
  trade dress. Nearly everything survives: lenses → stat block, shape JSONs →
  card art, ledger diagrams → "the map riders see" exhibit, duel → battle.
  BUILD-SPEC rewrite deliberately deferred until the card mock gate passes
  (premise before spec); D17 carries the draft North-Star. All prior boards
  stay in mocks/ for the record.

- D17 round-1 card mock judged (2026-06-12): cards yes, execution no. Owner:
  the map may not belong on the front at all; more interesting stats instead;
  polished and minimal like a modern board-game card, optimized for our game,
  not the baseball/Pokémon lineage; the familiar map maybe on the BACK; a
  real pivot, not a half-measure reactionary fix. Recorded as **D18
  (RATIFIED, owner-directed)**: game-first front (deck-rank chips + strength
  tracks on every stat row, line pills as the identity device, epithets, no
  map), the familiar diagram moves to the card back (lore side, credited),
  uniform pinstripe deck back stays the game-hidden state. Round-1 board
  stays in mocks/ for the record.

- D18 v2 board judged (2026-06-12): **premise PASSED** ("i like it"). The
  archive branch is dead. One directed amendment: a black or other dark
  background might be better (D19). The commissioned follow-through landed
  the same session: BUILD-SPEC.md rewritten around the D17 North-Star + D18
  card grammar; README first paragraph updated to the card vision.

- D19 ground fork resolved (2026-06-12): owner picked **C**, dark card on
  dark table. Owner then asked to confirm the comparison items (content and
  design): big letters, legible, strong brand identity, board-game card
  look, multiple versions welcome. Recorded as **D20**: stat-list review
  (PROPOSED: swap `lines` for `density`; pills already carry line count;
  winner spread improves; Paris's mesh becomes playable) + three
  stat-presentation variants in treatment C.

- D20 resolved (2026-06-12): owner picked **V1 (big ledger)** after the r3
  type pass (labels lead in bold near-white; designer-critique agent round;
  its label re-dimming rejected). Density swap confirmed; ratified defaults:
  line-count + scope tag beside the pills, 2-3 curated facts on lore backs.
  Still open: per-city declared scope (A operator vs B rider-scope, rec B),
  due before roster scale-up. BUILD-SPEC updated to the resolved state.

- D21 (2026-06-12): both rebuild-gate questions answered by the owner in
  the rebuild session. **Name: METRO MATCH ships** (URL unchanged).
  **Scope: B rider-scope** (each card declares the network its city's
  familiar map draws; binds at scale-up). The live page was rebuilt the
  same session (PR #159): `/is/building/world-metros/` is now the deck.
  DECK (12 cards roster order, 3 live with flip-to-lore backs + lazy
  ledger diagrams credited verbatim, 9 "soon" slots), BATTLE (vs cpu,
  pick-a-stat off the V1 ledger, first to 3, per-pair hash URLs), DAILY
  (one stations guess a day, localStorage streak), METHOD (rules,
  definitions, scope, sources, licences, why-not-Beijing). Generated by
  `_scripts/world_metros/build_metro_cards.py` from the committed
  meta.json; style.css/app.js hand-maintained. Soft-launch norms kept.
  Verified at 375/768/1280, keyboard-playable, reduced-motion respected,
  deck grid ships light (diagrams fetch only on flip).

## Current gate: owner verdict on the live page

All design gates, naming and scope are resolved (C ground, V1 ledger,
density swap, Metro Match, rider-scope B). The deck is live at
https://ajin.im/is/building/world-metros/ (still noindex/unlisted). The
owner judges the live page; that verdict opens or closes gate 3.

## Next exact action (after the owner verdict)

Roster scale-up to all 12 (BUILD-SPEC gate 3): freeze per-city scope rules
under rider-scope B (DATA-CONTRACT: Seoul L1 is the hard one; freeze and
record each rule on Method), per-line opened-year sourcing, full-deck rank
computation across 12, route-km + ridership as dated almanac rows, and the
nine remaining lore backs per DIAGRAM-LEDGER. Lifting any soft-launch norm
stays an owner call after that gate. Also pending in the main checkout:
register `build_metro_cards.py` in the untracked `publish.sh` (worktrees
cannot reach it).

## Blockers

None. (Seoul L1 scope freeze is deliberately deferred to the pipeline
stage, DATA-CONTRACT.md — this build keeps the mocks' lines 2–9 scope
behind the scope tag.)
