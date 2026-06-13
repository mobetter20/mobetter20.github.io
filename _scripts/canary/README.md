# canary watcher

Automation behind <https://ajin.im/is/building/did-claude-just-reset-usage/>.

Every 30 minutes a LaunchAgent reads Claude's usage from cfo's
`~/.local/share/cfo/state.json` (cfo extracts the meter from the CodexBar
menubar snapshot on its own 30-min LaunchAgent). Reading cfo's file means
this watcher carries no OAuth token of its own, and sidesteps the macOS TCC
block that stops a launchd job from reading CodexBar's Group Container
directly. It appends the reading to a local history log, and decides:

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

The page defines **"just" as a reset detected within the past 48 hours**.
That public definition and the verdict cutoff share the `data-hours`
value on `#definition` in the page's `index.html`.

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
