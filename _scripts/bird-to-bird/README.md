# Bird to Bird release ownership

`is/building/bird-to-bird/` is an exact generated export from the local `bird-words` project. Its source is `scripts/build-daily-release.mjs` in that project. Do not edit the published mirror or copy the private project wholesale.

For an approved release:

1. Update and review the canonical game source. Run `npm test`, `npm run audit`, `npm run build:daily` and `npm run check:daily-release` there.
2. Copy only the verified `.release/bird-to-bird/` tree into this site's `is/building/bird-to-bird/`. Keep all payload files and licenses. Any removed old file needs an explicit consumer review; do not silently merge leftovers into a new release.
3. Set `expected-manifest.sha256` beside this document to the exporter-reported SHA-256 of the exact copied `manifest.json`. This pin is a reviewed checksum, not a cryptographic signature or a replacement for source/content review.
4. Run `python3 -m unittest discover -s _scripts -p 'test_bird_to_bird.py'` and `python3 _scripts/check_bird_to_bird.py`, followed by the site's normal publication checks. Existing PR CI repeats the integrity check for game and script changes.
5. After deployment, compare the public manifest and payload bytes, check actual MIME/compression/cache behavior, and complete a route through next-puzzle, bird details and reload on the public URL. Apply the site's analytics opt-out and request blocking before browser tests.

The checker enforces the exact file set, the separately pinned manifest, allowed public paths and every file's size/hash. Source-side checks own vocabulary, graph rules, biological evidence, dependency closure and the public data projections. Updating both a payload and its pin is a deliberate release change requiring that upstream review.

The beta uses the existing all-puzzles mode and keeps its optional finite daily calendar. Publishing these files does not activate a content generator or recurring maintenance task. The Building cabinet remains a separately curated surface.
