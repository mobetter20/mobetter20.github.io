#!/usr/bin/env python3
"""Check the exact, source-audited Bird to Bird export without regenerating it."""

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = REPO_ROOT / "is/building/bird-to-bird"
PIN_FILE = REPO_ROOT / "_scripts/bird-to-bird/expected-manifest.sha256"
FIXED_FILES = frozenset({
    "index.html", "credits.html",
    "daily/index.html", "daily/boot.js", "daily/app.js", "daily/state.js",
    "daily/styles.css", "daily/content.json", "daily/notes.json", "daily/media.json",
    "route/engine.js", "route/world-lexicon.js", "prototype/styles.css",
    "prototype/assets/fonts/spectral-regular.ttf",
    "prototype/assets/fonts/spectral-medium.ttf",
    "prototype/assets/fonts/spectral-italic.ttf",
    "prototype/assets/fonts/spectral-OFL.txt",
    "prototype/assets/fonts/spectral-SOURCE.txt",
    "assets/fonts/space-grotesk-500-latin.woff2",
    "assets/fonts/OFL-Space-Grotesk.txt",
})
REUSED_PHOTOS = frozenset(
    f"route/assets/name-notes/{name}.jpg" for name in (
        "common-gull", "great-egret", "little-egret", "little-gull",
        "little-owl", "sooty-gull", "sooty-owl",
    )
)
BIRD_ASSET = re.compile(r"daily/assets/birds/avibase-[0-9A-F]{8}(?:-thumb)?\.(?:jpe?g|png)")
SHA256 = re.compile(r"[0-9a-f]{64}")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def allowed_payload_path(name):
    if not isinstance(name, str) or "\\" in name:
        return False
    path = PurePosixPath(name)
    if path.is_absolute() or path.as_posix() != name or ".." in path.parts:
        return False
    return name in FIXED_FILES or name in REUSED_PHOTOS or bool(BIRD_ASSET.fullmatch(name))


def check_release(directory=RELEASE_DIR, pin_file=PIN_FILE):
    directory, pin_file = Path(directory), Path(pin_file)
    require(directory.is_dir() and not directory.is_symlink(), "Release must be a real directory")
    require(pin_file.is_file() and not pin_file.is_symlink(), "Missing regular manifest pin")
    expected_sha = pin_file.read_text(encoding="ascii").strip()
    require(bool(SHA256.fullmatch(expected_sha)), "Invalid manifest SHA-256 pin")

    # Scan before reading the manifest so even a linked manifest is rejected.
    actual = set()
    for path in directory.rglob("*"):
        relative = path.relative_to(directory).as_posix()
        require(not path.is_symlink(), f"Symlink in release: {relative}")
        if path.is_dir():
            continue
        require(path.is_file(), f"Non-regular release file: {relative}")
        require(relative == "manifest.json" or allowed_payload_path(relative), f"Disallowed release path: {relative}")
        actual.add(relative)

    manifest_path = directory / "manifest.json"
    require("manifest.json" in actual, "Missing manifest.json")
    manifest_bytes = manifest_path.read_bytes()
    require(hashlib.sha256(manifest_bytes).hexdigest() == expected_sha, "Manifest differs from the approved SHA-256 pin")
    manifest = json.loads(manifest_bytes)
    require(manifest.get("schemaVersion") == 1, "Unsupported manifest schema")
    require(manifest.get("generator") == "bird-to-bird-local-release-v1", "Unexpected release generator")
    records = manifest.get("files")
    require(isinstance(records, list) and records, "Manifest needs payload records")
    expected = set()
    for record in records:
        require(isinstance(record, dict), "Invalid manifest file record")
        name = record.get("path")
        require(allowed_payload_path(name), f"Disallowed manifest path: {name}")
        require(name not in expected, f"Duplicate manifest path: {name}")
        require(type(record.get("bytes")) is int and record["bytes"] >= 0, f"Invalid byte count: {name}")
        require(isinstance(record.get("sha256"), str) and bool(SHA256.fullmatch(record["sha256"])), f"Invalid file hash: {name}")
        expected.add(name)
    require(FIXED_FILES <= expected, "Manifest omits required runtime files")
    require(actual == expected | {"manifest.json"}, f"Release file set differs: missing={sorted(expected - actual)}, extra={sorted(actual - expected - {'manifest.json'})}")
    for record in records:
        payload = (directory / record["path"]).read_bytes()
        require(len(payload) == record["bytes"], f"Byte count differs: {record['path']}")
        require(hashlib.sha256(payload).hexdigest() == record["sha256"], f"File hash differs: {record['path']}")
    return {"files": len(actual), "manifestSha256": expected_sha, "verified": True}


if __name__ == "__main__":
    try:
        print(json.dumps(check_release()))
    except (ValueError, OSError) as error:
        print(f"Bird to Bird integrity check failed: {error}", file=sys.stderr)
        sys.exit(1)
