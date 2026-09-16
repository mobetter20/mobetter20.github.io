# writes-publisher

Write in Obsidian, mark it, it lands on <https://ajin.im/writes>.

    ~/Documents/Ajin/Writing/publish/<anything>.md   ->   ajin.im/writes/<slug>/

The owner-facing contract lives in that folder's own `_README.md`, so it reads in
Obsidian next to the writing. This file is the operator's side.

## How a piece becomes a page

1. A markdown file in the drop folder carries `title:` and `publish: true`.
2. The watcher waits until you have stopped editing — 3 minutes of stillness, then
   the same content across two ticks at least 5 minutes apart. Typical time from
   last keystroke to live page is **5–10 minutes**, not seconds. That delay is the
   feature: it is what stops a half-written sentence reaching a public URL.
3. It writes `is/writing/essays/_src/<slug>.md`, assigning `order = max + 1`.
   Existing essays are never renumbered, so a publish touches exactly one file.
4. It runs `publish.sh` (all builds, link check, sitemap, commit, rebase, push).
5. It **proves** the result from git before telling you anything. Then a banner
   with the live URL.

## Why it refuses so much

It pushes to a public site with nobody reviewing, out of a vault that contains
private writing. Every guard below exists because of a specific way this could
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
| hand-edit detect | You edited `_src/<slug>.md` in the repo; the next vault save would silently discard it. |
| slug collision | Two drop files claiming one URL, or overwriting an essay this tool did not publish. |

Refusals notify **once per distinct problem**, not once per tick. A tool that
banners every 5 minutes gets muted, and a muted tool is an abandoned tool.

On any failure the staged `_src` changes are reverted, state is left untouched, and
the next tick retries. Nothing half-published survives a failed run.

## Install (once)

```sh
mkdir -p ~/.local/share/writes-publisher ~/.local/bin
cp _scripts/writes_publisher/publish_watcher.py ~/.local/bin/writes_publish_watcher.py
chmod +x ~/.local/bin/writes_publish_watcher.py
cp _scripts/writes_publisher/com.ajin.writes-publisher.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.ajin.writes-publisher.plist
```

The repo copy is the source; the runtime copy is `~/.local/bin`. After editing here:
re-copy, then `launchctl kickstart -k gui/$(id -u)/com.ajin.writes-publisher`.

## Operate

```sh
writes_publish_watcher.py --selftest   # pure logic, offline, no git
writes_publish_watcher.py --status     # what it believes is live / held / refused
writes_publish_watcher.py --dry-run    # full scan + guards, writes nothing
tail -40 ~/.local/share/writes-publisher/publisher.log
launchctl bootout gui/$(id -u)/com.ajin.writes-publisher    # kill switch
```

State: `~/.local/share/writes-publisher/state.json` (slug -> source, hashes, URL).
Safe to delete — the next run re-adopts anything whose `_src` file still matches its
drop file, rather than refusing forever.

## Unpublish

**Deliberately not automated.** Deleting the vault file does nothing; removing
`publish: true` does nothing. A public URL is cached and indexed, so retraction is a
decision, not a side effect of a file operation.

To retract:

```sh
rm is/writing/essays/_src/<slug>.md
rm -rf writes/<slug> wrote/<slug>
./publish.sh --message "Retract <slug>"
```

Then remove the slug from `state.json`, or delete the drop-folder file first so the
watcher does not simply publish it again on the next tick.

## Known gap

If the LaunchAgent is unloaded, nothing notices — there is no second daemon
watching this one. `RunAtLoad` + `StartInterval` mean launchd restarts it after a
crash or reboot, so the realistic way to end up dark is booting it out by hand. If
you published something and no banner arrived within ~15 minutes, run `--status`.
