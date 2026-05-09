# `_archive/`

Pages and content that have been pulled from the live site but kept in the
repo for possible revival. Directories starting with `_` are excluded by
default Jekyll/GH Pages behavior, so anything here is preserved in git but
not served at its original URL.

Each entry below records: the path it lived at, when it was paused, why,
and what it would take to bring it back.

## Paused entries

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
