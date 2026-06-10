# canary watcher

Automation behind <https://ajin.im/is/building/did-claude-just-reset-usage/>.

Every 30 minutes a LaunchAgent polls Claude's official usage meter
(`api.anthropic.com/api/oauth/usage`, token read from the macOS Keychain
item `Claude Code-credentials`), appends the reading to a local history
log, and decides:

- **reset candidate** — seven_day utilization dropped >10pp while
  `resets_at` stayed put (or moved >1h early = re-anchor). Held one tick,
  then **confirmed by the next poll** before publishing (single-poll
  flickers get discarded). On confirmation it rewrites the page's
  `state.json` on master via a `gh api` content PUT: new `last_reset`,
  a prepended `resets[]` entry, fresh `canary_now`.
- **normal weekly roll** — `resets_at` advanced at expiry. Ignored.
- **heartbeat** — if nothing happened for 24h, push fresh
  `last_polled_utc` + `canary_now` so the page's staleness banner stays
  quiet. GH Pages redeploys in ~40s either way.

## The page's state.json is machine-written

`is/building/did-claude-just-reset-usage/state.json` carries a `_note`
field saying so. Hand edits land fine but may be overwritten within 30
minutes; for durable hand edits (e.g. filling in `suspected_trigger` or
flipping `announced` after Anthropic posts), edit the LIVE file and the
watcher will preserve those fields — it only touches the fields named
above. The `index.html` next to it is hand-maintained as usual.

## Install (once)

```sh
mkdir -p ~/.local/share/canary ~/.local/bin
cp _scripts/canary/canary_watcher.py ~/.local/bin/canary_watcher.py
chmod +x ~/.local/bin/canary_watcher.py
cp _scripts/canary/com.ajin.canary-watcher.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.ajin.canary-watcher.plist
```

The repo copy is the source; the runtime copy is `~/.local/bin`.
After editing here: re-copy + `launchctl kickstart -k
gui/$(id -u)/com.ajin.canary-watcher`.

## Operate

```sh
python3 ~/.local/bin/canary_watcher.py --selftest    # detection logic, offline
python3 ~/.local/bin/canary_watcher.py --dry-run     # poll + decide, no push
tail -20 ~/.local/share/canary/watcher.log           # what launchd did
launchctl bootout gui/$(id -u)/com.ajin.canary-watcher   # kill switch
```

Failure modes: if the Mac is asleep or the job dies, the page itself
says so ("the canary has been asleep since …" after 36h stale) — the
live page is the watchdog. `gh` auth expiry or a content-PUT conflict
logs and retries on the next tick; nothing is lost (history is local,
append-only).
