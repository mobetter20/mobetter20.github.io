# Maintaining ajin.im

This is the practical guide for adding work and maintaining the site. [AGENTS.md](AGENTS.md) holds the design decisions and project rules. Git records the exact changes. Update this guide alongside changes to the workflow, and add a brief dated entry for meaningful fixes or releases.

For ordinary image additions, use the short [publishing recipe](PUBLISHING.md) and `_scripts/piece.py`. The detailed source map below is for maintenance, not a checklist to reread for every cartoon.

## Release status

**Release status, 2026-11-09:** the newspaper redesign was published through PR #220, the first eight image readers through PR #221, Austen's publication-date correction through PR #222, and Do you cycle? and On privilege through PR #223. The public readers, assets and Writing list were checked after deployment. Each later release PR records its deployment and live verification. Approval, a Git push and a successful build are distinct from a verified deployment.

The current image inventory is [content/image-pieces.json](content/image-pieces.json), which generates the public Writing list. Only Austen is eligible for the homepage. Credits sit beside the artwork instead of in a generic writing footer.

The local review page used for this release was <http://127.0.0.1:8744/_review/>, with page and viewport selectors. It works only while its local server is running; this address is not a public deployment or permanent hosting arrangement. Visitors use <https://ajin.im/is/writing/#all>. Ordinary pages can also be previewed with a loopback-only static server from a worktree.

## Adding pieces: what Ajin needs to do

Send the images to Codex or Claude, singly or in a batch. Supply preferred titles or separate captions if there are any. Otherwise the agent can propose descriptive titles from the work.

Example: “Publish these in Writing.” For a local review instead, say “Preview first.” Austen stays on Home by default.

The agent handles the web assets, filenames, accessible descriptions, reader pages, Writing list, and visual checks. Ajin does not need to edit JSON or run build commands. Publication is a separate instruction when the work is still a preview.

The agent uses `_scripts/piece.py` to prepare images, check a batch and verify deployed pages. It does not require an AI API or a running service. There is no upload form or automatic image drop folder. The existing approved-release folder publisher handles Markdown essays; its instructions are in [_scripts/writes_publisher/README.md](_scripts/writes_publisher/README.md). Do not put images there and assume they will publish.

## Adding an image: maintainer procedure

The `add` command implements steps 2 through 4 below, including lossless conversion and pixel checks. `illustrate` attaches artwork to an existing comedy article without adding another Writing entry. `check` implements the build and mechanical checks once for the whole batch. The commands and short release sequence are in [PUBLISHING.md](PUBLISHING.md).

1. Check the active branch, worktree and Git status. Use a feature worktree based on the current default branch; continue an existing one if its work is still under review. Keep the canonical checkout free for the essay publisher, and investigate unrelated changes before touching them.
2. Inspect the original image. Choose a stable, descriptive lowercase slug with hyphens. The helper writes the web asset under `assets/paper/pieces/<slug>.webp`, using Pillow's lossless WebP encoder and comparing all decoded RGBA pixels. Earlier additions used `cwebp -lossless`. Do not change the illustration, crop away captions, or stretch it to match other pieces.
3. Add a record to [content/image-pieces.json](content/image-pieces.json). Use an existing record as a structural example, with a new unique slug. The fields are:

   | Field | Meaning |
   |---|---|
   | `slug`, `title` | Stable URL segment and the title used in Writing and page metadata. Changing a title need not change its URL. |
   | `published_date` | Site publication date as `yyyy-mm-dd`, or blank when genuinely unknown. Preview dates must be checked at publication. Do not derive historical publication dates from downloaded filenames. |
   | `image`, `width`, `height` | Root-relative asset path and its actual pixel dimensions. The build validates them. |
   | `alt` | Describe the relevant scene and include the words needed to understand the joke. |
   | `caption` | Separate caption text, or an empty string when the caption is already in the artwork. |
   | `featured` | Set new pieces to `false`. Austen stays on Home until Ajin asks to change it. |
   | `show_title` | Optional boolean, default `false`. Set to `true` when an external title adds meaning or sets up the joke; it becomes a visible heading above the artwork. |
   | `mobile_panels` | Optional integer `2`, only for a deliberately composed 2:1 image containing two equal square panels. See the mobile guidance below. |

4. Keep `fallback_slug` set to `austen-at-work`. New pieces appear in Writing automatically. Sorting is by publication date, newest first; equal-date image entries retain their catalog order. Prepending a new same-day batch keeps that batch first without alphabetizing it. Undated work follows dated work.
   Before leaving a previously published piece undated, check the asset/source history and its release PR. Verify its actual archive position as well as whether its link exists. Austen first appeared in the published newspaper release (PR #220, 2026-11-09), so its date is known.
5. Build the generated pages and verify the result using the commands below. The generated image URL is `/is/writing/<slug>/`. Do not hand-edit that reader or the generated Writing page.
6. Review the new readers and their Writing links. Save the completed work locally while preview-only. Update the change record. Publishing requires the release steps below.

### Image presentation and credit

Keep the entire image and the native full-size link. Embedded titles and captions do not need a second visible copy outside the image. Each reader still has an accessible page heading.

An external title can be part of the work. “When you grow up poor” supplies the childhood context before the gum joke, so it is visibly displayed above the image using `show_title: true`. “A gifted child” uses the same opt-in treatment. This does not make visible headings the default for other pieces. The title remains in the browser tab, social metadata and Writing list regardless of its visibility on the reader.

The shared credit is **“Words and ideas by Ajin. Illustrations generated with AI.”** Its source is `CREDIT` in [_scripts/image_pieces.py](_scripts/image_pieces.py). It belongs beside the artwork on Home, the Writing selection, and image readers. It does not belong in Browse all or in a generic Writing footer.

At 375px, check the actual joke, including small lettering. Going to the Market and Do you cycle? use `mobile_panels: 2` to stack their complete left and right halves on phones while keeping the original strips on larger screens. Do not infer panel boundaries from aspect ratio alone. Children’s Museum remains one scene; its small age labels benefit from enlargement. Just Checking the Weather and On privilege are already arranged vertically.

Download names come from the public asset names, such as `childrens-museum.webp`, not the original ChatGPT filename. Page credits and external page titles are not embedded in downloaded images. Austen’s caption is also separate HTML, so saving that image alone omits the caption. A separate share/download export has not been implemented.

## Where to make changes

| Area | Owning source | Generated output or presentation |
|---|---|---|
| Home and its selected writing | `templates/root.html`, `_scripts/paper_site.py`, content catalogs | `_scripts/build_root.py` writes `index.html`; paper assets provide the newspaper presentation. |
| Writing selection and Browse all | `templates/writing.html`, `_scripts/paper_site.py`, image/comedy catalogs and essay sources | `_scripts/build_sections.py` writes `is/writing/index.html`. |
| Image readers | `content/image-pieces.json`, `_scripts/image_pieces.py` | `_scripts/build_sections.py` writes `is/writing/<slug>/index.html`; `assets/paper/image-pieces.css` and `writes.css` style it. |
| Building | `content/building.json`, `templates/building.html`, `_scripts/paper_site.py` | `_scripts/build_sections.py` writes `is/building/index.html`; the cabinet has its own styles. |
| Running | `templates/running.html`, `_scripts/build_root.py`; running sync supplies `content/stats.md` | Generated `is/running/index.html` and Home mileage. Trace the sync source before changing stats behavior. |
| Prose readers | `content/comedy.json`, standalone comedy Markdown, `is/writing/essays/_src/`; `_scripts/writes_common.py` | `_scripts/build_comedy.py` and `_scripts/build_essays.py`; shared `writes.css`. See AGENTS.md before importing or changing sources. |
| Sitemap | `_scripts/build_sitemap.py` | `sitemap.xml`; commit dates supply `lastmod`. |

The `/wrote/` and `/writes/` indexes redirect to the unified Writing list. Their individual prose reader URLs and `/writes/feed.xml` remain supported. Moving those URLs is a separate change because the essay publisher and existing links depend on them.

Do not treat removal from a catalog as deletion of a public page. The image build creates and updates readers but does not remove old reader directories. Before renaming or retiring an existing URL, trace links and publishing consumers, decide the intended redirect or retained page, and verify the result. Do not delete generated files speculatively.

## Building and checking

For an image addition, from the site worktree:

```sh
python3 _scripts/build_sections.py
python3 _scripts/build_root.py --root-only
python3 _scripts/build_sitemap.py
python3 -m unittest discover -s _scripts -p 'test_*.py'
python3 _scripts/build_sections.py --check
python3 _scripts/build_root.py --check-home
python3 _scripts/check_links.py
git diff --check
git status --short
```

For changes spanning prose or the full site, use the complete build sequence in [AGENTS.md](AGENTS.md). The CI checks in [.github/workflows/check-paper.yml](.github/workflows/check-paper.yml) verify generated files and publishing contracts. Normal builds must work without private exports.

For content-only additions using established layouts, visually check phone and desktop readers. Any new layout or stylesheet requires all three widths: 375, 768 and 1280px. Confirm complete artwork, readable captions or a working enlargement path, correct credit and accessible description, and no broken images or overflow. Follow the native links. The live verifier checks the readers, their images and stylesheets, Home and Writing against deployed source. If changing the homepage lead logic, also check disabled JavaScript, failed-image fallback, matching captions and links, and stability while images load.

For a simple local preview without the optional review controls:

```sh
python3 -m http.server 8745 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8745/is/writing/`. Use an available port and stop the server when that preview is no longer needed.

## Publishing and routine maintenance

1. Confirm which concrete preview Ajin approved for publication. Check publication dates and the final diff, run the required builds and visual checks, and commit only the intended work.
2. After publication approval, push the feature branch and open its PR. Follow the repository checks and approved merge workflow. Do not run the essay publisher or `publish.sh` to publish a preview branch.
3. Wait for Pages deployment and inspect the live changed pages, images and links before calling the release live. A pushed commit or green unit test is not deployment proof.
4. Restore the canonical checkout to a clean, synchronized `master` without disturbing concurrent work. Update the release status and change record with the verified result. Keep or remove the preview worktree according to whether it is still needed for review.

The essay publisher has its own maintenance gate and can publish approved Markdown independently. Read its README before altering it or manually editing its managed sources. Its production `--dry-run` can fetch, rebase and push; it is not a harmless offline test.

Keep documentation focused: current rules in AGENTS.md, operational instructions and significant changes here, exact diffs in Git. For investigation, use `git log --oneline`, `git show <commit>`, or `git log -- <path>`. Do not create a second exhaustive change log or describe planned work as implemented.

## Change record

### 2026-11-09: published newspaper release

PR #220 (`bd123db`, followed by generated-root commit `0fed583`) brought Home, Writing, Building and Running into the approved structure. Writing uses a readable newest-first list; “10 Reasons Why You Shouldn’t Read This List” is unlisted while its reader remains available. Building contains BIC, omits Crossings, and puts omen.ops before Kenbaiki. Running remains accessible through Home’s mileage box rather than a masthead category. Individual prose URLs remain intact.

### 2026-11-09: image-piece preview, not published

- `482ab15`: added the image catalog, individual reader generation, unified Writing entries, full-size links and artwork credits. Replaced the generic footer credit in the preview. Added build checks so future regeneration preserves these pages.
- `8460ed9`: pinned the homepage to Austen after Ajin chose it as the representative piece. New uploads no longer become homepage candidates automatically.
- `ba58b51`: added Going to the Market and an explicit mobile panel option so its two captioned panels remain readable on phones without changing the original download.
- `92b0fdd`: added Children’s Museum and Just Checking the Weather. At this checkpoint, all 33 existing tests passed, 1,083 internal links across 179 pages had no broken links, and the new readers were checked at all three viewport widths. Native full-size links worked; the museum’s small labels need enlargement on a phone. The worktree was clean and the live checkout unchanged.
- Added this maintenance guide and linked it from AGENTS.md so another chat or agent can find the workflow and release boundary without reconstructing the conversation.
- Added When you grow up poor and the provisionally titled A gifted child. Optional visible titles now let words outside an image supply the setup, without repeating headings on the six earlier readers or changing the artwork. The existing readers retain their layout; Austen remains pinned. Verified all eight readers at 375, 768 and 1280px, all 34 tests passed, and 1,103 internal links across 181 pages had no broken links. Still a local preview.

### 2026-11-09: image release approved

Ajin approved publishing the reviewed cartoon batch after the previews, including the two external titles. Keep Austen as the homepage lead. The earlier preview-only entries above are historical checkpoints, not a continuing hold on publication. Record the completed build, deployment and live-page checks in the release PR; inspect the actual public pages before reporting the release live.

### 2026-11-09: corrected Austen's archive position

The Austen piece was mistakenly left undated, placing it after all dated prose despite being published that day. Link-presence checks passed but did not catch this discovery problem. The asset/source first appeared in `0722caf` and was published through PR #220 on 2026-11-09. Setting that verified publication date places it after the seven newer cartoons and before the older prose. Future additions should verify archive position and release history before treating a date as unknown; Home's pinned selection and the reader URL stay the same.

### 2026-11-09: cycling and privilege cartoons

Added Do you cycle? and On privilege as individual readers and the newest entries in Writing. Both use lossless WebP assets with the original pixels preserved. The cycling comic uses the existing two-panel phone layout; On privilege has a visible external title that frames the joke. Neither is added to the homepage selection. This batch uses the existing catalog fields and reader templates; its release PR records the build, layout and live checks.

### 2026-11-09: repeatable publishing and the desk illustration

Added `_scripts/piece.py` and the short publishing recipe to remove repeated conversion, metadata editing and verification setup. Preparation refuses conflicting content, validates source data before replacement, compares decoded pixels and treats identical retries as no-ops. Checks run once per batch; live verification is read-only and cannot mistake a local build for deployment. Tests cover rollback, duplicates, preservation and stale public responses; CI installs the preparation dependency.

Mug Shot of My Desk now has its numbered-mug illustration before the prose. The optional `illustration` metadata is separate from imported text and preserved by slug during Medium refreshes; the reader adds the image, a short AI credit, native enlargement and social-image metadata. The article keeps its 2023-11-30 date, URL, text and archive position. Publication and live evidence are recorded in this change's release PR.
