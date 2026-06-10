# Bird-Universe Linking Rules

This document is workspace guidance for the bird-related sites under
`is/writing/`.
It lives in the committed dev tooling at `_scripts/bird-universe/` and is not
served as part of the published site output.

## Scope

These rules apply only when touching the Avian Municipal District / bird-universe
cluster:

- `is/writing/avian-district/`
- `is/writing/bird-coo/`
- `is/writing/bird-docket/`
- `is/writing/karen-hawk/`
- `is/writing/nest-court/`
- `is/writing/nest-court-proceedings/`
- `is/writing/nest-court-proceedings-pigeon/`
- `is/writing/nest-court-proceedings-starling/`
- `is/writing/perch-chat/`
- `is/writing/secondnest/`

Do not apply these rules to unrelated comedy, essays, or other writing projects.

## Canonical Topology

- `avian-district` is the canonical in-world district hub.
- `bird-docket` is the meta / out-of-world directory. It is no longer the
  official district parent.
- `nest-court` is the official court portal.
- `nest-court-proceedings*` pages are subordinate record surfaces under
  `nest-court`, not peer hubs.
- `bird-coo` is media.
- `secondnest` is community / personals.
- `perch-chat` is community chat / clerk-maintained service.
- `karen-hawk` is a commercial practitioner site.

## Linking Rules

### Parent links

- Once `avian-district` is live, parent-style district links should point upward
  to `avian-district`, not `bird-docket`.
- Do not flip parent links early. `avian-district` must be live with real URLs
  before migration is treated as complete.

### Lateral links

- Lateral links between bird sites should exist only when they have an in-world
  reason to exist.
- Keep bespoke joke lines, ad copy, institutional notices, and editorial
  references hand-authored. Do not try to generate them from data.

### Proceedings

- Proceedings pages should link back to `nest-court`, not attempt to act as
  standalone district parents.
- Proceedings pages may have limited side references when they fit the fiction,
  but should stay record-first and contained.

### Paths

- Prefer root-relative internal links for stable structural navigation:
  `/is/writing/nest-court/`
- Avoid adding new `../` / `../../` chains for repeated structural blocks unless
  there is a strong reason not to use root-relative paths.

## What Should Eventually Be Managed Centrally

Only repeated structural blocks should eventually be candidates for generation:

- `avian-district` service directory
- `nest-court` district resources
- `bird-docket` meta directory

Do not centralize or auto-generate:

- Municipal Coo notices
- Karen Hawk ad copy or chatbot references
- SecondNest notices / jokes
- Proceedings copy or testimony
- Bespoke in-world cross-references

## New Site Intake

Before adding a new bird-universe site:

1. Classify it as one of:
   - `official_hub`
   - `official_service`
   - `media`
   - `community`
   - `practitioner`
   - `record_surface`
   - `meta_directory`
   - `listed_only`
2. Add or update the registry:
   `_scripts/bird-universe/bird_universe_registry.json`
3. Decide whether it belongs in:
   - the future `avian-district` official directory
   - the `bird-docket` meta directory
   - `nest-court` district resources
4. Decide whether any bespoke cross-links should be hand-authored elsewhere.

## Migration Status

Current target migration:

1. Launch `avian-district` as the official in-world portal.
2. Repoint parent-style references from `bird-docket` to `avian-district`.
3. Keep `bird-docket` alive as the meta directory / writing-house-facing entry.
4. Only after the migration settles, consider generating repeated structural
   sections from the registry.

Known migration watchpoints:

- `is/writing/index.html`
- `is/writing/secondnest/index.html`

## What Is Committed vs Local

The bird-universe tooling and this policy doc now live committed under
`_scripts/bird-universe/` (the former `.codex-local/bird-universe/` location is
retired). They are dev-only: they run at build / pre-push time and are never
served as published site output.

Genuinely local / per-machine:

- `_scripts/bird-universe/config.json` — gitignored; each working copy points it
  at its own checkout of the separate world-bible registry repo.
- the world-bible entity registry (`02-registry.md`) — lives in a separate repo,
  not here.

## Enforcement

- The effective guardrail is the checker:
  `_scripts/bird-universe/check_bird_universe_links.py`
- Push-time enforcement happens through the local Git hook at:
  `.git/hooks/pre-push`
- `publish.sh` is not the safety model. Treat it as an optional local helper.
- If this repo is recloned or `.git` is replaced, the local hook and local
  excludes must be recreated.
