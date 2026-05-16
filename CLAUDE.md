# mobetter20.github.io

Static site hosted on GitHub Pages. Contains the creative house at `ajin.im/is/writing/` and the Avian Municipal District universe.

## World Bible

The world-building reference for the Avian Municipal District lives in two locations that must stay in sync:

- **Local (primary working copy):** the `bird-universe/` folder in the local writing directory
- **GitHub (backup):** private companion repo (see local notes)

Read `INDEX.md` for what to load and when. Modular files:
- `00-foundation.md` — philosophy, tone hierarchy, house principles
- `01-strategy.md` — current state, priorities, interconnections
- `02-registry.md` — characters, cases, locations, objects, workflow
- `03-coo-taxonomy.md` — 12 story categories for The Municipal Coo

**Before writing content** for any bird-universe site, check `02-registry.md` for entity facts.

**After publishing**, update the registry with new facts established (characters, locations, channel changes, etc.) in BOTH the local copy and the GitHub repo. Do not leave them out of sync.

## Build Scripts

`_scripts/build_bird_coo.py` generates all Municipal Coo HTML (index, issues, archive). Manual edits to generated files will be overwritten on next build. Make template changes in the build script.

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
