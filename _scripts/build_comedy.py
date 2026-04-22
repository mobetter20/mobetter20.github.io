from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPORT_ROOT = Path("/Users/ajin/Documents/New project/personal/ajin.im:is:writing/archive/wrote")
COMEDY_ROOT = REPO_ROOT / "is" / "writing" / "comedy"
COMEDY_SOURCE_ROOT = COMEDY_ROOT / "_src"


@dataclass(frozen=True)
class ComedyPost:
    source: Path
    title: str
    subtitle: str
    date: datetime
    canonical: str
    body_html: str
    slug: str

    @property
    def month_label(self) -> str:
        return self.date.strftime("%B %Y")

    @property
    def readable_date(self) -> str:
        return self.date.strftime("%B %-d, %Y")


@dataclass(frozen=True)
class StandaloneComedyPost:
    source: Path
    title: str
    body_md: str
    slug: str
    order: int = 0
    subtitle: str = ""


def normalize_text(value: str) -> str:
    value = html.unescape(re.sub(r"<[^>]+>", " ", value))
    value = value.replace("\xa0", " ")
    return re.sub(r"\s+", " ", value).strip()


def find(pattern: str, text: str, *, flags: int = re.S | re.I) -> str:
    match = re.search(pattern, text, flags)
    if not match:
        raise ValueError(f"pattern not found: {pattern}")
    return match.group(1)


def find_optional(pattern: str, text: str, *, flags: int = re.S | re.I) -> str:
    match = re.search(pattern, text, flags)
    return match.group(1) if match else ""


def slugify(value: str) -> str:
    value = html.unescape(value).lower()
    value = value.replace("\xa0", " ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def parse_front_matter(source_text: str) -> tuple[dict[str, str], str]:
    lines = source_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, source_text
    fm: dict[str, str] = {}
    idx = 1
    while idx < len(lines):
        line = lines[idx].strip()
        if line == "---":
            return fm, "\n".join(lines[idx + 1 :]).lstrip("\n")
        if ":" in line:
            key, value = line.split(":", 1)
            fm[key.strip()] = value.strip()
        idx += 1
    raise ValueError("front matter block not closed")


def markdown_inline_to_html(value: str) -> str:
    placeholder = "__BR_PLACEHOLDER__"
    value = value.replace("<br />", placeholder)
    value = html.escape(value)
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{html.escape(m.group(2), quote=True)}" target="_blank" rel="noreferrer noopener">{m.group(1)}</a>', value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", value)
    value = value.replace(placeholder, "<br />")
    return value


def markdown_to_html(body_md: str) -> str:
    lines = body_md.splitlines()
    blocks: list[str] = []
    i = 0

    def flush_paragraph(buffer: list[str]) -> None:
        if not buffer:
            return
        text = "\n".join(buffer).strip()
        if not text:
            return
        blocks.append(f"<p>{markdown_inline_to_html(text)}</p>")

    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if re.match(r"^#{2,4}\s+", line):
            level = len(re.match(r"^(#{2,4})\s+", line).group(1))
            content = line[level + 1 :].strip()
            blocks.append(f"<h{level}>{markdown_inline_to_html(content)}</h{level}>")
            i += 1
            continue
        if line.startswith("> "):
            quote_lines = [line[2:].strip()]
            i += 1
            while i < len(lines) and lines[i].startswith("> "):
                quote_lines.append(lines[i][2:].strip())
                i += 1
            quote_html = "<br />".join(markdown_inline_to_html(part) for part in quote_lines)
            blocks.append(f"<blockquote>{quote_html}</blockquote>")
            continue
        if re.match(r"^\s*([-*]|\d+\.)\s+", line):
            ordered = bool(re.match(r"^\s*\d+\.\s+", line))
            items: list[str] = []
            while i < len(lines) and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                item = re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i]).strip()
                items.append(f"<li>{markdown_inline_to_html(item)}</li>")
                i += 1
            tag = "ol" if ordered else "ul"
            blocks.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue
        paragraph_lines = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^#{2,4}\s+|^> |^\s*([-*]|\d+\.)\s+", lines[i]):
            paragraph_lines.append(lines[i].rstrip())
            i += 1
        flush_paragraph(paragraph_lines)
    return "\n".join(blocks)


def sanitize_anchor(match: re.Match[str]) -> str:
    href_match = re.search(r'href="([^"]+)"', match.group(0), re.I)
    if not href_match:
        return "<a>"
    href = html.escape(href_match.group(1), quote=True)
    if href.startswith(("http://", "https://")):
        return f'<a href="{href}" target="_blank" rel="noreferrer noopener">'
    return f'<a href="{href}">'


def clean_body(body_html: str) -> str:
    body_html = re.sub(r"<section\b[^>]*section--last[^>]*>.*?</section>", "", body_html, flags=re.S | re.I)
    body_html = re.sub(r"<figure\b.*?</figure>", "", body_html, flags=re.S | re.I)
    body_html = re.sub(r"<div\b[^>]*graf--mixtapeEmbed[^>]*>.*?</div>", "", body_html, flags=re.S | re.I)
    body_html = re.sub(r"<h4\b[^>]*>\s*</h4>", "", body_html, flags=re.S | re.I)
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


def indent_body(body_html: str) -> str:
    lines = [line.rstrip() for line in body_html.splitlines() if line.strip()]
    return "\n".join(f"        {line}" for line in lines)


def parse_post(source_path: Path) -> ComedyPost:
    text = source_path.read_text(encoding="utf-8", errors="ignore")
    title = normalize_text(find(r"<title>(.*?)</title>", text))
    subtitle = normalize_text(find_optional(r'<h4[^>]*graf--subtitle[^>]*>(.*?)</h4>', text))
    date_text = normalize_text(find(r"<time[^>]*>(.*?)</time>", text))
    canonical = find(r'<a href="([^"]+)" class="p-canonical">Canonical link</a>', text, flags=re.I)
    body_html = find(r'<section data-field="body" class="e-content">(.*?)</section>\s*<footer>', text)
    date = datetime.strptime(date_text, "%B %d, %Y")
    slug = slugify(title)
    return ComedyPost(
        source=source_path,
        title=title,
        subtitle=subtitle,
        date=date,
        canonical=canonical,
        body_html=body_html,
        slug=slug,
    )


def parse_standalone_post(source_path: Path) -> StandaloneComedyPost:
    text = source_path.read_text(encoding="utf-8", errors="ignore")
    front_matter, body_md = parse_front_matter(text)
    title = front_matter["title"]
    subtitle = front_matter.get("subtitle", "")
    order = int(front_matter.get("order", "0"))
    slug = source_path.stem
    return StandaloneComedyPost(
        source=source_path,
        title=title,
        body_md=body_md.strip(),
        slug=slug,
        order=order,
        subtitle=subtitle,
    )


def is_response_like(post: ComedyPost) -> bool:
    plain = normalize_text(post.body_html)
    title = re.sub(r"\s+", " ", post.title).strip(" .!?:;")
    body = re.sub(r"\s+", " ", plain).strip(" .!?:;")
    return title == body


def build_page(post: ComedyPost) -> str:
    subtitle_html = f'        <p class="post-subtitle">{html.escape(post.subtitle)}</p>\n' if post.subtitle else ""
    body_html = indent_body(clean_body(post.body_html))
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="icon" type="image/png" href="/img/a3.png" />
    <link rel="apple-touch-icon" href="/img/a3.png" />
    <title>{html.escape(post.title)} | ajin.im/is/writing/comedy</title>
    <meta name="description" content="{html.escape(post.subtitle or post.title)}" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=DM+Mono:wght@300;400;500&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="../../../../creative-house.css" />
    <script src="../../../../analytics.js" defer></script>
  </head>
  <body class="post-page">
    <main class="post-shell">
      <header class="post-head">
        <a class="back-link" href="../index.html">Back to comedy</a>
        <p class="path-mark">ajin.im is writing comedy</p>
        <p class="archive-meta">Medium years / {post.readable_date}</p>
        <h1 class="post-title">{html.escape(post.title)}</h1>
{subtitle_html}        <p class="post-note">
          Originally published on Medium on {post.readable_date}.
          <a href="{html.escape(post.canonical, quote=True)}" target="_blank" rel="noreferrer noopener">View original</a>
        </p>
      </header>

      <article class="post-body">
{body_html}
      </article>
    </main>
  </body>
</html>
"""


def build_standalone_page(post: StandaloneComedyPost) -> str:
    subtitle_html = f'        <p class="post-subtitle">{html.escape(post.subtitle)}</p>\n' if post.subtitle else ""
    body_html = indent_body(markdown_to_html(post.body_md))
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="icon" type="image/png" href="/img/a3.png" />
    <link rel="apple-touch-icon" href="/img/a3.png" />
    <title>{html.escape(post.title)} | ajin.im/is/writing/comedy</title>
    <meta name="description" content="{html.escape(post.subtitle or post.title)}" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=DM+Mono:wght@300;400;500&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="../../../../creative-house.css" />
    <script src="../../../../analytics.js" defer></script>
  </head>
  <body class="post-page">
    <main class="post-shell">
      <header class="post-head">
        <a class="back-link" href="../index.html">Back to comedy</a>
        <p class="path-mark">ajin.im is writing comedy</p>
        <p class="archive-meta">Standalone comedy</p>
        <h1 class="post-title">{html.escape(post.title)}</h1>
{subtitle_html}      </header>

      <article class="post-body">
{body_html}
      </article>
    </main>
  </body>
</html>
"""


def render_index(medium_posts: list[ComedyPost], standalone_posts: list[StandaloneComedyPost]) -> str:
    cards = []
    for post in sorted(standalone_posts, key=lambda item: item.order):
        cards.append(
            f"""            <article class="archive-card">
              <p class="archive-meta">Standalone comedy</p>
              <h2>
                <a href="./{post.slug}/index.html">
                  {html.escape(post.title)}
                </a>
              </h2>
            </article>"""
        )
    for post in medium_posts:
        cards.append(
            f"""            <article class="archive-card">
              <p class="archive-meta">Medium years / {post.month_label}</p>
              <h2>
                <a href="./{post.slug}/index.html">
                  {html.escape(post.title)}
                </a>
              </h2>
            </article>"""
        )

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="icon" type="image/png" href="/img/a3.png" />
    <link rel="apple-touch-icon" href="/img/a3.png" />
    <title>ajin.im/is/writing/comedy</title>
    <meta name="description" content="Comedy pieces by Ajin Im, largely from the Medium years." />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=DM+Mono:wght@300;400;500&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="../../../creative-house.css" />
    <script src="../../../analytics.js" defer></script>
  </head>
  <body class="archive-page">
    <main class="archive-shell">
      <header class="archive-head">
        <a class="back-link" href="../index.html">Back to the house</a>
        <p class="path-mark">ajin.im is writing comedy</p>
        <h1 class="sentence">...where marriage, objects, and small humiliations keep misbehaving.</h1>
        <p class="archive-intro">
          Domestic systems, bureaucratic logic, bodily events, and private embarrassments, all
          treated with the wrong amount of seriousness.
        </p>
      </header>

      <section class="archive-grid">
        <article class="archive-panel archive-panel-wide">
          <h2 class="panel-title">Comedy</h2>
          <p class="quiet-note">Pieces first published on Medium are marked below.</p>
          <div class="archive-list">
{chr(10).join(cards)}
          </div>
        </article>
      </section>
    </main>
  </body>
</html>
"""


def main() -> None:
    COMEDY_SOURCE_ROOT.mkdir(parents=True, exist_ok=True)

    medium_posts: list[ComedyPost] = []
    for source_path in sorted(EXPORT_ROOT.glob("*.html"), reverse=True):
        post = parse_post(source_path)
        if is_response_like(post):
            continue
        medium_posts.append(post)

    standalone_posts = [parse_standalone_post(path) for path in sorted(COMEDY_SOURCE_ROOT.glob("*.md"))]

    unique_medium_posts: list[ComedyPost] = []
    slug_counts: dict[str, int] = {}
    for post in medium_posts:
        count = slug_counts.get(post.slug, 0) + 1
        slug_counts[post.slug] = count
        if count > 1:
            post = ComedyPost(
                source=post.source,
                title=post.title,
                subtitle=post.subtitle,
                date=post.date,
                canonical=post.canonical,
                body_html=post.body_html,
                slug=f"{post.slug}-{count}",
            )
        unique_medium_posts.append(post)

    for post in unique_medium_posts:
        out_dir = COMEDY_ROOT / post.slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(build_page(post), encoding="utf-8")
        print(f"built {out_dir / 'index.html'}")

    for post in standalone_posts:
        out_dir = COMEDY_ROOT / post.slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(build_standalone_page(post), encoding="utf-8")
        print(f"built {out_dir / 'index.html'}")

    (COMEDY_ROOT / "index.html").write_text(render_index(unique_medium_posts, standalone_posts), encoding="utf-8")
    print(f"built {COMEDY_ROOT / 'index.html'}")


if __name__ == "__main__":
    main()
