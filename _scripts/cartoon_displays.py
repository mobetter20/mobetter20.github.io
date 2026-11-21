"""Build compact display copies without changing original cartoon artwork."""
from __future__ import annotations

from hashlib import sha256
from html import escape
import io
import json
from pathlib import Path
import re
import shutil

BASE = "assets/paper/cartoon-display"
RECIPE = "webp-screen-v1-q88-lanczos"
WIDTHS = (480, 640, 960, 1280)
GALLERY = "(max-width: 650px) calc(100vw - 32px), (max-width: 999px) min(700px, calc(100vw - 64px)), min(564px, calc((100vw - 112px) / 2))"
WRITING = "(max-width: 650px) min(310px, calc(100vw - 32px)), 310px"


def widths(piece):
    limit = piece["width"] if piece.get("mobile_panels") == 2 else min(piece["width"], WIDTHS[-1])
    return sorted({min(limit, width) for width in WIDTHS} | {limit})


def belongs_to_slug(path, slug):
    return bool(re.fullmatch(re.escape(f"{BASE}/{slug}/") + r"(?:manifest\.json|[1-9][0-9]*\.webp)", path))


def asset_paths(piece):
    directory = f"{BASE}/{piece['slug']}"
    return {f"{directory}/manifest.json", *(f"{directory}/{w}.webp" for w in widths(piece))}


def sizes(piece, context):
    if context == "gallery":
        return GALLERY
    if context == "writing":
        return WRITING
    mobile = "calc(200vw - 64px)" if piece.get("mobile_panels") == 2 else "calc(100vw - 32px)"
    ratio = piece["width"] / piece["height"]
    if context == "reader":
        return f"(max-width: 650px) {mobile}, (min-height: 650px) min(844px, calc(100vw - 56px), {70 * ratio:.4f}vh), min(844px, calc(100vw - 56px))"
    if context == "slide":
        return f"(max-width: 650px) {mobile}, min(808px, calc(100vw - 192px), max({460 * ratio:.4f}px, calc({100 * ratio:.4f}vh - {220 * ratio:.4f}px)))"
    raise ValueError(f"unknown cartoon display context {context}")


def _expected(piece, root):
    source = root / piece["image"].lstrip("/")
    digest = sha256(source.read_bytes()).hexdigest()
    token = sha256((RECIPE + ":" + digest).encode()).hexdigest()[:16]
    return source, root / BASE / piece["slug"], digest, token


def _read_current(piece, root):
    _, target, digest, token = _expected(piece, root)
    try:
        info = json.loads((target / "manifest.json").read_text())
        if info["recipe"] != RECIPE or info["source_sha256"] != digest:
            return None
        if sorted(int(k) for k in info["variants"]) != widths(piece):
            return None
        for w in widths(piece):
            binary = (target / f"{w}.webp").read_bytes()
            if sha256(binary).hexdigest() != info["variants"][str(w)]:
                return None
    except (OSError, KeyError, TypeError, ValueError):
        return None
    return [(f"/{BASE}/{piece['slug']}/{w}.webp?v={token}", w) for w in widths(piece)]


def generate(catalog, root):
    """Only explicit image publishing encodes files; normal prose/root builds do not."""
    from PIL import Image

    active = {piece["slug"] for piece in catalog["pieces"]}
    for piece in catalog["pieces"]:
        if _read_current(piece, root) is not None:
            continue
        source, target, digest, _ = _expected(piece, root)
        target.mkdir(exist_ok=True, parents=True)
        variants = {}
        with Image.open(source) as original:
            mode = "RGBA" if "transparency" in original.info or "A" in original.getbands() else "RGB"
            base = original.convert(mode)
            for w in widths(piece):
                h = max(1, round(base.height * w / base.width))
                out = base.resize((w, h), Image.Resampling.LANCZOS) if w != base.width else base
                payload = io.BytesIO()
                profile = original.info.get("icc_profile")
                params = {"icc_profile": profile} if profile else {}
                out.save(payload, "WEBP", quality=88, method=6, exact=True, **params)
                data = payload.getvalue()
                (target / f"{w}.webp").write_bytes(data)
                variants[str(w)] = sha256(data).hexdigest()
        for leftover in target.glob("*.webp"):
            if leftover.stem not in variants and belongs_to_slug(leftover.relative_to(root).as_posix(), piece["slug"]):
                leftover.unlink()
        (target / "manifest.json").write_text(json.dumps({
            "recipe": RECIPE, "source_sha256": digest, "variants": variants,
        }, indent=2) + "\n")
    # A withdrawn piece must not leave generated display art in the site tree.
    for directory in (root / BASE).iterdir():
        if not directory.is_dir() or directory.name in active:
            continue
        if all(belongs_to_slug(p.relative_to(root).as_posix(), directory.name) for p in directory.iterdir()):
            shutil.rmtree(directory)


def for_render(catalog, root, *, require=False):
    pieces = []
    for piece in catalog["pieces"]:
        if require:
            candidates = _read_current(piece, root)
            if candidates is None:
                raise ValueError(f"Missing or stale screen artwork for {piece['slug']}; run _scripts/piece.py check")
        else:
            candidates = _read_current(piece, root) if (root / piece["image"].lstrip("/")).is_file() else None
        pieces.append({**piece, "display_candidates": candidates} if candidates else piece)
    if require:
        active = {piece["slug"] for piece in pieces}
        for directory in (root / BASE).iterdir():
            if directory.is_dir() and directory.name not in active:
                raise ValueError(f"Unexpected screen artwork for {directory.name}; run _scripts/piece.py check")
    return {**catalog, "pieces": pieces}


def img(piece, context, *, css_class="", alt=None, lazy=False, high=False):
    candidates = piece.get("display_candidates")
    attrs = []
    if css_class:
        attrs.append(f'class="{escape(css_class, quote=True)}"')
    if candidates:
        fallback = next((url for url, w in candidates if w >= 640), candidates[-1][0])
        attrs.append(f'src="{escape(fallback, quote=True)}"')
        srcset = ", ".join(f"{url} {w}w" for url, w in candidates)
        attrs.append(f'srcset="{escape(srcset, quote=True)}"')
        attrs.append(f'sizes="{escape(sizes(piece, context), quote=True)}"')
    else:
        attrs.append(f'src="{escape("/" + piece["image"].lstrip("/"), quote=True)}"')
    attrs += [
        f'width="{piece["width"]}"', f'height="{piece["height"]}"',
        f'alt="{escape(piece["alt"] if alt is None else alt, quote=True)}"', 'decoding="async"',
        'loading="lazy"' if lazy else 'loading="eager"',
    ]
    if high and not lazy:
        attrs.append('fetchpriority="high"')
    return "<img " + " ".join(attrs) + ">"
