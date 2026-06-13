# SPEC: Hangul as an additive system (working title: `AC00`)

A single-file static HTML tool. One thesis, shown at three joints.

**Thesis:** Hangul composes by addition at every level. Strokes add to make letters, letters add to make a block, and the block is literally an integer. No other major script stays systematic all the way down; with Latin you eventually hit "why does A look like A" and the answer is an accident you memorize. Hangul never bottoms out into arbitrariness.

Name candidates (your call): `AC00` (the Unicode base codepoint, reads like a memory address, fits debug::u / omen.ops), `가획` (the stroke-addition principle itself), `+stroke`. I lean `AC00`.

---

## 0. The audience fork (decide first)

This assumption shapes the whole build:

- **A. Systems-curious audience (assumed).** People who'll enjoy the script-as-system reveal. No audio, no pronunciation, no "learn to read" promise. The payoff is the arithmetic and the 해례본 derivation. This is your lane and what the rest of this spec assumes.
- **B. Actual novice learners.** Then you need audio, romanization, spaced repetition, and you're back competing with letslearnhangul. Different tool. If this is the goal, stop and rescope.

Everything below is written for A.

---

## 1. Core interaction: the zoom spine

One gesture: a syllable decomposes downward through four levels, and each boundary makes an *addition* explicit. Worked example uses 한.

| Level | What shows | The addition at this level |
|---|---|---|
| 3. Codepoint | `한 = U+D55C` | `0xAC00 + 초성×588 + 중성×28 + 종성` (integer arithmetic) |
| 2. Block | the square, 초성/중성/종성 positions | spatial: positions filled by layout rule |
| 1. Jamo | `ㅎ` `ㅏ` `ㄴ` as discrete units | three letters placed into the square |
| 0. Strokes | each jamo's 해례본 derivation | 가획: base + stroke; vowel = primitives combined |

### Worked example: 한

```
초성 ㅎ  index 18
중성 ㅏ  index 0
종성 ㄴ  index 4

codepoint = 0xAC00 + (18 × 588) + (0 × 28) + 4
          = 44032 + 10584 + 0 + 4
          = 54620
          = U+D55C
```

Stroke level for the same syllable:

- `ㅎ` ← `ㅇ` → `ㆆ` (+stroke) → `ㅎ` (+stroke). Laryngeal series (후음).
- `ㅏ` ← `ㅣ` (human) + `ㆍ` (heaven), dot to the right.
- `ㄴ` ← base lingual primitive (설음), tongue tip at the alveolar ridge. No stroke added; it's a primitive.

This single example exercises all three additions (arithmetic, spatial, stroke), so use 한 as the default load state.

---

## 2. Two modes on the same spine

- **Compose (zoom out / build up).** Start from primitives or jamo, add strokes, drop jamo into positions, watch the codepoint compute live as you go. This is the playful core. Ship this first.
- **Decompose (zoom in / break down).** Type or paste a syllable, watch it fall apart down the four levels. This is the explanatory mode.

Same data, same visual spine, reversed direction. Build compose first; decompose is mostly the same components run backward.

---

## 3. Data model

The accuracy-critical part. Source the derivations from the 해례본 logic, not learner mnemonics (no "ㄱ looks like a gun").

### Codepoint composition

```
S = 0xAC00 + (초성_index × 588) + (중성_index × 28) + 종성_index
588 = 21 × 28   (medials × finals)
초성_index: 0–18   (19 initials)
중성_index: 0–20   (21 medials)
종성_index: 0–27   (28 finals, 0 = none)
```

Index arrays follow standard Unicode jamo order (Claude Code can hardcode them):

```
초성: ㄱ ㄲ ㄴ ㄷ ㄸ ㄹ ㅁ ㅂ ㅃ ㅅ ㅆ ㅇ ㅈ ㅉ ㅊ ㅋ ㅌ ㅍ ㅎ
중성: ㅏ ㅐ ㅑ ㅒ ㅓ ㅔ ㅕ ㅖ ㅗ ㅘ ㅙ ㅚ ㅛ ㅜ ㅝ ㅞ ㅟ ㅠ ㅡ ㅢ ㅣ
종성: (none) ㄱ ㄲ ㄳ ㄴ ㄵ ㄶ ㄷ ㄹ ㄺ ㄻ ㄼ ㄽ ㄾ ㄿ ㅀ ㅁ ㅂ ㅄ ㅅ ㅆ ㅇ ㅈ ㅊ ㅋ ㅌ ㅍ ㅎ
```

### Consonant derivation (가획)

Five primitives, each strengthened by adding strokes. Three 이체자 (variants) sit outside the stroke rule and are the documented exceptions that make the system credible.

| Class | Primitive | +stroke | +stroke | 이체자 (variant) |
|---|---|---|---|---|
| 아음 velar | ㄱ | ㅋ | | ㆁ |
| 설음 lingual | ㄴ | ㄷ | ㅌ | ㄹ |
| 순음 labial | ㅁ | ㅂ | ㅍ | |
| 치음 dental | ㅅ | ㅈ | ㅊ | ㅿ |
| 후음 laryngeal | ㅇ | ㆆ | ㅎ | |

Tense consonants are another addition: doubling. `ㄲ ㄸ ㅃ ㅆ ㅉ` from `ㄱ ㄷ ㅂ ㅅ ㅈ`.

### Vowel derivation

Three primitives: `ㆍ` heaven (dot), `ㅡ` earth (horizontal), `ㅣ` human (vertical).

```
ㅗ = ㅡ + ㆍ above
ㅏ = ㅣ + ㆍ right
ㅜ = ㅡ + ㆍ below
ㅓ = ㅣ + ㆍ left
iotated (add 2nd ㆍ): ㅛ ㅑ ㅠ ㅕ
compounds: ㅐ=ㅏ+ㅣ  ㅔ=ㅓ+ㅣ  ㅘ=ㅗ+ㅏ  ㅝ=ㅜ+ㅓ  ㅢ=ㅡ+ㅣ  (etc.)
```

### Block layout rule (Level 2)

Vowel orientation decides where the pieces sit in the square:

- **Vertical vowels** (ㅏㅑㅓㅕㅣ and the ㅐㅔ family): 초성 left, 중성 right, 종성 full-width bottom.
- **Horizontal vowels** (ㅗㅛㅜㅠㅡ): 초성 top, 중성 bottom, 종성 bottom.
- **Compound** (ㅘㅙㅚㅝㅞㅟㅢ): wrapped layout. Phase 2.

---

## 4. Visual direction

The main risk in merging the math layer and the shape layer is tonal clash: cold terminal vs warm calligraphy. Resolve it by keeping the whole tool in the systems register.

- Dark background, monospace chrome, restrained palette with one accent (your vermilion/ink accent works). Same family as omen.ops.
- Render Hangul glyphs in a clean typeface; render stroke-addition as **vector strokes drawn on a grid**, not skeuomorphic brush. Keep it diagrammatic.
- Articulator diagrams: minimal sagittal line drawings (mouth cross-section), single accent color, five of them only (velar, lingual, labial, dental, laryngeal). Not illustrative, not painterly.
- The codepoint readout is the hero of Level 3: show it as live hex + decimal, updating per keystroke.

---

## 5. Tech constraints

- Single `.html` file, no backend, no build step. Vanilla JS.
- Jamo decomposition is pure arithmetic; no library needed.
- Articulator diagrams and stroke animations are inline SVG.
- No external runtime deps. CDN only if unavoidable.

---

## 6. Phasing

- **Phase 1 (MVP, ship in a sitting).** Compose + decompose at the block/codepoint level. Vertical and horizontal vowels. Live arithmetic. No stroke layer. This is the standalone #2 from our chat.
- **Phase 2 (the merge).** Stroke level: drill a jamo into its 가획 chain with the five articulator diagrams and the vowel-primitive composition. This is where the shape story joins, under the additive frame.
- **Phase 3 (polish).** Compound-vowel layouts, archaic letters (`ㆍ ㆁ ㆆ ㅿ`) shown in the stroke layer as historical derivation, the "no arbitrary layer" framing copy, optional guided tour.

The zoom architecture lets Phase 2 graft under Phase 1 without rewriting it.

---

## 7. Open decisions for you

1. **Audience:** confirm A (systems-curious) vs B (learners). Everything assumes A.
2. **Default mode:** compose-first or decompose-first on load.
3. **Archaic letters:** modern jamo only, or include `ㆍ ㆁ ㆆ ㅿ` in the stroke layer for the full 해례본 derivation. Including them strengthens the "documented exceptions" story; adds scope.
4. **Name:** `AC00` / `가획` / `+stroke` / other.
