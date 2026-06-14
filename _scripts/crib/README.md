# KRIB · decode the Korean script

A logic puzzle that reverse-engineers the Korean alphabet from almost nothing. The script is a cipher: unknown symbols, one given word (나무 = namu), and a cascade where cracking one piece resolves every word that shares it. Openly Korean, no invented-script mystery. Learning Korean is a side effect, never the goal.

**Live:** https://ajin.im/is/building/krib/ (slug + handle both KRIB; old `/is/building/crib/` is a noindex redirect stub). Soft-launch (noindex, not hub-listed). First-draft corpus, refined live.

**Source of truth:** `is/building/crib/index.html` (single static file, vanilla JS, Google Fonts the only dep). Sibling tool: AC00 (`is/building/ac00/`), whose compose math the finale reuses.

## Ratified v1 contract (2026-06-14)

1. **Mechanic** — phoneme cryptogram + the block-composition bridge folded in (open a square, its pieces enter a shared key; recurrence carries the bridge). The bridge is not its own tier.
2. **Curve** — 5 staged levers, one wrinkle per band: loop → withhold the crib → widen the sound bank → finals (a piece in any position) → thin the overlap. Anchor-withholding is band 2, not the whole lever.
3. **Length** — one sitting, 7 cryptogram levels + a finale, ~22 basic jamo. The recovered key **persists across levels**, so it reads as reconstructing one alphabet, not seven puzzles.
4. **Finale** — flip decode→encode: read one unseen line, then compose two unseen words (봄, 길) from the recovered alphabet via AC00's codepoint math.
5. **Naming**: handle **KRIB**. The on-page 해독 seal was removed (owner call, 2026-06-14: it read as a confusing logo); the title and OG carry "decode the Korean script". 해독 stays the project working title in the canon only.

## v1.1 copy + UX pass (2026-06-14)

Re-grounded on the constitution (decode voice over tutor voice; minimal load-bearing UX). Changes: masthead rewritten dry (dropped "no Korean needed" and the "real alphabet" framing); band labels became terse console events shown only when a lever engages (crib withheld / sound bank widened / finals in play / overlap thinned); how-lines on level 1 only; three counters collapsed to one `key M / 22`; the key sits above the squares so the cascade fires in view; **level navigation** added (prev/next stepper, completed levels reviewable read-only, work preserved). Page copy is em-dash-free per house rule.

## Corpus + verification

`crib_solver.py` checks every level is **logic-forced** (each new piece reachable via a word where it is the only distinct unknown, given the carried key). Run it after any corpus edit:

```
python3 crib_solver.py   # expect: ALL LEVELS CLEAN, alphabet size 22
```

The corpus in the solver must mirror `LEVELS` in `index.html`. First-draft glosses are loose; refine live.

## Canon

- `NORTH-STAR.md` — the constitution (cryptanalysis primary, decode voice, honest ceiling). Wins on conflict.
- `HANDOFF.md` — the build handoff. The morpheme/grammar tier was prototyped and **cut** (its decode target is metalanguage, so it plays as a grammar lesson); the script is the whole scope.
- Prototypes (in `~/Downloads/Decode_hangul/` and `~/Downloads/`, not committed): `dig-proto` (phoneme loop, accepted), `flow-proto` (bridge fold), `curve-proto` (the ramp + persistence). Rejected tiers: grammar / grid / morph / bridge.

## Phase 2 (parked)

Tense consonants (ㄲ ㄸ ㅃ ㅆ ㅉ), iotated + compound vowels (ㅑ ㅕ ㅛ ㅠ, ㅘ ㅢ), cluster finals (ㄳ ㄵ), ㅇ as silent initial (its dual nature is the curated edge held out of v1), a daily/endless mode, irregular verbs. v1 is the regular core only.
