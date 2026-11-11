"""Validation and render contracts for image-led Writing pieces."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import build_sections
import image_pieces


def png(width: int, height: int) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + (13).to_bytes(4, "big") + b"IHDR" + width.to_bytes(4, "big") + height.to_bytes(4, "big")


class ImagePiecesTest(unittest.TestCase):
    def make_catalog(self, root: Path, *, pieces=None, fallback_slug="first") -> Path:
        image = root / "assets" / "paper" / "first.png"
        image.parent.mkdir(parents=True)
        image.write_bytes(png(7, 9))
        pieces = pieces or [{
            "slug": "first", "title": "First piece", "published_date": "2026-11-09",
            "image": "assets/paper/first.png", "width": 7, "height": 9,
            "alt": "A first image", "caption": "", "featured": True,
        }]
        path = root / "content" / "image-pieces.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"schema_version": 1, "fallback_slug": fallback_slug, "pieces": pieces}))
        return path

    def test_catalog_validates_dimensions_and_returns_public_href(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = image_pieces.load_catalog(self.make_catalog(root), root)
            self.assertEqual(catalog["pieces"][0]["href"], "/is/writing/first/")
            data = json.loads((root / "content/image-pieces.json").read_text())
            data["pieces"][0]["width"] = 8
            (root / "content/image-pieces.json").write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "dimensions"):
                image_pieces.load_catalog(root / "content/image-pieces.json", root)

    def test_catalog_rejects_bad_dates_and_route_collisions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.make_catalog(root)
            data = json.loads(path.read_text())
            data["pieces"][0]["published_date"] = "2026-02-30"
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "published_date"):
                image_pieces.load_catalog(path, root)
            data["pieces"][0]["published_date"] = ""
            path.write_text(json.dumps(data))
            occupied = root / "is/writing/first"
            occupied.mkdir(parents=True)
            (occupied / "index.html").write_text("a prose page")
            with self.assertRaisesRegex(ValueError, "collides"):
                image_pieces.load_catalog(path, root)

    def test_reader_contains_accessible_art_and_social_metadata(self):
        piece = {
            "slug": "first", "title": "First piece", "published_date": "",
            "image": "assets/paper/first.png", "width": 7, "height": 9,
            "alt": "A first image", "caption": "A caption", "featured": True,
            "href": "/is/writing/first/",
        }
        page = image_pieces.render_piece(piece)
        self.assertIn(image_pieces.GENERATOR_MARKER, page)
        self.assertIn('class="read-page image-piece"', page)
        self.assertIn('class="piece-title"', page)
        self.assertEqual(page.count('href="/is/writing/cartoons/#first" target="_self"'), 1)
        self.assertEqual(page.count('href="/is/writing/#all" target="_self"'), 1)
        self.assertIn('<footer class="site-foot piece-actions"><a class="back" href="/is/writing/#all"', page)
        self.assertEqual(page.count('data-share-url="https://ajin.im/is/writing/first/"'), 1)
        self.assertIn('data-share-title="First piece"', page)
        self.assertNotIn('mailto:', page)
        self.assertNotIn('View full size</a>', page)
        self.assertIn('href="/assets/paper/first.png" target="_self"', page)
        self.assertIn('aria-label="View First piece full size"', page)
        self.assertIn('width="7" height="9" alt="A first image"', page)
        self.assertIn('<figcaption>A caption</figcaption>', page)
        self.assertIn(image_pieces.CREDIT, page)
        self.assertIn('property="og:image:width" content="7"', page)
        self.assertIn('name="twitter:card" content="summary_large_image"', page)

    def test_mobile_panels_are_explicit_and_reject_ambiguous_layouts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.make_catalog(root)
            data = json.loads(path.read_text())
            piece = data['pieces'][0]
            piece.update(width=18, height=9, mobile_panels=2)
            (root / 'assets/paper/first.png').write_bytes(png(18, 9))
            path.write_text(json.dumps(data))
            loaded = image_pieces.load_catalog(path, root)['pieces'][0]
            page = image_pieces.render_piece(loaded)
            self.assertIn('class="piece-complete"', page)
            self.assertEqual(page.count('class="piece-panel" aria-hidden="true"'), 2)
            self.assertIn('class="piece-panels" role="img" aria-label="A first image"', page)
            self.assertIn('href="/assets/paper/first.png" target="_self"', page)
            for bad in (1, 3, True, '2', None):
                piece['mobile_panels'] = bad
                path.write_text(json.dumps(data))
                with self.assertRaisesRegex(ValueError, 'mobile_panels'):
                    image_pieces.load_catalog(path, root)
            piece.update(mobile_panels=2, width=7)
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, '2:1'):
                image_pieces.load_catalog(path, root)

    def test_visible_title_is_opt_in_and_requires_a_boolean(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.make_catalog(root)
            data = json.loads(path.read_text())
            data['pieces'][0]['title'] = 'A "gifted" child <perhaps>'
            path.write_text(json.dumps(data))
            default_page = image_pieces.render_piece(image_pieces.load_catalog(path, root)['pieces'][0])
            data['pieces'][0]['show_title'] = False
            path.write_text(json.dumps(data))
            self.assertEqual(default_page, image_pieces.render_piece(image_pieces.load_catalog(path, root)['pieces'][0]))
            data['pieces'][0]['show_title'] = True
            path.write_text(json.dumps(data))
            page = image_pieces.render_piece(image_pieces.load_catalog(path, root)['pieces'][0])
            self.assertIn('image-piece piece-with-title', page)
            self.assertEqual(page.count('<h1 '), 1)
            self.assertIn('<h1 class="piece-title">A &quot;gifted&quot; child &lt;perhaps&gt;</h1>', page)
            self.assertIn('href="/assets/paper/first.png" target="_self"', page)
            for bad in (0, 1, 'true', 'false', None):
                data['pieces'][0]['show_title'] = bad
                path.write_text(json.dumps(data))
                with self.assertRaisesRegex(ValueError, 'show_title'):
                    image_pieces.load_catalog(path, root)

    def test_future_catalog_piece_is_a_section_output(self):
        catalog = {"schema_version": 1, "fallback_slug": "new-piece", "pieces": [{
            "slug": "new-piece", "title": "New", "published_date": "",
            "image": "assets/paper/new.png", "width": 1, "height": 1,
            "alt": "New art", "caption": "", "featured": True,
            "href": "/is/writing/new-piece/",
        }]}
        with patch.object(image_pieces, "load_catalog", return_value=catalog):
            output = build_sections.expected_sections()
        self.assertIn("is/writing/new-piece/index.html", output)
        self.assertIn(image_pieces.GENERATOR_MARKER, output["is/writing/new-piece/index.html"])


if __name__ == "__main__":
    unittest.main()
