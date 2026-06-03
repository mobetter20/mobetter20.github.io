# mobetter20.github.io

Static site hosted on GitHub Pages. Contains the creative house at `ajin.im/is/writing/` and the Avian Municipal District universe.

## Design System — typographic tiers

Governing rule: **consistent chrome, free content.** The wrapper is uniform; what's inside is free to vary by tier. When adding or restyling a page, classify it first, then give it that tier's chrome.

**Tier test — does the visitor *dwell* in the page, or *scan past* it?**

| Tier | Test | Serif | Where |
|---|---|---|---|
| **Frame** | scan-and-navigate; points at things | Source Serif 4 | `/`, `/is/running`, `/is/reading`, `/is/learning`, `/is/building` |
| **House** | dwell; the page *is* the made thing | Cormorant (`creative-house.css`) | `/is/writing` + rooms (bird-coo, bird-docket), the `/wrote` archive (essays + comedy, pieces at `/wrote/<slug>/`) |
| **Bespoke** | a singular work whose form is part of the art | its own | avian-district, secondnest, konbini, the `every-few-years` essay, perch-chat, Small Ware's sub-tools |

Tier follows a page's **nature, not its URL parent** — konbini (bespoke) sits under frame `/is/learning`; Small Ware (house) sits under frame `/is/building`. A sub-page keeps its own tier and gets a working up-link to its parent; it does NOT inherit the parent's serif.

**Chrome = a 5-part envelope:** (1) the "ajin.im is ___" title device — faint prefix, italic verb, "ajin.im" links home (`target="_self"`); (2) a way home / up-link; (3) a contact/footer line; (4) DM Mono for labels; (5) warm-dark palette (bg `#1a1612` frame / `#110d0b` house, text `#e8e0d0`).

**Chrome is a gradient, not a switch:**
- **Frame + House** wear the FULL envelope. The title device renders in the page's own serif: frame uses `.title` (in `templates/*.html`), house uses `.house-title` (in `creative-house.css`). Same device, tier-local serif.
- **Bespoke** wear only the ANCHORS — a way home + palette sympathy + DM Mono if labels appear. Do NOT force the title device on them; their singular design is intentional, and flattening it is a regression.
- **The "made by ajin.im" colophon** is the standard form of that *way home* for Bespoke pages and standalone sites (own domain) that don't wear the title device. It's a maker's *signature* — meta, sitting outside the fiction — so it rides fiction-heavy worlds (the bird-universe, BIC) where a back-breadcrumb would break character; keep it to one discreet, muted footer line. Internal ajin.im pages link `/` (same tab); standalone sites link `https://ajin.im` (new tab, `rel=noopener`). **On:** omen.ops, BIC (propagandaformyself.xyz), seoulcrushing, bird-universe **avian-district** (in-world hub). **NOT on:** standard section pages (title device already links home), the sealed bird-universe leaf rooms, **bird-coo / The Municipal Coo** (it added footer bulk — rejected 2026-06), or archived/noindex pages. Per-site bird-universe status (front door = bird-coo, internal hub = avian-district, archived = bird-docket) lives in `_scripts/bird-universe/bird_universe_registry.json`.

Within the house, `.house-title` marks **section entrances and orphan URLs** (`/is/writing` → "ajin.im *is* writing"; `/wrote` → "ajin.im *wrote*", past tense). Individual works (comedy pieces, essays, Coo issues) carry their own title as content. The device tolerates the page's tense/phrasing — a sub-hub may extend its parent's verb, e.g. Small Ware → "ajin.im *is* building small."

**Favicon scheme:** `a1` = frame hubs (`/`, running, reading, learning, building); `a2` = error/404; `a3` = house + all generated pages; bespoke pages carry their own art. (Single 180px PNGs today; full sized-set + manifest deferred.)

## World Bible

The world-building reference for the Avian Municipal District lives in two locations that must stay in sync:

- **Local (primary working copy):** the `bird-universe/` folder in the local writing directory
- **GitHub (backup):** `github.com/mobetter20/ajin-universe-bible` (private)

Read `INDEX.md` for what to load and when. Modular files:
- `00-foundation.md` — philosophy, tone hierarchy, house principles
- `01-strategy.md` — current state, priorities, interconnections
- `02-registry.md` — characters, cases, locations, objects, workflow
- `03-coo-taxonomy.md` — 12 story categories for The Municipal Coo

**Before writing content** for any bird-universe site, check `02-registry.md` for entity facts.

**After publishing**, update the registry with new facts established (characters, locations, channel changes, etc.) in BOTH the local copy and the GitHub repo. Do not leave them out of sync.

## Build Scripts

`_scripts/build_root.py` generates the stats-driven pages — `index.html` (the root `ajin.im is …` page), `is/running/`, `is/reading/`, `is/learning/` — from `templates/{root,running,reading,learning}.html` + `content/stats.md`. **Edit the templates, never the generated `index.html` files.** Direct edits are overwritten on the next build, and `.github/workflows/rebuild-root-on-stats.yml` rebuilds them automatically whenever a template, `stats.md`, or the script changes. Each generated file carries a `GENERATED FILE — DO NOT EDIT` banner under its doctype as an in-file reminder.

`_scripts/build_bird_coo.py` generates all Municipal Coo HTML (index, issues, archive). Manual edits to generated files will be overwritten on next build. Make template changes in the build script.

The script also auto-updates the "From the Municipal Coo" excerpt block on `is/writing/avian-district/index.html`. The block lives between `<!-- COO-EXCERPT-START -->` and `<!-- COO-EXCERPT-END -->` markers — manual edits inside that range will be overwritten on next build. Edit the renderer in `_scripts/build_bird_coo.py` (`render_avian_district_excerpt`) instead.

`_scripts/build_essays.py` and `_scripts/build_comedy.py` generate the writing-archive pieces into `/wrote/<slug>/` (essays from `is/writing/essays/_src/`; comedy from external Medium exports + `is/writing/comedy/_src/`). `_scripts/build_wrote.py` renders the single combined index `/wrote/index.html` by importing both generators — it is the source of truth for the archive listing, so the index can never drift from the pieces that exist. Run order in `publish.sh`: `build_comedy.py` → `build_essays.py` → `build_wrote.py`. The old section indexes `is/writing/essays/index.html` and `is/writing/comedy/index.html` are redirect stubs to `/wrote/`; do not add piece links by hand. To add an essay: drop its markdown in `is/writing/essays/_src/` and register it in `build_essays.POST_DEFS` (or, for a hand-built bespoke page like `every-few-years`, add it to `build_wrote.BESPOKE_ESSAYS`).

## CSS / Layout Changes

Any change to padding, margin, width, max-width, grid, or flexbox layout requires verification at three widths before committing:

1. **Mobile** (375px) — check nothing overflows or misaligns
2. **Tablet** (~768px) — check breakpoint transitions
3. **Desktop** (1280px+) — check content is properly constrained

Before adding padding or margin to any element, check if that selector appears in a `@media` block — mobile overrides will stack with your change and cause double-padding or misalignment.

When changing a container's width or padding, inspect the computed width of the changed element AND the elements visually adjacent to it (above/below) to confirm they still align.

## Cross-Site Links

- Use root-relative paths (`/is/writing/nest-court/`) not relative (`../nest-court/`)
- All cross-site links must include `target="_blank"`
- The pre-push hook enforces root-relative paths for structural links

## AMD Tooling

`_scripts/bird-universe/` contains three tools that automate cross-reference checks
when working on Avian Municipal District pages. Read `_scripts/bird-universe/README.md`
for full details. Quick reference:

- **`generate_graph.py`** — produces `bird_universe_graph.json`, a precomputed
  cross-reference cache (sites + characters + cases, with reverse-index
  `mentions` per entity). Runs from `publish.sh` before other build scripts.
  When you need to know "where is X mentioned?" or "is this case in the
  registry?", read this file instead of re-greping HTML and re-reading
  `02-registry.md`. Path to the registry repo is configured in
  `_scripts/bird-universe/config.json`.
- **`check_bird_universe_links.py`** — pre-push validator. In addition to
  registry/structural rules, now also verifies that every `<a href="#X">`
  in bird-universe pages has a matching `id="X"` on the same page. SVG
  internal references (`<textPath>`, `<use>`, `<clipPath>`) are intentionally
  not checked.
- **`lint_identifiers.py`** — pre-push warning system. Scans HTML for
  case-number patterns (`AMNC-YYYY-NNN[A-Z]`) and form-ID patterns
  (`CL-XX-NN`). Errors on case-format typos; warns on identifiers in HTML
  that aren't in the registry yet. Also warns when
  `bird_universe_graph.json` is stale relative to `02-registry.md` (rebuild
  with `generate_graph.py`). Character-name linting is intentionally
  deferred — single-token names like "Conrad" / "Dennis" collide with
  ordinary English.
