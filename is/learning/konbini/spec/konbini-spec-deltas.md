# Konbini Spec Deltas — Japanese-First World

This document records corrections to `konbini-mvp-spec-v2.md` and `konbini-content-templates.md` made during the final pre-build content review. These deltas take precedence over the original spec where they conflict. Claude Code should treat these as authoritative.

---

## Core correction: The konbini is Japanese

Original spec conflated "English-speaking user" with "app has English UI." Wrong. A real konbini's signs, packaging, clerk dialogue, and printed notices are all in Japanese. The user is a Japanese learner using the app for immersion, so the world must be Japanese. English appears only in learner-facing explanations (vocab popup meaning field, About page, exit line).

This changes several things across content, UI, and parser.

---

## 1. Bilingual item descriptions

Item frontmatter now has two description fields, not one:

```yaml
description_jp: 九月《くがつ》にとれた鮭《さけ》。少し寒《さむ》い土地《とち》の米《こめ》。どちらにも何《なに》も聞《き》かなかった。
description_en: A salmon caught in September. Rice from a slightly colder place. Neither was asked anything.
```

**Rendering:** Japanese shown primary. English shown below in smaller muted text (e.g., `font-size: 13px; color: var(--color-text-tertiary); font-style: italic`). The English is gloss, not title.

**Flash behavior unchanged:** full-screen flash on item entry, ~1.5s, both JP and EN visible during the flash.

---

## 2. Furigana via `《》` notation

Content files may include furigana markup on any kanji word that isn't a `[word-id]`:

```
九月《くがつ》  →  <ruby>九月<rt>くがつ</rt></ruby>
土地《とち》    →  <ruby>土地<rt>とち</rt></ruby>
```

**Parser rule:** Any `[漢字]+《[ひらがな]+》` sequence converts to ruby HTML at build time. This is orthogonal to `[word-id]` tap markers. A single word can be either a tap target (uses vocab.md's reading field for furigana) or plain furigana-annotated text, not both.

**For `[word-id]` tap markers:** the parser auto-generates ruby from the vocab entry's `reading` field. No author burden. Example: `[benizake]` → `<ruby>紅鮭<rt>べにざけ</rt></ruby>` with tap-target styling applied.

**MVP behavior:** furigana always visible. A v2 settings toggle can hide it globally via CSS (`.hide-furigana rt { display: none; }`). Don't build the toggle now.

---

## 3. UI strings file (new file type)

New directory: `content/ui/`. Contains `strings.md` holding every UI-chrome string in JP primary / EN gloss format.

**Parser reads** `content/ui/strings.md` and makes strings available via a typed accessor:

```typescript
getUIString(key: string): { jp: string, en: string }
```

**Rendering convention:** Japanese always primary in the UI. English gloss shown only where it aids accessibility (aria-label, title attributes, screen-reader text). No bilingual display in the UI itself except for the About page (which is authorial voice).

**Exception — exit line.** The post-checkout exit line is English-only intentionally. It's the leave-the-fiction moment. JP version in the strings file can be null or identical to EN.

Schema of `strings.md`:
```markdown
## key_name
jp: Japanese text with 《ふりがな》
en: English gloss

## key_name_with_style
jp_style: deadpan
jp: ...
en: ...
```

The `jp_style` field is optional metadata (for CSS class hooks on specifically styled strings like empty-state deadpan copy).

---

## 4. Dialogue: all choices valid, clerk branches on response

Replaces the `correct` / `wrong-register` labels from the original template. Player choices are now all valid Japanese responses with different social registers. Clerk responds slightly differently based on which was chosen.

New block type: `::clerk-branch[response_id]` — a clerk line that only renders if the previous `::player-choice` selected the option tagged with that `response_id`.

Example:
```markdown
::player-choice
a: [onegai]します | wants_receipt
b: [daijoubu]です | declines_receipt
::

::clerk-branch[wants_receipt]
はい、[receipt]です。
::

::clerk-branch[declines_receipt]
かしこまりました。
::
```

**Parser rule:** `::clerk-branch[id]` blocks must have their `id` matching a response tag from the immediately preceding `::player-choice`. Orphan branches fail the build.

**Rendering:** After the player taps an option, only the matching `::clerk-branch` blocks render in sequence. Other branches are skipped. Linear flow continues after.

**Parser convenience:** the `| response_id` tags on choices may include `polite`, `casual-polite`, `wants_receipt`, `declines_receipt`, etc. — these are free-form strings at the author's discretion.

---

## 5. Vocabulary popup rendering — furigana in surface

The popup's surface-form display should show furigana via ruby:

```
<ruby>紅鮭<rt>べにざけ</rt></ruby>
```

Rather than two separate fields as originally spec'd (surface + reading). The `reading` field in vocab.md is still used — it becomes the ruby annotation. Showing reading separately below is redundant and the popup becomes lighter.

**Popup fields remain:**
- Surface (with ruby furigana)
- JLPT level + POS (small, muted)
- English meaning
- Etymology (when present)
- Korean parallel (when present, prefixed `韓国語:` per UI strings file)

Buttons use Japanese labels from UI strings file (`保存` / `閉じる`).

---

## 6. Parser rule additions summary

Adding to the existing 7 error rules:

- **Unresolved `《ふりがな》` markup:** If furigana notation is malformed (e.g., unmatched `《` or `》`), fail with specific error.
- **Orphan `::clerk-branch` blocks:** A clerk-branch with no matching preceding player-choice response_id fails the build.
- **Missing UI string keys:** If the app references a UI string key that doesn't exist in `content/ui/strings.md`, fail. (This requires a list of known keys — Claude Code should enumerate them from code references during build.)

Existing warnings remain; no new warnings needed.

---

## 7. Frontmatter field changes

**Items:**
- `description` → split into `description_jp` (required) and `description_en` (required)
- Other fields unchanged.

**Notices:** unchanged (already mostly Japanese, just verify no English bleed).

**Dialogue:** unchanged.

**Vocab:** unchanged.

**UI strings:** new file, schema defined in section 3 above.

---

## 8. Specific content decisions finalized

**About page:** four-stanza Japanese version in `content/ui/strings.md` under `about_body`. English version also there for accessibility. Signed 「店長」(store manager) — replaces "— Management" which was my earlier English draft.

**Empty state JP rewrites:** deadpan register preserved. The translations are not literal — "それはそれでよろしい" is a more natural Japanese deadpan for "this is defensible" than a direct translation would be.

**Exit line remains English-only.** Intentional. The moment you leave the konbini is when English returns.

---

## 9. What did NOT change

- Payment rounding rule (next ¥1000; next ¥500 if ≤ ¥500)
- Take-to-register flow (add and stay)
- First-item-tap flash (full-screen, 1.5s)
- LocalStorage schema
- Out-of-scope list
- Tech stack
- Build order

---

## Handoff order

1. Read `konbini-mvp-spec-v2.md` (the spec)
2. Read `konbini-content-templates.md` (template contract)
3. Read this deltas document — apply these corrections over the spec/templates
4. Read `claude-code-prompt.md` (build instructions)
5. Content bundle in `konbini-content/` or `konbini-content-day-one.tar.gz`

Total new/changed file types the parser handles:
- items, notices, dialogue, vocab (original 4)
- ui/strings.md (new)

Total block types the parser handles:
- `::banner`, `::hero`, `::footer`, `::nutrition`, `::section`, `::fineprint` (items)
- `::heading`, `::body` (notices, implicit)
- `::clerk`, `::player-choice`, `::clerk-branch`, `::action`, `::exit` (dialogue)

Total markup conventions:
- `[word-id]` — tap target, auto-furigana from vocab entry
- `《ふりがな》` — manual furigana on any preceding kanji word
- `{{placeholder}}` — runtime substitution in dialogue
- `| tag` — response_id on player choice options
