# 해독 — NORTH STAR (ratified)

The constitution for the decode game. This is the top document. Where it conflicts with the GDD (`dig-gdd.md`) or the AC00 spec (`hangul-zoom-spec.md`), this wins. Those hold subordinate detail: the GDD holds tier and mechanic specifics, the AC00 spec holds the shared engine. Both are reconciled to the principles below.

> **Scope amendment (ratified 2026-06-14).** The morpheme / grammar tier was prototyped (`grammar-proto.html`), tested, and **cut from the core**. It reads as a grammar lesson because its decode target is grammatical function, which is metalanguage. Governing diagnosis: the cryptanalysis loop is genre-neutral, and the subject matter decides puzzle versus lesson. Decoding sounds is concrete, so it plays. Decoding grammar is a grammar exercise by definition. **The core scope is the script, the writing system.** Morphology and the featural-morph verb are parked as possible later content, not core spine. The block-composition layer stays a live, unvalidated thread that may surface inside the phoneme cryptogram. Where any section below still frames morphology as a live tier, this amendment governs.

---

## What it is

A logic puzzle. You reverse-engineer a real writing system and language starting from almost nothing. Openly Korean, no invented-script mystery. The script goes first and is the marquee: crack a whole alphabet from inscriptions yourself, in one sitting. Learning real Korean is a side effect, never the objective.

Working title `해독`. Engine and sibling: `AC00` (the composition tool, "a syllable is an integer").

## North star, one line

A logic puzzle whose primary verb is cryptanalysis, pointed at Korean because Korean is decodable at every level, with genuine rule discovery as a secondary mode.

---

## Ratified principles

These exist to stop the project drifting back into the two failure modes already hit and rejected: the grammar-quiz and the answer-key.

1. **Cryptanalysis is the primary verb.** The player reconstructs an unknown mapping from a crib plus structure, and the payoff is cascade: one cracked unit lights up everything that contains it. Every candidate tier must pass this test before it's built. Name the unknown unit, name the crib, name what cascades. A tier with no such framing will play like grammar class and gets reshaped or dropped.

2. **Rule discovery, when used, must be genuine.** The player formulates the rule themselves by constructing probes and reading valid / not-valid feedback, the way Eleusis and Zendo work, proven when they can generate only-valid forms. Banned outright: stating the rule, offering candidate rules to choose from, and reducing the task to sorting pre-labeled examples. Those are recognition and classification, not discovery. This mode stays secondary, used as spice on the decode spine.

3. **One engine, every level.** The cryptanalysis loop is not specific to the alphabet. Korean composes at every level, so the same loop runs with phonemes as the cipher units, then morphemes as the cipher units, with block composition as the bridge between them. This shared loop is the spine of the whole game.

4. **Game first.** The success metric is whether the puzzle is satisfying on its own terms, with learning as a side effect that gives it real-world payoff. This licenses the scope cuts below, and it forbids re-scoping the thing into a language course.

5. **Decode voice, never tutor voice.** Confirmation reads "rule locked," not "great job." Progress is a logbook of recovered rules, not a fluency meter. The register is `omen.ops` / `debug::u`, and that register is load-bearing.

6. **Minimal, functional UX.** Before adding any element, check whether something already on screen carries that signal (position, highlight, an existing label). No redundant signifiers, no decorative chrome. Keep only what is load-bearing.

7. **Honest ceiling.** The game builds decoding competence over a curated, regular core. It does not produce fluency or conversation, and must not claim to.

---

## The spine: one loop, every level

The reason Korean specifically: it is compositional and regular at every level, so the decode loop runs again and again, and the cascade stays generous (decode few, unlock many). That generosity is what makes a small-content puzzle feel deep.

- **Phonemes** are the cipher units in the script tier. Validated by prototype.
- **Block composition** is the bridge: discovering that a block splits into reusable atoms is what turns the "alphabet" from whole blocks into parts, which is what makes any cascade possible above the symbol level. This is AC00's thesis, discovered rather than shown.
- **Morphemes** are the cipher units in the agglutination tier: the same cryptogram one level up, with a few glossed sentences as the crib. Crack 었 = past once and it lights up every sentence holding it. **Unvalidated: no prototype yet. The phoneme loop is proven; that the same loop holds one level up is a reasonable bet, not a tested fact.**

A featural script also cracks fast, and that speed is itself a payoff: you decoded a writing system in minutes because someone engineered it to be decodable.

---

## Tiers (ordered by decodability, not textbook order)

| Tier | Unknown unit | Crib | What cascades | Status |
|---|---|---|---|---|
| 1 · script *(marquee)* | symbol → sound | one given word (나무 = namu) | every word sharing an atom | validated |
| bridge · block assembly | how atoms pack into a block | the anchor's own structure | all blocks become decomposable | testing |
| ~~2 · morphology~~ *(cut from core)* | morpheme → function | a few glossed sentences | every sentence sharing a morpheme | cut: reads as lesson; parked |

Particles, predicate slots, the honorific axis, and Sino-root composition all live inside Tier 2 as morpheme-level decodes, not as rule-quizzes. Genuine rule-discovery beats (for example 이/가 conditioning or vowel harmony) appear only as construct-and-validate spice. **Finale:** read one unmodified Korean sentence cold, using only what was cracked. That transfer item is the win condition pattern at every tier: produce or read something unseen.

---

## Scope (the game-first cuts)

- Root meanings are **given**. Seeds are the puzzle's givens, like clue numbers in a logic grid. The player decodes the rules and mappings, not the dictionary.
- Irregular **edges are cut** (irregular verbs, suppletive honorifics). The corpus is curated to be regular. Edges are parked as possible later premium content, not v1 baggage.

---

## Tech

Single-file static HTML, no backend, vanilla JS, Google Fonts the only dependency. Reuses AC00's engine: the jamo arrays and the composition / decomposition math. Tokens: bg `#101013`; vermilion / ochre / teal for 초 / 중 / 종.

---

## Status

- `dig-proto.html` validates the script-tier cryptogram, the core feel. **Accepted.**
- The 이/가 quiz was built, rejected, and deleted. Do not rebuild its shape (answer key plus rule menu).
- Bridge layer (block decomposition) and Tier 2 (morphology) are **unvalidated**. The morpheme loop is a hypothesis extended from the proven phoneme loop. Logic and basic play for these get tested in chat prototypes before any move to Claude Code.
- UX: the tap-symbol popover interaction landed. Further passes deferred.

## Supersedes / reconcile

- **`dig-gdd.md`** (GDD): subordinate detail. Strike its quiz-style Tier 2 prototype target, and recast its rule-discovery framing as construct-and-validate per principle 2.
- **`hangul-zoom-spec.md`** (AC00 spec): unchanged, now framed as 해독's engine.
- **`CLAUDE.md`**: scoped to AC00 only. The game needs its own handoff once the tiers are specced.
