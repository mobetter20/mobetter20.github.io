#!/usr/bin/env bash
#
# bank_coo.sh — bank a Municipal Coo issue (build, show footprint, commit).
#
# Run from the MAIN checkout (not a git worktree) AFTER:
#   1. the new Issue(...) is added to _scripts/build_bird_coo.py, and
#   2. any new canon is registered in the bird-universe repo.
#
# Usage: _scripts/bank_coo.sh <YYYY-MM-DD> [--force] [--land]
#   --force  proceed past an unexpected footprint instead of stopping
#   --land   after committing, push to master via the clean-publish helper
#            (.codex-local/publishing/publish_clean_change.sh) — no PR
#
# Deliberately does NOT regenerate the graph cache: that tracks the AMD
# registry, not the issue list. If you changed registry canon, run
# _scripts/bird-universe/generate_graph.py and commit it separately.

set -euo pipefail
ROOT="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DATE="" FORCE=0 LAND=0
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    --land)  LAND=1 ;;
    -*) echo "unknown flag: $arg" >&2; exit 2 ;;
    *) DATE="$arg" ;;
  esac
done
[[ -n "$DATE" ]] || { echo "usage: bank_coo.sh <YYYY-MM-DD> [--force] [--land]" >&2; exit 2; }

# Guard 1: must be the main checkout. Worktrees lack the gitignored
# _scripts/bird-universe/config.json that the identifier lint reads, and the
# clean-publish / gh-merge paths misbehave from a worktree.
if [[ "$(git rev-parse --git-dir)" != "$(git rev-parse --git-common-dir)" ]]; then
  echo "Refusing: this is a git worktree. Run bank_coo.sh from the main checkout." >&2
  exit 1
fi
# Guard 2: the only pre-existing change may be your new Issue in the build
# script — anything else means the tree is dirty and the footprint below
# wouldn't be trustworthy.
PREDIRT="$(git status --porcelain | grep -vE '_scripts/build_bird_coo\.py' || true)"
if [[ -n "$PREDIRT" ]]; then
  echo "Working tree has changes other than _scripts/build_bird_coo.py:" >&2
  echo "$PREDIRT" >&2
  echo "Commit or stash them first." >&2
  exit 1
fi

NEW="is/writing/bird-coo/issues/${DATE}.html"
echo "Building The Municipal Coo (real date)..."
python3 _scripts/build_bird_coo.py

echo
echo "=== footprint (eyeball this — esp. whether the live mirror changed) ==="
git status --porcelain
echo "======================================================================"

# The new issue file must exist.
if ! git status --porcelain | grep -qF -- "$NEW"; then
  echo "WARNING: $NEW was not created — wrong date, or Issue(...) not added to ISSUES?" >&2
  [[ "$FORCE" -eq 1 ]] || { echo "Fix it, or re-run with --force." >&2; exit 1; }
fi

# A bank should only touch the build script, bird-coo output, and the avian
# excerpt. Anything else is worth a human glance before it lands.
SURPRISES="$(git status --porcelain \
  | grep -vE '(_scripts/build_bird_coo\.py|is/writing/bird-coo/|is/writing/avian-district/index\.html)' \
  || true)"
if [[ -n "$SURPRISES" ]]; then
  echo "WARNING: changes outside the expected bank footprint:" >&2
  echo "$SURPRISES" >&2
  [[ "$FORCE" -eq 1 ]] || { echo "Eyeball the above; re-run with --force to proceed." >&2; exit 1; }
fi

git add _scripts/build_bird_coo.py is/writing/bird-coo is/writing/avian-district/index.html
git commit -m "Bank Municipal Coo ${DATE}"
SHA="$(git rev-parse HEAD)"
echo "Committed ${SHA}."

if [[ "$LAND" -eq 1 ]]; then
  echo "Landing on master via publish_clean_change.sh..."
  .codex-local/publishing/publish_clean_change.sh "$ROOT" "$SHA" master
else
  echo "Not landed. To ship straight to master:"
  echo "  .codex-local/publishing/publish_clean_change.sh \"$ROOT\" $SHA master"
fi
