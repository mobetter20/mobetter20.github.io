"""Render the essays at /writes/<slug>/ plus the Atom feed.

The `_src/` directory IS the registry: every `*.md` in it is an essay, and files
whose name starts with `_` are notes, not posts. There is no second list to keep
in sync (the old POST_DEFS + Medium-export scaffolding retired 2026-09-16).

Front matter: `title` and `order` are required, `date` and `excerpt` optional.
`order` sorts ascending, 0 = newest, and must be unique — the build fails loudly
rather than silently guessing at a tie. `_scripts/writes_publisher/` maintains
those numbers automatically when publishing from Obsidian.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

import writes_common


REPO_ROOT = Path(__file__).resolve().parents[1]
ESSAY_ROOT = REPO_ROOT / "is" / "writing" / "essays"
SOURCE_ROOT = ESSAY_ROOT / "_src"
WROTE_ROOT = REPO_ROOT / "wrote"
WRITES_ROOT = REPO_ROOT / "writes"


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
    if "title" not in front_matter:
        raise ValueError(f"{source_path.name}: front matter needs a `title:`")
    if "order" not in front_matter:
        raise ValueError(f"{source_path.name}: front matter needs an `order:` (0 = newest)")
    title = front_matter["title"]
    try:
        order = int(front_matter["order"])
    except ValueError as exc:
        raise ValueError(f"{source_path.name}: `order:` must be an integer") from exc
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
    """Every `*.md` in _src/ is an essay. `_`-prefixed files are notes, not posts."""
    posts = [
        parse_markdown_post(path)
        for path in sorted(SOURCE_ROOT.glob("*.md"))
        if not path.name.startswith("_")
    ]
    orders = [post.order for post in posts]
    clashes = sorted({o for o in orders if orders.count(o) > 1})
    if clashes:
        where = ", ".join(
            f"{post.source.name}={post.order}" for post in posts if post.order in clashes
        )
        raise ValueError(
            f"duplicate `order:` in {SOURCE_ROOT.relative_to(REPO_ROOT)} — {where}. "
            "Order must be unique (0 = newest)."
        )
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
