import copy
from html import escape
import re
import unittest

import cartoon_collection
import image_pieces
import build_sitemap


class CartoonCollectionTest(unittest.TestCase):
    def test_catalog_addition_enters_overview_and_sequence(self):
        catalog = copy.deepcopy(image_pieces.load_catalog())
        extra = {**catalog['pieces'][0], 'slug':'collection-fixture', 'title':'Collection fixture',
                 'href':'/is/writing/collection-fixture/', 'published_date':'2026-12-01', 'featured':False}
        catalog['pieces'].append(extra)
        pages = cartoon_collection.expected_pages(catalog)
        overview = pages['is/writing/cartoons/index.html']
        self.assertIn('collection-fixture', overview)
        self.assertIn('/is/writing/cartoons/slides/collection-fixture/#cartoon', overview)
        self.assertIn('is/writing/cartoons/slides/collection-fixture/index.html', pages)
        self.assertEqual(overview.count('loading="eager"'), 2)
        self.assertEqual(overview.count('loading="lazy"'), 10)
        self.assertIn('1 / 12', pages['is/writing/cartoons/slides/collection-fixture/index.html'])

    def test_sequence_bounds_and_entry_alias(self):
        catalog = image_pieces.load_catalog()
        pieces = cartoon_collection.ordered(catalog)
        pages = cartoon_collection.expected_pages(catalog)
        first = pages[f'is/writing/cartoons/slides/{pieces[0]["slug"]}/index.html']
        last = pages[f'is/writing/cartoons/slides/{pieces[-1]["slug"]}/index.html']
        self.assertIn('slide-arrow-spacer slide-previous', first)
        self.assertIn('slide-arrow-spacer slide-next', last)
        self.assertEqual(pages['is/writing/cartoons/slides/index.html'], first)
        for page in pages.values():
            if 'class="slide-shell wrap"' in page:
                self.assertIn(f'data-first-slide="/is/writing/cartoons/slides/{pieces[0]["slug"]}/"', page)

    def test_no_empty_catalog_and_slide_canonical_metadata(self):
        with self.assertRaisesRegex(ValueError, 'at least one'):
            cartoon_collection.expected_pages({'pieces': []})
        piece = cartoon_collection.ordered(image_pieces.load_catalog())[0]
        page = cartoon_collection.slide_page([piece], 0)
        self.assertIn(f'<link rel="canonical" href="https://ajin.im{piece["href"]}">', page)
        self.assertIn(f'<meta property="og:image" content="https://ajin.im{piece["image"]}">', page)
        self.assertIn(f'<meta property="og:image:width" content="{piece["width"]}">', page)
        self.assertIn(f'<meta property="og:image:height" content="{piece["height"]}">', page)
        self.assertNotIn('noindex', page)

    def test_every_slide_shares_its_canonical_piece_not_the_collection(self):
        pieces = cartoon_collection.ordered(image_pieces.load_catalog())
        for index, piece in enumerate(pieces):
            page = cartoon_collection.slide_page(pieces, index)
            self.assertEqual(page.count('data-share-url='), 1)
            self.assertIn(f'data-share-url="https://ajin.im{piece["href"]}"', page)
            self.assertIn(f'data-share-title="{escape(piece["title"], quote=True)}"', page)
            self.assertIn('class="piece-share" hidden', page)
            self.assertLess(page.index('/share.js?'), page.index('/cartoons.js?'))
        overview = cartoon_collection.overview_page(pieces)
        self.assertNotIn('data-share-url=', overview)
        self.assertNotIn('/share.js?', overview)

    def test_phone_panels_keep_the_native_enlargement_link(self):
        piece = next(p for p in image_pieces.load_catalog()['pieces'] if p.get('mobile_panels') == 2)
        page = cartoon_collection.slide_page([piece], 0)
        art_link = re.search(r'<a class="slide-image-link".*?</a>', page, re.S).group(0)
        self.assertIn('class="slide-panels"', art_link)
        self.assertIn(f'href="{piece["image"]}"', art_link)
        self.assertIn('target="_blank"', art_link)

    def test_sitemap_keeps_canonical_readers_and_collection_only(self):
        self.assertFalse(build_sitemap.is_excluded('is/writing/cartoons/index.html'))
        for piece in image_pieces.load_catalog()['pieces']:
            self.assertFalse(build_sitemap.is_excluded(f'is/writing/{piece["slug"]}/index.html'))
            self.assertTrue(build_sitemap.is_excluded(f'is/writing/cartoons/slides/{piece["slug"]}/index.html'))
        self.assertTrue(build_sitemap.is_excluded('is/writing/cartoons/slides/index.html'))


if __name__ == '__main__':
    unittest.main()
