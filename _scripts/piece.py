"""Prepare image content, check a batch, and verify its public deployment.

No AI calls, Git writes, publishing, or background service. See --help and
PUBLISHING.md for the short agent workflow. Pillow is needed only to prepare art.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen
from zoneinfo import ZoneInfo

import build_comedy
import image_pieces

ROOT = Path(__file__).resolve().parents[1]
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def prepare(args, root: Path = ROOT) -> str:
    """Prepare one source addition. Reject conflicts; an identical retry is safe."""
    lock = root / 'content/.piece.lock'
    try:
        with lock.open('x') as output:
            output.write(str(os.getpid()))
    except FileExistsError as error:
        raise ValueError('another preparation holds content/.piece.lock; check that process before retrying') from error
    try:
        return _prepare(args, root)
    finally:
        lock.unlink()


def _prepare(args, root: Path) -> str:
    from PIL import Image

    slug = args.slug if args.mode == 'illustrate' else args.slug or build_comedy.slugify(args.title)
    if not SLUG.fullmatch(slug):
        raise ValueError('provide a safe lowercase --slug with hyphens')
    if not args.alt.strip() or (args.mode == 'add' and not args.title.strip()):
        raise ValueError('title and alt must contain text')
    path = root / ('content/image-pieces.json' if args.mode == 'add' else 'content/comedy.json')
    before = path.read_bytes()
    data = json.loads(before)
    if args.mode == 'add':
        image_pieces.load_catalog(path, root)
        existing = next((p for p in data['pieces'] if p['slug'] == slug), None)
        if not existing and (root / 'is/writing' / slug).exists():
            raise ValueError(f'route already exists: {slug}')
        route = f'/is/writing/{slug}/'
        asset = f'/assets/paper/pieces/{slug}.webp'
    else:
        build_comedy.load_medium_data(path, root=root)
        post = next((p for p in data['posts'] if p['slug'] == slug), None)
        if post is None:
            raise ValueError(f'no existing comedy article: {slug}')
        existing = post.get('illustration')
        route = f'/wrote/{slug}/'
        asset = f'/assets/paper/illustrations/{slug}.webp'
    if existing:
        asset = existing['image']
    target = root / asset.lstrip('/')
    if not target.resolve().is_relative_to(root.resolve() / 'assets'):
        raise ValueError('asset must stay inside this checkout')

    with Image.open(args.image) as source:
        if getattr(source, 'n_frames', 1) != 1:
            raise ValueError('animated images need a separate presentation decision')
        if source.getexif().get(274, 1) != 1:
            raise ValueError('image has orientation metadata; normalize and review it before adding')
        source.load()
        original = source.convert('RGBA')
        color_profile = source.info.get('icc_profile', b'')
    width, height = original.size
    art = dict(image=asset, width=width, height=height, alt=args.alt.strip())
    if args.mode == 'add':
        today = datetime.now(ZoneInfo('Asia/Seoul')).date()
        stamp = args.date or (existing or {}).get('published_date') or today.isoformat()
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', stamp):
            raise ValueError('date must be yyyy-mm-dd')
        if date.fromisoformat(stamp) > today:
            raise ValueError('future publication dates are not supported')
        record = dict(slug=slug, title=args.title.strip(), published_date=stamp,
                      **art, caption=args.caption, featured=False)
        if args.show_title:
            record['show_title'] = True
        if args.mobile_panels:
            if width != 2 * height:
                raise ValueError('two square mobile panels require a 2:1 image')
            record['mobile_panels'] = 2
    else:
        record = art

    if existing:
        with Image.open(target) as saved:
            identical = saved.size == original.size and saved.convert('RGBA').tobytes() == original.tobytes()
        if existing == record and identical:
            return f'UNCHANGED {route}'
        raise ValueError(f'{slug} already exists with different content; review the replacement explicitly')

    # Conversion and all candidate validation precede the catalog replacement.
    # Exclusive asset creation cannot overwrite another batch's file.
    with tempfile.TemporaryDirectory(prefix='ajin-piece-') as directory:
        encoded = Path(directory) / 'image.webp'
        original.save(encoded, format='WEBP', lossless=True, quality=100, method=6,
                      exact=True, icc_profile=color_profile)
        with Image.open(encoded) as saved:
            if saved.size != original.size or saved.convert('RGBA').tobytes() != original.tobytes():
                raise ValueError('lossless conversion did not preserve the source pixels')
        # A killed preparation may leave a complete asset before its catalog
        # replacement. Reuse only the exact expected bytes, including metadata.
        recovered = target.exists()
        if recovered and target.read_bytes() != encoded.read_bytes():
            raise ValueError(f'asset already exists with different content: {asset}')
        target.parent.mkdir(parents=True, exist_ok=True)
        created = False
        candidate = None
        try:
            if not recovered:
                with target.open('xb') as output:
                    created = True
                    output.write(encoded.read_bytes())
            if args.mode == 'add':
                data['pieces'].insert(0, record)
            else:
                post['illustration'] = record
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                             prefix='.piece-', suffix='.json', delete=False) as output:
                candidate = Path(output.name)
                json.dump(data, output, ensure_ascii=False, indent=2)
                output.write('\n')
                output.flush()
                os.fsync(output.fileno())
            if args.mode == 'add':
                image_pieces.load_catalog(candidate, root)
            else:
                build_comedy.load_medium_data(candidate, root=root)
            if path.read_bytes() != before:
                raise ValueError('catalog changed during preparation; retry from current state')
            os.replace(candidate, path)
        except BaseException:
            if created:
                target.unlink(missing_ok=True)
            raise
        finally:
            if candidate:
                candidate.unlink(missing_ok=True)
    return f'READY {route} ({width}×{height}; {target.stat().st_size:,} bytes; pixels preserved)'


def run(command: list[str]) -> str:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        raise ValueError(f"{' '.join(command)} failed:\n{result.stdout}{result.stderr}")
    return result.stdout + result.stderr


def check() -> None:
    """One full batch check, with quiet successful builders and useful failures."""
    for script in ('build_comedy.py', 'build_essays.py', 'build_writes.py',
                   'build_wrote.py', 'build_root.py', 'build_sitemap.py'):
        run([sys.executable, f'_scripts/{script}'])
    report = run([sys.executable, '-m', 'unittest', 'discover', '-s', '_scripts', '-p', 'test_*.py'])
    print(next((line for line in report.splitlines() if line.startswith('Ran ')), 'Tests passed'))
    run(['node', '--test', '_scripts/test_cartoon_swipe.js', '_scripts/test_analytics.js'])
    run([sys.executable, '_scripts/build_sections.py', '--check'])
    run([sys.executable, '_scripts/build_root.py', '--check-home'])
    links = run([sys.executable, '_scripts/check_links.py'])
    print(next((line for line in links.splitlines() if line.startswith('OK:')), links.strip()))
    run(['git', 'diff', '--check'])
    print('PASS: generated pages, sources and sitemap rebuilt. Review changed artwork before publishing.')


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        value = values.get('src') if tag in ('img', 'script') else values.get('href') if tag == 'link' and values.get('rel') == 'stylesheet' else None
        if value and value.startswith('/') and not value.startswith('//'):
            self.paths.add(value.split('?', 1)[0])


def local_path(route: str, root: Path) -> Path:
    if not route.startswith('/') or route.startswith('//') or any(c in route for c in ('?', '#', '\\')):
        raise ValueError(f'expected a root-relative path without query or fragment: {route}')
    path = root / route.lstrip('/')
    path = path / 'index.html' if route.endswith('/') else path
    path = path.resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f'local file is missing or outside this checkout: {route}')
    return path


def fetch(route: str) -> bytes:
    with urlopen('https://ajin.im' + route, timeout=20) as response:
        if response.status != 200:
            raise ValueError(f'{route}: HTTP {response.status}')
        return response.read()


def verify_live(routes: list[str], *, root: Path = ROOT, reader=fetch) -> int:
    paths = set(routes) | {'/', '/is/writing/'}
    for route in list(paths):
        if not route.endswith('/'):
            raise ValueError('supply reader routes ending in /')
        parser = Assets()
        parser.feed(local_path(route, root).read_text())
        paths.update(parser.paths)
    expected = {route: local_path(route, root).read_bytes() for route in paths}

    def compare(route):
        if hashlib.sha256(reader(route)).digest() != hashlib.sha256(expected[route]).digest():
            raise ValueError(f'{route}: public bytes differ from this checkout')

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(compare, sorted(paths)))
    return len(paths)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest='mode', required=True)
    for mode in ('add', 'illustrate'):
        command = commands.add_parser(mode, help='add a cartoon' if mode == 'add' else 'illustrate an existing comedy article')
        command.add_argument('image', type=Path)
        command.add_argument('--alt', required=True)
        command.add_argument('--slug', required=mode == 'illustrate')
        if mode == 'add':
            command.add_argument('--title', required=True)
            command.add_argument('--date', help='defaults to today in Asia/Seoul')
            command.add_argument('--caption', default='')
            command.add_argument('--show-title', action='store_true')
            command.add_argument('--mobile-panels', type=int, choices=[2])
    commands.add_parser('check', help='rebuild and validate once for the entire batch')
    live = commands.add_parser('verify-live', help='read-only public page and asset checks')
    live.add_argument('routes', nargs='+')
    live.add_argument('--wait', type=int, default=0, metavar='SECONDS', help='bounded wait for CDN propagation')
    return result


def main() -> None:
    args = parser().parse_args()
    try:
        if args.mode in ('add', 'illustrate'):
            branch = run(['git', 'branch', '--show-current']).strip()
            if not branch or branch in ('master', 'main'):
                raise ValueError('prepare images on a feature branch, not the live checkout')
            print(prepare(args))
        elif args.mode == 'check':
            check()
        else:
            if not 0 <= args.wait <= 600:
                raise ValueError('--wait must be between 0 and 600 seconds')
            deadline = time.monotonic() + args.wait
            while True:
                try:
                    count = verify_live(args.routes)
                    print(f'LIVE: {count} public pages/assets match this checkout; Home and Writing included.')
                    break
                except (OSError, ValueError):
                    if time.monotonic() >= deadline:
                        raise
                    time.sleep(min(10, max(0, deadline - time.monotonic())))
    except (OSError, ValueError, ImportError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
