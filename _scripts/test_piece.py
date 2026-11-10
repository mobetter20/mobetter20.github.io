"""Content preparation must be repeatable and preserve existing published work."""
from argparse import Namespace
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

import build_comedy
import image_pieces
import piece


class PieceWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'content').mkdir()
        (self.root / 'assets/paper').mkdir(parents=True)
        self.source = self.root / 'source.png'
        Image.new('RGBA', (16, 8), (70, 90, 110, 128)).save(self.source)
        Image.new('RGB', (8, 8), 'white').save(self.root / 'assets/paper/fallback.png')
        self.catalog = self.root / 'content/image-pieces.json'
        self.catalog.write_text(json.dumps(dict(schema_version=1, fallback_slug='fallback', pieces=[
            dict(slug='fallback', title='Fallback', published_date='2026-11-08', image='/assets/paper/fallback.png',
                 width=8, height=8, alt='A square', caption='', featured=True)
        ])))
        self.comedy = self.root / 'content/comedy.json'
        self.article = dict(slug='desk', title='Desk', subtitle='Options', date='2023-11-30',
                            canonical='https://medium.com/example', body_html='<h4>Mug 1</h4><p>Original words.</p>')
        self.comedy.write_text(json.dumps(dict(schema_version=1, posts=[self.article])))

    def args(self, mode='add'):
        return Namespace(mode=mode, image=self.source, slug='new' if mode=='add' else 'desk',
                         title='New', alt='A translucent rectangle', date='2026-11-09',
                         caption='', show_title=False, mobile_panels=None)

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    def test_add_preserves_pixels_and_keeps_home_selection(self):
        piece.prepare(self.args(), self.root)
        data = image_pieces.load_catalog(self.catalog, self.root)
        new = data['pieces'][0]
        self.assertEqual(new['published_date'], '2026-11-09')
        self.assertFalse(new['featured'])
        self.assertNotIn('mobile_panels', new)  # A 2:1 shape alone is not a panel decision.
        self.assertNotIn('show_title', new)
        self.assertEqual([p['slug'] for p in data['pieces'] if p['featured']], ['fallback'])
        with Image.open(self.source) as source, Image.open(self.root / new['image'].lstrip('/')) as saved:
            self.assertEqual(source.convert('RGBA').tobytes(), saved.convert('RGBA').tobytes())
        before = self.snapshot()
        self.assertTrue(piece.prepare(self.args(), self.root).startswith('UNCHANGED'))
        self.assertEqual(before, self.snapshot())

    def test_conflicting_retry_and_bad_input_do_not_change_files(self):
        piece.prepare(self.args(), self.root)
        for key, value in [('title','Different'), ('alt',''), ('slug','../escape'),
                           ('date','2026-02-30'), ('date','9999-12-31')]:
            args = self.args()
            setattr(args, key, value)
            before = self.snapshot()
            with self.assertRaises(ValueError):
                piece.prepare(args, self.root)
            self.assertEqual(before, self.snapshot())
        (self.root / 'is/writing/taken').mkdir(parents=True)
        args = self.args(); args.slug = 'taken'
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'route already exists'):
            piece.prepare(args, self.root)
        self.assertEqual(before, self.snapshot())

    def test_validation_failure_rolls_back_only_its_new_asset(self):
        original = image_pieces.load_catalog
        calls = 0
        def fail_candidate(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise ValueError('candidate rejected')
            return original(*args, **kwargs)
        before = self.snapshot()
        with patch.object(image_pieces, 'load_catalog', side_effect=fail_candidate):
            with self.assertRaisesRegex(ValueError, 'candidate rejected'):
                piece.prepare(self.args(), self.root)
        self.assertEqual(before, self.snapshot())

    def test_lock_refuses_concurrent_preparation(self):
        lock = self.root / 'content/.piece.lock'
        lock.write_text('another process')
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'another preparation'):
            piece.prepare(self.args(), self.root)
        self.assertEqual(before, self.snapshot())

    def test_interrupted_preparation_reuses_only_the_exact_leftover_asset(self):
        before = self.catalog.read_bytes()
        piece.prepare(self.args(), self.root)
        asset = self.root / 'assets/paper/pieces/new.webp'
        timestamp = asset.stat().st_mtime_ns
        self.catalog.write_bytes(before)  # Simulate interruption before catalog replacement.
        piece.prepare(self.args(), self.root)
        self.assertEqual(asset.stat().st_mtime_ns, timestamp)
        self.catalog.write_bytes(before)
        Image.new('RGB', (16, 8), 'red').save(asset, format='WEBP', lossless=True)
        snapshot = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'different content'):
            piece.prepare(self.args(), self.root)
        self.assertEqual(snapshot, self.snapshot())

    def test_illustration_preserves_article_and_survives_medium_import(self):
        args = self.args('illustrate')
        piece.prepare(args, self.root)
        post = json.loads(self.comedy.read_text())['posts'][0]
        self.assertEqual({k:v for k,v in post.items() if k != 'illustration'}, self.article)
        before = self.snapshot()
        self.assertTrue(piece.prepare(args, self.root).startswith('UNCHANGED'))
        self.assertEqual(before, self.snapshot())
        with patch.object(build_comedy, 'REPO_ROOT', self.root):
            loaded = build_comedy.load_medium_data(self.comedy)
            imported = [replace(loaded[0], illustration=None)]
            build_comedy.write_medium_data(imported, self.comedy)
            self.assertEqual(build_comedy.load_medium_data(self.comedy)[0].illustration, post['illustration'])

    def test_illustration_schema_and_social_preview(self):
        piece.prepare(self.args('illustrate'), self.root)
        post = build_comedy.load_medium_data(self.comedy, root=self.root)[0]
        rendered = build_comedy.build_page(post)
        self.assertLess(rendered.index('<figure'), rendered.index('<h4>Mug 1'))
        self.assertIn('<p>Original words.</p>', rendered)
        self.assertIn('<figcaption>Illustration generated with AI.</figcaption>', rendered)
        self.assertIn('<a href="/assets/paper/illustrations/desk.webp" target="_self" aria-label="View illustration full size"><img', rendered)
        self.assertNotIn('View full size</a>', rendered)
        self.assertIn('https://ajin.im/wrote/desk/', rendered)
        self.assertIn('https://ajin.im/assets/paper/illustrations/desk.webp', rendered)
        self.assertIn('summary_large_image', rendered)
        self.assertIn('name="twitter:image"', rendered)
        self.assertNotIn('prose-images.css', build_comedy.build_page(replace(post, illustration=None)))
        for changes in ({'width': True}, {'height': 999}, {'alt': ''}, {'extra': 'field'},
                        {'image':'/assets/../../outside.png'}):
            with self.assertRaises((ValueError, OSError)):
                build_comedy.validate_illustration({**post.illustration, **changes}, self.root)

    def test_live_verification_checks_reader_assets_and_shared_entrances(self):
        for path in ('index.html', 'is/writing/index.html', 'wrote/desk/index.html'):
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('<img src="/assets/paper/fallback.png"><link rel="stylesheet" href="/style.css?v=one"><script src="/slide.js?v=one"></script>')
        (self.root / 'style.css').write_text('body{}')
        (self.root / 'slide.js').write_text('/* gesture controller */')
        requested = set()
        def reader(route):
            requested.add(route)
            return piece.local_path(route, self.root).read_bytes()
        self.assertEqual(piece.verify_live(['/wrote/desk/'], root=self.root, reader=reader), 6)
        self.assertEqual(requested, {'/', '/is/writing/', '/wrote/desk/', '/style.css', '/slide.js', '/assets/paper/fallback.png'})
        with self.assertRaisesRegex(ValueError, 'public bytes differ'):
            piece.verify_live(['/wrote/desk/'], root=self.root, reader=lambda route:b'stale')
        with self.assertRaises(ValueError):
            piece.local_path('/../../outside', self.root)


if __name__ == '__main__':
    unittest.main()
