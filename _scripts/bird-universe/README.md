# bird-universe tooling

Automation for the Avian Municipal District (AMD) static-site workflow. Three
tools cooperate to reduce the friction of "add a new AMD page" and to keep the
universe internally consistent.

## Files

| File | Purpose |
|---|---|
| `BIRD-UNIVERSE-LINKING.md` | Hand-maintained doc of cross-site link rules |
| `bird_universe_registry.json` | Hand-maintained site topology (sites, kinds, parents) |
| `config.json` | Local config — path to the registry repo (see below) |
| `bird_universe_graph.json` | **Generated.** Precomputed cross-reference cache. Do not hand-edit. |
| `generate_graph.py` | Builds `bird_universe_graph.json` |
| `check_bird_universe_links.py` | Pre-push structural validator |
| `lint_identifiers.py` | Pre-push warning system for case/form identifiers |

## Configuration

`config.example.json` is committed as a template. To set up locally:

```bash
cp _scripts/bird-universe/config.example.json _scripts/bird-universe/config.json
# then edit config.json with your absolute path
```

The actual `config.json` is gitignored — each working copy has its own. The
path it contains points at the directory containing `02-registry.md` (the
entity registry, a SEPARATE repo from this publishing repo). The path is
intentionally not defaulted to anything so the failure mode is loud rather
than silent on a different machine.

## generate_graph.py

Produces `bird_universe_graph.json`, a single-file precomputed cache with
schema (v1):

```jsonc
{
  "version": 1,
  "registry_source_sha": "sha256 of 02-registry.md content",
  "sites": [...],         // verbatim from bird_universe_registry.json
  "characters": [
    {
      "name": "...",
      "species": "...",
      "location": "...",
      "key_facts": "...",
      "active_cases": ["AMNC-..."],
      "mentions": ["is/writing/.../index.html", ...]
    }
  ],
  "cases": [
    {
      "number": "AMNC-...",
      "type": "...",
      "parties": "...",
      "filed": "...",
      "status": "...",
      "key_facts": "...",
      "mentions": [...],
      "dedicated_page": null
    }
  ]
}
```

Future entity types (locations, ordinances, forms) are intentionally deferred
until a downstream consumer needs them.

**When to read this file:**
- Asking "which pages mention case X?" or "which pages mention character Y?"
- Confirming whether an identifier is in the registry before adding it to HTML
- Replacing repeated grep+read passes over canon files in agent sessions

**When to regenerate:**
- Automatically: every `publish.sh` (added before other build steps)
- Manually: `python3 _scripts/bird-universe/generate_graph.py` after editing
  `02-registry.md` or after adding/editing AMD HTML

The committed JSON is the cache — re-running with no source changes produces
byte-identical output (the `registry_source_sha` field changes only when
`02-registry.md` changes).

## check_bird_universe_links.py

Pre-push validator. Existing checks (registry schema, structural link rules,
parent routing) plus a new check:

- **Anchor target validation.** Every `<a href="#X">` in a bird-universe HTML
  file must have a matching `id="X"` on the same page. Scoped to `<a>`
  elements only. SVG internal references (`<textPath href="#topArc">`,
  `<use href="#sym">`, `<clipPath>`) resolve through `<defs>` not body
  `id`s and are intentionally not checked.

Failure modes:
- Exit 0: all green
- Exit 1: one or more structural errors — push blocked

## lint_identifiers.py

Pre-push warning system. Scans bird-universe HTML for entity identifiers and
cross-checks against `bird_universe_graph.json`.

| Identifier kind | Pattern | Behavior |
|---|---|---|
| Case number | `AMNC-YYYY-NNN[A-Z]` | Error on case-variant typos (`amnc-…`); warn on unregistered |
| Form ID | `CL-XX-NN` | Error on lowercase / mixed-case; warn on uppercase but unregistered (until forms join the graph schema) |

Character names are intentionally NOT linted in v1 — single-token registry
entries like "Conrad", "Dennis", "Robin" collide with ordinary English and
would flood with false positives. `bird_universe_graph.json`'s
`characters[].mentions` is available for manual cross-check.

Failure modes:
- Exit 0: warnings allowed (not push-blocking)
- Exit 1: any error — push blocked

Requires `bird_universe_graph.json` to exist (run `generate_graph.py` first).
The pre-push hook checks for both files and skips this step if either is
missing.

## Pre-push hook chain

```
pre-push
├── check_bird_universe_links.py     (always; blocking on error)
└── lint_identifiers.py              (if graph + linter present; blocking on error, warnings allowed)
```

## Deferred

- **Screenshot tool for triple-width CSS check.** Held back until CSS-churn
  rate justifies a ~200MB Playwright install. Manual triple-width check
  remains the rule per CLAUDE.md.
- **Locations / ordinances / forms in graph schema.** Add when a consumer
  beyond the linter materializes.
- **Character-name linting.** Add when a way to disambiguate single-token
  names from English words emerges (e.g., a `data-character="..."` attribute
  on character mentions).
