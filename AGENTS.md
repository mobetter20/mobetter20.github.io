# mobetter20.github.io

Static site hosted on GitHub Pages. Ajin's writing, cartoons, worlds and builds.

**North-Star:** A distinctive front door into Writing and Building, with Running as a small personal thread beneath them. Keep Writing's newspaper reading experience and complete artwork, Building's cabinet, and Running's journey as distinct worlds rather than flattening them into one house style.

## Maintenance documentation

For routine image additions, start with [PUBLISHING.md](PUBLISHING.md) and `_scripts/piece.py`; use the fixed defaults and one batch check instead of reconstructing the workflow from chat history. Read [MAINTENANCE.md](MAINTENANCE.md) for source ownership, unusual changes or publishing behavior. Keep the guides current when behavior changes; routine content batches belong in the catalog and release PR, without rewriting a running inventory in the guide. Git records exact changes. Distinguish a local preview, a pushed branch and a verified live release. A successful build or local commit does not mean published. `CLAUDE.md` imports this file, so the same entry point applies across agents.

## Design System — typographic tiers

Governing rule: **consistent chrome, free content.** The approved newspaper entrances, Building cabinet, Running blue journey and Bus rack are scoped exceptions described under Information architecture. Read those before applying the older envelope. The wrapper is uniform; what's inside is free to vary by tier. When adding or restyling a page, classify it first, then give it that tier's chrome.

**Tier test — does the visitor *dwell* in the page, or *scan past* it?**

| Tier | Test | Serif | Where |
|---|---|---|---|
| **Frame** | scan-and-navigate; points at things | EB Garamond | `/`, `/is/running`, `/is/reading`, `/is/learning`, `/is/building` |
| **House** | dwell; the page *is* the made thing | EB Garamond (`creative-house.css`) | `/is/writing` + rooms (bird-coo, bird-docket) |
| **Bespoke** | a singular work whose form is part of the art | its own | avian-district, secondnest, konbini, perch-chat, Small Ware's sub-tools |

Tier follows a page's **nature, not its URL parent** — konbini (bespoke) sits under frame `/is/learning`; Small Ware (house) sits under frame `/is/building`. A sub-page keeps its own tier and gets a working up-link to its parent; it does NOT inherit the parent's serif.

**Chrome = a 5-part envelope:** (1) the "ajin.im is ___" title device — faint prefix, italic verb, "ajin.im" links home (`target="_self"`); (2) a way home / up-link; (3) a contact/footer line; (4) DM Mono for labels; (5) warm-dark palette (bg `#1a1612` frame / `#110d0b` house, text `#e8e0d0`).

**Chrome is a gradient, not a switch:**
- **Frame + House** wear the FULL envelope. The title device renders in the page's own serif: frame uses `.title` (in `templates/*.html`), house uses `.house-title` (in `creative-house.css`). Same device, shared serif EB Garamond — tier is carried by palette + chrome + content, not typeface.
- **Bespoke** wear only the ANCHORS — a way home + palette sympathy + DM Mono if labels appear. Do NOT force the title device on them; their singular design is intentional, and flattening it is a regression.
- **The "made by ajin.im" colophon** is the standard form of that *way home* for Bespoke pages and standalone sites (own domain) that don't wear the title device. It's a maker's *signature* — meta, sitting outside the fiction — so it rides fiction-heavy worlds (the bird-universe, BIC) where a back-breadcrumb would break character; keep it to one discreet, muted footer line. Internal ajin.im pages link `/` (same tab); standalone sites link `https://ajin.im` (new tab, `rel=noopener`). **On:** omen.ops, BIC (propagandaformyself.xyz), seoulcrushing, bird-universe **avian-district** (in-world hub). **NOT on:** standard section pages (title device already links home), the sealed bird-universe leaf rooms, **bird-coo / The Municipal Coo** (it added footer bulk — rejected 2026-06), or archived/noindex pages. Per-site bird-universe status (front door = bird-coo, internal hub = avian-district, archived = bird-docket) lives in `_scripts/bird-universe/bird_universe_registry.json`.

The newspaper Home and unified Writing page use EB Garamond, IBM Plex Mono, cream `#fffef8`, ink `#101b33`, blue `#1c4286`, and yellow `#fff200`. Their original varied editorial typography is intentional. Individual writing readers share those fonts and colors but keep a single reading column. `/writes/` and `/wrote/` are compatibility redirects to `/is/writing/#all`; article URLs and the essay feed remain durable. The other worlds keep their own visual identities.

**Favicon scheme:** `a1` = frame hubs (`/`, running, reading, learning, building); `a2` = error/404; `a3` = house + all generated pages; bespoke pages carry their own art. (Single 180px PNGs today; full sized-set + manifest deferred.)

## Information architecture

- **Home (`/`)** is Home C: complete pinned Austen artwork and caption on the left, the real Kenbaiki machine preview on the right, then a smaller centered Earth/runner/Moon Running strip, then email. It contains no essay, comedy, Municipal Coo or catalog list. Austen is a static reader link, not a rotating selection; retain `featured` catalog fields only for compatibility. Home reads the image catalog and running stats, never prose. The image, caption and native same-tab reader link must agree. Home's static Austen art is the no-JavaScript and failed-image fallback.
- **Writing (`/is/writing/`)** remains the newspaper selection with one early "Browse all writing" link. `#all` opens one column of article titles ordered by publication date, newest first, in 22px regular EB Garamond. Undated work follows dated pieces; do not invent dates. "10 Reasons Why You Shouldn't Read This List" is unlisted through `paper_site.UNLISTED_COMEDY_SLUGS`; its reader URL and source remain available. No visible archive heading, search, dates, counts, mode toolbar, or duplicated browse link. Keep the accessible hidden heading. Home and the Writing selection omit the illustration credit. The Municipal Coo stays a separate publication.
- **Writing selection:** Ajin chose “Wife Evolves Into a Scarier Pokemon” for the feature slot and “Step on Me Please” for the sidebar on 2026-11-10. Use the actual opening text, including the trash-can setup; do not invent subtitles or dates. Wish Depletion and Anger remain in Browse all.
- **Building (`/is/building/`)** is its own blue/yellow cabinet. Canonical choices live in `content/building.json`: BIC, Seoul Crushing, Instrument Bus, then omen.ops, Kenbaiki, Passport Stamp Archive, Metro Match, LunarOnce, the sky over Seoul. Crossings is unlisted, not deleted. Do not restore a section-button strip or footer Home link; the cabinet title already links Home. `night` controls the project's dark press-face.
- **Running (`/is/running/`)** keeps the Earth/runner/Moon journey, now in blue with the newspaper's type. It is not a category in the masthead. Its figures come from `content/stats.md`, updated by the existing running sync.
- **Navigation:** the newspaper category links, Home title, mileage box and reader return links explicitly use `target="_self"`. Article links and external projects retain their existing new-tab behavior. Arrows describe actual behavior: → same tab, ↗ new tab.
- **Future essays:** the `_src/` directory remains the registry. Every published essay is rendered at `/writes/<slug>/` and linked from the unified Writing archive. Publisher proof is the exact archive link plus committed source and reader, not a Home card. Direct arrivals and reader returns go to unified Writing. Zero essays is valid; do not restore the seven retracted essays.
- **Cartoons:** all 11 catalog cartoons have an overview at `/is/writing/cartoons/`, an entry slide at `/is/writing/cartoons/slides/#cartoon`, and native slide URLs at `/is/writing/cartoons/slides/<slug>/#cartoon`. Writing's “All cartoons” enters slides; overview links to slides. Swiping is a touch-only enhancement over native arrows, never a replacement. No-JavaScript arrows remain functional. The original individual reader routes stay canonical. Credit is absent on Home and Writing selection, but appears at the bottom of the overview, slides and individual readers; the collection omits email. The supplied versioned Market PNG replaces its displayed art while the older asset remains retained.
- **Distinct worlds:** Coo, BIC, Instrument Bus, Seoul Crushing and the individual builds retain their own interfaces. These entrance changes do not flatten their designs.
- **Image pieces:** `content/image-pieces.json` owns titles, publication dates, assets, dimensions, accessible descriptions and optional captions. Each piece has its own `/is/writing/<slug>/` page and appears in the newest-first Writing list. Keep complete artwork and native enlargement; avoid duplicating a title or caption embedded in the image. Existing undated work stays undated. New pieces belong in Writing and on their own pages, not Home. The shared credit is "Words and ideas by Ajin. Illustrations generated with AI." belongs at the bottom of cartoon overview/slides/readers, never in the archive or entrance pages. Existing prose URLs and the automatic essay publisher remain unchanged.
- `assets/paper/home-preview.png` is the 1200x630 Home social preview. Recapture it when Home materially changes.

## Build Scripts

`_scripts/build_root.py` generates Home, Running, Reading and Learning from `templates/` and `content/stats.md`. Home reads the image catalog and running stats, not prose. `--check-home` verifies exact source/output agreement. **Daily running sync must continue to change only `content/stats.md`, `index.html`, and `is/running/index.html`.** It does not generate Writing or Building.

`_scripts/build_sections.py` owns Writing, Building, individual image readers, cartoon collection/slide pages and the old writing section-index redirects. It reads `content/comedy.json`, `content/building.json`, `content/image-pieces.json`, and the essay registry. `_scripts/image_pieces.py` validates the image catalog and renders readers; `_scripts/cartoon_collection.py` renders the overview and native slides; both use the paper reader family. `_scripts/build_writes.py` calls sections and then refreshes Home during normal publishing. Edit source catalogs, templates and renderers, not generated HTML. Paper assets are in `assets/paper/`; `assets/entrances/cabinet.css` remains shared and is not globally restyled.

For a deliberately composed pair of equal square panels in a 2:1 image, optional `mobile_panels: 2` stacks the full left and right halves on phones. This is presentation only: the original asset and full-size link remain intact. Never infer panel divisions automatically from an image’s shape; verify the seam and caption legibility before using it.

Optional `show_title: true` makes the existing piece title visible above the artwork when it supplies part of the joke or its setup. It defaults to false; do not add repeated headings to existing images. Keep the title in the Writing list and page metadata either way. The visible title uses the reader's newspaper typography and stays outside the image file.

The committed `content/comedy.json` holds 50 Medium articles plus one standalone Markdown piece. The owner-confirmed Medium comment `585a1f5d093f` is excluded from import and removed from the public archive and reader routes. Ordinary builds never require private exports. `_scripts/build_comedy.py --import-medium` is an explicit importer. It removes verified promotional nodes, never an entire `section--last`: short articles and substantive final sections use that class. Empty bodies, duplicate slugs and malformed data fail the build.

Comedy posts may have an optional `illustration` object with exactly `image`, `width`, `height` and `alt`. It is a local addition rendered before the prose, with native enlargement, an AI illustration credit and matching social-image metadata. The importer preserves it by slug. Do not insert it into `body_html`: the Medium cleaner deliberately strips imported figures. Adding an illustration must not change the article's text, date, title, URL or list position.

Validation before publication:

```sh
python3 -m unittest discover -s _scripts -p 'test_*.py'
python3 _scripts/build_comedy.py
python3 _scripts/build_essays.py
python3 _scripts/build_writes.py
python3 _scripts/build_wrote.py
python3 _scripts/build_root.py
python3 _scripts/build_root.py --check-home
python3 _scripts/build_sections.py --check
python3 _scripts/check_links.py
python3 _scripts/build_sitemap.py
node _scripts/test_cartoon_swipe.js
```

The PR workflow `check-paper.yml` repeats the deterministic build without private files and rejects generated drift, missing social artwork, and stale sitemap routes. Sitemap `lastmod` dates follow Git commits and are refreshed by the root workflow after merge. The existing root/stats workflow keeps its narrow staging list. Re-run the layout at 375, 768 and 1280px after layout changes, including every eligible image lead, the archive and a reader. Test native image-page navigation, no-JavaScript and failed-image fallbacks, caption/link consistency, complete uncropped artwork and layout stability during image loading.

`_scripts/canary/` is **retired (2026-11-08)**: LaunchAgent `com.ajin.canary-watcher` is unloaded (plist parked in `~/Library/LaunchAgents/_retired-20261108/`), `is/building/did-claude-just-reset-usage/` stays up as a noindex, unlisted record (its `state.json` carries `retired`, which the page reads), and nothing writes to master on its behalf any more. Revival steps are in `_scripts/canary/README.md`.

`_scripts/build_bird_coo.py` generates all Municipal Coo HTML (index, issues, archive). Manual edits to generated files will be overwritten on next build. Make template changes in the build script.

The script also auto-updates the "From the Municipal Coo" excerpt block on `is/writing/avian-district/index.html`. The block lives between `<!-- COO-EXCERPT-START -->` and `<!-- COO-EXCERPT-END -->` markers — manual edits inside that range will be overwritten on next build. Edit the renderer in `_scripts/build_bird_coo.py` (`render_avian_district_excerpt`) instead.

The writing readers are generated by `_scripts/build_comedy.py` and `_scripts/build_essays.py` using `writes.css` and `_scripts/writes_common.py`. `_scripts/build_writes.py` and `_scripts/build_wrote.py` generate the compatibility redirects, not competing indexes. The essay feed stays at `/writes/feed.xml`.

To add an essay, place its Markdown in `is/writing/essays/_src/`. Every `*.md` is an essay; `_`-prefixed notes are skipped. Front matter requires `title:` and a unique `order:` (highest newest); `date:` and `excerpt:` are optional. Bespoke essays use `build_writes.BESPOKE_ESSAYS`. The existing `_scripts/writes_publisher/` watches approved releases from `~/Documents/Ajin-Publishing/`; read its README before manually editing essay sources while armed. It requires a clean, synchronized canonical checkout. Worktrees let development proceed without disturbing scheduled publishing.

## CSS / Layout Changes

Any change to padding, margin, width, max-width, grid, or flexbox layout requires verification at three widths before committing:

1. **Mobile** (375px) — check nothing overflows or misaligns
2. **Tablet** (~768px) — check breakpoint transitions
3. **Desktop** (1280px+) — check content is properly constrained

Before adding padding or margin to any element, check if that selector appears in a `@media` block — mobile overrides will stack with your change and cause double-padding or misalignment.

When changing a container's width or padding, inspect the computed width of the changed element AND the elements visually adjacent to it (above/below) to confirm they still align.

## Cross-Site Links

### Analytics and browser checks

`analytics.js` is handwritten source, with navigation and GA4 loading in separate blocks. GA4 is allowed only on the exact production origins `https://ajin.im` and `http://ajin.im` in a non-automated browser with readable opt-out storage. HTTP currently also serves the real site; do not silently exclude those visitors. Local/file previews, other origins and ports, `navigator.webdriver`, and storage failures must send no analytics. `?notrack` persists the browser's `_notrack` flag; `?track` clears only that manual flag and cannot bypass the origin or automation guards. If both parameters appear, `notrack` wins. Do not remove these guards to make a browser check pass.

Before any agent-controlled visit to the live site, set `_notrack=1` in an origin-scoped browser-context init script and block Google Analytics / Google Tag Manager requests at the browser-context level. Install these before the first navigation, including for new tabs. Assert that no tracking request was attempted. Some agent browsers report `navigator.webdriver=false`, so the webdriver guard is a second line of defence, not a substitute for isolating test traffic. For a normal-visitor positive control, use a fresh isolated context with every Google endpoint blocked; never send a real analytics event as a test. Keep navigation checks enabled even when analytics is off.

Run `node --test _scripts/test_analytics.js` when changing the shared loader. CI and the publishing batch check run it automatically. After an analytics change deploys, verify the live script bytes, an unmarked automated-browser negative control, and a network-blocked normal-visitor positive control. See MAINTENANCE.md for the collection boundary and historical-data limits.

- Use root-relative paths (`/is/writing/nest-court/`) not relative (`../nest-court/`)
- The pre-push hook enforces root-relative paths for structural links
- **New tabs are global, by design.** `/analytics.js` (loaded on every page) runs a `retarget()` on load that sets `target="_blank"` on *every* `<a href>` except in-page `#anchors` and links that already declare a target. The home cabinet and Bus return explicitly override this where described above. Elsewhere, **links without explicit targets open in a new tab** — internal page-to-page navigation included, not just cross-site/external links. This is intentional: the current page stays open when you click out.
  - You don't need to hand-add `target="_blank"` — analytics.js does it. Adding it explicitly (e.g. on a cross-site link) is a harmless fallback; analytics.js skips links that already have a target.
  - **Don't infer tab behavior from a page's own markup** — it's overridden at runtime. To verify, inspect the rendered DOM (read `a.target`), not the source.
  - On the approved entrances, → denotes same-tab navigation and ↗ denotes a new tab. Elsewhere, inspect the actual runtime target before using an arrow: analytics supplies `_blank` when no explicit target exists. Do not infer same-tab behavior merely from an internal URL.

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

## Metro Cards (was: World Metros Atlas)

A bespoke build at `/is/building/metro-match/` (soft-launched, noindex; URL
moved from `world-metros` at D33, stub redirects; the
atlas-era prototype is live and gets rebuilt as a card deck per DECISIONS
D17–D19). Before touching anything metro-related, read
`_scripts/world_metros/README.md` — reading order, product contract, data
contract, and the decision log live there. Open forks need owner ratification
before frontend work starts (see `_scripts/world_metros/STATUS.md`).
