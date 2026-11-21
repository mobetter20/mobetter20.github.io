# Publishing and managing ajin.im

Start here for routine additions and edits. [MAINTENANCE.md](MAINTENANCE.md) maps the source files, checks and recovery procedures; [AGENTS.md](AGENTS.md) records the site's design and editorial rules. Exact changes and release evidence live in Git and release PRs.

| What you want to do | Simplest route | What changes |
|---|---|---|
| Publish an essay or comedy prose | Put an approved Markdown release in `~/Documents/Ajin-Publishing/` | Its reader, Browse all and the prose feed |
| Publish a cartoon | Open `~/Applications/Publish Cartoon.app` | Its reader, Browse all and the cartoon collection/slides |
| Change the Writing selection | Name the piece and the slot to replace | Only the requested curated placement |
| Edit or withdraw existing work | Use the source/retraction guidance below | The existing piece; keep its URL for normal edits |

## Publish writing without an agent

Keep drafts in your private writing folder. Save only the approved release as a top-level `.md` file in `~/Documents/Ajin-Publishing/`, with this opening block followed by the text:

```markdown
---
title: Your piece title
publish: true
date: 2026-11-21
slug: your-piece-title
excerpt: A complete introductory sentence.
---

Your writing starts here.
```

Use the actual publication date. The date is metadata, not a scheduled release; putting the file in the folder can publish it even if the date is in the future. `title` and `publish: true` are required; `slug`, `date` and `excerpt` are optional, but keeping an explicit `slug` avoids changing the URL if you later retitle the piece. This is simple `key: value` metadata: do not add YAML quotes around values. The publisher assigns the internal ordering number.

Leave the Mac awake and connected. After the file stops changing, the watcher waits for stability, usually 5 to 10 minutes, then builds and pushes. **Its notice confirms a Git push, not a live page.** GitHub Pages deploys afterward. Visit the given URL to read the result; if it remains missing, see the troubleshooting table below. The cartoon app separately waits for and verifies its live result.

The writing folder does not upload local attachments. Use ordinary Markdown links to public URLs; `[[wikilinks]]` are rejected. Ask the agent when adding an illustration to prose. Both essays and comedy prose can use this release path; older Medium imports and the existing standalone comedy source remain in their current locations.

## Publish cartoons without an agent

Open **Publish Cartoon** in your Mac's Applications folder. Choose the finished image, confirm its title, write a short description of the scene and its words for screen readers, then click **Publish**. The title remains hidden above the artwork. Leave the app running until it gives you the checked live URL. It uses no AI and has no background watcher.

The app runs the existing image preparation, checks and GitHub release in its own worktree. It never edits the essay publisher or the canonical checkout. It waits for a successful deployment and checks public pages and artwork before saying the cartoon is live. If interrupted, repeat the same image, title and description to resume; an identical already-published cartoon is verified without another post. A different image or description under an existing title requires an explicit edit, not another upload.

Maintainer installation, after the source is committed on canonical `master`:

```sh
python3 _scripts/cartoon_publisher.py --install-app "$HOME/Applications"
```

The app launcher points to that checkout's script, so ordinary source updates take effect without rebuilding the launcher. The app derives its URL from the title. A title with no usable Latin characters needs a separate URL slug, which the image preparation command or an agent can supply. The same operation for ordinary titles is available as `python3 _scripts/cartoon_publisher.py --image '/path/to/image.png' --title 'A title' --alt 'Scene and words.'`. Do not use the launcher for previews: clicking Publish authorizes the public release. Cancelling before Publish makes no publishing changes.

## What gets featured

Adding work updates Browse all, ordered by publication date, newest first. It never expands or changes the hand-picked Writing selection or Home.

Writing has two independent essay slots: the top slot above Scientist currently shows **An Open Letter to Jensen Huang From His Leather Jacket**; the lower brief shows **A good time to be Randall Flagg.** The selected comedy features include **Wife Evolves Into a Scarier Pokemon** and **Step on Me Please**. Home separately keeps Austen, Kenbaiki and the smaller Running strip.

A plain request such as “Replace the top essay with Dear Seoul; keep Randall Flagg below” is enough. No code instructions are needed. [The source map](MAINTENANCE.md#where-to-make-changes) identifies the exact controls for another session.

## Editing and removing work

- **Writing published from the release folder:** edit the same release file, keeping its `slug` and publication date. It republishes after the stability wait. Editing only a private draft does not update the site. If no explicit `slug` is present, add the current URL slug before changing its title.
- **Older writing or a hand-edited site source:** ask for the exact correction. The agent identifies its owning source; the automatic publisher deliberately refuses to overwrite independent edits.
- **Cartoon changes:** request the replacement image, title or description for the existing piece. The app is for new cartoons and identical retries; it refuses to overwrite different published content under the same title.
- **Removal:** say whether to remove only the listing or also retire the direct URL. Deleting a local release file or setting `publish: false` does not remove an existing public page. Retraction includes stopping its automatic source from republishing it and checking links, feed and sitemap. Never delete only generated HTML.

## If publishing gets stuck

| Symptom | Meaning and next step |
|---|---|
| Cartoon app reports an interruption | Retry the same image, title and description. The saved release is reused. |
| Cartoon title already exists with different content | Request an edit to that piece; do not make a duplicate URL to work around the refusal. |
| Writing reports conflicting release files | Keep one release export per URL. Every file in that collision is held until it is resolved. |
| Writing has no notice after about 15 minutes | Check the Mac is awake, the file is top-level and has `publish: true`; ask the agent to inspect read-only status and existing logs. |
| Writing was pushed but the URL is missing or stale | Check the latest GitHub Pages deployment and public page. The push notice alone does not prove deployment. |
| Writing reports a hand edit or repository changes | Ask the agent to reconcile the source safely. Do not delete publisher state or force a retry. |

Neither workflow uses AI or needs Codex tokens when run directly. An agent remains useful for editorial decisions, illustrations, retractions and unusual failures.

## Publishing with an agent

Ajin can attach images and say **“Publish these”**, or **“Add this illustration to [article]”**. Preferred titles are optional. “Preview first” keeps the work local. The agent still supplies an accurate accessible description and checks the artwork; the commands do the bookkeeping. No AI API or background uploader is involved. Publishing to the site is separate from social posting; the workflow does not cross-post.

## Fixed defaults for images

- New cartoons get their own reader and a newest-first Writing entry. Date defaults to today in Asia/Seoul; confirm it if a preview spans days. Future publication dates are rejected.
- Austen stays on Home. New images are never featured automatically.
- Home C is fixed: complete Austen art/caption, Kenbaiki machine preview, then the smaller Running strip and email. Do not add prose, comedy, Coo or catalog rotation to Home.
- Every catalog cartoon is surfaced through Writing, the overview and native slides. The viewer swaps prepared slides in place and warms only neighbouring artwork. Swipe is an optional touch enhancement; native arrows must remain sufficient without JavaScript or when enhanced loading fails.
- Preserve the complete image in lossless WebP with a clean filename, actual dimensions and pixel verification. The same batch check generates smaller screen copies automatically. Opening the art full size still uses the lossless original. Publish the intended artwork as supplied; the workflow does not add a byline to an unsigned image.
- Hide external titles on readers, slides and the cartoon overview by default, even when a title adds context. Use `--show-title` only when Ajin explicitly requests a visible heading. Supplying a title alone does not opt in. Keep titles in Writing, URLs, sharing metadata and accessible headings; preserve separate captions. Never infer panel divisions from aspect ratio.
- An illustration belongs to its existing article. Keep that article's title, text, publication date, URL and archive position.
- Existing credits and reader styles apply. Routine additions do not require new design options or a review of the whole site.

## Agent recipe

1. Check Git status. Reuse the review worktree on a fresh feature branch from current `origin/master`; leave the canonical checkout available for the essay publisher. Inspect the supplied art and choose its title/description and any explicit presentation options.
2. Run `add` or `illustrate` below for each image. Identical retries do nothing; conflicts stop without overwriting published content. Batch additions before checking.
3. Run `check` **once per batch**, then `node --test _scripts/test_cartoon_swipe.js _scripts/test_cartoon_navigation.js` when cartoon navigation changes. The batch check rebuilds pages and sitemap, runs the test suite, checks generated output and internal links, and prints a short result. Inspect each changed reader on a phone and desktop. Use 375, 768 and 1280px for any new layout or stylesheet change. Confirm the joke is readable and complete; use the native enlargement link for fine detail.
4. Commit only this batch, push and create its PR. Run the existing PR checks. When publication is authorized, merge with the checked head SHA and wait for the latest Pages deployment, including any generated-root commit. Do not treat green tests or a pushed commit as a live release.
5. Update the review checkout to deployed `origin/master`, run `verify-live` for the changed readers, and inspect the public result. Record the release and checks in the PR. Restore a clean canonical `master`, remove the merged feature branch, and give Ajin the live links.

For every agent browser review, install the origin-scoped `_notrack` init script and block Google Analytics / Google Tag Manager requests at the context level before the first live navigation. Verify zero attempted analytics requests; new tabs must inherit the guard. Local previews and webdriver browsers are also excluded by `analytics.js`. See [MAINTENANCE.md](MAINTENANCE.md#analytics-and-test-traffic) for the positive and negative controls required when changing that loader. The HTTP-only live verifier does not execute tracking code.

This is the routine path, not an exception to approval or Git safety. Changes to the schema, layout, publishing behavior or homepage selection need the usual broader review. Publication authorization persists within the agreed task; do not repeatedly ask for the same approval.

## Commands

Run from the site worktree. The preparation commands use Pillow, already installed on the current Mac. For a new environment: `python3 -m pip install -r _scripts/publishing-requirements.txt`.

```sh
python3 _scripts/piece.py add '/path/to/image.png' \
  --title 'A title' --alt 'Describe the scene and its relevant words.'

# Optional, only after inspecting the artwork:
# --slug stable-url --mobile-panels 2 --caption 'Separate caption'
# --date 2026-11-09
# --show-title only when Ajin explicitly asks to show the title above the art

python3 _scripts/piece.py illustrate '/path/to/image.png' \
  --slug mug-shot-of-my-desk --alt 'Describe the illustration.'

python3 _scripts/piece.py check
node --test _scripts/test_cartoon_swipe.js _scripts/test_cartoon_navigation.js

# After deployment, using the checkout at the deployed commit:
python3 _scripts/piece.py verify-live /wrote/mug-shot-of-my-desk/ --wait 120
```

`add` and `illustrate` prepare assets and source data only. `check` regenerates local outputs. None commits, pushes, merges or deploys. `verify-live` only reads public pages: it compares reader, original and responsive image candidates, stylesheet, collection scripts/assets, Home and Writing bytes with the checkout using normal URLs. Include changed overview and slide routes in the command for a cartoon release. A stale response or mismatch fails; optional `--wait` bounds CDN-propagation retries. Browser review remains necessary for actual legibility.

If preparation reports a lock, check the PID in `content/.piece.lock`. Wait for an active preparation; remove a stale lock only after confirming its process ended. An identical complete asset left by an interrupted run is reused on retry, without overwriting it. A conflicting title, image or existing illustration requires a deliberate replacement, not another add command.

For source ownership, import behavior and unusual changes, see [MAINTENANCE.md](MAINTENANCE.md). Routine content additions are recorded by their catalog entries and release PRs; update the maintenance guide when the workflow or behavior changes.
