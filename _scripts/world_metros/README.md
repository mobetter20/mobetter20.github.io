# World Metros Atlas — dev docs + tooling

A one-URL interactive atlas of ~10–12 category-defining metro systems, eventually at
`/is/building/world-metros/` (bespoke tier). Signature device: every network drawn from
real OSM geometry at **one shared scale**, north-up, so physical forms compare honestly.

Nothing here is live yet. No page exists under `is/building/world-metros/` yet.

## Reading order (mandatory for any agent picking this up)

1. [STATUS.md](STATUS.md) — what's done, the current gate, the next exact action.
2. [BUILD-SPEC.md](BUILD-SPEC.md) — the product contract (views, invariants, acceptance).
3. [DATA-CONTRACT.md](DATA-CONTRACT.md) — system scopes, data source, schema, ranking definitions, licences.
4. [DECISIONS.md](DECISIONS.md) — append-only dated decision log. PROPOSED entries need owner (Ajin) ratification.

Source of truth is these files plus git history — never a Claude/Codex session memory.
The project registry stanza lives in `~/projects.md` (`world-metros-atlas`).

## Commands

```sh
python3 _scripts/world_metros/audit_osm_sources.py    # re-verify validator status + sizes for candidate cities
python3 _scripts/world_metros/proof_same_scale.py     # regenerate the same-scale proof SVG (writes to /tmp)
```

Both are stdlib-only (urllib + json), no venv needed.

## Provenance

Files in this directory are hand-maintained dev docs/tools — no generator writes here.
The future page build will follow repo convention: a `_scripts/world_metros/build_*.py`
generator, registered in the local `publish.sh` (untracked, main checkout only).
