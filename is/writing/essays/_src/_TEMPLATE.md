# Essay template — `is/writing/essays/`

How to add a new essay to the loose-pieces site. Read this before writing the HTML by hand or asking Claude to do it.

---

## File layout per essay

```
is/writing/essays/<slug>/index.html   ← rendered page (uses creative-house.css)
is/writing/essays/_src/<slug>.md      ← markdown source, kept for re-export
```

Slug rules: lowercase, hyphenated, descriptive. Match the title roughly. Examples: `already-seen`, `the-house-chips-of-ai`, `every-few-years`.

---

## Markdown source convention

```markdown
### <Title>

**<Optional one-line subtitle / dek. Goes OUTSIDE the body card, not inside it.>**

<Opening paragraph. This is the lead of the body — first paragraph inside the card.>

<More body paragraphs.>

#### <Section heading>

<Section paragraphs.>

#### <Next section heading>

...
```

- `###` → `<h1 class="post-title">` (the page title; only one)
- `**bold one-liner**` directly under the title → `<p class="post-subtitle">` in `.post-head` (outside the body card)
- `####` → `<h3>` inside `.post-body` (italic serif section heads)
- Plain prose → `<p>`

If the essay has no subtitle, omit the bold line — the `.post-subtitle` element should not be emitted.

---

## HTML scaffold

Copy this when generating the page. Update `<TITLE>`, `<SLUG>`, `<META_DESCRIPTION>`, `<SUBTITLE>`, and the body.

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="icon" type="image/png" href="/img/a3.png" />
    <link rel="apple-touch-icon" href="/img/a3.png" />
    <title><TITLE> | ajin.im/is/writing/essays</title>
    <meta name="description" content="<META_DESCRIPTION>" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=DM+Mono:wght@300;400;500&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="../../../../creative-house.css" />
    <script src="../../../../analytics.js" defer></script>
  </head>
  <body class="post-page">
    <main class="post-shell">
      <header class="post-head">
        <a class="back-link" href="../index.html">Back to essays</a>
        <p class="path-mark">ajin.im is writing essays</p>
        <h1 class="post-title"><TITLE></h1>
        <p class="post-subtitle"><SUBTITLE></p>
      </header>

      <article class="post-body">
        <p><LEAD_PARAGRAPH></p>
        <p>...</p>

        <h3><SECTION_HEADING></h3>
        <p>...</p>
      </article>
    </main>
  </body>
</html>
```

Notes:
- The four-deep relative path (`../../../../creative-house.css`) is correct for `is/writing/essays/<slug>/index.html`.
- Subtitle (`.post-subtitle`) lives **inside `.post-head`** — outside the body card. Putting bolded one-liners as the first `<p>` inside `.post-body` looks like a misplaced subtitle and reads worse.
- Section headings inside `.post-body` are styled at three sizes — `<h2>` (large, 2rem), `<h3>` (1.7rem), `<h4>` (1.35rem). For most essays, `<h3>` reads as a clean chapter break; reserve `<h2>` for very long pieces with major parts.
- Smart quotes and en/em dashes: in HTML, prefer entity references (`&rsquo;`, `&ldquo;`, `&rdquo;`, `&mdash;`, `&ndash;`) for safety. The Markdown source can stay typographic.

---

## After creating the essay

Update both archive pages:

1. **`is/writing/loose/index.html`** — add a new `archive-card` at the top of the essays section with:
   - `<span class="loose-tag loose-tag-essay">essay</span> New &middot; YYYY` (only the actual newest essay carries `New · YYYY`; demote the prior `New` entry to plain `essay`)
   - One-sentence excerpt below the title
2. **`is/writing/essays/index.html`** — add a new `essay-entry` at the top of the `essay-list` (the `essay-feature` slot is curatorial; do not auto-promote a new essay into it — ask first)

---

## Comedy pieces, for reference

Comedy follows the same shell but adds Medium-era metadata:

```html
<header class="post-head">
  <a class="back-link" href="../index.html">Back to comedy</a>
  <p class="path-mark">ajin.im is writing comedy</p>
  <p class="archive-meta">Medium years / <Month Day, YYYY></p>
  <h1 class="post-title"><Title></h1>
  <p class="post-subtitle"><Subtitle></p>
  <p class="post-note">
    Originally published on Medium on <Month Day, YYYY>.
    <a href="<URL>" target="_blank" rel="noreferrer noopener">View original</a>
  </p>
</header>
```

Essays generally don't need `archive-meta` or `post-note`.
