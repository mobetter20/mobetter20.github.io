from __future__ import annotations

import html
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPORT_ROOT = Path("/Users/ajin/Documents/New project/personal/ajin.im:is:writing/archive/wrote")
COMEDY_ROOT = REPO_ROOT / "is" / "writing" / "comedy"

PILOT_POSTS = [
    {
        "source": "2022-09-24_I-Am-Chekhov-s-Gun--And-I-Have-Free-Will-daec5abff55d.html",
        "slug": "i-am-chekhovs-gun-and-i-have-free-will",
    },
    {
        "source": "2022-10-04_Announcing---the-Spousal-Credit-System-1ee9e0d9c3a3.html",
        "slug": "announcing-the-spousal-credit-system",
    },
    {
        "source": "2022-10-25_Bean-Bag---Spineless-Chair-for-Spineless-People-63afc8541f1f.html",
        "slug": "bean-bag-spineless-chair-for-spineless-people",
    },
    {
        "source": "2023-01-27_Suspicious-Cake-Erosion-Reported-7cba275b35b3.html",
        "slug": "suspicious-cake-erosion-reported",
    },
    {
        "source": "2022-10-15_What-Do-You-Want----Questions-From-My-Fridge-8a4fe5031147.html",
        "slug": "what-do-you-want-questions-from-my-fridge",
    },
]


def find(pattern: str, text: str, *, flags: int = re.S | re.I) -> str:
    match = re.search(pattern, text, flags)
    if not match:
        raise ValueError(f"pattern not found: {pattern}")
    return match.group(1)


def normalize_text(value: str) -> str:
    value = html.unescape(re.sub(r"<[^>]+>", " ", value))
    value = value.replace("\xa0", " ")
    return re.sub(r"\s+", " ", value).strip()


def sanitize_anchor(match: re.Match[str]) -> str:
    href_match = re.search(r'href="([^"]+)"', match.group(0), re.I)
    if not href_match:
        return "<a>"
    href = html.escape(href_match.group(1), quote=True)
    if href.startswith(("http://", "https://")):
        return f'<a href="{href}" target="_blank" rel="noreferrer noopener">'
    return f'<a href="{href}">'


def clean_body(body_html: str) -> str:
    body_html = re.sub(
        r"<section\b[^>]*section--last[^>]*>.*?Wouldn.*?rather be laughing\?.*?</section>",
        "",
        body_html,
        flags=re.S | re.I,
    )
    body_html = re.sub(r"<figure\b.*?</figure>", "", body_html, flags=re.S | re.I)
    body_html = re.sub(r"<div\b[^>]*graf--mixtapeEmbed[^>]*>.*?</div>", "", body_html, flags=re.S | re.I)
    body_html = re.sub(r"<h4\b[^>]*graf--kicker[^>]*>.*?</h4>", "", body_html, flags=re.S | re.I)
    body_html = re.sub(r"<h3\b[^>]*graf--title[^>]*>.*?</h3>", "", body_html, flags=re.S | re.I)
    body_html = re.sub(r"<h4\b[^>]*graf--subtitle[^>]*>.*?</h4>", "", body_html, flags=re.S | re.I)
    body_html = re.sub(r"<p\b[^>]*>\s*Thanks to .*?</p>", "", body_html, flags=re.S | re.I)
    body_html = re.sub(r"<hr\b[^>]*>", "", body_html, flags=re.I)
    body_html = re.sub(r"</?(?:section|div)\b[^>]*>", "", body_html, flags=re.I)
    body_html = re.sub(r"<p\b[^>]*>", "<p>", body_html, flags=re.I)
    body_html = re.sub(r"<blockquote\b[^>]*>", "<blockquote>", body_html, flags=re.I)
    body_html = re.sub(r"<ul\b[^>]*>", "<ul>", body_html, flags=re.I)
    body_html = re.sub(r"<ol\b[^>]*>", "<ol>", body_html, flags=re.I)
    body_html = re.sub(r"<li\b[^>]*>", "<li>", body_html, flags=re.I)
    body_html = re.sub(r"<h2\b[^>]*>", "<h2>", body_html, flags=re.I)
    body_html = re.sub(r"<h3\b[^>]*>", "<h3>", body_html, flags=re.I)
    body_html = re.sub(r"<h4\b[^>]*>", "<h4>", body_html, flags=re.I)
    body_html = re.sub(r"<strong\b[^>]*>", "<strong>", body_html, flags=re.I)
    body_html = re.sub(r"<em\b[^>]*>", "<em>", body_html, flags=re.I)
    body_html = re.sub(r"<br\b[^>]*>", "<br />", body_html, flags=re.I)
    body_html = re.sub(r"<a\b[^>]*>", sanitize_anchor, body_html, flags=re.I)
    body_html = re.sub(r"<(p|blockquote|ul|ol|li|h2|h3|h4)>\s*</\1>", "", body_html)
    body_html = body_html.replace("\xa0", " ")
    body_html = re.sub(r"\n{3,}", "\n\n", body_html).strip()
    return body_html


def build_page(title: str, subtitle: str, date: str, canonical: str, body_html: str) -> str:
    subtitle_html = ""
    if subtitle:
        subtitle_html = f'        <p class="post-subtitle">{html.escape(subtitle)}</p>\n'

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="icon" type="image/png" href="/img/a3.png" />
    <link rel="apple-touch-icon" href="/img/a3.png" />
    <title>{html.escape(title)} | ajin.im/is/writing/comedy</title>
    <meta
      name="description"
      content="{html.escape(subtitle or title)}"
    />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=DM+Mono:wght@300;400;500&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="../../../../creative-house.css" />
  </head>
  <body class="post-page">
    <main class="post-shell">
      <header class="post-head">
        <a class="back-link" href="../index.html">Back to comedy</a>
        <p class="path-mark">ajin.im is writing comedy</p>
        <p class="archive-meta">Medium years / {html.escape(date)}</p>
        <h1 class="post-title">{html.escape(title)}</h1>
{subtitle_html}        <p class="post-note">
          Originally published on Medium on {html.escape(date)}.
          <a href="{html.escape(canonical, quote=True)}" target="_blank" rel="noreferrer noopener">View original</a>
        </p>
      </header>

      <article class="post-body">
{body_html}
      </article>
    </main>
  </body>
</html>
"""


def indent_body(body_html: str) -> str:
    lines = [line.rstrip() for line in body_html.splitlines() if line.strip()]
    return "\n".join(f"        {line}" for line in lines)


def main() -> None:
    for post in PILOT_POSTS:
        source_path = EXPORT_ROOT / post["source"]
        text = source_path.read_text(encoding="utf-8", errors="ignore")

        title = normalize_text(find(r"<title>(.*?)</title>", text))
        subtitle = normalize_text(find(r'<h4[^>]*graf--subtitle[^>]*>(.*?)</h4>', text))
        date = normalize_text(find(r"<time[^>]*>(.*?)</time>", text))
        canonical = find(r'<a href="([^"]+)" class="p-canonical">Canonical link</a>', text, flags=re.I)
        body_html = find(
            r'<section data-field="body" class="e-content">(.*?)</section>\s*<footer>',
            text,
        )

        cleaned_body = indent_body(clean_body(body_html))
        page_html = build_page(title, subtitle, date, canonical, cleaned_body)

        out_dir = COMEDY_ROOT / post["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(page_html, encoding="utf-8")
        print(f"built {out_dir / 'index.html'}")


if __name__ == "__main__":
    main()
