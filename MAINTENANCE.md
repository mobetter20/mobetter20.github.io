# Maintaining ajin.im

This is the practical guide for adding work and maintaining the site. [AGENTS.md](AGENTS.md) holds the design decisions and project rules. Git records the exact changes. Update this guide alongside changes to the workflow, and add a brief dated entry for meaningful fixes or releases.

## Release status

**As of 2026-11-09:** the newspaper redesign was published through PR #220. The subsequent image-piece work is saved locally on `codex/image-pieces-preview` in the sibling `ajin-image-preview` worktree. It has not been pushed or published. Keep that work local until Ajin explicitly approves publication.

The preview contains six image readers: Austen, C’est la vie, Thought + Time ≠ Insight, Going to the Market, Children’s Museum, and Just Checking the Weather. Only Austen is eligible for the homepage. The preview also replaces the generic writing-footer credit with a credit beside the artwork. These are preview behaviors until the image release is deployed.

The current local review page is <http://127.0.0.1:8744/_review/>. It has page and viewport selectors. It works only while the local preview server is running; this address is not a public deployment or permanent hosting arrangement. Ordinary pages can also be previewed with a loopback-only static server from the worktree.

## Adding pieces: what Ajin needs to do

Send the images to Codex or Claude, singly or in a batch. Supply preferred titles or separate captions if there are any. Otherwise the agent can propose descriptive titles from the work.

Example: “Add these to Writing. Keep Austen on Home. Preview first.”

The agent handles the web assets, filenames, accessible descriptions, reader pages, Writing list, and visual checks. Ajin does not need to edit JSON or run build commands. Publication is a separate instruction when the work is still a preview.

There is currently no image upload form or automatic image drop folder. The existing approved-release folder publisher handles Markdown essays. Its operating instructions are in [_scripts/writes_publisher/README.md](_scripts/writes_publisher/README.md). Do not put images there and assume they will publish. A new image uploader has been discussed but is not implemented or approved.

## Adding an image: maintainer procedure

1. Check the active branch, worktree and Git status. Continue the existing preview worktree while this release is under review. Keep the canonical checkout free for the essay publisher, and investigate unrelated changes before touching them.
2. Inspect the original image. Choose a stable, descriptive lowercase slug with hyphens. Add the web asset under `assets/paper/pieces/<slug>.webp`. The current conversion uses lossless WebP, for example `cwebp -lossless -m 6 "source.png" -o "assets/paper/pieces/new-piece.webp"`. Verify the dimensions and pixel preservation. Do not change the illustration, crop away captions, or stretch it to match other pieces.
3. Add a record to [content/image-pieces.json](content/image-pieces.json). Use an existing record as a structural example, with a new unique slug. The fields are:

   | Field | Meaning |
   |---|---|
   | `slug`, `title` | Stable URL segment and the title used in Writing and page metadata. Changing a title need not change its URL. |
   | `published_date` | Site publication date as `yyyy-mm-dd`, or blank when genuinely unknown. Preview dates must be checked at publication. Do not derive historical publication dates from downloaded filenames. |
   | `image`, `width`, `height` | Root-relative asset path and its actual pixel dimensions. The build validates them. |
   | `alt` | Describe the relevant scene and include the words needed to understand the joke. |
   | `caption` | Separate caption text, or an empty string when the caption is already in the artwork. |
   | `featured` | Set new pieces to `false`. Austen stays on Home until Ajin asks to change it. |
   | `mobile_panels` | Optional integer `2`, only for a deliberately composed 2:1 image containing two equal square panels. See the mobile guidance below. |

4. Keep `fallback_slug` set to `austen-at-work`. New pieces appear in Writing automatically. Sorting is by publication date, newest first; equal-date image entries retain their catalog order. Prepending a new same-day batch keeps that batch first without alphabetizing it. Undated work follows dated work.
5. Build the generated pages and verify the result using the commands below. The generated image URL is `/is/writing/<slug>/`. Do not hand-edit that reader or the generated Writing page.
6. Review the new readers and their Writing links. Save the completed work locally while preview-only. Update the change record. Publishing requires the release steps below.

### Image presentation and credit

Keep the entire image and the native full-size link. Embedded titles and captions do not need a second visible copy outside the image. Each reader still has an accessible page heading.

The shared credit is **“Words and ideas by Ajin. Illustrations generated with AI.”** Its source is `CREDIT` in [_scripts/image_pieces.py](_scripts/image_pieces.py). It belongs beside the artwork on Home, the Writing selection, and image readers. It does not belong in Browse all or in a generic Writing footer.

At 375px, check the actual joke, including small lettering. Going to the Market uses `mobile_panels: 2` to stack its complete left and right halves on phones while keeping the original strip on larger screens. Do not infer panel boundaries from aspect ratio alone. Children’s Museum remains one scene; its small age labels benefit from enlargement. Just Checking the Weather is already arranged vertically.

Download names come from the public asset names, such as `childrens-museum.webp`, not the original ChatGPT filename. Page credits are not embedded in downloaded images. Austen’s caption is also separate HTML, so saving that image alone omits the caption. A separate share/download export has not been implemented.

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

Visually check new readers at 375, 768 and 1280px. Confirm full artwork, readable captions or a working enlargement path, correct credit, accessible description, and no broken images or horizontal overflow. Follow the full-size and All writing links. Check the archive order and that Home still shows Austen. If changing the homepage lead logic, also check disabled JavaScript, failed-image fallback, matching captions and links, and stability while images load.

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
