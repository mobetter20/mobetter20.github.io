# 해독 — Build Handoff

> Drop this into the game repo as `CLAUDE.md` so you load it automatically. It's the entry point, not the law. The constitution is `NORTH-STAR.md`. The validated mechanic is `dig-proto.html`. Read both before you build anything.

---

## 0 · How to work on this

Ajin wants a collaborator that assesses, not one that types to dictation. Hold to this above the rest of the doc.

- **Challenge what's here.** If a decision is weak, unjustified, or self-contradictory, say so and argue your case before you build around it. Default agreement is a failure mode, not politeness.
- **Surface your own assumptions first.** State them out loud ("I'm assuming X, checking that") instead of filling gaps quietly. Silent gap-filling is the thing to watch for, more than blind compliance.
- **Know what's settled and what isn't.** Section 2 is ratified: build on it unless you've spotted a real problem and named it. Section 4 is open: it's yours to decide with Ajin, so don't quietly harden those into arbitrary choices without flagging that you're choosing.
- **Critique over encouragement.** Specific, direct, with the reason attached. Don't soften to be agreeable.
- **House style:** no em dashes; vary sentence structure; when you offer options give pros, cons, and a recommendation; comprehensive but scannable, no walls of text.

---

## 1 · What you're building

A logic puzzle that decodes the Korean writing system starting from almost nothing. The player treats the script as a cipher: unknown symbols, one given crib, and a cascade where cracking a single unit unlocks everything that contains it. It's openly Korean, no invented-script mystery. Learning real Korean is a side effect, never the goal. The interface speaks like a decode console, not a tutor.

Single-file static HTML, vanilla JS, no backend.

---

## 2 · Locked (ratified — build on these; flag loudly before relitigating)

- **Core mechanic: the phoneme cryptogram.** `dig-proto.html` is the reference implementation and has been validated as the game-like core. The loop: words shown whole and unreadable, one anchor word given (나무 = namu), the player assigns sounds to unknown jamo, assignments propagate, words cascade-resolve. That loop is the spine. The file is the source of truth for the feel and the interaction; this doc deliberately won't re-spec it.
- **Scope: the game is the script.** The writing system, not the language. This is the load-bearing call. Section 3 explains why grammar sits outside it.
- **Seeds are given.** Root meanings are handed to the player, like clue-numbers in a logic grid. The puzzle is the mappings and rules, never the dictionary.
- **Irregular edges are cut.** The corpus is curated to be regular. Irregular verbs and suppletive forms are parked as possible later content, not v1 weight.
- **Decode voice.** "rule locked," never "great job." Progress is a logbook of recovered rules, not a fluency meter. Register is `omen.ops` / `debug::u`, and it's load-bearing.
- **Tech and tokens.** Single-file static HTML, vanilla JS, Google Fonts the only dependency. bg `#101013`; vermilion / ochre / teal for 초 / 중 / 종; IBM Plex Mono + Noto Sans KR. Reuse AC00's jamo arrays and composition math (already carried in `dig-proto.html`).

If you think one of these is wrong, make the argument explicitly. The standing default is that they're settled.

---

## 3 · Tried and rejected (don't rebuild these; argue back if you see what we missed)

Each was prototyped in chat and cut for a stated reason. The reasoning is open to challenge if you find a hole, but each cut was deliberate, not an oversight.

- **Grammar / morpheme decode** (`grammar-proto.html`, optional in `rejected/`). Same cryptogram loop, but the decode target is grammatical function (subject, object, past). That target is metalanguage, so it plays as a grammar lesson however clean the loop is. The diagnosis that sets the scope: **the cryptanalysis loop is genre-neutral, and the subject matter decides whether it reads as a puzzle or a lesson.** Decoding sounds is concrete and plays. Decoding grammar is a grammar exercise by definition. This is the whole reason the scope is the script. Grammar is out of the core, parked as possible premium content.
- **Featural morph, 가획 add-stroke** (`morph-proto.html`). Stroke count maps to sound family by family, so it's patchwork rather than one universal rule, which makes it weak as discovery. Parked as an optional manipulation / compose feel. It's the verb from Ajin's separate Hangular project, not part of the graded decode here.
- **Featural grid** (`grid-proto.html`). The clean consonant grid is only about six cells, too few to induce a rule from. Expanding into the messy sibilant and glottal rows turns it back into patchwork.
- **Comparison-bridge** (`bridge-proto.html`). Tap two symbols, find the shared atoms. Passive recognition, and trivial for anyone who already reads Korean.
- **이/가 quiz** (built, then deleted). Labeled examples plus a menu of candidate rules is recognition, not discovery. Do not rebuild this shape.

---

## 4 · Open (yours to decide with Ajin — these are context, not orders)

Genuinely unsettled. Treat the notes as constraints to design inside, not as answers to implement.

- **Difficulty curve.** The lever is anchor-withholding: as the recovered key grows, hand out fewer free anchors and force more inference. How steep, and over how many beats, is open.
- **Length.** Level count and corpus size are unset. Bounds: regular core only, cascade stays generous (decode few, unlock many), no irregular edges.
- **The block-composition beat.** Whether "a block splits into reusable atoms" gets foregrounded as its own discovery moment or stays implicit inside the phoneme cryptogram. See section 5. This is a live thread, not a closed call.
- **Finale.** The win pattern is reading something unseen: one unmodified line, cold, using only what was cracked. The exact form is open.
- **Naming.** Working title 해독. Not final.
- **UX past the validated popover.** The tap-symbol sound popover landed and is in `dig-proto.html`. Anything beyond it is open, under the minimal-UX principle: check whether something on screen already carries a signal before adding an element for it.

---

## 5 · Live thread: rule discovery in composition

Ajin still believes composition holds genuine rule discovery, and that intuition is open, not resolved. Two grounded leads, neither chased yet:

- Composition **already lives inside** the phoneme cryptogram. The blocks being decoded are built from the atoms being cracked, so building the core out may make a composition discovery surface on its own, without a bolted-on tier.
- The **block-layout rule** (vowel orientation decides where the pieces sit in the square) is the one composition rule with enough instances to be genuinely inducible, since there are thousands of blocks to generalize from. It may also be too simple to carry its own tier. Open question.

Don't force this. If the build makes a composition-discovery beat fall out naturally, raise it with Ajin rather than manufacturing one.

---

## 6 · Files

- **Canonical (the build runs on these):** this doc (as `CLAUDE.md`), `NORTH-STAR.md`, `dig-proto.html`.
- **Reference:** `hangul-zoom-spec.md` (the AC00 codepoint math; needed only if the block-composition layer gets built).
- **Optional, for challenge-ability:** a `rejected/` folder holding the four cut prototypes, so you can inspect what was actually tried if you want to contest a cut.
- **Deliberately left out:** the AC00-scoped `CLAUDE.md`, `dig-gdd.md` (superseded by NORTH-STAR), `ac00.html` (a separate tool), and the Hangular project files (a separate game). They'd only create drift.
