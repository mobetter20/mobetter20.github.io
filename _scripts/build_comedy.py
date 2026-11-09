from __future__ import annotations

import html
import hashlib
import argparse
import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import writes_common
import image_pieces


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPORT_ROOT = Path.home() / "Documents/New project/personal/ajin.im:is:writing/archive/wrote"
COMEDY_ROOT = REPO_ROOT / "is" / "writing" / "comedy"
COMEDY_SOURCE_ROOT = COMEDY_ROOT / "_src"
WROTE_ROOT = REPO_ROOT / "wrote"
COMEDY_DATA_PATH = REPO_ROOT / "content" / "comedy.json"
SCHEMA_VERSION = 1
SAFE_SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


@dataclass(frozen=True)
class ComedyPost:
    source: Path
    title: str
    subtitle: str
    date: datetime
    canonical: str
    body_html: str
    slug: str
    illustration: dict | None = None

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


def is_verified_terminal_promo(inner_html: str) -> bool:
    """Recognise only the four ending forms observed in the saved exports.

    These are publisher boilerplate, not inferred from their position or a
    `section--last` class.  Keeping this list literal makes future imports
    conservative: unfamiliar endings remain published until deliberately
    reviewed.
    """
    text = normalize_text(inner_html).casefold()
    return text.startswith((
        "wouldn’t you rather be laughing? follow ",
        "wouldn't you rather be laughing? follow ",
        "click here to subscribe to muddyum’s newsletter",
        "click here to subscribe to muddyum's newsletter",
        "this piece was first published in ",
        "this piece was originally published in ",
    ))


def strip_verified_promos(body_html: str) -> str:
    def remove(match: re.Match[str]) -> str:
        return "" if is_verified_terminal_promo(match.group(2)) else match.group(0)

    # Exports use paragraph and blockquote nodes for these exact tails.
    return re.sub(r"<(p|blockquote)\b[^>]*>(.*?)</\1>", remove, body_html, flags=re.S | re.I)


def clean_body(body_html: str) -> str:
    """Keep a Medium export's article, removing only known export furniture.

    `section--last` is structural, not a footer marker: short posts and the
    final part of long posts commonly have it.  Removing that section used to
    erase six complete published posts and the end of the numbered-list post.
    """
    body_html = strip_verified_promos(body_html)
    body_html = re.sub(r"<figure\b.*?</figure>", "", body_html, flags=re.S | re.I)
    body_html = re.sub(r"<div\b[^>]*graf--mixtapeEmbed[^>]*>.*?</div>", "", body_html, flags=re.S | re.I)
    body_html = re.sub(r"<h4\b[^>]*>\s*</h4>", "", body_html, flags=re.S | re.I)
    body_html = re.sub(r"<h4\b[^>]*graf--kicker[^>]*>.*?</h4>", "", body_html, flags=re.S | re.I)
    body_html = re.sub(r"<h3\b[^>]*graf--title[^>]*>.*?</h3>", "", body_html, flags=re.S | re.I)
    body_html = re.sub(r"<h4\b[^>]*graf--subtitle[^>]*>.*?</h4>", "", body_html, flags=re.S | re.I)
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
    body_html = indent_body(clean_body(post.body_html))
    if post.illustration:
        art = post.illustration
        src = html.escape(art['image'], quote=True)
        alt = html.escape(art['alt'], quote=True)
        body_html = f'''        <figure class="prose-illustration">
          <a href="{src}" target="_self" aria-label="View illustration full size"><img src="{src}" width="{art['width']}" height="{art['height']}" alt="{alt}" /></a>
          <figcaption>Illustration generated with AI. <a href="{src}" target="_self">View full size</a></figcaption>
        </figure>
{body_html}'''
    note_html = (
        '<p class="post-note">Originally published on Medium on '
        f"{html.escape(post.readable_date)}. "
        f'<a href="{html.escape(post.canonical, quote=True)}" target="_blank" rel="noreferrer noopener">View original</a></p>'
    )
    page = writes_common.reading_page(
        title=post.title,
        body_html=body_html,
        canonical=f"https://ajin.im/wrote/{post.slug}/",
        description=post.subtitle or post.title,
        kicker=f"the comedy years · {post.month_label}",
        back_href="/is/writing/#all",
        back_label="← All writing",
        subtitle=post.subtitle,
        note_html=note_html,
    )
    if post.illustration:
        version = hashlib.sha256((REPO_ROOT / 'assets/paper/prose-images.css').read_bytes()).hexdigest()[:10]
        extra = f'''    <link rel="stylesheet" href="/assets/paper/prose-images.css?v={version}" />
    <meta property="og:image" content="https://ajin.im{src}" />
    <meta property="og:image:width" content="{art['width']}" />
    <meta property="og:image:height" content="{art['height']}" />
    <meta property="og:image:alt" content="{alt}" />
    <meta name="twitter:image" content="https://ajin.im{src}" />
    <meta name="twitter:image:alt" content="{alt}" />'''
        page = page.replace('  </head>', extra + '\n  </head>').replace(
            '<meta name="twitter:card" content="summary" />',
            '<meta name="twitter:card" content="summary_large_image" />',
        )
    return page


def build_standalone_page(post: StandaloneComedyPost) -> str:
    body_html = indent_body(markdown_to_html(post.body_md))
    return writes_common.reading_page(
        title=post.title,
        body_html=body_html,
        canonical=f"https://ajin.im/wrote/{post.slug}/",
        description=post.subtitle or post.title,
        kicker="the comedy years",
        back_href="/is/writing/#all",
        back_label="← All writing",
        subtitle=post.subtitle,
    )


def _uniquify_slugs(posts: list[ComedyPost]) -> list[ComedyPost]:
    """Preserve the historic slug policy when importing old Medium exports."""
    unique_posts: list[ComedyPost] = []
    slug_counts: dict[str, int] = {}
    for post in posts:
        count = slug_counts.get(post.slug, 0) + 1
        slug_counts[post.slug] = count
        if count > 1:
            post = ComedyPost(
                source=post.source, title=post.title, subtitle=post.subtitle,
                date=post.date, canonical=post.canonical, body_html=post.body_html,
                slug=f"{post.slug}-{count}",
            )
        unique_posts.append(post)
    return unique_posts


def import_medium_posts(export_root: Path = EXPORT_ROOT) -> list[ComedyPost]:
    """Read the private Medium export.  This is an explicit local refresh only."""
    sources = sorted(export_root.glob("*.html"), reverse=True)
    if not sources:
        raise ValueError(f"no Medium export files found at {export_root}; refusing to replace committed comedy data")
    medium_posts: list[ComedyPost] = []
    for source_path in sources:
        post = parse_post(source_path)
        if is_response_like(post):
            continue
        medium_posts.append(post)
    posts = _uniquify_slugs(medium_posts)
    validate_medium_posts(posts, export_root)
    return posts


def validate_illustration(art: object, root: Path | None = None) -> dict:
    """A local addition, independent of the imported article's text and date."""
    root = root or REPO_ROOT
    if not isinstance(art, dict) or set(art) != {'image', 'width', 'height', 'alt'}:
        raise ValueError('illustration needs exactly image, width, height and alt')
    if not isinstance(art['alt'], str) or not art['alt'].strip():
        raise ValueError('illustration alt must be non-empty text')
    image = art['image']
    if not isinstance(image, str) or not image.startswith('/assets/'):
        raise ValueError('illustration image must be a root-relative /assets/ path')
    path = (root / image.lstrip('/')).resolve()
    if not path.is_relative_to((root / 'assets').resolve()):
        raise ValueError('illustration image must stay inside assets')
    if any(type(art[k]) is not int or art[k] <= 0 for k in ('width', 'height')):
        raise ValueError('illustration dimensions must be positive integers')
    if image_pieces.image_dimensions(path) != (art['width'], art['height']):
        raise ValueError('illustration dimensions do not match the asset')
    return dict(art)


def validate_medium_posts(posts: list[ComedyPost], source: Path, root: Path | None = None) -> None:
    if not posts:
        raise ValueError(f"no comedy posts in {source}; refusing to replace committed comedy data")
    seen: set[str] = set()
    for post in posts:
        if not SAFE_SLUG_RE.fullmatch(post.slug):
            raise ValueError(f"invalid comedy slug in {source}: {post.slug}")
        if post.slug in seen:
            raise ValueError(f"duplicate comedy slug in {source}: {post.slug}")
        seen.add(post.slug)
        if not normalize_text(clean_body(post.body_html)):
            raise ValueError(f"empty comedy body after cleaning in {source}: {post.slug}")
        if post.illustration is not None:
            validate_illustration(post.illustration, root)


def write_medium_data(
    posts: list[ComedyPost], path: Path = COMEDY_DATA_PATH, *, allow_removals: bool = False
) -> None:
    validate_medium_posts(posts, path)
    # A partial local export is far more likely than an intentional archive
    # deletion. Compare before writing and require an explicit CLI escape hatch.
    illustrations = {}
    if path.exists():
        existing = load_medium_data(path)
        illustrations = {post.slug: post.illustration for post in existing if post.illustration}
        missing = sorted({post.slug for post in existing} - {post.slug for post in posts})
        if missing and not allow_removals:
            raise ValueError(
                f"import would remove {len(missing)} committed comedy posts ({', '.join(missing)}); "
                "refusing to replace data without --allow-removals"
            )
    data = {
        "schema_version": SCHEMA_VERSION,
        "posts": [
            {
                "slug": post.slug,
                "title": post.title,
                "subtitle": post.subtitle,
                "date": post.date.date().isoformat(),
                "canonical": post.canonical,
                "body_html": clean_body(post.body_html),
                **({'illustration': illustrations.get(post.slug) or post.illustration}
                   if illustrations.get(post.slug) or post.illustration else {}),
            }
            for post in posts
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    # Write beside the target, then replace atomically: an interrupted refresh
    # leaves either the old complete catalog or the new complete catalog.
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as temporary:
            temporary.write(encoded)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def load_medium_data(path: Path = COMEDY_DATA_PATH, *, root: Path | None = None) -> list[ComedyPost]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"missing committed comedy data: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid comedy JSON at {path}: {error.msg}") from error
    if data.get("schema_version") != SCHEMA_VERSION or not isinstance(data.get("posts"), list):
        raise ValueError(f"invalid comedy JSON schema at {path}")

    required = ("slug", "title", "date", "canonical", "body_html")
    posts: list[ComedyPost] = []
    seen: set[str] = set()
    for number, item in enumerate(data["posts"], 1):
        if (not isinstance(item, dict)
                or any(not isinstance(item.get(key), str) or not item[key].strip() for key in required)
                or not isinstance(item.get("subtitle"), str)):
            raise ValueError(f"invalid comedy post #{number} in {path}: required fields are slug, title, subtitle, date, canonical, body_html")
        slug = item["slug"]
        if not SAFE_SLUG_RE.fullmatch(slug):
            raise ValueError(f"invalid comedy slug in {path}: {slug}")
        if slug in seen:
            raise ValueError(f"duplicate comedy slug in {path}: {slug}")
        seen.add(slug)
        try:
            date = datetime.strptime(item["date"], "%Y-%m-%d")
        except ValueError as error:
            raise ValueError(f"invalid comedy date for {slug} in {path}: {item['date']}") from error
        illustration = validate_illustration(item['illustration'], root) if 'illustration' in item else None
        post = ComedyPost(path, item["title"], item["subtitle"], date, item["canonical"], item["body_html"], slug, illustration)
        if not normalize_text(clean_body(post.body_html)):
            raise ValueError(f"empty comedy body after cleaning in {path}: {slug}")
        posts.append(post)
    validate_medium_posts(posts, path, root)
    return posts


def load_posts() -> tuple[list[ComedyPost], list[StandaloneComedyPost]]:
    """Load committed public comedy data.  Never depends on private exports."""
    medium_posts = load_medium_data()

    standalone_posts = [parse_standalone_post(path) for path in sorted(COMEDY_SOURCE_ROOT.glob("*.md"))]
    medium_slugs = {post.slug for post in medium_posts}
    for post in standalone_posts:
        if not SAFE_SLUG_RE.fullmatch(post.slug):
            raise ValueError(f"invalid standalone comedy slug: {post.slug}")
        if post.slug in medium_slugs:
            raise ValueError(f"comedy slug collision between Medium data and standalone source: {post.slug}")

    return medium_posts, standalone_posts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--import-medium", action="store_true", help="refresh committed comedy.json from the local private Medium export")
    parser.add_argument("--allow-removals", action="store_true", help="allow an import to remove slugs from committed comedy.json")
    args = parser.parse_args()
    if args.allow_removals and not args.import_medium:
        parser.error("--allow-removals is only valid with --import-medium")
    if args.import_medium:
        posts = import_medium_posts()
        write_medium_data(posts, allow_removals=args.allow_removals)
        print(f"wrote {COMEDY_DATA_PATH} ({len(posts)} Medium posts)")
        return

    unique_medium_posts, standalone_posts = load_posts()

    for post in unique_medium_posts:
        out_dir = WROTE_ROOT / post.slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(build_page(post), encoding="utf-8")
        print(f"built {out_dir / 'index.html'}")

    for post in standalone_posts:
        out_dir = WROTE_ROOT / post.slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(build_standalone_page(post), encoding="utf-8")
        print(f"built {out_dir / 'index.html'}")


if __name__ == "__main__":
    main()
