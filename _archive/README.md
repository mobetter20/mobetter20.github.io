# `_archive/`

Pages and content that have been pulled from the live site but kept in the
repo for possible revival. Directories starting with `_` are excluded by
default Jekyll/GH Pages behavior, so anything here is preserved in git but
not served at its original URL.

Each entry below records: the path it lived at, when it was paused, why,
and what it would take to bring it back.

## Paused entries

### `joseon/` (the Joseon files)

- **Was at**: `ajin.im/is/building/joseon/`
- **Now at**: `_archive/joseon/index.html` (with `<meta name="robots" content="noindex, nofollow">` added as belt-and-braces)
- **Paused**: 2026-06-08
- **Why**: a "collection card + hub" that grouped the three Joseon-data pieces (omen.ops, the sky over Seoul, The Joseon Review). The Joseon Review was pulled back to soft-launch, leaving only two pieces, short of earning a separate hub (the Instrument Bus has 9, Seoul Crushing 4). Kept for revival if a third Joseon piece lands or The Joseon Review ships for real.
- **What it was**: a calm frame hub (building-index chrome) listing the three pieces; the grouping itself was the seal-safe cross-link between them, no sideways links inside the sealed pieces. Lede: "Three pieces, all built from real Joseon records."
- **Was linked from**: a collection card on `/is/building/` ("the Joseon files · 3 live →"). That card has been removed; omen.ops + the sky over Seoul are back as individual rows under "Lately".

#### To revive

1. `git mv _archive/joseon/ is/building/joseon/`
2. Optional: remove the `<meta name="robots" content="noindex, nofollow">` line from `is/building/joseon/index.html`
3. Re-add the collection card to `is/building/index.html` (a `.project` with an `is-collection` chip linking `/is/building/joseon/`), and move omen.ops + the sky over Seoul out of "Lately" back into the hub.
4. Re-list The Joseon Review in the hub once it is out of soft-launch.
5. Update `~/projects.md` (`the-joseon-files` stanza) + `creative-constellation.md`, and remove this entry.

### `works/`

- **Was at**: `ajin.im/works`
- **Now at**: `_archive/works/index.html` (with `<meta name="robots" content="noindex, nofollow">` added as belt-and-braces)
- **Paused**: 2026-05-09
- **Why**: not needed at the moment. Author wants the option to revive later.
- **What it was**: a "Taste as a Service" pitch page for bilingual copywriting / editorial strategy work.
- **Was linked from**: only the homepage footer (`professionally, ajin.im/works`). That link has been removed from `templates/root.html`. No other internal links existed at time of pause.

#### To revive

1. `git mv _archive/works/ works/`
2. Optional: remove the `<meta name="robots" content="noindex, nofollow">` line from `works/index.html`
3. Add the homepage footer link back to `templates/root.html`. The block looked like:
   ```html
   <div class="works">
     professionally, <a href="/works">ajin.im/works</a>
   </div>
   ```
   along with its CSS (`.works { ... }` and `.works a { ... }`, plus the shared `.detail a, .works a { ... }` selectors). See git history of `templates/root.html` around the pause date for the exact rules.
4. Run `python3 _scripts/build_root.py` to regenerate `index.html`.
5. Remove this entry from this README.
