#!/usr/bin/env python3
"""Pull run distance from Garmin Connect → all-time km total.

Shells out to the existing sync_garmin_connect.py in the garmin_activity repo
(its own venv handles API + auth + token refresh). Then reads the normalized
activities.jsonl and sums distance_m for every activity_kind == "run" dated
strictly before today. Re-summing from source every run means late-uploaded
activities auto-count on the next pass — no dedup logic needed.

Garmin credentials come from macOS keychain — not env vars, so launchd jobs
(which don't inherit shell env) still work. Set them up once with:
    security add-generic-password -a default -s mobetter-stats-garmin-email -w "<GARMIN_EMAIL>"
    security add-generic-password -a default -s mobetter-stats-garmin-pw    -w "<GARMIN_PASSWORD>"

Exits non-zero on any sync failure. Does NOT modify stats.md — prints:
    GARMIN_TOTAL_RUN_KM=<float>
    GARMIN_LAST_RUN_DATE=<ISO|empty>

Usage:
    python3 _scripts/sync_from_garmin.py
    python3 _scripts/sync_from_garmin.py --no-sync       # skip API, use cached jsonl
    python3 _scripts/sync_from_garmin.py --today 2026-04-24
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

GARMIN_DIR = Path("/Users/ajin/Documents/New project/personal/garmin_activity")
GARMIN_PY = GARMIN_DIR / ".venv" / "bin" / "python"
GARMIN_SYNC = GARMIN_DIR / "sync_garmin_connect.py"
ACTIVITIES_JSONL = GARMIN_DIR / "data" / "state" / "activities.jsonl"

RUN_KINDS = {"run"}


class GarminError(RuntimeError):
    pass


def keychain_get(service: str, account: str = "default") -> str | None:
    proc = subprocess.run(
        ["security", "find-generic-password", "-a", account, "-s", service, "-w"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def run_garmin_sync() -> None:
    if not GARMIN_PY.is_file():
        raise GarminError(f"garmin venv python missing: {GARMIN_PY}")
    if not GARMIN_SYNC.is_file():
        raise GarminError(f"garmin sync script missing: {GARMIN_SYNC}")

    email = keychain_get("mobetter-stats-garmin-email")
    password = keychain_get("mobetter-stats-garmin-pw")
    if not email or not password:
        raise GarminError(
            "garmin credentials missing from keychain. Set with:\n"
            '  security add-generic-password -a default -s mobetter-stats-garmin-email -w "<EMAIL>"\n'
            '  security add-generic-password -a default -s mobetter-stats-garmin-pw    -w "<PASSWORD>"'
        )

    env = {**os.environ, "GARMIN_EMAIL": email, "GARMIN_PASSWORD": password}
    proc = subprocess.run(
        [str(GARMIN_PY), str(GARMIN_SYNC), "--no-build"],
        cwd=str(GARMIN_DIR),
        capture_output=True,
        text=True,
        env=env,
        timeout=180,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise GarminError(f"garmin sync exited {proc.returncode}:\n{detail}")


def sum_all_run_km(cutoff: date) -> tuple[float, date | None]:
    """Sum km for ALL runs in activities.jsonl with local_day strictly before cutoff.

    Re-sums from source of truth every run — late-uploaded activities auto-count
    on the next run, no dedup or missing-window logic needed.
    """
    if not ACTIVITIES_JSONL.is_file():
        return 0.0, None
    total_m = 0.0
    last_run: date | None = None
    for line in ACTIVITIES_JSONL.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        if (row.get("activity_kind") or "").lower() not in RUN_KINDS:
            continue
        day_str = row.get("local_day") or ""
        if not day_str:
            continue
        try:
            day = date.fromisoformat(day_str)
        except ValueError:
            continue
        if day >= cutoff:
            continue
        total_m += float(row.get("distance_m") or 0)
        if last_run is None or day > last_run:
            last_run = day
    return total_m / 1000.0, last_run


def main() -> int:
    p = argparse.ArgumentParser(description="Pull run km from Garmin into stats.md")
    p.add_argument("--no-sync", action="store_true", help="skip API call, read cached jsonl")
    p.add_argument("--today", type=str, default=None)
    args = p.parse_args()

    if not args.no_sync:
        try:
            run_garmin_sync()
        except GarminError as e:
            print(str(e), file=sys.stderr)
            return 1

    today = date.fromisoformat(args.today) if args.today else date.today()
    km, last_run = sum_all_run_km(today)
    print(f"GARMIN_TOTAL_RUN_KM={km:.3f}")
    print(f"GARMIN_LAST_RUN_DATE={last_run.isoformat() if last_run else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
