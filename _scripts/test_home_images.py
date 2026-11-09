"""Image publishing must update discovery without changing legacy prose routes."""
import copy
import json
import re
import unittest
from unittest.mock import patch

import image_pieces
import paper_site


class ImageDiscoveryTest(unittest.TestCase):
    def test_new_piece_enters_archive_but_only_eligible_art_rotates(self):
        catalog = copy.deepcopy(image_pieces.load_catalog())
        extra = {**catalog['pieces'][0], 'slug':'another-piece', 'title':'Another piece',
                 'href':'/is/writing/another-piece/', 'published_date':'2026-11-10', 'featured':False}
        catalog['pieces'].append(extra)
        with patch.object(image_pieces, 'load_catalog', return_value=catalog):
            home = paper_site.home_image_lead()
            archive = paper_site.render_writing([]).split('<ol id="writing-list"')[1].split('</ol>')[0]
        payload = json.loads(re.search(r'id="home-image-catalog">(.*?)</script>', home, re.S)[1])
        self.assertNotIn('another-piece', [item['slug'] for item in payload['pieces']])
        self.assertEqual(payload['fallback']['href'], '/is/writing/austen-at-work/')
        self.assertLess(archive.index('/is/writing/another-piece/'), archive.index('/wrote/'))
        self.assertIn('href="/is/writing/austen-at-work/" target="_self"', home)
        self.assertEqual(home.count(image_pieces.CREDIT), 1)
        self.assertNotIn('cartoon-dialog', home)

    def test_caption_cannot_escape_embedded_catalog(self):
        catalog = copy.deepcopy(image_pieces.load_catalog())
        featured = next(piece for piece in catalog['pieces'] if piece['featured'])
        featured['caption'] = '</script><p>Example & more</p>'
        with patch.object(image_pieces, 'load_catalog', return_value=catalog):
            home = paper_site.home_image_lead()
        payload = re.search(r'id="home-image-catalog">(.*?)</script>', home, re.S)[1]
        self.assertNotIn('<', payload)
        self.assertEqual(json.loads(payload)['pieces'][0]['caption'], featured['caption'])


if __name__ == '__main__':
    unittest.main()
