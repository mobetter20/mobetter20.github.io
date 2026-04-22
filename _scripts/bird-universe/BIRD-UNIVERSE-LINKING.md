# Bird-Universe Linking Rules

This document is local-only workspace guidance for the bird-related sites under
`/Users/ajin/Documents/New project/personal/mobetter20.github.io/is/writing/`.
It is not part of the public site and should not be committed.

## Scope

These rules apply only when touching the Avian Municipal District / bird-universe
cluster:

- `/Users/ajin/Documents/New project/personal/mobetter20.github.io/is/writing/avian-district/`
- `/Users/ajin/Documents/New project/personal/mobetter20.github.io/is/writing/bird-coo/`
- `/Users/ajin/Documents/New project/personal/mobetter20.github.io/is/writing/bird-docket/`
- `/Users/ajin/Documents/New project/personal/mobetter20.github.io/is/writing/karen-hawk/`
- `/Users/ajin/Documents/New project/personal/mobetter20.github.io/is/writing/nest-court/`
- `/Users/ajin/Documents/New project/personal/mobetter20.github.io/is/writing/nest-court-proceedings/`
- `/Users/ajin/Documents/New project/personal/mobetter20.github.io/is/writing/nest-court-proceedings-pigeon/`
- `/Users/ajin/Documents/New project/personal/mobetter20.github.io/is/writing/nest-court-proceedings-starling/`
- `/Users/ajin/Documents/New project/personal/mobetter20.github.io/is/writing/perch-chat/`
- `/Users/ajin/Documents/New project/personal/mobetter20.github.io/is/writing/secondnest/`

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
2. Add or update the local registry:
   `/Users/ajin/Documents/New project/personal/mobetter20.github.io/.codex-local/bird-universe/bird_universe_registry.json`
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

- `/Users/ajin/Documents/New project/personal/mobetter20.github.io/is/writing/index.html`
- `/Users/ajin/Documents/New project/personal/mobetter20.github.io/is/writing/secondnest/index.html`

## Local-Only Rule

These files are intentionally local-only:

- `.codex-local/bird-universe/*`
- the bird-site `AGENTS.md` files

Do not commit them. Do not move them into public site directories in tracked
form. If a future workflow needs repo-visible automation, keep it generic and
non-fictional, and continue storing the bird-universe policy layer locally.

## Enforcement

- The effective guardrail is the local checker:
  `/Users/ajin/Documents/New project/personal/mobetter20.github.io/.codex-local/bird-universe/check_bird_universe_links.py`
- Push-time enforcement should happen through the local Git hook at:
  `/Users/ajin/Documents/New project/personal/mobetter20.github.io/.git/hooks/pre-push`
- `publish.sh` is not the safety model. Treat it as an optional local helper.
- If this repo is recloned or `.git` is replaced, the local hook and local
  excludes must be recreated.
