#!/usr/bin/env python3
"""Publish essays from an Obsidian drop folder to https://ajin.im/writes.

Contract (also stated for the owner in the drop folder's own `_README.md`):

    ~/Documents/Ajin/Writing/publish/<anything>.md   top level only, never recursive
    front matter needs `title:` and exactly `publish: true`
    optional: `date:` (year), `slug:`, `excerpt:`

A file without `publish: true` is ignored, so drafts live safely in the folder.
Absence of the marker means nothing happens — that is the safe default, because the
vault it sits in contains private writing.

This pushes to a PUBLIC site with no human in the loop, so it refuses far more
readily than it publishes. Every refusal notifies once (not every tick) and leaves
state untouched so the next tick retries.

Guards, and the failure each one exists to stop:
  * two-tick stability   — "added publish: true, then went to lunch mid-sentence"
  * mtime debounce       — autosave while typing
  * wikilink reject      — [[Private Note]] would publish a private note's title
  * conflict-copy skip   — Obsidian/iCloud "foo 1.md", Dropbox "conflicted copy"
  * branch assert        — repo parked on a topic branch: push succeeds, site never updates
  * clean-tree assert    — publish.sh does `git add -A`; would sweep up unrelated WIP
  * nothing-unpushed     — a commit deliberately kept local would ride out to public
  * post-publish verify  — publish.sh exits 0 on "No changes to publish", so exit code
                           alone would banner "it's live" for a page that 404s
  * hand-edit detect     — owner edited _src/<slug>.md directly; don't clobber it
  * state reconcile      — lost state file must self-heal, not refuse forever

Operate:
    publish_watcher.py --selftest    pure logic, offline
    publish_watcher.py --status      what it thinks is published / pending
    publish_watcher.py --dry-run     full scan + guards, writes nothing
    publish_watcher.py               one real tick (what launchd runs)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

DROP = Path.home() / "Documents/Ajin/Writing/publish"
SITE = Path.home() / "Documents/New project/personal/mobetter20.github.io"
SRC = SITE / "is" / "writing" / "essays" / "_src"
BRANCH = "master"
SITE_BASE = "https://ajin.im"

STATE_DIR = Path.home() / ".local/share/writes-publisher"
STATE_PATH = STATE_DIR / "state.json"
LOCK_PATH = STATE_DIR / "lock.json"
LOG_PATH = STATE_DIR / "publisher.log"

DEBOUNCE_SECONDS = 180          # file must have been still this long
STABILITY_SECONDS = 300         # ...and unchanged across ticks this far apart
LOCK_STALE_SECONDS = 900
LOG_MAX_BYTES = 1_000_000
PUBLISH_TIMEOUT = 900

# Named conflict copies are unambiguous. The "foo 1.md" / "foo (2).md" shapes are
# not — "Chapter 2.md" is a perfectly good title — so those only count as conflicts
# when the original they were forked from is sitting next to them.
NAMED_CONFLICT = (
    re.compile(r"conflicted copy", re.I),          # Dropbox
    re.compile(r"\bsync-conflict\b", re.I),        # Syncthing
)
NUMBERED_COPY = re.compile(r"^(?P<stem>.+?)[ ](?:(?P<bare>\d+)|\((?P<paren>\d+)\))\.md$", re.I)
WIKILINK = re.compile(r"!?\[\[")
SLUG_OK = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


# ---------------------------------------------------------------- small helpers

def log(message: str) -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"{stamp} {message}", flush=True)


def rotate_log() -> None:
    try:
        if LOG_PATH.exists() and LOG_PATH.stat().st_size > LOG_MAX_BYTES:
            tail = LOG_PATH.read_bytes()[-200_000:]
            LOG_PATH.write_bytes(b"[log truncated]\n" + tail)
    except OSError:
        pass


def notify(subject: str, body: str) -> None:
    log(f"NOTIFY {subject} :: {body}")
    try:
        sys.path.insert(0, str(SITE / "_scripts"))
        from notify import notify as site_notify  # type: ignore

        site_notify(subject, body)
        return
    except Exception:  # noqa: BLE001 - never let notification failure break a run
        pass
    try:
        safe_t = subject.replace('"', '\\"')[:100]
        safe_b = body.replace('"', '\\"')[:200]
        subprocess.run(
            ["osascript", "-e", f'display notification "{safe_b}" with title "{safe_t}"'],
            capture_output=True,
        )
    except Exception:  # noqa: BLE001
        pass


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(value: str) -> str:
    value = value.lower().replace(" ", " ")
    value = re.sub(r"[‘’“”']", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def parse_front_matter(text: str) -> tuple[dict[str, str], str] | None:
    """None when the block is missing or unterminated (i.e. still being typed)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fm: dict[str, str] = {}
    for i in range(1, len(lines)):
        line = lines[i].strip()
        if line == "---":
            return fm, "\n".join(lines[i + 1:]).strip("\n")
        if ":" in line:
            key, value = line.split(":", 1)
            fm[key.strip().lower()] = value.strip()
    return None


def looks_like_conflict_copy(name: str, siblings: set[str] | None = None) -> bool:
    if any(p.search(name) for p in NAMED_CONFLICT):
        return True
    m = NUMBERED_COPY.match(name)
    if not m:
        return False
    if siblings is None:
        return True
    return f"{m.group('stem')}.md" in siblings


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(SITE), *args],
        capture_output=True, text=True, check=check,
    )


# --------------------------------------------------------------------- state

def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"version": 1, "published": {}, "pending": {}, "errors": {}, "last_run": ""}
    try:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        log("state file unreadable — starting fresh (reconcile will re-adopt)")
        return {"version": 1, "published": {}, "pending": {}, "errors": {}, "last_run": ""}
    for key in ("published", "pending", "errors"):
        state.setdefault(key, {})
    return state


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(STATE_PATH)


def notify_once(state: dict, key: str, subject: str, body: str) -> None:
    """Notify only when this exact problem is new — a tool that banners every 30
    minutes gets muted, and a muted tool is an abandoned tool."""
    fingerprint = sha(f"{subject}\x00{body}")
    if state["errors"].get(key) == fingerprint:
        log(f"(suppressed repeat) {subject} :: {body}")
        return
    state["errors"][key] = fingerprint
    notify(subject, body)


def clear_error(state: dict, key: str) -> None:
    state["errors"].pop(key, None)


# ------------------------------------------------------------------- lockfile

def acquire_lock() -> bool:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if LOCK_PATH.exists():
        try:
            held = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            held = {}
        pid, at = held.get("pid"), held.get("at", 0)
        alive = False
        if isinstance(pid, int):
            try:
                os.kill(pid, 0)
                alive = True
            except OSError:
                alive = False
        if alive and (time.time() - at) < LOCK_STALE_SECONDS:
            log(f"another run holds the lock (pid {pid}) — skipping tick")
            return False
        log(f"stealing stale lock (pid {pid}, age {int(time.time() - at)}s)")
    LOCK_PATH.write_text(
        json.dumps({"pid": os.getpid(), "at": time.time()}), encoding="utf-8"
    )
    return True


def release_lock() -> None:
    try:
        LOCK_PATH.unlink(missing_ok=True)
    except OSError:
        pass


# ------------------------------------------------------------------ candidates

@dataclass
class Candidate:
    path: Path
    slug: str
    title: str
    date: str
    excerpt: str
    body: str

    @property
    def content_hash(self) -> str:
        return sha(f"{self.title}\x00{self.date}\x00{self.excerpt}\x00{self.body}")

    def src_text(self, order: int) -> str:
        lines = ["---", f"title: {self.title}", f"order: {order}"]
        if self.date:
            lines.append(f"date: {self.date}")
        if self.excerpt:
            lines.append(f"excerpt: {self.excerpt}")
        lines += ["---", "", self.body, ""]
        return "\n".join(lines)


def scan_drop(state: dict) -> list[Candidate]:
    if not DROP.is_dir():
        return []
    out: list[Candidate] = []
    paths = sorted(DROP.glob("*.md"))
    siblings = {p.name for p in paths}
    for path in paths:
        name = path.name
        if name.startswith("_"):
            continue
        if looks_like_conflict_copy(name, siblings):
            log(f"skip (looks like a sync conflict copy): {name}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            log(f"skip (unreadable): {name} — {exc}")
            continue

        parsed = parse_front_matter(text)
        if parsed is None:
            log(f"skip (front matter missing or unterminated): {name}")
            continue
        fm, body = parsed

        if fm.get("publish", "").strip().lower() != "true":
            continue
        if not fm.get("title"):
            notify_once(state, f"file:{name}", "ajin.im — not published",
                        f"{name} has publish: true but no title:")
            continue
        if not body.strip():
            log(f"skip (marked publish but body is empty): {name}")
            continue
        if WIKILINK.search(body) or WIKILINK.search(fm.get("excerpt", "")):
            notify_once(state, f"file:{name}", "ajin.im — not published",
                        f"{name} contains [[wikilinks]]. They would publish as raw text "
                        "and can expose private note titles. Replace them first.")
            continue

        title = fm["title"]
        slug = fm.get("slug") or slugify(title)
        if not SLUG_OK.match(slug) or slug.startswith("_") or slug.endswith(".local"):
            notify_once(state, f"file:{name}", "ajin.im — not published",
                        f"{name}: unusable slug {slug!r}. Set a `slug:` of lowercase "
                        "words and hyphens.")
            continue

        clear_error(state, f"file:{name}")
        out.append(Candidate(path, slug, title, fm.get("date", ""),
                             fm.get("excerpt", ""), body))
    return out


def reconcile(state: dict, candidates: list[Candidate]) -> None:
    """Self-heal a lost/partial state file.

    If _src/<slug>.md already holds exactly what this drop file would produce, it
    IS ours — adopt it rather than refusing as a collision forever."""
    for cand in candidates:
        if cand.slug in state["published"]:
            continue
        src_file = SRC / f"{cand.slug}.md"
        if not src_file.exists():
            continue
        try:
            existing = src_file.read_text(encoding="utf-8")
        except OSError:
            continue
        order = _order_of(existing)
        if order is not None and existing == cand.src_text(order):
            state["published"][cand.slug] = {
                "source": cand.path.name,
                "content_hash": cand.content_hash,
                "src_hash": sha(existing),
                "url": f"{SITE_BASE}/writes/{cand.slug}/",
                "published_at": "adopted",
            }
            log(f"reconciled existing essay into state: {cand.slug}")


def _order_of(src_text: str) -> int | None:
    m = re.search(r"^order:\s*(-?\d+)\s*$", src_text, re.M)
    return int(m.group(1)) if m else None


def ready_to_publish(state: dict, candidates: list[Candidate]) -> list[Candidate]:
    """Debounce + two-tick stability + change detection + safety refusals."""
    ready: list[Candidate] = []
    seen_slugs: dict[str, Candidate] = {}
    pending = state["pending"]
    live_names = {c.path.name for c in candidates}
    for stale in [k for k in pending if k not in live_names]:
        pending.pop(stale, None)

    for cand in candidates:
        name, key = cand.path.name, f"file:{cand.path.name}"

        if cand.slug in seen_slugs:
            notify_once(state, key, "ajin.im — not published",
                        f"{name} and {seen_slugs[cand.slug].path.name} both claim the "
                        f"URL /writes/{cand.slug}/. Give one a different `slug:`.")
            continue
        seen_slugs[cand.slug] = cand

        record = state["published"].get(cand.slug)
        if record and record.get("content_hash") == cand.content_hash:
            pending.pop(name, None)
            continue

        if record and record.get("source") not in (None, name):
            notify_once(state, key, "ajin.im — not published",
                        f"{name} claims /writes/{cand.slug}/, already published from "
                        f"{record['source']}. Give one a different `slug:`.")
            continue

        src_file = SRC / f"{cand.slug}.md"
        if src_file.exists():
            current = src_file.read_text(encoding="utf-8")
            if not record:
                notify_once(state, key, "ajin.im — not published",
                            f"{name} would overwrite the existing essay "
                            f"/writes/{cand.slug}/ that this tool did not publish. "
                            "Choose a different `slug:`.")
                continue
            if record.get("src_hash") and sha(current) != record["src_hash"]:
                notify_once(state, key, "ajin.im — not published",
                            f"{cand.slug}.md was hand-edited in the site repo. "
                            "Publishing would discard those edits. Resolve by hand.")
                continue

        try:
            age = time.time() - cand.path.stat().st_mtime
        except OSError:
            continue
        if age < DEBOUNCE_SECONDS:
            log(f"holding (edited {int(age)}s ago): {name}")
            pending[name] = {"hash": cand.content_hash, "first_seen": time.time()}
            continue

        prior = pending.get(name)
        if not prior or prior.get("hash") != cand.content_hash:
            log(f"holding for stability check: {name}")
            pending[name] = {"hash": cand.content_hash, "first_seen": time.time()}
            continue
        if (time.time() - prior.get("first_seen", 0)) < STABILITY_SECONDS:
            log(f"holding (stable {int(time.time() - prior['first_seen'])}s of "
                f"{STABILITY_SECONDS}s): {name}")
            continue

        clear_error(state, key)
        ready.append(cand)
    return ready


# ----------------------------------------------------------------- git guards

def preflight(state: dict) -> str | None:
    """Return a refusal reason, or None when it is safe to publish."""
    if not SITE.is_dir():
        return f"site repo not found at {SITE}"
    try:
        head = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    except subprocess.CalledProcessError as exc:
        return f"git failed: {exc.stderr.strip()[:200]}"
    if head != BRANCH:
        return f"site repo is on branch {head!r}, not {BRANCH!r}"

    fetched = git("fetch", "origin", BRANCH, check=False)
    if fetched.returncode != 0:
        return f"git fetch failed: {fetched.stderr.strip()[:200]}"

    dirty = git("status", "--porcelain").stdout.strip()
    if dirty:
        first = dirty.splitlines()[:3]
        return ("site repo has uncommitted changes, so publishing would sweep them "
                "into a public commit: " + "; ".join(first))

    ahead = git("rev-list", "--count", f"origin/{BRANCH}..HEAD").stdout.strip()
    if ahead != "0":
        return resume_or_refuse(int(ahead))
    return None


OUR_COMMIT = re.compile(r"^(Add essay: .+|Add \d+ essays)$")


def resume_or_refuse(ahead: int) -> str | None:
    """Unpushed commits are normally a refusal: pushing them would put work the owner
    deliberately kept local onto a public site.

    The exception is a commit WE made on an earlier tick that committed but failed to
    push (rebase conflict, network). Refusing those forever would wedge the tool until
    a human intervened, so resume them — a push, never a reset."""
    subjects = git("log", "--format=%s", f"origin/{BRANCH}..HEAD").stdout.strip().splitlines()
    foreign = [s for s in subjects if not OUR_COMMIT.match(s)]
    if foreign:
        return (f"site repo has {ahead} unpushed commit(s) that this tool did not make "
                f"({foreign[0][:60]!r}); publishing would push them to the public site")

    log(f"resuming {ahead} stranded publish commit(s) from an earlier tick")
    pulled = git("pull", "--rebase", "origin", BRANCH, check=False)
    if pulled.returncode != 0:
        git("rebase", "--abort", check=False)
        return f"could not rebase a stranded publish commit: {pulled.stderr.strip()[:160]}"
    pushed = git("push", "origin", BRANCH, check=False)
    if pushed.returncode != 0:
        return f"could not push a stranded publish commit: {pushed.stderr.strip()[:160]}"
    still = git("rev-list", "--count", f"origin/{BRANCH}..HEAD").stdout.strip()
    if still != "0":
        return f"stranded commit still unpushed after retry ({still} ahead)"
    return None


def run_publish(message: str) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            ["./publish.sh", "--message", message],
            cwd=str(SITE), capture_output=True, text=True, timeout=PUBLISH_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return False, f"publish.sh timed out after {PUBLISH_TIMEOUT}s"
    tail = (proc.stdout + proc.stderr).strip().splitlines()[-6:]
    return proc.returncode == 0, "\n".join(tail)


def verify_published(staged: dict[str, str]) -> str | None:
    """publish.sh exits 0 even when it pushed nothing ("No changes to publish"), so
    the exit code is not evidence. Prove it from git instead."""
    fetched = git("fetch", "origin", BRANCH, check=False)
    if fetched.returncode != 0:
        return f"could not verify: git fetch failed: {fetched.stderr.strip()[:160]}"
    contained = git("merge-base", "--is-ancestor", "HEAD", f"origin/{BRANCH}", check=False)
    if contained.returncode != 0:
        return "local commit is not on origin — nothing was actually pushed"
    for slug, expected in staged.items():
        shown = git("show", f"HEAD:is/writing/essays/_src/{slug}.md", check=False)
        if shown.returncode != 0 or shown.stdout != expected:
            return f"{slug}: source is not in the pushed commit"
        page = git("cat-file", "-e", f"HEAD:writes/{slug}/index.html", check=False)
        if page.returncode != 0:
            return f"{slug}: page was not generated into the pushed commit"
    return None


# --------------------------------------------------------------------- staging

def next_order() -> int:
    orders = []
    for path in SRC.glob("*.md"):
        if path.name.startswith("_"):
            continue
        order = _order_of(path.read_text(encoding="utf-8"))
        if order is not None:
            orders.append(order)
    return (max(orders) + 1) if orders else 0


def stage(candidates: list[Candidate]) -> dict[str, str]:
    """Write each piece into _src/. Existing essays are never renumbered: `order` is
    a monotonic counter, so a publish touches exactly one file per piece."""
    staged: dict[str, str] = {}
    counter = next_order()

    def mtime(cand: Candidate) -> float:
        try:  # the drop file can vanish between scan and stage
            return cand.path.stat().st_mtime
        except OSError:
            return 0.0

    for cand in sorted(candidates, key=mtime):
        record = None
        src_file = SRC / f"{cand.slug}.md"
        if src_file.exists():
            record = _order_of(src_file.read_text(encoding="utf-8"))
        order = record if record is not None else counter
        if record is None:
            counter += 1
        text = cand.src_text(order)
        src_file.write_text(text, encoding="utf-8")
        staged[cand.slug] = text
    return staged


def revert_staged(slugs: list[str]) -> None:
    """Undo a failed run completely.

    preflight guarantees the tree was clean before staging, so everything dirty now
    came from this run and is safe to discard. The generated pages matter as much as
    the source: leaving `writes/<slug>/` behind means the NEXT publish sweeps it up
    via `git add -A` and ships a page nobody decided to ship."""
    git("checkout", "--", ".", check=False)
    for slug in slugs:
        tracked = git("cat-file", "-e", f"HEAD:is/writing/essays/_src/{slug}.md", check=False)
        if tracked.returncode == 0:
            continue
        (SRC / f"{slug}.md").unlink(missing_ok=True)
        for generated in (SITE / "writes" / slug, SITE / "wrote" / slug):
            page = generated / "index.html"
            page.unlink(missing_ok=True)
            try:
                generated.rmdir()
            except OSError:
                pass


# ------------------------------------------------------------------------ tick

def tick(dry_run: bool = False) -> int:
    state = load_state()
    state["last_run"] = now_iso()

    candidates = scan_drop(state)
    reconcile(state, candidates)
    ready = ready_to_publish(state, candidates)

    if not ready:
        log(f"nothing ready ({len(candidates)} marked file(s) in drop folder)")
        if not dry_run:
            save_state(state)
        return 0

    titles = ", ".join(c.title for c in ready)
    refusal = preflight(state)
    if refusal:
        notify_once(state, "preflight", "ajin.im — publish on hold", refusal)
        log(f"REFUSED: {refusal}")
        if not dry_run:
            save_state(state)
        return 1
    clear_error(state, "preflight")

    if dry_run:
        log(f"DRY RUN — would publish: {titles}")
        for cand in ready:
            log(f"  /writes/{cand.slug}/  <- {cand.path.name}")
        return 0

    log(f"publishing: {titles}")
    staged = stage(ready)
    message = (f"Add essay: {ready[0].title}" if len(ready) == 1
               else f"Add {len(ready)} essays")
    ok, detail = run_publish(message)
    problem = verify_published(staged) if ok else detail

    if not ok or problem:
        revert_staged([c.slug for c in ready])
        notify_once(state, "publish", "ajin.im — publish FAILED",
                    f"{titles}: {problem or detail}. Will retry; nothing is live.")
        log(f"FAILED: {problem or detail}")
        save_state(state)
        return 1

    clear_error(state, "publish")
    urls = []
    for cand in ready:
        url = f"{SITE_BASE}/writes/{cand.slug}/"
        state["published"][cand.slug] = {
            "source": cand.path.name,
            "content_hash": cand.content_hash,
            "src_hash": sha(staged[cand.slug]),
            "url": url,
            "published_at": now_iso(),
        }
        state["pending"].pop(cand.path.name, None)
        urls.append(url)
    save_state(state)
    notify("ajin.im — published", f"{titles}\n" + "\n".join(urls))
    log("published: " + " ".join(urls))
    return 0


# -------------------------------------------------------------------- commands

def cmd_status() -> int:
    state = load_state()
    print(f"drop folder : {DROP}")
    print(f"site repo   : {SITE}")
    print(f"state       : {STATE_PATH}")
    print(f"last run    : {state.get('last_run') or 'never'}")
    published = state.get("published", {})
    print(f"\npublished ({len(published)}):")
    for slug, rec in sorted(published.items()):
        print(f"  {slug:52s} {rec.get('published_at', '?')}")
    pending = state.get("pending", {})
    if pending:
        print(f"\nheld for stability ({len(pending)}):")
        for name, rec in sorted(pending.items()):
            age = int(time.time() - rec.get("first_seen", 0))
            print(f"  {name:52s} stable {age}s / {STABILITY_SECONDS}s")
    errors = state.get("errors", {})
    if errors:
        print(f"\noutstanding refusals ({len(errors)}): {', '.join(sorted(errors))}")
        print("  (run --dry-run to see the reason)")
    return 0


def cmd_selftest() -> int:
    ok = True

    def check(label: str, got, want) -> None:
        nonlocal ok
        if got != want:
            ok = False
            print(f"  FAIL {label}: got {got!r}, want {want!r}")
        else:
            print(f"  ok   {label}")

    print("slugify")
    check("basic", slugify("The Dislike Button and the Rise of Bad Engagement"),
          "the-dislike-button-and-the-rise-of-bad-engagement")
    check("curly apostrophe", slugify("Don’t Look"), "dont-look")
    check("trailing punctuation", slugify("Korea was the beta test zone."),
          "korea-was-the-beta-test-zone")

    print("conflict copies")
    for name in ("note conflicted copy.md", "note.sync-conflict-x.md"):
        check(name, looks_like_conflict_copy(name, set()), True)
    with_original = {"note.md", "note 1.md", "note (2).md"}
    check("note 1.md beside note.md", looks_like_conflict_copy("note 1.md", with_original), True)
    check("note (2).md beside note.md", looks_like_conflict_copy("note (2).md", with_original), True)
    check("Chapter 2.md standing alone",
          looks_like_conflict_copy("Chapter 2.md", {"Chapter 2.md"}), False)
    check("ordinary name", looks_like_conflict_copy("the-dislike-button.md", set()), False)
    check("digit in real title", looks_like_conflict_copy("10-reasons.md", set()), False)

    print("front matter")
    check("unterminated", parse_front_matter("---\ntitle: x\n"), None)
    check("absent", parse_front_matter("just prose\n"), None)
    parsed = parse_front_matter("---\ntitle: X\npublish: true\n---\n\nbody\n")
    check("parsed fm", parsed[0], {"title": "X", "publish": "true"})
    check("parsed body", parsed[1], "body")

    print("wikilink reject")
    check("plain link", bool(WIKILINK.search("see [[Private Note]]")), True)
    check("embed", bool(WIKILINK.search("![[Daily#x]]")), True)
    check("markdown link ok", bool(WIKILINK.search("[text](https://x)")), False)

    print("slug validation")
    check("good", bool(SLUG_OK.match("a-good-slug")), True)
    check("trailing hyphen", bool(SLUG_OK.match("bad-")), False)
    check("underscore", bool(SLUG_OK.match("bad_slug")), False)

    print("src rendering")
    cand = Candidate(Path("x.md"), "s", "T", "2026", "E", "body text")
    check("round trip", _order_of(cand.src_text(7)), 7)
    check("optional lines dropped",
          Candidate(Path("x.md"), "s", "T", "", "", "b").src_text(0),
          "---\ntitle: T\norder: 0\n---\n\nb\n")

    print("\nSELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="scan and check, write nothing")
    ap.add_argument("--status", action="store_true", help="print what it thinks is live")
    ap.add_argument("--selftest", action="store_true", help="pure logic checks, offline")
    args = ap.parse_args()

    if args.selftest:
        return cmd_selftest()
    if args.status:
        return cmd_status()

    rotate_log()
    if not acquire_lock():
        return 0
    try:
        return tick(dry_run=args.dry_run)
    except Exception as exc:  # noqa: BLE001 - a crash must be visible, not silent
        log(f"CRASH {type(exc).__name__}: {exc}")
        notify("ajin.im — publisher crashed", f"{type(exc).__name__}: {exc}")
        return 1
    finally:
        release_lock()


if __name__ == "__main__":
    sys.exit(main())
