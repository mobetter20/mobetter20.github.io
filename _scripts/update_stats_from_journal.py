#!/usr/bin/env python3
"""Fold Garmin run distance + daily journal Read/Learn events into stats.md.

Source of truth:
  - total_km: baseline_km + all-time run distance from Garmin Connect.
  - reading_current / reading_year: mutated by `Read: started/finished/paused`
    markers in journal files.
  - learning prose: untouched by this script; `Learn:` markers surface in the
    commit body for manual follow-up.

On Garmin failure: send email + macOS banner, prefix commit body with WARN,
skip total_km update. Journal Read/Learn still processes so reading lists
don't stall behind a Garmin outage.

On journal Read hard-error (marker with no unique match): abort without
advancing last_processed so the user can fix and re-run.

Usage:
    python3 _scripts/update_stats_from_journal.py              # sync + commit + push
    python3 _scripts/update_stats_from_journal.py --dry-run    # no writes
    python3 _scripts/update_stats_from_journal.py --no-push    # commit, no push
    python3 _scripts/update_stats_from_journal.py --skip-garmin  # skip Garmin (test)
    python3 _scripts/update_stats_from_journal.py --today YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "_scripts"
STATS_PATH = REPO_ROOT / "content" / "stats.md"
BUILD_ROOT = SCRIPTS_DIR / "build_root.py"
SYNC_GARMIN = SCRIPTS_DIR / "sync_from_garmin.py"
JOURNAL_DIR = Path("/Users/ajin/Documents/New project/personal/Journal")

sys.path.insert(0, str(SCRIPTS_DIR))
from notify import notify  # noqa: E402

JOURNAL_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")
READ_MARKER_RE = re.compile(r"^(started|finished|paused)\s+(.+)$", re.I)
LEARN_MARKER_RE = re.compile(r"^(started|stopped)\s+(.+)$", re.I)


class JournalError(Exception):
    pass


@dataclass
class JournalResult:
    journal_date: date
    reads: list[tuple[str, str]] = field(default_factory=list)
    learn_notes: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# ---------- journal parsing ----------

def strip_comment(line: str) -> str:
    if line.startswith("#"):
        return line
    idx = line.find(" #")
    if idx == -1:
        return line.rstrip()
    return line[:idx].rstrip()


def parse_journal(path: Path) -> JournalResult:
    journal_date = date.fromisoformat(path.stem)
    result = JournalResult(journal_date=journal_date)
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = strip_comment(raw).strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if not value:
            continue
        try:
            if key == "read":
                action, phrase = parse_marker(value, READ_MARKER_RE, "Read")
                if action:
                    result.reads.append((action, phrase))
            elif key == "learn":
                action, phrase = parse_marker(value, LEARN_MARKER_RE, "Learn")
                if action:
                    result.learn_notes.append(f"{action} {phrase}")
        except JournalError as e:
            result.errors.append(str(e))
    return result


def parse_marker(value: str, pattern: re.Pattern[str], key_name: str) -> tuple[str | None, str]:
    m = pattern.match(value)
    if not m:
        return None, ""
    action = m.group(1).lower()
    phrase = m.group(2).strip()
    if len(phrase) >= 2 and phrase[0] in "\"'" and phrase[-1] == phrase[0]:
        phrase = phrase[1:-1].strip()
    if not phrase:
        raise JournalError(f"{key_name}: empty phrase after '{action}'")
    return action, phrase


# ---------- stats.md surgery ----------

@dataclass
class StatsFile:
    lines: list[str]
    path: Path

    @classmethod
    def load(cls, path: Path) -> "StatsFile":
        return cls(path.read_text(encoding="utf-8").splitlines(), path)

    def save(self) -> None:
        self.path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")

    def section_range(self, name: str) -> tuple[int, int]:
        start = None
        for i, line in enumerate(self.lines):
            if line.strip().startswith("##") and line.strip()[2:].strip() == name:
                start = i + 1
                break
        if start is None:
            raise ValueError(f"stats.md missing section: ## {name}")
        end = len(self.lines)
        for j in range(start, len(self.lines)):
            if self.lines[j].strip().startswith("##"):
                end = j
                break
        return start, end

    def get_running_kv(self, key: str) -> str:
        start, end = self.section_range("running")
        for i in range(start, end):
            s = self.lines[i].strip()
            if s.startswith("#") or ":" not in s:
                continue
            k, v = s.split(":", 1)
            if k.strip() == key:
                return v.strip()
        raise ValueError(f"stats.md running: missing key {key}")

    def set_running_kv(self, key: str, new_value: str) -> None:
        start, end = self.section_range("running")
        for i in range(start, end):
            s = self.lines[i].strip()
            if s.startswith("#") or ":" not in s:
                continue
            k, _ = s.split(":", 1)
            if k.strip() == key:
                self.lines[i] = f"{k.strip()}: {new_value}"
                return
        raise ValueError(f"stats.md running: cannot set missing key {key}")

    def get_bullets(self, section: str) -> list[str]:
        start, end = self.section_range(section)
        return [self.lines[i].strip()[1:].strip() for i in range(start, end) if self.lines[i].strip().startswith("-")]

    def set_bullets(self, section: str, bullets: list[str]) -> None:
        start, end = self.section_range(section)
        preserved = [self.lines[i] for i in range(start, end) if self.lines[i].strip() and not self.lines[i].strip().startswith("-")]
        new_section: list[str] = list(preserved)
        for b in bullets:
            new_section.append(f"- {b}")
        if end < len(self.lines) and self.lines[end].strip().startswith("##"):
            new_section.append("")
        self.lines[start:end] = new_section


# ---------- reading mutations (idempotent) ----------

def title_of(bullet: str) -> str:
    for sep in (" — ", " – ", " -- "):
        if sep in bullet:
            return bullet.split(sep, 1)[0].strip().lower()
    return bullet.strip().lower()


def match_title(needle: str, haystack: list[str]) -> int | None:
    n = title_of(needle)
    matches = [i for i, b in enumerate(haystack) if title_of(b).startswith(n)]
    return matches[0] if len(matches) == 1 else None


def apply_reads(
    reads: list[tuple[str, str]],
    current: list[str],
    year: list[str],
) -> tuple[list[str], list[str], list[str]]:
    current = list(current)
    year = list(year)
    errors: list[str] = []

    for action, phrase in reads:
        if action == "started":
            # Idempotent: skip if already in current.
            if match_title(phrase, current) is not None:
                continue
            current.append(phrase)
        elif action in {"finished", "paused"}:
            idx = match_title(phrase, current)
            if idx is None:
                # Idempotent: if already in year, skip silently — we already processed this.
                if match_title(phrase, year) is not None:
                    continue
                errors.append(f"Read: {action} {phrase!r} — no unique match in reading_current")
                continue
            removed = current.pop(idx)
            title_only = removed.split(" — ", 1)[0].split(" – ", 1)[0].strip()
            year.append(f"{title_only} (paused)" if action == "paused" else title_only)
        else:
            errors.append(f"Read: unknown action {action!r}")

    return current, year, errors


# ---------- orchestration ----------

def discover_journals(last_processed: date, cutoff_exclusive: date) -> list[Path]:
    if not JOURNAL_DIR.is_dir():
        return []
    out: list[Path] = []
    for entry in sorted(JOURNAL_DIR.iterdir()):
        m = JOURNAL_RE.match(entry.name)
        if not m:
            continue
        d = date.fromisoformat(m.group(1))
        if last_processed < d < cutoff_exclusive:
            out.append(entry)
    return out


def run_git(*args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{proc.stderr}")
    return proc.stdout


def run_build_root() -> None:
    proc = subprocess.run([sys.executable, str(BUILD_ROOT)], cwd=REPO_ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"build_root.py failed:\n{proc.stderr}")


def call_garmin_sync(today: date) -> tuple[bool, float | None, str, str | None]:
    """Returns (ok, total_run_km, last_run_date_iso, error_message)."""
    proc = subprocess.run(
        [sys.executable, str(SYNC_GARMIN), "--today", today.isoformat()],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return False, None, "", (proc.stderr or proc.stdout or "").strip()

    total_km: float | None = None
    last_run = ""
    for line in proc.stdout.splitlines():
        if line.startswith("GARMIN_TOTAL_RUN_KM="):
            try:
                total_km = float(line.split("=", 1)[1])
            except ValueError:
                pass
        elif line.startswith("GARMIN_LAST_RUN_DATE="):
            last_run = line.split("=", 1)[1].strip()
    if total_km is None:
        return False, None, "", f"sync_from_garmin printed no GARMIN_TOTAL_RUN_KM:\n{proc.stdout}"
    return True, total_km, last_run, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Fold Garmin + journal into stats.md")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-push", action="store_true")
    parser.add_argument("--today", type=str, default=None)
    parser.add_argument("--skip-garmin", action="store_true", help="for testing; skip Garmin sync")
    args = parser.parse_args()

    today = date.fromisoformat(args.today) if args.today else date.today()

    stats = StatsFile.load(STATS_PATH)
    last_processed = date.fromisoformat(stats.get_running_kv("last_processed"))
    total_km_before = int(stats.get_running_kv("total_km").replace(",", ""))
    baseline_km = int(stats.get_running_kv("baseline_km").replace(",", ""))

    # --- Garmin ---
    garmin_ok = False
    garmin_total_km: float | None = None
    garmin_last_run = ""
    garmin_error: str | None = None
    if not args.skip_garmin:
        garmin_ok, garmin_total_km, garmin_last_run, garmin_error = call_garmin_sync(today)
        if garmin_error:
            print(f"garmin sync failed: {garmin_error}", file=sys.stderr)
            notify(
                f"ajin.im stats: Garmin sync failed {today.isoformat()}",
                f"{garmin_error}\n\ntotal_km will not advance until this is fixed.\n"
                f"Logs: ~/Library/Logs/mobetter-stats.err.log",
            )

    # --- Journals: Read/Learn only ---
    journals = discover_journals(last_processed, today)
    all_reads: list[tuple[str, str]] = []
    all_learn: list[tuple[date, str]] = []
    hard_errors: list[str] = []
    last_journal_ok: date | None = None
    for path in journals:
        jr = parse_journal(path)
        if jr.errors:
            hard_errors.append(f"{path.name}: " + "; ".join(jr.errors))
            break
        all_reads.extend(jr.reads)
        for note in jr.learn_notes:
            all_learn.append((jr.journal_date, note))
        last_journal_ok = jr.journal_date

    current = stats.get_bullets("reading_current")
    year = stats.get_bullets("reading_year")
    new_current, new_year, read_errors = apply_reads(all_reads, current, year)
    hard_errors.extend(read_errors)

    if hard_errors:
        print("errors — aborting without advancing last_processed:", file=sys.stderr)
        for e in hard_errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    # --- Decide what changed ---
    new_total_km = total_km_before
    if garmin_ok and garmin_total_km is not None:
        new_total_km = baseline_km + int(round(garmin_total_km))

    reading_changed = new_current != current or new_year != year
    total_changed = new_total_km != total_km_before

    if not journals and not total_changed:
        print(f"nothing to do (last_processed={last_processed}, today={today}, garmin_ok={garmin_ok})")
        return 0

    # Summary
    print(f"garmin_ok={garmin_ok}, last_run={garmin_last_run or '—'}, "
          f"total_km {total_km_before} → {new_total_km}")
    if last_journal_ok:
        print(f"processed {len(journals)} journal(s) up to {last_journal_ok}")
    if all_reads:
        print(f"  read events: {all_reads}")
    if all_learn:
        print(f"  learn notes (manual edit needed): {all_learn}")

    if args.dry_run:
        print("--dry-run: no writes, no commit")
        return 0

    # --- Apply changes ---
    if total_changed:
        stats.set_running_kv("total_km", str(new_total_km))
    if last_journal_ok:
        stats.set_running_kv("last_processed", last_journal_ok.isoformat())
    if reading_changed:
        stats.set_bullets("reading_current", new_current)
        stats.set_bullets("reading_year", new_year)
    stats.save()

    run_build_root()

    run_git("add", "content/stats.md", "index.html")
    status = run_git("status", "--porcelain", "content/stats.md", "index.html")
    if not status.strip():
        print("nothing to commit after build.")
        return 0

    # --- Commit message ---
    if last_journal_ok and journals:
        first = journals[0].stem
        last = last_journal_ok.isoformat()
        range_str = last if first == last else f"{first}→{last}"
        subject = f"Update stats from journal ({range_str})"
    else:
        subject = f"Update stats ({today.isoformat()})"

    body_lines: list[str] = []
    if garmin_error:
        body_lines.append(f"WARN: Garmin sync failed on {today.isoformat()} — total_km not advanced")
    if garmin_ok and total_changed:
        body_lines.append(f"+{new_total_km - total_km_before} km running → {new_total_km} total (from Garmin)")
    for d, note in all_learn:
        body_lines.append(f"Learn note {d}: {note} (stats.md learning section needs manual edit)")
    commit_msg = subject + ("\n\n" + "\n".join(body_lines) if body_lines else "")
    run_git("commit", "-m", commit_msg)

    if not args.no_push:
        print(run_git("push"))

    print(f"committed: {subject}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
