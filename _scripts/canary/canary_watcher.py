#!/usr/bin/env python3
"""canary watcher: reads Claude's usage from cfo's state.json (which extracts
it from the CodexBar menubar snapshot), detects quiet quota resets, and
publishes state.json for
https://ajin.im/is/building/did-claude-just-reset-usage/

Runs every 30 min via LaunchAgent (com.ajin.canary-watcher); see
_scripts/canary/README.md for install/uninstall. The runtime copy lives
at ~/.local/bin/canary_watcher.py — edit here, then re-copy.

Publishing goes through `gh api` content PUTs against master (the live
file is the source of truth; no local checkout is touched). The page's
state.json is therefore MACHINE-UPDATED — hand edits to it may be
overwritten within 30 minutes.

Detection (mirrors the page's "signatures" section):
  reset      seven_day utilization drops >10pp vs the previous poll
             while resets_at stays put (tolerance 120s)
  re-anchor  same drop, but resets_at moved >1h before the old window's
             natural end
  roll       resets_at advances at expiry — not published
  flicker    a candidate must be CONFIRMED by the next poll before
             anything publishes (single weird readings are discarded)

Local state under ~/.local/share/canary/:
  usage-history.jsonl  every poll, append-only
  publisher.json       last push + pending candidate
"""
from __future__ import annotations

import base64
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = "mobetter20/mobetter20.github.io"
PAGE_PATH = "is/building/did-claude-just-reset-usage/state.json"
GH = "/opt/homebrew/bin/gh"

DATA_DIR = Path("~/.local/share/canary").expanduser()
HISTORY = DATA_DIR / "usage-history.jsonl"
PUBSTATE = DATA_DIR / "publisher.json"
CFO_STATE = Path("~/.local/share/cfo/state.json").expanduser()

DROP_PP = 10.0          # utilization drop that counts as a candidate
WINDOW_TOL_S = 120      # resets_at jitter tolerance (server emits ~1s noise)
REANCHOR_MIN_S = 3600   # resets_at moved >1h early => re-anchor, not roll
CONFIRM_TOL_PP = 15.0   # next poll must still be near the dropped value
HEARTBEAT_H = 24        # freshness push cadence when nothing happens


def now_utc():
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_ts(s):
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)


def log(msg):
    print("%s %s" % (iso(now_utc()), msg), flush=True)


# ── poll ────────────────────────────────────────────────────────────────

def poll():
    """Read Claude usage from cfo's state.json.

    cfo extracts the meter from CodexBar's menubar
    snapshot every 30 min and writes it under ~/.local/share — a path this
    background agent can read. CodexBar's own Group Container cannot be read
    from a launchd job (macOS TCC: "Operation not permitted"), and cfo already
    holds the access to do the extraction. Neither path needs an OAuth token of
    our own; the prior api.anthropic.com poll 401'd whenever its Keychain
    access token expired during an idle stretch.
    """
    st = json.loads(CFO_STATE.read_text())
    claude = st["providers"]["claude"]
    wk = claude["weekly"]       # 7-day window
    sess = claude["session"]    # 5-hour window
    t = st.get("meta", {}).get("codexbar_generated_at") or st["computed_at"]
    return {
        "t": t,
        "u7": float(wk["used_pct"]),
        "r7": wk["resets_at"],
        "u5": float(sess["used_pct"]),
    }


# ── local state ─────────────────────────────────────────────────────────

def last_history_line():
    if not HISTORY.is_file():
        return None
    line = None
    with HISTORY.open() as f:
        for line in f:
            pass
    return json.loads(line) if line else None


def append_history(entry):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with HISTORY.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def load_pubstate():
    if PUBSTATE.is_file():
        return json.loads(PUBSTATE.read_text())
    return {}


def save_pubstate(st):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PUBSTATE.write_text(json.dumps(st, indent=2))


# ── detection ───────────────────────────────────────────────────────────

def classify(prev, cur):
    """Return None or a candidate dict for a prev->cur transition."""
    if prev is None:
        return None
    drop = prev["u7"] - cur["u7"]
    if drop <= DROP_PP:
        return None
    old_end = parse_ts(prev["r7"])
    new_end = parse_ts(cur["r7"])
    cur_t = parse_ts(cur["t"])
    if abs((new_end - old_end).total_seconds()) <= WINDOW_TOL_S:
        window = "unchanged"
    elif (old_end - cur_t).total_seconds() > REANCHOR_MIN_S:
        window = "re-anchored"
    else:
        return None  # normal weekly roll
    return {
        "prev_t": prev["t"], "t": cur["t"],
        "from_pct": prev["u7"], "to_pct": cur["u7"],
        "r7": cur["r7"], "window": window,
    }


def confirm(pending, cur):
    """Next poll validates a pending candidate (filters flickers)."""
    if cur["u7"] > pending["to_pct"] + CONFIRM_TOL_PP:
        return False
    if pending["window"] == "unchanged":
        return abs((parse_ts(cur["r7"]) - parse_ts(pending["r7"])).total_seconds()) <= WINDOW_TOL_S
    return True


# ── publish ─────────────────────────────────────────────────────────────

def gh_api(args, payload=None):
    cmd = [GH, "api"] + args
    inp = None
    if payload is not None:
        cmd += ["--input", "-"]
        inp = json.dumps(payload)
    r = subprocess.run(cmd, capture_output=True, text=True, input=inp, timeout=60)
    if r.returncode != 0:
        raise RuntimeError("gh api %s failed: %s" % (args[0], r.stderr.strip()[:300]))
    return json.loads(r.stdout)


def fetch_live_state():
    d = gh_api(["repos/%s/contents/%s" % (REPO, PAGE_PATH)])
    return json.loads(base64.b64decode(d["content"]).decode()), d["sha"]


def put_live_state(state, sha, message):
    body = json.dumps(state, indent=2, ensure_ascii=False) + "\n"
    gh_api(
        ["-X", "PUT", "repos/%s/contents/%s" % (REPO, PAGE_PATH)],
        payload={
            "message": message,
            "content": base64.b64encode(body.encode()).decode(),
            "sha": sha,
        },
    )


def bracket(prev_iso, cur_iso):
    p, c = parse_ts(prev_iso), parse_ts(cur_iso)
    return "between %02d:%02d and %02d:%02d UTC, %s %d" % (
        p.hour, p.minute, c.hour, c.minute, c.strftime("%b"), c.day)


def publish(cur, reset=None, dry=False):
    state, sha = fetch_live_state()
    state["last_polled_utc"] = cur["t"]
    state["canary_now"] = {
        "seven_day_used_pct": cur["u7"],
        "seven_day_resets_at": cur["r7"],
    }
    if reset:
        detected = parse_ts(reset["t"])
        state["last_reset"] = {
            "detected_utc": reset["t"],
            "bracket": bracket(reset["prev_t"], reset["t"]),
            "from_pct": round(reset["from_pct"]),
            "to_pct": round(reset["to_pct"]),
            "window": reset["window"],
            "announced": False,
            "suspected_trigger": None,
        }
        state.setdefault("resets", []).insert(0, {
            "date": detected.strftime("%Y-%m-%d"),
            "counter": "%d%% → %d%%" % (round(reset["from_pct"]), round(reset["to_pct"])),
            "window": reset["window"],
            "announced": "no",
            "note": "auto-detected by the canary",
        })
        msg = "canary: reset detected %s (%d%% → %d%%)" % (
            reset["t"], round(reset["from_pct"]), round(reset["to_pct"]))
    else:
        msg = "canary: heartbeat %s" % cur["t"]
    if dry:
        log("DRY would publish: %s" % msg)
        return
    put_live_state(state, sha, msg)
    log("published: %s" % msg)


# ── selftest ────────────────────────────────────────────────────────────

def selftest():
    a = {"t": "2026-06-09T21:30:00Z", "u7": 77.0, "r7": "2026-06-11T22:59:59+00:00", "u5": 1}
    b = {"t": "2026-06-09T22:13:00Z", "u7": 0.0, "r7": "2026-06-11T23:00:00+00:00", "u5": 1}
    c = {"t": "2026-06-09T22:43:00Z", "u7": 2.0, "r7": "2026-06-11T23:00:00+00:00", "u5": 1}
    roll_prev = {"t": "2026-06-11T22:45:00Z", "u7": 90.0, "r7": "2026-06-11T23:00:00+00:00", "u5": 1}
    roll_cur = {"t": "2026-06-11T23:15:00Z", "u7": 1.0, "r7": "2026-06-18T23:00:00+00:00", "u5": 1}
    rean_cur = {"t": "2026-05-28T19:06:00Z", "u7": 0.0, "r7": "2026-05-28T22:59:59+00:00", "u5": 1}
    rean_prev = {"t": "2026-05-28T10:40:00Z", "u7": 37.0, "r7": "2026-06-01T07:00:00+00:00", "u5": 1}
    flicker = {"t": "2026-06-09T22:43:00Z", "u7": 75.0, "r7": "2026-06-11T23:00:00+00:00", "u5": 1}

    cand = classify(a, b)
    assert cand and cand["window"] == "unchanged", "reset not classified"
    assert confirm(cand, c), "genuine reset not confirmed"
    assert not confirm(cand, flicker), "flicker wrongly confirmed"
    assert classify(roll_prev, roll_cur) is None, "weekly roll misclassified"
    rc = classify(rean_prev, rean_cur)
    assert rc and rc["window"] == "re-anchored", "re-anchor not classified"
    assert classify(b, c) is None, "small accrual misclassified"
    assert bracket(a["t"], b["t"]) == "between 21:30 and 22:13 UTC, Jun 9", "bracket format"
    print("selftest: PASS")


# ── main ────────────────────────────────────────────────────────────────

def main():
    args = set(sys.argv[1:])
    if "--selftest" in args:
        selftest()
        return 0
    dry = "--dry-run" in args

    cur = poll()
    prev = last_history_line()
    if prev and prev["t"] == cur["t"]:
        log("no new CodexBar reading (updatedAt=%s); skipping tick" % cur["t"])
        return 0
    append_history(cur)
    pub = load_pubstate()

    pending = pub.get("pending")
    if pending:
        if confirm(pending, cur):
            log("pending reset CONFIRMED (%s%% -> %s%%)" % (pending["from_pct"], pending["to_pct"]))
            try:
                publish(cur, reset=pending, dry=dry)
                if not dry:
                    pub["pending"] = None
                    pub["last_push_utc"] = cur["t"]
            except Exception as e:  # keep pending; retry next tick
                log("publish failed, retrying next tick: %s" % e)
        else:
            log("pending candidate discarded as flicker")
            pub["pending"] = None
        save_pubstate(pub)
        return 0

    cand = classify(prev, cur)
    if cand:
        log("reset candidate (%s%% -> %s%%, window %s); awaiting confirmation"
            % (cand["from_pct"], cand["to_pct"], cand["window"]))
        pub["pending"] = cand
        save_pubstate(pub)
        return 0

    last_push = pub.get("last_push_utc")
    due = (last_push is None or
           (now_utc() - parse_ts(last_push)).total_seconds() > HEARTBEAT_H * 3600)
    if due or "--force-heartbeat" in args:
        try:
            publish(cur, dry=dry)
            if not dry:
                pub["last_push_utc"] = cur["t"]
                save_pubstate(pub)
        except Exception as e:
            log("heartbeat publish failed: %s" % e)
    else:
        log("ok: u7=%s%% window=%s (no action)" % (cur["u7"], cur["r7"][:16]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
