# STATUS — Metro Match (was World Metros Atlas)

_Last updated: 2026-06-12 (reconcile session: the parallel gate-3 body D25-D31 merged to master as PR #164; this session's card-IA round, URL move and three-face flip recorded as D32-D34 and shipped on top)._

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

- D22 (2026-06-12): owner reviewed the D21 live page and directed three
  fixes (two with picks), all shipped the same session. Empty
  route-km/ridership rows hidden until sourced (card shows four live
  stats). Daily stat now rotates across opened/stations/span/density with
  a rebuilt, centered, bigger layout (pills on each choice, value on
  reveal). Legibility pass: nothing below ~9px, the 6.5px attribution +
  footnotes lifted, scope tag moved to its own line (no clip at 16 refs),
  lore backs trimmed to two facts to fit the larger type. Re-verified
  375/768/1280, keyboard, reduced-motion, console clean.

- D23 + D24 (2026-06-12): owner reviewed the D22 page and recurated the
  roster with a ranked 15-list + reasons; picks: keep Cairo (deck of 16),
  Guangzhou for the PRD seat, deck order = the ranking. Beijing's "why
  not" reverses. (A "Why sixteen" Method section + absence note shipped
  with this round, then was cut at the owner's revision the same day:
  Method is method; the rationale reaches visitors as lore-back facts.)
  Newcomers' soon cards say "diagram audit pending" (dual audit due at
  scale-up). Same round: masthead replaced (premise + verbs), nav tabs to
  sans 12.5px/600, daily type up a step (iOS flag). Themes (frequency /
  fares / integration as switchable stat sets) ratified to BUILD INTO the
  scale-up (D24); nothing themed renders yet. NOTE: the session that took
  these picks crashed (oversized screenshots) and was rewound; the picks
  were recovered verbatim from the session JSONL and re-recorded here.
  Standing norm from that crash: no screenshots in this project's
  sessions; verify by DOM probes and open the preview URL for the owner.

- BUILD-SPEC gate 3 BUILT (2026-06-12): the roster scale-up to all 16
  shipped to the deck. Dual audit done (Madrid/Copenhagen/Guangzhou GOOD
  on the OSM validator; DIAGRAM-LEDGER stanzas for all four newcomers,
  licences read off the Commons pages, structures graded on the downloaded
  files; all 16 lore-back diagrams committed). Per-city scopes FROZEN
  under rider-scope B (D25; Seoul L1 closes IN as the whole capital
  corridor the familiar map draws; Guangfo / Copenhagen M1-M4 / Madrid
  Metro-not-ML / Moscow incl. MCC / HK incl. Airport Express all recorded
  on Method + DATA-CONTRACT). Pipeline rebuilt for 16 cities (hull
  density, named-complex station counts, exact span; `meta.json`
  committed). Almanac researched against live pages (opened + per-line
  years, route-km, ridership, and the theme figures, each dated + sourced
  in `almanac.json`; Seoul ridership = the scope-matched capital-region
  4.42B from Korea Railroad Statistics). D24 themes ship as CORE / SERVICE
  / MONEY switchable stat sets, every figure a dated snapshot. Battle +
  daily run the full deck on the core six (battles can tie). Verified at
  375/768/1280, columns lock 1/2/4, keyboard-playable, reduced-motion
  intact, console clean, no overflow, soft-launch norms kept (noindex, not
  in sitemap, no hub card, no home teaser). D25/D26 in DECISIONS.

- D27 BUILT (2026-06-12, same session, owner design-session pivot): the
  deck grows to EIGHTEEN. Owner disliked the 2-per-row band and reversed
  the 1/2/4 grid lock; the grid is now 1/2/3 columns (never 4), and 18 is
  even at every tier (verified [3,3,3,3,3,3] at 1280, 9x2 at 768, 18x1 at
  375, no orphan). Osaka (the merchant) and Istanbul (the crossing) join
  at 17/18 with the full newcomer pipeline: OSM validator GOOD, scopes
  frozen (Osaka Metro's 9 lines incl. New Tram, JR/monorail out; Istanbul
  M-lines, Marmaray excluded and flagged for owner confirm), geometry
  extracted, DIAGRAM-LEDGER stanzas (Osaka PD wide-area SVG with a c.2011
  caveat, Istanbul current CC BY-SA 4.0 SVG), almanac researched (Osaka
  ridership annualized, service-hours left null; Istanbul published),
  lore backs + epithets. PRIORITY done first: Seoul completed: Sinbundang
  (empty in the validator) pulled from Overpass into a committed
  supplement, so Seoul now carries all 24 line identities (730 stations).
  Count strings, deck-back, badge, method all read 18. Re-verified
  375/768/1000/1280, battle (153 pairs) + daily across 18, console clean,
  no overflow, soft-launch norms kept. D27 in DECISIONS.

- D30 + D31 (2026-06-12, parallel session, merged as PR #164): the daily
  got smart (two deterministic forms: close-pair DUELs + PICK-the-number
  with honest distractors, avalanche date hash, bank board in mocks/) and
  the second set was recomposed from the research-chip menu + named
  SCALE / CHARACTER (drop newest line, add BIGGEST HUB computed from the
  snapshot, interchange relabeled "transfer"; meta.json gains
  biggest_hub).

- D32 (2026-06-12, this session; built as "D30" pre-merge, renumbered):
  the card-IA round. Board (`mocks/card-ia-board.html`): three candidates
  on real cards + the 18-back overlap map (26 collisions incl. 3 factual
  contradictions). Owner verdicts: B/C (figures shoved onto front or
  back) rejected as ugly; the lore bar = factually correct, plain (not
  overwritten), interesting; the dedup shrank to 11 slim edits (3
  must-fixes, 7 repeat swaps, 1 NYC clarifier), applied to content.json
  with a plain-pass; set captions ride each stat face.

- D33 (2026-06-12, this session): URL moved to
  `/is/building/metro-match/` (owner-directed); a noindex redirect stub
  sits at the old world-metros path; generator, geometry OUT_DIR, mocks
  and living docs updated. Internal names (the `_scripts/world_metros/`
  dir, the `world-metros-atlas` registry stanza) deliberately stay.

- D34 (2026-06-12, this session): one flip cycles three faces,
  SCALE -> CHARACTER -> MAP; the deck-level toggle is gone (supersedes
  the D32 standing shape and D31's relabeled toggle). Deck cards render
  two single-ledger fronts + a stashed map side; app.js cycles them with
  a locked card height; diagrams lazy-load on the map turn. Owner
  authorized publish ("u can put it on metromatch... i will be
  testing"); soft-launch norms stay while the owner tests live.

- D35 (2026-06-12, owner-directed during live testing): header polish.
  The chrome joins main's column via an .hframe, the masthead centers
  over the deck (the page's one left-anchored stray), the DECK OF 18
  badge is cut (soft-launch leftover), and the wordmark links to #deck
  as the in-app way back. Verified 375/768/1280/1990, console clean.

- D36 (2026-06-13): fact-check pass on the live deck. Owner "yes fix all
  now" on a 10-finding external check; verified each against data + live
  sources. Singapore driverless 6->4 (reverts a wrong D32 lore edit; NSL/EWL
  keep captains), Delhi 3->2, Hong Kong owns its network (opened 1979->1910
  via East Rail, route-km 209->271), stations over-count (~+20% vs official)
  disclosed in Method + wishlisted for a re-extraction round, lore/Method
  honesty fixes (Beijing one-operator, nothing-leaves-the-page, opened
  sourcing), redirect stub carries query+hash. Verified + shipped. D36 in
  DECISIONS.

- D36 (2026-06-12, owner-commissioned): THE RANKS tab. Per-stat
  leaderboards for all eleven stats (SCALE + CHARACTER picker), podium
  top three, card-grammar rows, tightest-race battle links, no combined
  score ever. Verified 375/768/1280, keyboard cycle, console clean.

## Current gate: owner live-testing the shipped deck

The deck of 18 (gate 3, D25-D31) + this session's D32-D34 are LIVE at
https://ajin.im/is/building/metro-match/ (still noindex/unlisted; the
old world-metros URL redirects). Listing it on /is/building, the
sitemap or the home teaser is a SEPARATE owner call. Items carried to
the live review: the 15 new epithets; the Istanbul scope call (Marmaray
excluded, could be pulled in); the Seoul-tops-ridership claim
(full-capital scope, sourced); Osaka's two soft spots (c.2011 diagram
caveat; no sourced service-day figure); and the daily's known
hash-collision property (a question can repeat within a week or two).

## Next exact action

Owner tests the live page and reports; fixes land as new rounds on a
fresh branch (the ship branch was squash-merged; continuing one needs
`git rebase --onto origin/master <old-head>`). Post-ship housekeeping
done this session: registry stanza updated (new URL), generators
registered in the main checkout's untracked `publish.sh`. Lifting any
soft-launch norm (index, sitemap, hub card, home teaser) stays a
SEPARATE owner call.

## Blockers

None.
