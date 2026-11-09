# Routine image publishing

Ajin can attach images and say **“Publish these”**, or **“Add this illustration to [article]”**. Preferred titles are optional. “Preview first” keeps the work local. The agent still supplies an accurate accessible description and checks the artwork; the commands do the bookkeeping. No AI API or background uploader is involved.

## Fixed defaults

- New cartoons get their own reader and a newest-first Writing entry. Date defaults to today in Asia/Seoul; confirm it if a preview spans days. Future publication dates are rejected.
- Austen stays on Home. New images are never featured automatically.
- Home C is fixed: complete Austen art/caption, Kenbaiki machine preview, then the smaller Running strip and email. Do not add prose, comedy, Coo or catalog rotation to Home.
- Every catalog cartoon is surfaced through Writing, the overview and native slides. Swipe is an optional touch enhancement; native arrows must remain sufficient without JavaScript.
- Preserve the complete image in lossless WebP with a clean filename, actual dimensions and pixel verification.
- Hide the external title unless it adds a setup beyond the image. Never infer panel divisions from aspect ratio.
- An illustration belongs to its existing article. Keep that article's title, text, publication date, URL and archive position.
- Existing credits and reader styles apply. Routine additions do not require new design options or a review of the whole site.

## Agent recipe

1. Check Git status. Reuse the review worktree on a fresh feature branch from current `origin/master`; leave the canonical checkout available for the essay publisher. Inspect the supplied art and choose its title/description and any explicit presentation options.
2. Run `add` or `illustrate` below for each image. Identical retries do nothing; conflicts stop without overwriting published content. Batch additions before checking.
3. Run `check` **once per batch**, then `node _scripts/test_cartoon_swipe.js` when cartoon navigation changes. The batch check rebuilds pages and sitemap, runs the test suite, checks generated output and internal links, and prints a short result. Inspect each changed reader on a phone and desktop. Use 375, 768 and 1280px for any new layout or stylesheet change. Confirm the joke is readable and complete; use the native enlargement link for fine detail.
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
# --slug stable-url --show-title --mobile-panels 2 --caption 'Separate caption'
# --date 2026-11-09

python3 _scripts/piece.py illustrate '/path/to/image.png' \
  --slug mug-shot-of-my-desk --alt 'Describe the illustration.'

python3 _scripts/piece.py check
node _scripts/test_cartoon_swipe.js

# After deployment, using the checkout at the deployed commit:
python3 _scripts/piece.py verify-live /wrote/mug-shot-of-my-desk/ --wait 120
```

`add` and `illustrate` prepare assets and source data only. `check` regenerates local outputs. None commits, pushes, merges or deploys. `verify-live` only reads public pages: it compares reader, image, stylesheet, collection scripts/assets, Home and Writing bytes with the checkout using normal URLs. Include changed overview and slide routes in the command for a cartoon release. A stale response or mismatch fails; optional `--wait` bounds CDN-propagation retries. Browser review remains necessary for actual legibility.

If preparation reports a lock, check the PID in `content/.piece.lock`. Wait for an active preparation; remove a stale lock only after confirming its process ended. An identical complete asset left by an interrupted run is reused on retry, without overwriting it. A conflicting title, image or existing illustration requires a deliberate replacement, not another add command.

For source ownership, import behavior and unusual changes, see [MAINTENANCE.md](MAINTENANCE.md). Routine content additions are recorded by their catalog entries and release PRs; update the maintenance guide when the workflow or behavior changes.
