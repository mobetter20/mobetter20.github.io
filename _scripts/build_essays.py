from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

import writes_common


REPO_ROOT = Path(__file__).resolve().parents[1]
ESSAY_ROOT = REPO_ROOT / "is" / "writing" / "essays"
SOURCE_ROOT = ESSAY_ROOT / "_src"
EXPORT_ROOT = Path.home() / "Documents/New project/personal/ajin.im:is:writing/archive/essay"
WROTE_ROOT = REPO_ROOT / "wrote"
WRITES_ROOT = REPO_ROOT / "writes"


POST_DEFS = [
    {
        "source": "the-house-chips-of-ai.md",
        "title": "The House Chips of AI",
        "order": 0,
    },
    {
        "source": "already-seen.md",
        "title": "Already Seen",
        "order": 1,
    },
    {
        "source": "adventure-is-danger-past-tense.md",
        "title": "Adventure Is Danger, Past Tense",
        "order": 3,
    },
    {
        "source": "call-of-the-void.md",
        "title": "Call of the Void",
        "order": 4,
    },
    {
        "source": "korea-was-the-beta-test-zone-for-modern-loneliness.md",
        "title": "Korea was the beta test zone for modern loneliness.",
        "order": 6,
    },
    {
        "source": "how-to-cry-on-the-subway-and-not-be-seen.md",
        "title": "How to Cry on the Subway and Not Be Seen",
        "order": 7,
    },
]


@dataclass(frozen=True)
class EssayPost:
    source: Path
    title: str
    order: int
    body_md: str
    excerpt: str
    slug: str
    date: str = ""

    @property
    def readable_order(self) -> str:
        return str(self.order)

    @property
    def year(self) -> str:
        return self.date[:4] if self.date else ""


def slugify(value: str) -> str:
    value = html.unescape(value).lower().replace("\xa0", " ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value)


def convert_inline_html_to_markdown(value: str) -> str:
    value = value.replace("\xa0", " ")

    def replace_link(match: re.Match[str]) -> str:
        href = html.unescape(match.group(1))
        text = convert_inline_html_to_markdown(match.group(2))
        return f"[{text}]({href})"

    value = re.sub(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>', replace_link, value, flags=re.S | re.I)
    value = re.sub(r"</?(?:strong|b)[^>]*>", lambda m: "**", value, flags=re.I)
    value = re.sub(r"</?(?:em|i)[^>]*>", lambda m: "*", value, flags=re.I)
    value = re.sub(r"<br\s*/?>", "<br />", value, flags=re.I)
    value = strip_tags(value)
    value = html.unescape(value)
    value = re.sub(r"[ \t]+", " ", value).strip()
    return value


def paragraph_to_markdown(paragraph_html: str) -> str:
    text = convert_inline_html_to_markdown(paragraph_html)
    if not text:
        return ""
    if text == "---":
        return "---"
    bullet = re.match(r"^[\s•\u2022]+(.*)$", text)
    if bullet:
        text = f"- {bullet.group(1).strip()}"
    return text


def clean_export_fragment(html_text: str) -> str:
    html_text = re.sub(r'<div class="captioned-image-container">.*?</div>\s*', "", html_text, flags=re.S | re.I)
    html_text = re.sub(r"<figure\b.*?</figure>", "", html_text, flags=re.S | re.I)
    html_text = re.sub(r'<div class="subscription-widget-wrap-editor".*?</div>', "", html_text, flags=re.S | re.I)
    html_text = re.sub(r"<div>\s*<hr\s*/?>\s*</div>", "<p>---</p>", html_text, flags=re.S | re.I)
    html_text = re.sub(r"</?div\b[^>]*>", "", html_text, flags=re.S | re.I)
    return html_text


def export_html_to_markdown(export_path: Path) -> str:
    raw = export_path.read_text(encoding="utf-8", errors="ignore")
    cleaned = clean_export_fragment(raw)
    paragraphs = re.findall(r"<p\b[^>]*>(.*?)</p>", cleaned, flags=re.S | re.I)
    blocks: list[str] = []
    list_items: list[str] = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
          blocks.append("\n".join(list_items))
          list_items = []

    for paragraph in paragraphs:
        md = paragraph_to_markdown(paragraph)
        if md:
            if md == "---":
                flush_list()
                if blocks and blocks[-1] != "---":
                    blocks.append("---")
                elif not blocks:
                    blocks.append("---")
                continue
            if md.startswith("- "):
                list_items.append(md)
                continue
            if md == "." and blocks:
                blocks[-1] = blocks[-1].rstrip() + "."
                continue
            flush_list()
            blocks.append(md)
    flush_list()
    return "\n\n".join(blocks).strip() + "\n"


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


def parse_markdown_post(source_path: Path) -> EssayPost:
    source_text = source_path.read_text(encoding="utf-8")
    front_matter, body_md = parse_front_matter(source_text)
    title = front_matter["title"]
    order = int(front_matter.get("order", "999"))
    excerpt = front_matter.get("excerpt", "")
    slug = source_path.stem
    if not excerpt:
        excerpt = excerpt_from_markdown(body_md)
    return EssayPost(
        source=source_path,
        title=title,
        order=order,
        body_md=body_md,
        excerpt=excerpt,
        slug=slug,
        date=front_matter.get("date", ""),
    )


def excerpt_from_markdown(body_md: str, max_words: int = 24) -> str:
    first_paragraph = ""
    for block in body_md.split("\n\n"):
        block = block.strip()
        if block and block != "---":
            first_paragraph = block
            break
    words = re.split(r"\s+", strip_tags(first_paragraph).replace("<br />", " "))
    words = [word for word in words if word]
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]).rstrip(" ,.;:") + "..."


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
        if text == "---":
            blocks.append("<hr />")
            return
        blocks.append(f"<p>{markdown_inline_to_html(text)}</p>")

    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line == "---":
            blocks.append("<hr />")
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
        while i < len(lines) and lines[i].strip() and not re.match(r"^#{2,4}\s+|^> |^\s*([-*]|\d+\.)\s+|^---$", lines[i]):
            paragraph_lines.append(lines[i].rstrip())
            i += 1
        flush_paragraph(paragraph_lines)
        continue

    return "\n".join(blocks)


def ensure_source_markdown() -> None:
    SOURCE_ROOT.mkdir(parents=True, exist_ok=True)
    for post_def in POST_DEFS:
        source_path = SOURCE_ROOT / post_def["source"]
        if source_path.exists():
            continue
        export_path = EXPORT_ROOT / post_def["export"]
        body_md = export_html_to_markdown(export_path)
        source_text = (
            "---\n"
            f'title: {post_def["title"]}\n'
            f'order: {post_def["order"]}\n'
            "---\n\n"
            f"{body_md}"
        )
        source_path.write_text(source_text, encoding="utf-8")


def build_post_page(post: EssayPost) -> str:
    body_html = indent_body(markdown_to_html(post.body_md))
    kicker = f"{post.year} · a thought" if post.year else "a thought"
    return writes_common.reading_page(
        title=post.title,
        body_html=body_html,
        canonical=f"https://ajin.im/writes/{post.slug}/",
        description=post.excerpt or post.title,
        kicker=kicker,
        back_href="/writes/",
        back_label="← ajin.im/writes",
        feed_url="/writes/feed.xml",
    )


def indent_body(body_html: str) -> str:
    lines = [line.rstrip() for line in body_html.splitlines() if line.strip()]
    return "\n".join(f"        {line}" for line in lines)


def load_posts() -> list[EssayPost]:
    ensure_source_markdown()
    posts: list[EssayPost] = []
    for post_def in POST_DEFS:
        source_path = SOURCE_ROOT / post_def["source"]
        posts.append(parse_markdown_post(source_path))
    return sorted(posts, key=lambda post: post.order)


SITE_BASE_URL = "https://ajin.im"
ESSAY_FEED_TITLE = "ajin.im — Collected Writing"
ESSAY_FEED_ALTERNATE = f"{SITE_BASE_URL}/writes/"
ESSAY_FEED_SELF = f"{SITE_BASE_URL}/writes/feed.xml"
ESSAY_FEED_PATH = WRITES_ROOT / "feed.xml"


def xml_escape(value: str) -> str:
    """html.escape(quote=True) yields valid XML entity/char references."""
    return html.escape(value, quote=True)


def render_feed(posts: list[EssayPost]) -> str:
    """Build a valid Atom 1.0 feed from the live essays.

    Mirrors build_bird_coo.render_feed. Essay front matter carries only a
    year (`date: 2026`), so timestamps are pinned to YYYY-01-01 — coarse but
    honest; the feed exists for discovery/followability, not minute-accuracy.
    Posts are emitted in `order` (0 first = the featured/most-recent piece)."""
    def timestamp(post: EssayPost) -> str:
        year = post.year or "2026"
        return f"{year}-01-01T00:00:00Z"

    entries = []
    for post in posts:
        entry_url = f"{SITE_BASE_URL}/writes/{post.slug}/"
        ts = timestamp(post)
        summary = post.excerpt or post.title
        entries.append(
            "<entry>\n"
            f"<id>{xml_escape(entry_url)}</id>\n"
            f'<link rel="alternate" href="{xml_escape(entry_url)}"/>\n'
            f"<title>{xml_escape(post.title)}</title>\n"
            f"<updated>{ts}</updated>\n"
            f"<published>{ts}</published>\n"
            f'<summary type="text">{xml_escape(summary)}</summary>\n'
            "</entry>"
        )

    feed_updated = max((timestamp(p) for p in posts), default="2026-01-01T00:00:00Z")
    entries_block = ("\n" + "\n".join(entries) + "\n") if entries else "\n"
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<feed xmlns="http://www.w3.org/2005/Atom">\n'
        f"<title>{xml_escape(ESSAY_FEED_TITLE)}</title>\n"
        f'<link rel="alternate" href="{xml_escape(ESSAY_FEED_ALTERNATE)}"/>\n'
        f'<link rel="self" href="{xml_escape(ESSAY_FEED_SELF)}"/>\n'
        f"<id>{xml_escape(ESSAY_FEED_ALTERNATE)}</id>\n"
        f"<updated>{feed_updated}</updated>\n"
        "<author><name>ajin</name></author>"
        f"{entries_block}"
        "</feed>\n"
    )


def main() -> None:
    posts = load_posts()
    for post in posts:
        out_dir = WRITES_ROOT / post.slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(build_post_page(post), encoding="utf-8")
        # The piece moved from /wrote/<slug>/ to /writes/<slug>/ — leave a redirect.
        old_dir = WROTE_ROOT / post.slug
        old_dir.mkdir(parents=True, exist_ok=True)
        (old_dir / "index.html").write_text(
            writes_common.redirect_stub(f"/writes/{post.slug}/", title="Moved to ajin.im/writes"),
            encoding="utf-8",
        )
        print(f"built {out_dir / 'index.html'}")
    ESSAY_FEED_PATH.write_text(render_feed(posts), encoding="utf-8")
    print(f"built {ESSAY_FEED_PATH}")


if __name__ == "__main__":
    main()
