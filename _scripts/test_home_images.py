"""Image publishing must update discovery without changing legacy prose routes."""
import copy
import unittest
from unittest.mock import patch

import image_pieces
import paper_site


class ImageDiscoveryTest(unittest.TestCase):
    def test_new_piece_enters_archive_without_replacing_the_pinned_home_art(self):
        catalog = copy.deepcopy(image_pieces.load_catalog())
        extra = {**catalog['pieces'][0], 'slug':'another-piece', 'title':'Another piece',
                 'href':'/is/writing/another-piece/', 'published_date':'2026-11-10', 'featured':True}
        catalog['pieces'].append(extra)
        with patch.object(image_pieces, 'load_catalog', return_value=catalog):
            home = paper_site.home_image_lead()
            archive = paper_site.render_writing([]).split('<ol id="writing-list"')[1].split('</ol>')[0]
        self.assertNotIn('another-piece', home)
        self.assertLess(archive.index('/is/writing/another-piece/'), archive.index('/wrote/'))
        self.assertIn('href="/is/writing/austen-at-work/" target="_self"', home)
        self.assertNotIn(image_pieces.CREDIT, home)
        self.assertNotIn('cartoon-dialog', home)

    def test_caption_is_text_not_html(self):
        catalog = copy.deepcopy(image_pieces.load_catalog())
        featured = next(piece for piece in catalog['pieces'] if piece['featured'])
        featured['caption'] = '</script><p>Example & more</p>'
        with patch.object(image_pieces, 'load_catalog', return_value=catalog):
            home = paper_site.home_image_lead()
        self.assertNotIn(featured['caption'], home)
        self.assertIn('&lt;/script&gt;&lt;p&gt;Example &amp; more&lt;/p&gt;', home)


if __name__ == '__main__':
    unittest.main()
