#!/usr/bin/env python3
"""Daily-bank review board (owner ask 2026-06-12: "how many would be
banked? i would like to check all").

The daily has no stored bank: each day's question derives from the date
hash (stat, form, contestants). This board enumerates the COMPLETE
question space the D30 rules can produce, plus the literal next-120-day
schedule, so the owner can review every question.

Fidelity: values and display strings are read from the built page's
#mm-data JSON island (the exact data app.js uses), and the hash /
selection logic below mirrors app.js line for line. A 30-day parity check
against the real JS (run via the preview) accompanies the build; see the
session record.

Usage:
    python3 _scripts/world_metros/mocks/build_daily_bank_board.py
"""

import datetime
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PAGE = os.path.join(REPO, "is", "building", "world-metros", "index.html")

DUEL_Q = {
    "opened": "Which opened earlier?",
    "stations": "Which has more stations?",
    "span": "Which reaches further?",
    "density": "Which packs stations tighter?",
    "routekm": "Which reports more route-km?",
    "ridership": "Which carries more riders a year?",
}
PICK_Q = {
    "opened": "When did %C% open?",
    "stations": "How many stations does %C% have?",
    "span": "How far apart are %C%'s furthest stations?",
    "density": "How many stations per square km does %C% pack?",
    "routekm": "How many route-km does %C% report?",
    "ridership": "How many rides a year does %C% report?",
}


def load_island():
    html = open(PAGE).read()
    m = re.search(r'<script id="mm-data" type="application/json">(.*?)</script>',
                  html, re.S)
    return json.loads(m.group(1))


def js_hash(s):
    # mirrors app.js hashStr incl. the avalanche finalizer
    h = 0
    for ch in s:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    h ^= h >> 16
    h = (h * 0x45D9F3B) & 0xFFFFFFFF
    h ^= h >> 16
    h = (h * 0x45D9F3B) & 0xFFFFFFFF
    h ^= h >> 16
    return h


def is_close(stat, a, b):
    if a == b:
        return False
    if stat == "opened":
        return abs(a - b) <= 12
    return max(a, b) / min(a, b) <= 1.3


def better(data, stat, x, y):
    low = data["stats"][stat]["win"] == "low"
    vx = data["cities"][x]["values"][stat]
    vy = data["cities"][y]["values"][stat]
    return x if ((vx < vy) if low else (vx > vy)) else y


def close_pairs(data, stat):
    out = []
    for x, y in data["pairs"]:
        if is_close(stat, data["cities"][x]["values"][stat],
                    data["cities"][y]["values"][stat]):
            out.append([x, y])
    return out


def pick_options(data, stat, city):
    truth = data["cities"][city]["values"][stat]
    others = []
    for c in data["live"]:
        v = data["cities"][c]["values"][stat]
        if v != truth and v not in others:
            others.append(v)
    others.sort(key=lambda v: abs(v - truth))
    return truth, others[:3]


def challenge(data, date_str):
    h = js_hash(date_str)
    stat = data["statOrder"][h % len(data["statOrder"])]
    if (h // 11) % 2 == 0:
        pool = close_pairs(data, stat)
        if pool:
            pair = list(pool[(h // 7) % len(pool)])
            if (h // 53) % 2:
                pair.reverse()
            return {"mode": "duel", "stat": stat, "pair": pair}
    city = data["live"][(h // 13) % len(data["live"])]
    truth, distractors = pick_options(data, stat, city)
    values = distractors[:]
    values.insert((h // 29) % 4, truth)
    return {"mode": "pick", "stat": stat, "city": city,
            "values": values, "truth": truth}


def disp_for(data, stat, value):
    for c in data["live"]:
        if data["cities"][c]["values"][stat] == value:
            return data["cities"][c]["disp"][stat]
    return str(value)


def name(data, c):
    return data["cities"][c]["name"].upper()


def main():
    data = load_island()
    stats = data["statOrder"]

    # schedule: the next 120 days, literally
    rows = []
    start = datetime.date(2026, 6, 12)
    for i in range(120):
        ds = (start + datetime.timedelta(days=i)).isoformat()
        ch = challenge(data, ds)
        if ch["mode"] == "duel":
            a, b = ch["pair"]
            w = better(data, ch["stat"], a, b)
            q = DUEL_Q[ch["stat"]]
            body = (f'{name(data, a)} ({data["cities"][a]["disp"][ch["stat"]]}) vs '
                    f'{name(data, b)} ({data["cities"][b]["disp"][ch["stat"]]})')
            ans = name(data, w)
        else:
            q = PICK_Q[ch["stat"]].replace("%C%", name(data, ch["city"]))
            body = " / ".join(disp_for(data, ch["stat"], v) for v in ch["values"])
            ans = disp_for(data, ch["stat"], ch["truth"])
        rows.append(f'<tr><td>{ds}</td><td>{ch["mode"]}</td><td>{ch["stat"]}</td>'
                    f'<td>{q}</td><td>{body}</td><td>{ans}</td></tr>')
    schedule = "".join(rows)

    # duel bank: every eligible close pair, per stat
    duel_sections = []
    duel_total = 0
    for stat in stats:
        pool = close_pairs(data, stat)
        duel_total += len(pool)
        rws = []
        for a, b in pool:
            w = better(data, stat, a, b)
            rws.append(
                f'<tr><td>{name(data, a)}</td><td>{data["cities"][a]["disp"][stat]}</td>'
                f'<td>{name(data, b)}</td><td>{data["cities"][b]["disp"][stat]}</td>'
                f'<td>{name(data, w)}</td></tr>')
        duel_sections.append(
            f'<details><summary>{stat} · {len(pool)} close pairs</summary>'
            f'<table><tr><th>a</th><th>value</th><th>b</th><th>value</th>'
            f'<th>wins</th></tr>{"".join(rws)}</table></details>')

    # pick bank: one fixed option set per city per stat
    pick_sections = []
    for stat in stats:
        rws = []
        for c in data["live"]:
            truth, distractors = pick_options(data, stat, c)
            opts = " · ".join(disp_for(data, stat, v) for v in distractors)
            rws.append(f'<tr><td>{name(data, c)}</td>'
                       f'<td><b>{disp_for(data, stat, truth)}</b></td>'
                       f'<td>{opts}</td></tr>')
        pick_sections.append(
            f'<details><summary>{stat} · 18 questions</summary>'
            f'<table><tr><th>city</th><th>truth</th>'
            f'<th>the three distractors (other cities&rsquo; real values)</th></tr>'
            f'{"".join(rws)}</table></details>')
    pick_total = len(stats) * len(data["live"])

    html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Metro Match · daily bank board (D30 review)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/is/building/world-metros/style.css">
<style>
  body {{ padding: 0 22px 60px; }}
  .bb {{ max-width: 880px; margin: 26px auto; }}
  .bb h1 {{ font-size: 16px; font-weight: 800; letter-spacing: .22em; color: var(--text); }}
  .bb h1 em {{ font-style: normal; color: var(--lblue); }}
  .bb h2 {{ font-family: var(--mono); font-size: 12px; letter-spacing: .16em;
           color: var(--lblue); text-transform: uppercase; margin: 34px 0 8px; }}
  .bb p {{ font-size: 13px; color: var(--soft); line-height: 1.65; margin: 8px 0; max-width: 760px; }}
  .bb b {{ color: var(--body); }}
  .bb table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
  .bb th {{ font-family: var(--mono); font-size: 9px; letter-spacing: .12em; color: var(--grey);
           text-transform: uppercase; text-align: left; padding: 6px 10px 6px 0;
           border-bottom: 1px solid var(--edge); }}
  .bb td {{ padding: 7px 10px 7px 0; border-bottom: 1px solid #1d1d23; color: var(--soft);
           font-size: 12px; line-height: 1.5; vertical-align: top; }}
  .bb td b {{ color: var(--goodtext); font-weight: 600; }}
  .bb details {{ margin: 10px 0; }}
  .bb summary {{ font-family: var(--mono); font-size: 11px; letter-spacing: .1em;
                color: var(--grey); cursor: pointer; text-transform: uppercase; padding: 5px 0; }}
  .bb summary:hover {{ color: var(--body); }}
</style>
</head><body>
<div class="bb">
  <h1>METRO <em>MATCH</em> · DAILY BANK BOARD</h1>
  <p><b>How the daily works:</b> there is no stored question list. Each
  day the date string hashes to a number; the hash picks the stat (six-way
  rotation), the form (roughly half head-to-head, half pick-the-number)
  and the contestants. So the bank is the full space the rules can
  produce, enumerated below for review.</p>
  <p><b>The space:</b> {duel_total} eligible duels (close pairs only:
  values within 30 percent, or 12 years for opened, never equal) plus
  {pick_total} pick questions (18 cities by 6 stats; the wrong three
  options are always other cities&rsquo; real values nearest the truth).
  {duel_total + pick_total} distinct questions in all. The hash walks
  this space unevenly (some questions recur before others appear), so the
  first table shows the literal next 120 days as visitors will get them.</p>

  <h2>The next 120 days, as they will fire</h2>
  <table><tr><th>date</th><th>form</th><th>stat</th><th>question</th>
  <th>shown</th><th>answer</th></tr>{schedule}</table>

  <h2>Duel bank · every eligible close pair ({duel_total})</h2>
  {"".join(duel_sections)}

  <h2>Pick bank · every city-stat question ({pick_total})</h2>
  <p>Truth in green; the three distractors shown beside it.</p>
  {"".join(pick_sections)}
</div>
</body></html>
"""
    out = os.path.join(HERE, "daily-bank-board.html")
    with open(out, "w") as fh:
        fh.write(html)
    print(f"wrote {out} ({os.path.getsize(out) / 1024:.0f} KB); "
          f"duels {duel_total} + picks {pick_total} = {duel_total + pick_total}")


if __name__ == "__main__":
    main()
