# mobetter20.github.io

Static site hosted on GitHub Pages. Contains the creative house at `ajin.im/is/writing/` and the Avian Municipal District universe.

## World Bible

The world-building reference for the Avian Municipal District lives in a private repo:
**github.com/mobetter20/ajin-universe-bible** (private)

Modular files:
- `INDEX.md` — what to load and when
- `00-foundation.md` — philosophy, tone hierarchy, house principles
- `01-strategy.md` — current state, priorities, interconnections
- `02-registry.md` — characters, cases, locations, objects, workflow
- `03-coo-taxonomy.md` — 12 story categories for The Municipal Coo

**Before writing content** for any bird-universe site, check `02-registry.md` for entity facts. After publishing, update the registry with new facts established.

## Build Scripts

`_scripts/build_bird_coo.py` generates all Municipal Coo HTML (index, issues, archive). Manual edits to generated files will be overwritten on next build. Make template changes in the build script.

## Cross-Site Links

- Use root-relative paths (`/is/writing/nest-court/`) not relative (`../nest-court/`)
- All cross-site links must include `target="_blank"`
- The pre-push hook enforces root-relative paths for structural links
