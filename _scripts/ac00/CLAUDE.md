# CLAUDE.md — AC00

Single-file static HTML tool. Working title `AC00` (the Unicode base codepoint for Hangul syllables). Part of ajin.im's family of single-file tools (debug::u, deadend, lemon, omen.ops): dark monospace aesthetic, human/cultural subject run through a systems lens.

## Thesis

Hangul composes by addition at every level. Strokes add to make letters, letters pack into a block, and the block is literally an integer:

```
codepoint = 0xAC00 + 초성_index×588 + 중성_index×28 + 종성_index
```

The eventual full claim (Phase 2): the script never bottoms out into arbitrariness. Latin eventually hits "why does A look like A" and the answer is an accident; Hangul's shapes derive from articulation + stroke-addition rules documented in the 훈민정음 해례본.

## Current state

**SHIPPED (Phase 1, 2026-06-13):** live at https://ajin.im/is/building/ac00/ (soft-launch: noindex, no hub listing; lifting that is Ajin's call). Source of truth is `is/building/ac00/index.html` in mobetter20.github.io; a local Downloads snapshot (not committed) is the pre-ship mock. The page has:

- **Compose mode**: 19/21/28 jamo chip pickers, live glyph + schematic + equation
- **Decompose mode**: text input (default 한글은 정수다), clickable per-syllable chips, same view
- Live equation panel: base + three terms → hex/decimal + UTF-8 bytes
- Layout-rule detection (vertical / horizontal / wrapped compound vowel) with matching schematic redraw
- Random syllable button
- State persists across mode switches
- URL state: `#한` or `#D55C` loads that syllable in compose mode; user interactions rewrite the hash via replaceState
- Decompose is the default mode on load (when no hash is present)
- Ship chrome: noindex meta, text-only OG/twitter meta (subtitle verbatim, no image card), `/img/a3.png` favicon, `/analytics.js`, `made by ajin.im` footer link

## Hard constraints

- **Single .html file, no build step, no backend, vanilla JS.** Google Fonts CDN (IBM Plex Mono, Noto Sans KR) is the only external dependency.
- Schematic block diagram stays **beside** the rendered glyph, never overlaid on it. Overlays can't align with real font metrics; honest-schematic over fake precision.
- 해례본-derived facts only in any explanatory copy. No learner mnemonics ("ㄱ looks like a gun" is banned).

## Design tokens (do not drift)

```
bg      #101013    panel  #17171b    panel2 #1d1d22
line    #2a2a31    text   #e8e4da    dim    #6e6a60   faint #44423c
초성 cho  #e3492b  (vermilion)
중성 jung #d9a441  (ochre)
종성 jong #4fa3a5  (teal)
mono: IBM Plex Mono · hangul: Noto Sans KR
```

**Signature device**: the three role colors thread through chip selection, schematic regions, and equation terms simultaneously. They encode the mapping between spatial position and arithmetic term. Any new feature touching jamo must respect this correspondence.

## Reference data

```
초성 (19): ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ
중성 (21): ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ
종성 (28): ∅ ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ

vowel layout classes (by 중성 index):
  vertical  {0,1,2,3,4,5,6,7,20}      ㅏㅐㅑㅒㅓㅔㅕㅖㅣ
  horizontal {8,12,13,17,18}           ㅗㅛㅜㅠㅡ
  wrapped    remainder                 ㅘㅙㅚㅝㅞㅟㅢ etc.

valid syllable range: U+AC00 가 … U+D7A3 힣 (11,172 blocks)
decompose: s = cp − 0xAC00; cho = ⌊s/588⌋; jung = ⌊(s mod 588)/28⌋; jong = s mod 28
```

## Decisions (resolved 2026-06-13)

1. **Default mode on load**: decompose-first (a shared `#syllable` URL opens in compose instead)
2. **Framing copy**: none for Phase 1; subtitle + footer already carry the thesis, the bigger "never bottoms out" claim waits for Phase 2
3. **Name**: `AC00`, at `/is/building/ac00/`
4. **Listing**: soft-launch (noindex, not on /is/building); hub-listing is a later owner call

## Roadmap

**Phase 1 polish**
- ~~URL state~~ DONE at ship (reads `#한`/`#D55C`, writes on interaction)
- ~~OG meta tags + favicon~~ DONE at ship (text-only meta, a3 favicon)
- Mobile pass beyond the current single breakpoint (3-width check passed at ship; a deeper device pass stays open)
- Keyboard input in compose mode (typing a Korean syllable loads it): nice-to-have, still open

**Phase 2 (the stroke layer — the merge that justifies the project)**
- Zoom from a selected jamo down to its 해례본 derivation
- Consonants: 가획 chains from 5 primitives (ㄱ velar, ㄴ lingual, ㅁ labial, ㅅ dental, ㅇ laryngeal), each with a minimal sagittal articulator SVG; 이체자 (ㆁ ㄹ ㅿ) flagged as the documented exceptions; tense = doubling
- Vowels: ㆍ ㅡ ㅣ primitives (heaven/earth/human) composing outward
- Full derivation table is in `hangul-zoom-spec.md` §3

**Phase 3**
- Archaic letters (ㆍ ㆁ ㆆ ㅿ) in the stroke layer
- Thesis/tour copy ("never bottoms out into arbitrariness")

## Companion file

`hangul-zoom-spec.md` — the full original spec with the derivation tables, worked example (한 = U+D55C), and audience rationale. Read it before starting Phase 2.
