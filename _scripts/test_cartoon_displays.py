"""Small display assets never own the artwork, identity or editorial choices."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PIL import Image

import cartoon_collection
import cartoon_displays as displays
import image_pieces
import piece


class CartoonDisplayTest(unittest.TestCase):
    def setUp(self):
        staging = TemporaryDirectory()
        self.addCleanup(staging.cleanup)
        self.root = Path(staging.name)
        self.source = self.root / 'assets/paper/pieces/fixture.png'
        self.source.parent.mkdir(parents=True)
        self.record = {
            'slug': 'sample', 'image': '/assets/paper/pieces/fixture.png', 'alt': 'Exact words',
            'width': 700, 'height': 350, 'title': 'One title', 'caption': '',
            'href': '/is/writing/sample/', 'published_date': '2026-11-21',
        }
        self.catalog = {'pieces': [self.record]}
        self.write_art(115)
        self.variants = self.root / displays.BASE / 'sample'

    def write_art(self, value):
        Image.new('RGBA', (700, 350), (44, 88, value, 141)).save(self.source)

    def test_generated_derivatives_are_small_and_repeatable_and_original_is_not_changed(self):
        original = self.source.read_bytes()
        displays.generate(self.catalog, self.root)
        record = displays.for_render(self.catalog, self.root, require=True)['pieces'][0]
        self.assertEqual([width for _, width in record['display_candidates']], [480, 640, 700])
        before = {}
        for relative, width in record['display_candidates']:
            f = self.root / relative.lstrip('/').split('?')[0]
            with Image.open(f) as im:
                self.assertEqual(im.size, (width, width // 2))
                self.assertEqual(im.getchannel('A').getextrema(), (141, 141))
            before[f] = (f.read_bytes(), f.stat().st_mtime_ns)
        displays.generate(self.catalog, self.root)
        self.assertEqual(before, {f: (f.read_bytes(), f.stat().st_mtime_ns) for f in before})
        self.assertEqual(self.source.read_bytes(), original)
        reader = image_pieces.render_piece(record)
        slide = cartoon_collection.slide_page([record], 0)
        for page in (reader, slide):
            self.assertIn('srcset=', page)
            self.assertIn(f'href="{record["image"]}"', page)
            self.assertIn(f'content="https://ajin.im{record["image"]}"', page)
            self.assertIn(f'data-share-url="https://ajin.im{record["href"]}"', page)

    def test_stale_source_and_stale_derived_bytes_require_a_rebuild(self):
        displays.generate(self.catalog, self.root)
        old = displays.for_render(self.catalog, self.root, require=True)
        self.write_art(218)
        with self.assertRaisesRegex(ValueError, 'stale'):
            displays.for_render(self.catalog, self.root, require=True)
        displays.generate(self.catalog, self.root)
        new = displays.for_render(self.catalog, self.root, require=True)
        self.assertNotEqual(old, new)
        (self.variants / '480.webp').write_bytes(b'damaged')
        with self.assertRaisesRegex(ValueError, 'stale'):
            displays.for_render(self.catalog, self.root, require=True)

    def test_retired_piece_removes_only_its_generated_assets(self):
        displays.generate(self.catalog, self.root)
        remaining = {'pieces': [{**self.record, 'slug': 'second'}]}
        displays.generate(remaining, self.root)
        self.assertFalse(self.variants.exists())
        self.assertTrue(self.source.exists())
        displays.for_render(remaining, self.root, require=True)

    def test_split_panel_sizes_and_live_parser_cover_all_viewport_candidates_and_original(self):
        self.record['mobile_panels'] = 2
        displays.generate(self.catalog, self.root)
        item = displays.for_render(self.catalog, self.root, require=True)['pieces'][0]
        for html in (image_pieces.render_piece(item), cartoon_collection.slide_page([item], 0)):
            self.assertEqual(html.count('calc(200vw - 64px)'), 3)
            parser = piece.Assets()
            parser.feed(html)
            self.assertIn(item['image'], parser.paths)
            for url, _ in item['display_candidates']:
                self.assertIn(url, parser.paths)
