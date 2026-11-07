"""Dynamic, strictly parsed inventory for the ajin.im home machine.

The writing source is build_essays' registry.  The building source remains the
hand-authored /is/building/ page, so adding a project has exactly one editing
home.  This module deliberately fails on a structural change instead of
quietly dropping a choice from the home page.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
import html
import re
from pathlib import Path
from typing import Iterable


class CatalogError(ValueError):
    """The source inventory is incomplete or no longer matches its contract."""


SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class Choice:
    title: str
    href: str
    status: str
    description: str
    collection: bool = False


class _BuildingParser(HTMLParser):
    """Parse only the project-card contract used by /is/building/index.html."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self._active: dict | None = None
        self.choices: list[Choice] = []
        self._capture: str | None = None
        self._capture_depth: int | None = None
        self._parts: list[str] = []

    @staticmethod
    def _classes(attrs: list[tuple[str, str | None]]) -> set[str]:
        return set(dict(attrs).get("class", "").split())

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        classes = self._classes(attrs)
        if tag == "div" and "project" in classes:
            if self._active is not None:
                raise CatalogError("nested .project cards are not supported")
            self._active = {
                "depth": self.depth,
                "title": "",
                "href": "",
                "status": "",
                "description": "",
                "collection": False,
            }
        if self._active is not None:
            if tag == "span" and "project-name" in classes:
                self._capture = "title"
                self._capture_depth = self.depth
                self._parts = []
            elif tag == "span" and "project-status" in classes:
                self._capture = "status"
                self._capture_depth = self.depth
                self._parts = []
                self._active["collection"] = "is-collection" in classes
            elif tag == "p" and "project-desc" in classes:
                self._capture = "description"
                self._capture_depth = self.depth
                self._parts = []
            elif tag == "a" and self._capture == "title":
                self._active["href"] = attrs_dict.get("href", "")
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.depth += 1

    def handle_data(self, data: str) -> None:
        if self._capture is not None:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        self.depth -= 1
        if self._active is not None and self._capture is not None:
            # Inline markup belongs to the field until its own element closes.
            if tag in {"span", "p"} and self.depth == self._capture_depth:
                value = " ".join("".join(self._parts).split())
                self._active[self._capture] = value
                self._capture = None
                self._capture_depth = None
                self._parts = []
        if tag == "div" and self._active is not None and self.depth == self._active["depth"]:
            record = self._active
            self._active = None
            missing = [key for key in ("title", "href", "status", "description") if not record[key]]
            if missing:
                raise CatalogError(f"project card is missing {', '.join(missing)}")
            self.choices.append(
                Choice(
                    title=record["title"],
                    href=record["href"],
                    status=record["status"],
                    description=record["description"],
                    collection=bool(record["collection"]),
                )
            )

    def close(self) -> None:
        super().close()
        if self._active is not None:
            raise CatalogError("unclosed .project card")


def load_building_choices(path: Path) -> list[Choice]:
    if not path.is_file():
        raise CatalogError(f"building source not found: {path}")
    parser = _BuildingParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    if not parser.choices:
        raise CatalogError("building source contains no .project cards")
    urls = [choice.href for choice in parser.choices]
    duplicates = sorted({href for href in urls if urls.count(href) > 1})
    if duplicates:
        raise CatalogError(f"building source contains duplicate project URLs: {', '.join(duplicates)}")
    if not any(choice.collection for choice in parser.choices):
        raise CatalogError("building source contains no collection cards")
    return parser.choices


def essay_choices(posts: Iterable[object]) -> list[Choice]:
    choices: list[Choice] = []
    for post in posts:
        slug = str(getattr(post, "slug", ""))
        title = str(getattr(post, "title", "")).strip()
        if not SLUG.fullmatch(slug):
            raise CatalogError(f"essay has invalid slug: {slug!r}")
        if not title:
            raise CatalogError(f"essay {slug} has no title")
        choices.append(Choice(title=title, href=f"/writes/{slug}/?from=machine", status=("Latest thought" if not choices else f"{max(1, round(len(str(getattr(post, 'body_md', '')).split()) / 220))} min read"), description=""))
    # Zero essays is allowed: Ajin retracts essays while revising them (Nov 2026).
    slugs = [choice.href.split("/")[2] for choice in choices]
    duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if duplicates:
        raise CatalogError(f"essay registry contains duplicate slugs: {', '.join(duplicates)}")
    return choices


def _choice_markup(
    *,
    choice: Choice,
    number: int,
    class_name: str,
    local: bool,
    same_tab: bool = False,
    essay_slug: str = "",
) -> str:
    href = escape(choice.href, quote=True)
    attrs = [f'href="{href}"', f'class="choice {class_name}"']
    if essay_slug:
        attrs.extend([f'id="{escape(essay_slug, quote=True)}"', f'data-essay-slug="{escape(essay_slug, quote=True)}"'])
    if local or same_tab:
        attrs.append('target="_self"')
    if class_name in {"collection", "build"}:
        attrs.append(f'data-project-url="{href}"')
    if not local and not same_tab:
        attrs.extend(['target="_blank"', 'rel="noopener"'])
    action = "Read" if local else "Open"
    arrow = "→" if local or same_tab else "↗"
    desc = f'<span class="choice-desc">{escape(choice.description)}</span>' if choice.description else ""
    return (
        f'<a {" ".join(attrs)}><span class="label"><span class="label-top">'
        f'<span>{number:02d}</span><span>{escape(choice.status)}</span></span>'
        f'<span class="choice-title">{escape(choice.title)}</span>{desc}</span>'
        f'<span class="press-face"><span class="light" aria-hidden="true"></span>'
        f'<span>{action}</span><span aria-hidden="true">{arrow}</span></span></a>'
    )


WORLDS = (
    # The Coo leads. The building collections (Seoul Crushing, Instrument Bus) join
    # these in one "Worlds" group: Ajin chose not to distinguish them (Nov 2026).
    Choice("The Municipal Coo", "/is/writing/bird-coo/", "Weekly newspaper", "The newspaper of the Avian Municipal District."),
    Choice("Bureau of Interior Conditions", "https://propagandaformyself.xyz", "Fictional world", "Where feelings become filings."),
)


def _group_title(name: str, count: int) -> str:
    return f'<div class="group-title"><span>{name}</span><span>{count:02d}</span></div>'


def render_worlds(start: int = 1, collections: Iterable[Choice] = ()) -> tuple[str, int]:
    collections = list(collections)
    markup = "".join(
        _choice_markup(choice=choice, number=start + index, class_name="world", local=False)
        for index, choice in enumerate(WORLDS)
    ) + "".join(
        _choice_markup(choice=choice, number=start + len(WORLDS) + index, class_name="collection",
                       local=False, same_tab=True)
        for index, choice in enumerate(collections)
    )
    total = len(WORLDS) + len(collections)
    return f'{_group_title("Worlds", total)}<div class="worlds lead">{markup}</div>', total


# Comedy cards on the home tray. Read from the committed, generated /wrote/ index
# (the Medium exports behind it are not in the repo, so CI could not rebuild them).
# Leave COMEDY_PICKS empty to show the newest COMEDY_SHOWN pieces, or list slugs to
# hand-pick them in order.
WROTE_INDEX_PATH = Path(__file__).resolve().parents[1] / "wrote" / "index.html"
COMEDY_PICKS: tuple[str, ...] = ()
COMEDY_SHOWN = 7
_WROTE_LINE = re.compile(
    r'<a class="line" href="/wrote/([a-z0-9-]+)/">(?:<span class="d">([^<]*)</span>)?'
    r'<span class="t">([^<]+)</span></a>')


def comedy_choices(index_path: Path = WROTE_INDEX_PATH) -> tuple[list[Choice], int]:
    if not index_path.is_file():
        raise CatalogError(f"comedy index not found: {index_path}")
    pieces = [(slug, html.unescape(title), date) for slug, date, title in _WROTE_LINE.findall(index_path.read_text(encoding="utf-8"))]
    if not pieces:
        raise CatalogError("comedy index lists no pieces")
    by_slug = {slug: (slug, title, date) for slug, title, date in pieces}
    missing = [slug for slug in COMEDY_PICKS if slug not in by_slug]
    if missing:
        raise CatalogError(f"COMEDY_PICKS not in the comedy index: {', '.join(missing)}")
    chosen = [by_slug[s] for s in COMEDY_PICKS] if COMEDY_PICKS else pieces[:COMEDY_SHOWN]
    choices = [Choice(title, f"/wrote/{slug}/", date.replace("·", " · ") if date else "Comedy", "")
               for slug, title, date in chosen]
    return choices, len(pieces)


def render_essays(posts: Iterable[object], start: int = 1) -> tuple[str, int]:
    """The Writing group: published essays (if any), comedy cards, then the archive."""
    essays = essay_choices(posts)
    essay_markup = "".join(
        _choice_markup(
            choice=choice,
            number=start + index,
            class_name="thought",
            local=True,
            essay_slug=choice.href.split("/")[2],
        )
        for index, choice in enumerate(essays)
    )
    comedy, comedy_total = comedy_choices()
    comedy_markup = "".join(
        _choice_markup(choice=choice, number=start + len(essays) + index, class_name="thought", local=True)
        for index, choice in enumerate(comedy)
    )
    archive = Choice("The comedy years", "/wrote/", f"All {comedy_total} · 2022–2023", "")
    archive_markup = _choice_markup(choice=archive, number=start + len(essays) + len(comedy),
                                    class_name="archive", local=False)
    total = len(essays) + len(comedy) + 1
    return (f'{_group_title("Writing", total)}<div class="pieces">'
            f'{essay_markup}{comedy_markup}{archive_markup}</div>'), total


def render_building(path: Path, start: int = 1) -> tuple[str, str]:
    """Single pieces only; the collections render inside the Worlds group."""
    choices = load_building_choices(path)
    collections = [choice for choice in choices if choice.collection]
    builds = [choice for choice in choices if not choice.collection]
    if not builds:
        raise CatalogError("building source contains no individual build cards")
    build_markup = "".join(
        _choice_markup(choice=choice, number=start + index, class_name="build", local=False)
        for index, choice in enumerate(builds)
    )
    html = f'{_group_title("Builds", len(builds))}<div class="pieces">{build_markup}</div>'
    return html, f"{len(collections):02d} collections / {len(builds):02d} pieces"


def render_home(posts: Iterable[object], building_path: Path) -> dict[str, str]:
    """One open tray, numbered as one sequence: worlds (incl. collections), builds, writing."""
    choices = load_building_choices(building_path)
    collections = [choice for choice in choices if choice.collection]
    worlds_html, count = render_worlds(1, collections)
    next_number = 1 + count
    building_html, _ = render_building(building_path, next_number)
    next_number += sum(not choice.collection for choice in choices)
    essays_html, _ = render_essays(posts, next_number)
    return {"worlds": worlds_html, "building": building_html, "essays": essays_html}
