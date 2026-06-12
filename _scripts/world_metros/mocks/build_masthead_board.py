#!/usr/bin/env python3
"""Masthead + wordmark-hover board (owner flags on D35, 2026-06-12:
"masthead center align looks weird, give me solution mocks first" and
"metro match logo only match color change on hover also looks awkward").

Two judged sections, no live changes before the verdict:
  M. masthead alignment: three candidates, each shown as a framed header +
     masthead + a placeholder 3-card row (card outlines, not live cards:
     the question is the block's alignment against the grid edges).
  W. wordmark hover: four live-hoverable treatments.

Usage:
    python3 _scripts/world_metros/mocks/build_masthead_board.py
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))

INTRO = ("Stat cards for the world&rsquo;s great metro systems, every number "
         "dated and sourced. <b>Each card has three faces: scale, character, "
         "the map. Flip to cycle them; pick a stat and beat the cpu; one "
         "guess a day in the daily.</b>")

BAND = ('<span class="mbnd"><i style="background:#f62e36"></i>'
        '<i style="background:#00a23f"></i><i style="background:#0079c2"></i>'
        '<i style="background:#ff9500"></i><i style="background:#9c5e31"></i>'
        '<i style="background:#794698"></i></span>')


def header(wclass="w2"):
    return (f'<div class="mhead"><div class="mframe">'
            f'<span class="mwordmark {wclass}"><a href="#nogo">METRO <em>MATCH</em></a></span>'
            f'<span class="mnav"><b>THE DECK</b><span>THE BATTLE</span>'
            f'<span>THE DAILY</span><span>METHOD</span></span>'
            f'</div></div>')


def cards():
    cs = []
    for n in ("TOKYO", "SEOUL", "SINGAPORE"):
        cs.append(f'<div class="mcard"><div class="mname">{n}</div>'
                  f'<div class="msub">13 lines &middot; Metro + Toei</div>'
                  f'{BAND}<div class="mrow"></div><div class="mrow"></div></div>')
    return '<div class="mgrid">' + "".join(cs) + '</div>'


def m_candidate(key, title, note, intro_class):
    return (f'<section class="cand"><h2>{key} &middot; {title}</h2>'
            f'<p class="note">{note}</p>'
            f'<div class="stage">{header()}'
            f'<div class="mmain"><p class="mintro {intro_class}">{INTRO}</p>'
            f'{cards()}</div></div></section>')


def w_candidate(key, title, note, wclass):
    return (f'<div class="wcand"><h3>{key} &middot; {title}</h3>'
            f'<p class="note">{note}</p>{header(wclass)}</div>')


def main():
    m = "".join([
        m_candidate("M1", "LEFT AT THE FRAME (pre-D35 alignment, framed)",
                    "The masthead returns to left-aligned at the content "
                    "column edge, where the wordmark also sits now. The text "
                    "edge and the card edge still differ: the deck centers "
                    "inside the column.",
                    "i-left"),
        m_candidate("M2", "CENTERED (what is live now, the reference)",
                    "The masthead centers over the centered deck: one axis, "
                    "but centered ragged body text is the thing that reads "
                    "weird.",
                    "i-center"),
        m_candidate("M3", "LEFT AT THE GRID EDGE (recommended)",
                    "Left-aligned text whose block is exactly as wide as the "
                    "deck grid, so the masthead's left edge locks to the "
                    "first card's left edge at every column count. Editorial "
                    "text, deck stays centered, no stray edges.",
                    "i-grid"),
    ])
    w = "".join([
        w_candidate("W1", "WHOLE MARK LIFTS",
                    "Both words go full white on hover; one motion, no "
                    "two-tone flicker.", "w1"),
        w_candidate("W2", "MATCH FLIPS (what is live now, the reference)",
                    "Only the blue MATCH turns white; the flagged awkward "
                    "one.", "w2"),
        w_candidate("W3", "NAV UNDERLINE (recommended)",
                    "Hover draws the same blue underline the active nav tab "
                    "wears: the page's existing link grammar, colours stay "
                    "put.", "w3"),
        w_candidate("W4", "NO HOVER",
                    "Cursor only; the logo is quietly clickable and never "
                    "changes.", "w4"),
    ])

    html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Metro Match &middot; masthead + wordmark board (D35 follow-up)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --table:#0f0f12; --chrome:#131318; --edge:#26262c; --card:#1b1b21;
    --cedge:#32323a; --rowline:#232329; --text:#f2f2ee; --body:#e8e8e3;
    --soft:#c4c4bf; --grey:#9a9a93; --lblue:#7fb0e8;
    --mono:'DM Mono',ui-monospace,monospace;
    --sans:-apple-system,'Helvetica Neue','Segoe UI',Arial,sans-serif;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:var(--table); color:var(--body); font-family:var(--sans);
         padding:0 22px 60px; -webkit-font-smoothing:antialiased; }}
  .bb {{ max-width:980px; margin:26px auto; }}
  .bb h1 {{ font-size:16px; font-weight:800; letter-spacing:.22em; color:var(--text); }}
  .bb h1 em {{ font-style:normal; color:var(--lblue); }}
  .bb > p {{ font-size:13px; color:var(--soft); line-height:1.65; margin:10px 0; max-width:760px; }}
  .cand {{ margin:38px 0; }}
  .cand h2, .bb h2 {{ font-family:var(--mono); font-size:12px; letter-spacing:.16em;
            color:var(--lblue); text-transform:uppercase; margin-bottom:6px; }}
  .wcand h3 {{ font-family:var(--mono); font-size:11px; letter-spacing:.14em;
            color:var(--lblue); text-transform:uppercase; margin-bottom:4px; }}
  .note {{ font-size:12px; color:var(--soft); line-height:1.6; max-width:720px; margin-bottom:12px; }}
  .stage {{ border:1px solid var(--edge); border-radius:10px; overflow:hidden; }}

  /* mini header */
  .mhead {{ background:var(--chrome); border-bottom:1px solid var(--edge); padding:13px 0 10px; }}
  .mframe {{ display:flex; align-items:baseline; gap:22px; max-width:920px;
            margin:0 auto; padding:0 22px; }}
  .mwordmark {{ font-size:15px; font-weight:700; letter-spacing:.24em; color:var(--text); }}
  .mwordmark a {{ color:inherit; text-decoration:none; }}
  .mwordmark em {{ font-style:normal; color:var(--lblue); }}
  .mnav {{ display:flex; gap:14px; font-size:12.5px; font-weight:600;
          letter-spacing:.08em; color:var(--grey); }}
  .mnav b {{ color:var(--text); border-bottom:2px solid var(--lblue); padding-bottom:5px; }}

  /* hover treatments */
  .w1 a:hover, .w1 a:hover em {{ color:#fff; }}
  .w2 a:hover em {{ color:var(--text); }}
  .w3 a {{ border-bottom:2px solid transparent; padding-bottom:5px; }}
  .w3 a:hover {{ border-bottom-color:var(--lblue); }}
  /* w4: nothing */

  /* mini main + masthead variants */
  .mmain {{ max-width:920px; margin:0 auto; padding:0 22px 26px; }}
  .mintro {{ font-size:13px; color:var(--soft); line-height:1.65; padding:18px 2px 4px; }}
  .mintro b {{ color:var(--text); font-weight:600; }}
  .i-left {{ max-width:640px; }}
  .i-center {{ max-width:640px; margin:0 auto; text-align:center; }}
  .i-grid {{ max-width:854px; margin:0 auto; text-align:left; }}

  /* placeholder card row (alignment context only, not live cards) */
  .mgrid {{ display:grid; grid-template-columns:repeat(3,270px); gap:22px 22px;
           justify-content:center; padding:16px 0 4px; }}
  .mcard {{ width:270px; height:198px; border-radius:12px; background:var(--card);
           border:1px solid var(--cedge); padding:15px; }}
  .mname {{ font-size:24px; font-weight:800; letter-spacing:.04em; color:var(--text); }}
  .msub {{ font-family:var(--mono); font-size:9.5px; color:var(--soft); margin-top:5px; }}
  .mbnd {{ display:flex; height:14px; border-radius:7px; overflow:hidden; margin-top:12px; }}
  .mbnd i {{ flex:1; }}
  .mrow {{ height:30px; border-bottom:1px solid var(--rowline); }}
  .wcand {{ margin:26px 0; }}
</style>
</head><body>
<div class="bb">
  <h1>METRO <em>MATCH</em> &middot; MASTHEAD + WORDMARK BOARD</h1>
  <p>Two judgments, nothing live changes before your verdict. The card rows
  are placeholder outlines: the question is where the masthead block sits
  against the header frame and the grid edges, not the cards themselves.
  Hover the wordmark in section W: each one is live.</p>
  {m}
  <h2 style="margin-top:46px">W &middot; wordmark hover (hover each)</h2>
  {w}
</div>
</body></html>
"""
    out = os.path.join(HERE, "masthead-board.html")
    with open(out, "w") as fh:
        fh.write(html)
    print(f"wrote {out} ({os.path.getsize(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
