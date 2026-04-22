#!/usr/bin/env python3
"""Fold daily journal entries into content/stats.md.

Reads one journal file per day from JOURNAL_DIR, parses `Key: value` lines,
and applies:
  Run:   accumulate km into stats.md running.total_km
  Read:  started/finished/paused markers mutate reading_current + reading_year
  Learn: started/stopped markers flag the commit message (no auto-edit)

Advances stats.md running.last_processed on success. Other keys (Sleep, State,
goal, "One thing that happened") are ignored by design.

Usage:
    python3 _scripts/update_stats_from_journal.py              # apply + commit + push
    python3 _scripts/update_stats_from_journal.py --dry-run    # print, no writes
    python3 _scripts/update_stats_from_journal.py --no-push    # commit locally only
    python3 _scripts/update_stats_from_journal.py --today YYYY-MM-DD  # override cutoff
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STATS_PATH = REPO_ROOT / "content" / "stats.md"
INDEX_PATH = REPO_ROOT / "index.html"
BUILD_ROOT = REPO_ROOT / "_scripts" / "build_root.py"
JOURNAL_DIR = Path("/Users/ajin/Documents/New project/personal/Journal")

MI_TO_KM = 1.609344
JOURNAL_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")
RUN_SEGMENT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(km|kilometer|kilometers|mi|mile|miles)?", re.I)
READ_MARKER_RE = re.compile(r"^(started|finished|paused)\s+(.+)$", re.I)
LEARN_MARKER_RE = re.compile(r"^(started|stopped)\s+(.+)$", re.I)


class JournalError(Exception):
    """Bad grammar in a journal file. Caller decides whether to skip or abort."""


@dataclass
class JournalResult:
    journal_date: date
    run_km: float = 0.0
    reads: list[tuple[str, str]] = field(default_factory=list)  # (action, phrase)
    learn_notes: list[str] = field(default_factory=list)        # flagged for commit body
    errors: list[str] = field(default_factory=list)


# ---------- journal parsing ----------

def strip_comment(line: str) -> str:
    """Strip `#` comment to end of line, but NOT `#` at column 0 (markdown heading)."""
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
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if not value:
            continue

        try:
            if key == "run":
                result.run_km += parse_run(value)
            elif key == "read":
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


def parse_run(value: str) -> float:
    """Extract total km. Requires an explicit km/mi unit — bare numbers and prose
    (e.g. 'good. did stretching', '3x 400m intervals') count as 0."""
    lower = value.strip().lower()
    if not lower or lower in {"rest", "off", "-", "none", "skip"}:
        return 0.0
    total = 0.0
    for num_str, unit in RUN_SEGMENT_RE.findall(value):
        if not unit:
            continue
        km = float(num_str)
        if unit.lower().startswith("mi"):
            km *= MI_TO_KM
        total += km
    return total


def parse_marker(value: str, pattern: re.Pattern[str], key_name: str) -> tuple[str | None, str]:
    m = pattern.match(value)
    if not m:
        # Bare `Read: chapter 3` without a marker is a log, not an event — silently ignore.
        return None, ""
    action = m.group(1).lower()
    phrase = m.group(2).strip()
    # Strip surrounding quotes (either kind) for convenience.
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
        """Return (start_line_after_header, end_line_exclusive) for `## name`."""
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
        out: list[str] = []
        for i in range(start, end):
            s = self.lines[i].strip()
            if s.startswith("-"):
                out.append(s[1:].strip())
        return out

    def set_bullets(self, section: str, bullets: list[str]) -> None:
        start, end = self.section_range(section)
        # Capture non-bullet, non-blank lines (comments) and re-emit them above the bullets.
        preserved: list[str] = []
        for i in range(start, end):
            s = self.lines[i]
            stripped = s.strip()
            if stripped and not stripped.startswith("-"):
                preserved.append(s)
        new_section: list[str] = []
        if preserved:
            new_section.extend(preserved)
        for b in bullets:
            new_section.append(f"- {b}")
        # Keep one trailing blank line between sections.
        if end < len(self.lines) and self.lines[end].strip().startswith("##"):
            new_section.append("")
        self.lines[start:end] = new_section


# ---------- reading mutations ----------

def title_of(bullet: str) -> str:
    """`The Knockout Queen — Rufi Thorpe` → `the knockout queen` (lowercased, stripped)."""
    for sep in (" — ", " – ", " -- "):
        if sep in bullet:
            return bullet.split(sep, 1)[0].strip().lower()
    return bullet.strip().lower()


def match_title(needle: str, haystack: list[str]) -> int | None:
    """Case-insensitive prefix match on the TITLE portion of bullets. Returns index or None."""
    n = title_of(needle)
    matches = [i for i, b in enumerate(haystack) if title_of(b).startswith(n)]
    if len(matches) == 1:
        return matches[0]
    return None


def apply_reads(
    reads: list[tuple[str, str]],
    current: list[str],
    year: list[str],
) -> tuple[list[str], list[str], list[str]]:
    """Return (new_current, new_year, errors). Pure — does not mutate args."""
    current = list(current)
    year = list(year)
    errors: list[str] = []

    for action, phrase in reads:
        if action == "started":
            current.append(phrase)
        elif action in {"finished", "paused"}:
            idx = match_title(phrase, current)
            if idx is None:
                errors.append(f"Read: {action} {phrase!r} — no unique match in reading_current")
                continue
            removed = current.pop(idx)
            title_only = removed.split(" — ", 1)[0].split(" – ", 1)[0].strip()
            if action == "paused":
                year.append(f"{title_only} (paused)")
            else:
                year.append(title_only)
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
        if d <= last_processed:
            continue
        if d >= cutoff_exclusive:
            continue
        out.append(entry)
    return out


def run_git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{proc.stderr}")
    return proc.stdout


def run_build_root() -> None:
    proc = subprocess.run(
        [sys.executable, str(BUILD_ROOT)], cwd=REPO_ROOT, capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(f"build_root.py failed:\n{proc.stderr}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fold daily journal entries into stats.md")
    parser.add_argument("--dry-run", action="store_true", help="print plan, write nothing")
    parser.add_argument("--no-push", action="store_true", help="commit locally, skip push")
    parser.add_argument("--today", type=str, default=None, help="override today (YYYY-MM-DD)")
    args = parser.parse_args()

    today = date.fromisoformat(args.today) if args.today else date.today()

    stats = StatsFile.load(STATS_PATH)
    last_processed = date.fromisoformat(stats.get_running_kv("last_processed"))
    total_km_before = int(stats.get_running_kv("total_km").replace(",", ""))

    journals = discover_journals(last_processed, today)
    if not journals:
        print(f"no new journals (last_processed={last_processed}, today={today})")
        return 0

    added_km = 0.0
    all_reads: list[tuple[str, str]] = []
    all_learn: list[tuple[date, str]] = []
    hard_errors: list[str] = []
    last_ok: date | None = None

    for path in journals:
        jr = parse_journal(path)
        if jr.errors:
            hard_errors.append(f"{path.name}: " + "; ".join(jr.errors))
            break  # stop at first bad day so user can fix and re-run
        added_km += jr.run_km
        all_reads.extend(jr.reads)
        for note in jr.learn_notes:
            all_learn.append((jr.journal_date, note))
        last_ok = jr.journal_date

    current = stats.get_bullets("reading_current")
    year = stats.get_bullets("reading_year")
    new_current, new_year, read_errors = apply_reads(all_reads, current, year)
    if read_errors:
        hard_errors.extend(read_errors)

    if hard_errors:
        print("errors — aborting without advancing last_processed:", file=sys.stderr)
        for e in hard_errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    if last_ok is None:
        print("no processable journals (all empty or errored).")
        return 0

    new_total_km = total_km_before + int(round(added_km))

    print(f"processed {len(journals)} journal(s) up to {last_ok}")
    print(f"  run km added: {added_km:.2f} (total {total_km_before} → {new_total_km})")
    if all_reads:
        print(f"  read events: {all_reads}")
    if all_learn:
        print(f"  learn notes (manual edit needed): {all_learn}")

    if args.dry_run:
        print("--dry-run: no writes, no commit")
        return 0

    stats.set_running_kv("total_km", str(new_total_km))
    stats.set_running_kv("last_processed", last_ok.isoformat())
    stats.set_bullets("reading_current", new_current)
    stats.set_bullets("reading_year", new_year)
    stats.save()

    run_build_root()

    run_git("add", "content/stats.md", "index.html")
    status = run_git("status", "--porcelain", "content/stats.md", "index.html")
    if not status.strip():
        print("nothing to commit after build.")
        return 0

    first = journals[0].stem
    last = last_ok.isoformat()
    range_str = last if first == last else f"{first}→{last}"
    subject = f"Update stats from journal ({range_str})"
    body_lines: list[str] = []
    if added_km:
        body_lines.append(f"+{added_km:.1f} km running → {new_total_km} total")
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
