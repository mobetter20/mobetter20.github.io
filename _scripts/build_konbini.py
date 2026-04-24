#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
KONBINI_ROOT = REPO_ROOT / "is" / "learning" / "konbini"
CONTENT_ROOT = KONBINI_ROOT / "content"
OUTPUT_PATH = KONBINI_ROOT / "content.json"


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
BLOCK_RE = re.compile(r"^::([a-z-]+)(?:\[(.*?)\])?\n(.*?)^::\s*$", re.DOTALL | re.MULTILINE)
FURIGANA_RE = re.compile(r"《[^》]*》")
FURIGANA_UNCLOSED_RE = re.compile(r"《[^》]*$|^[^《]*》", re.MULTILINE)


class BuildError(Exception):
    pass


def parse_frontmatter(raw: str, source: Path) -> tuple[dict, str]:
    match = FRONTMATTER_RE.match(raw)
    if not match:
        raise BuildError(f"{source}: missing or malformed frontmatter")
    fm_text, body = match.group(1), match.group(2)
    fm: dict = {}
    current_key = None
    current_block: list[str] | None = None
    for line in fm_text.splitlines():
        if current_block is not None:
            if line.startswith("  ") or line == "":
                current_block.append(line[2:] if line.startswith("  ") else "")
                continue
            fm[current_key] = "\n".join(current_block).rstrip()
            current_block = None
        m = re.match(r"^([a-z_][a-z0-9_]*):\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if value == "|":
            current_key = key
            current_block = []
        else:
            fm[key] = _coerce(value)
    if current_block is not None:
        fm[current_key] = "\n".join(current_block).rstrip()
    return fm, body


def _coerce(value: str):
    if value in ("null", ""):
        return None
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        return value


def validate_furigana(text: str, source: Path) -> None:
    opens = text.count("《")
    closes = text.count("》")
    if opens != closes:
        raise BuildError(
            f"{source}: unmatched 《 or 》 ({opens} opens, {closes} closes)"
        )


def parse_blocks(body: str, source: Path) -> list[dict]:
    blocks: list[dict] = []
    for m in BLOCK_RE.finditer(body):
        block_type = m.group(1)
        arg = m.group(2)
        inner = m.group(3).rstrip()
        validate_furigana(inner, source)
        if arg is not None:
            validate_furigana(arg, source)
        blocks.append(_shape_block(block_type, arg, inner, source))
    return blocks


def _shape_block(block_type: str, arg: str | None, body: str, source: Path) -> dict:
    block: dict = {"type": block_type}
    if arg is not None:
        block["arg"] = arg
    if block_type == "player-choice":
        options = []
        for line in body.splitlines():
            line = line.strip()
            if not line:
                continue
            m = re.match(r"^([a-z]):\s*(.*?)(?:\s*\|\s*(.+))?$", line)
            if not m:
                raise BuildError(
                    f"{source}: malformed player-choice option: {line!r}"
                )
            label, text, tag = m.group(1), m.group(2).strip(), (m.group(3) or "").strip() or None
            options.append({"label": label, "text": text, "response_id": tag})
        block["options"] = options
    elif block_type == "nutrition":
        rows = []
        for line in body.splitlines():
            line = line.strip()
            if not line:
                continue
            if "|" not in line:
                raise BuildError(f"{source}: nutrition row missing |: {line!r}")
            left, right = line.split("|", 1)
            rows.append({"left": left.strip(), "right": right.strip()})
        block["rows"] = rows
    else:
        block["body"] = body
    return block


def parse_sections(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current = None
    buffer: list[str] = []
    for line in body.splitlines():
        m = re.match(r"^##\s+(.+)$", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buffer).strip()
            current = m.group(1).strip()
            buffer = []
        elif current is not None:
            buffer.append(line)
    if current is not None:
        sections[current] = "\n".join(buffer).strip()
    return sections


def validate_dialogue(blocks: list[dict], source: Path) -> None:
    last_choice_tags: set[str] | None = None
    for block in blocks:
        if block["type"] == "player-choice":
            last_choice_tags = {
                o["response_id"]
                for o in block["options"]
                if o["response_id"] is not None
            }
        elif block["type"] == "clerk-branch":
            arg = block.get("arg")
            if arg is None:
                raise BuildError(f"{source}: clerk-branch missing [id]")
            if last_choice_tags is None or arg not in last_choice_tags:
                raise BuildError(
                    f"{source}: clerk-branch[{arg}] has no matching preceding player-choice response_id"
                )


def build_items() -> dict:
    items: dict = {}
    for path in sorted((CONTENT_ROOT / "items").glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(raw, path)
        sections = parse_sections(body)
        for required in ("id", "name_jp", "name_en", "price", "zone", "description_jp", "description_en"):
            if required not in fm or fm[required] in (None, ""):
                raise BuildError(f"{path}: missing required field '{required}'")
        validate_furigana(fm["description_jp"], path)
        items[fm["id"]] = {
            **fm,
            "front": parse_blocks(sections.get("front", ""), path),
            "back": parse_blocks(sections.get("back", ""), path),
        }
    return items


def build_notices() -> dict:
    notices: dict = {}
    for path in sorted((CONTENT_ROOT / "notices").glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(raw, path)
        sections = parse_sections(body)
        body_text = sections.get("body", "")
        blocks = parse_blocks(body_text, path)
        # Remaining prose (lines between :: blocks) is kept as raw paragraphs.
        prose = re.sub(BLOCK_RE, "", body_text).strip()
        validate_furigana(prose, path)
        notices[fm["id"]] = {
            **fm,
            "blocks": blocks,
            "prose": prose,
        }
    return notices


def build_dialogue() -> dict:
    dialogue: dict = {}
    for path in sorted((CONTENT_ROOT / "dialogue").glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(raw, path)
        sections = parse_sections(body)
        blocks = parse_blocks(sections.get("script", ""), path)
        validate_dialogue(blocks, path)
        dialogue[fm["id"]] = {**fm, "script": blocks}
    return dialogue


def build_vocab() -> dict:
    vocab_path = CONTENT_ROOT / "vocab.md"
    raw = vocab_path.read_text(encoding="utf-8")
    _, body = parse_frontmatter(raw, vocab_path)
    entries: dict = {}
    current_id = None
    current: dict = {}
    for line in body.splitlines():
        m = re.match(r"^##\s+([a-z0-9-]+)\s*$", line)
        if m:
            if current_id is not None:
                entries[current_id] = current
            current_id = m.group(1)
            current = {}
            continue
        if current_id is None:
            continue
        m = re.match(r"^([a-z_][a-z0-9_]*):\s*(.*)$", line)
        if m:
            current[m.group(1)] = _coerce(m.group(2).strip())
    if current_id is not None:
        entries[current_id] = current
    return entries


def build_ui_strings() -> dict:
    path = CONTENT_ROOT / "ui" / "strings.md"
    raw = path.read_text(encoding="utf-8")
    _, body = parse_frontmatter(raw, path)
    strings: dict = {}
    current_key = None
    current: dict = {}
    multiline_key: str | None = None
    multiline_buf: list[str] = []
    for line in body.splitlines():
        if multiline_key is not None:
            if line.startswith("  ") or line == "":
                multiline_buf.append(line[2:] if line.startswith("  ") else "")
                continue
            current[multiline_key] = "\n".join(multiline_buf).rstrip()
            multiline_key = None
            multiline_buf = []
        m = re.match(r"^###\s+(.+)$", line)
        if m:
            if current_key is not None:
                strings[current_key] = current
            current_key = m.group(1).strip()
            current = {}
            continue
        if line.startswith("## ") or current_key is None:
            continue
        m = re.match(r"^(jp|en|jp_style):\s*(.*)$", line)
        if m:
            key, value = m.group(1), m.group(2).strip()
            if value == "|":
                multiline_key = key
                multiline_buf = []
            else:
                current[key] = _coerce(value) if value else ""
    if multiline_key is not None:
        current[multiline_key] = "\n".join(multiline_buf).rstrip()
    if current_key is not None:
        strings[current_key] = current
    return strings


def main() -> int:
    try:
        output = {
            "items": build_items(),
            "notices": build_notices(),
            "dialogue": build_dialogue(),
            "vocab": build_vocab(),
            "ui_strings": build_ui_strings(),
        }
    except BuildError as exc:
        print(f"build error: {exc}", file=sys.stderr)
        return 1
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"wrote {OUTPUT_PATH.relative_to(REPO_ROOT)}: "
        f"{len(output['items'])} items, "
        f"{len(output['notices'])} notices, "
        f"{len(output['dialogue'])} dialogues, "
        f"{len(output['vocab'])} vocab, "
        f"{len(output['ui_strings'])} ui strings"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
