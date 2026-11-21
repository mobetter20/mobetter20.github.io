# writes-publisher

Approved Markdown release exports are pushed for publication at `https://ajin.im/writes/<slug>/`. Private manuscripts remain in the everyday Obsidian vault. See [PUBLISHING.md](../../PUBLISHING.md) for the owner-facing workflow.

    ~/Documents/Ajin-Publishing/<anything>.md   ->   ajin.im/writes/<slug>/

The release-folder contract is tracked in [RELEASE-README.md](RELEASE-README.md)
and installed as that folder's `_README.md`. Keep the two copies identical. The
external folder is not nested or symlinked into the everyday Obsidian vault.
This file is the operator's side.

## How a piece becomes a page

1. A markdown file in the drop folder carries `title:` and `publish: true`.
   Optional `date:` accepts `YYYY`, `YYYY-MM`, or `YYYY-MM-DD`. Use the full
   publication date when known; the Atom feed retains it. Partial dates use
   the first day of the known period, and invalid calendar dates fail the build.
2. The watcher waits until you have stopped editing — 3 minutes of stillness, then
   the same content across two ticks at least 5 minutes apart. Typical time from
   last keystroke to push is usually **5 to 10 minutes**. That delay is the
   feature: it is what stops a half-written sentence reaching a public URL.
3. It writes `is/writing/essays/_src/<slug>.md`, assigning `order = max + 1`.
   Existing essays are never renumbered, so a publish touches exactly one file.
4. It runs `publish.sh` (all builds, link check, sitemap, commit, rebase, push).
5. It proves the source, generated reader and exact unified-Writing archive link are still present at the fetched remote tip. It reports **pushed; deployment pending**, with the expected URL. It does not wait for a successful Pages deployment or compare public bytes. Use the deployed-commit live verifier for that proof; do not describe a push notice as verified publication.

## Why it refuses so much

It pushes to a public site with nobody reviewing, from an approved-release folder; private writing remains in the everyday
vault. Every guard below exists because of a specific way this could
put the wrong words on the internet or lie to you about having published.

| Guard | The failure it stops |
|---|---|
| `publish: true` required | Everything else in the vault is invisible to it. Absence is the safe default. |
| two-tick stability | You typed `publish: true`, then wandered off mid-sentence. |
| mtime debounce | Obsidian autosaving while you type. |
| `[[wikilink]]` reject | They publish as raw text and can expose private note titles. |
| conflict-copy skip | Sync forks (`foo 1.md`, `conflicted copy`) republishing stale text. A numbered name only counts as a conflict when the original is beside it, so `Chapter 2.md` is safe. |
| branch assert | Repo parked on a topic branch: the push succeeds and the site never changes. |
| clean-tree assert | `publish.sh` runs `git add -A`, so unrelated work in progress would be committed and pushed. |
| nothing-unpushed assert | A commit you deliberately kept local would ride out to the public site. |
| post-publish verify | **`publish.sh` exits 0 when it pushed nothing.** Without this the tool banners "it's live" for a page that 404s, and the commit sits local forever. |
| hand-edit detect | You edited `_src/<slug>.md` in the repo; the next release save would silently discard it. |
| slug collision | Two drop files claiming one URL, or overwriting an essay this tool did not publish. |
| OS file lock | Two publisher processes entering the same tick, including a run that takes longer than 900 seconds. |

Slug collisions are removed before both state reconciliation and readiness. All
colliding files are held, their pending timers are cleared, and no matching local
source is adopted. Once resolved, the stability window starts again.

Refusals notify **once per distinct problem**, not once per tick. A tool that
banners every 5 minutes gets muted, and a muted tool is an abandoned tool.

On failure, the watcher tries to revert uncommitted outputs from its attempt and
records the problem. A commit may already have been pushed when a later check
fails, so the outcome is **unconfirmed**, not "nothing is live." Inspect Git,
state and Pages before a manual retry. Never remove state as a general repair.

## Install (once)

```sh
mkdir -p ~/.local/share/writes-publisher ~/.local/bin
cp _scripts/writes_publisher/publish_watcher.py ~/.local/bin/writes_publish_watcher.py
chmod +x ~/.local/bin/writes_publish_watcher.py
cp _scripts/writes_publisher/RELEASE-README.md ~/Documents/Ajin-Publishing/_README.md
cp _scripts/writes_publisher/com.ajin.writes-publisher.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.ajin.writes-publisher.plist
```

The repo copy is the source; the runtime copy is `~/.local/bin`. For an existing
installation, use the maintenance sequence below. Do not kill and replace a
running publisher just to pick up a source edit.

When changing publication proof, update the installed runtime to the reviewed
verifier before releasing the maintenance hold. Verify its content hash against
the committed source and run the offline checks before resuming the job.

## Operate

```sh
writes_publish_watcher.py --selftest   # pure logic, offline, no git
writes_publish_watcher.py --status     # pushed records, held/refused releases and OS lock activity
writes_publish_watcher.py --dry-run    # scan with live Git guards; can fetch/rebase/push stranded commits
tail -40 ~/.local/share/writes-publisher/publisher.log
launchctl bootout gui/$(id -u)/com.ajin.writes-publisher    # kill switch
```

State: `~/.local/share/writes-publisher/state.json` (slug -> source, hashes, URL).
The internal `published` key is retained for compatibility; it records Git-push
proof, not live deployment. Preserve the file. If state is lost, reconciliation
adopts a matching release only after proving its source, reader and archive link
are still present at the fetched remote tip. An older local commit alone is not
enough. Independently edited sources still require review.

`lock.json` persists after the process exits. Its PID/time fields are diagnostic;
file existence or an old timestamp does not establish activity. `--status` probes
the OS lock without changing the file. An active process holds one open descriptor
through the complete tick; no age-based lock stealing or unlinking is allowed.

## Unpublish

**Deliberately not automated.** Deleting the release export does nothing; removing
`publish: true` does nothing. A public URL is cached and indexed, so retraction is a
decision, not a side effect of a file operation.

To retract, first confirm whether Ajin means unlist or retire the direct URL.
Hold and drain the watcher, then remove the approved release export from its
watched input or set `publish: false` so it cannot republish. Preserve a private
backup outside the release folder. Trace any curated placement, feed, archive,
compatibility redirect and sitemap reference before changing the owning source.

Retire the source and its intended generated readers in a review worktree,
regenerate, check and publish through the reviewed PR route. Verify the requested
public behavior and absence from discovery. Reconcile only that slug's runtime
state while the hold remains, and release the hold after confirming there is no
eligible automatic input. Do not remove only generated HTML or run `publish.sh`
from a preview branch.

## Interpreter

The LaunchAgent runs `/opt/homebrew/bin/python3.13`, which has Full Disk Access.
`/usr/bin/python3` does not: under launchd it reads `~/Documents/Ajin-Publishing` as empty,
so nothing ever publishes and the log just says `0 marked file(s)`. If that line appears
while a release with `publish: true` is in the folder, check the interpreter first.

## Known gap

If the LaunchAgent is unloaded, nothing notices — there is no second daemon
watching this one. `RunAtLoad` + `StartInterval` mean launchd restarts it after a
crash or reboot, so the realistic way to end up dark is booting it out by hand. If
you published something and no banner arrived within ~15 minutes, run `--status`.

## Maintenance gate

The nonexpiring `~/.local/share/writes-publisher/maintenance` marker pauses every
CLI mode before logging, locking, state access or Git. Any directory entry,
including a dangling symlink, pauses successfully; inspection errors fail closed
with exit 75. Only confirmed absence permits normal operation.

Hold the marker before installing a reviewed gated runtime. Let already-loaded
old code finish naturally, freeze all manual publisher entrypoints and site work,
and verify both publisher entrypoints and orphaned repository processes have
drained before unregistering the job or moving release files. Idle launchd or
an absent JSON lock alone does not establish drain. Keep backups outside both
release roots. Reload with the marker still held, verify unchanged candidate and
site-source identities, then remove only the operator-owned marker. Do not replay
a stale state backup after any intervening publication.

Install the committed runtime atomically using a temporary file in `~/.local/bin`,
preserving its executable mode, and compare its SHA-256 with the repository source.
Reload the LaunchAgent while the marker is still held; do not change its interpreter
or timing. Confirm the held invocation changes no state or site files, then remove
only the marker owned by this maintenance operation. Run the offline self-test and
read-only status, and observe one naturally scheduled tick: fresh `last_run`, exit
0, expected pushed records, no new errors/pending releases, and unchanged approved
input/source hashes. An ordinary idle tick is sufficient when no new release is
queued. Record that evidence in the release PR.

For migration from the old JSON-only lock, an acquirable OS lock is not proof that
old code drained. Check both known watcher entrypoints and their repository child
processes as well as launchd and the old PID record before replacing it.

Production `--dry-run` is not a maintenance test: its live Git guards can fetch,
rebase and push stranded essay commits. Use isolated fixtures with subprocess
and network effects prohibited for offline verification.
