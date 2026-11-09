"""The committed comedy archive must be reproducible without private exports."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_comedy


class ComedyDataTest(unittest.TestCase):
    def test_committed_data_matches_existing_readers_and_standalone(self):
        medium, standalone = build_comedy.load_posts()
        self.assertEqual(len(medium), 50)
        self.assertEqual(len(standalone), 1)
        expected = {post.slug for post in medium + standalone}
        readers = {
            path.parent.name for path in build_comedy.WROTE_ROOT.glob("*/index.html")
            if "http-equiv=\"refresh\"" not in path.read_text(encoding="utf-8")
        }
        self.assertEqual(expected, readers)

    def test_default_load_does_not_touch_private_exports(self):
        with patch.object(build_comedy, "EXPORT_ROOT", Path("/definitely-not-present")):
            medium, standalone = build_comedy.load_posts()
        self.assertEqual((len(medium), len(standalone)), (50, 1))

    def test_known_last_sections_and_numbered_list_are_retained(self):
        medium, _ = build_comedy.load_posts()
        by_slug = {post.slug: post for post in medium}
        self.assertIn("So farewell to the fork", by_slug["farewell-to-the-fork"].body_html)
        self.assertEqual(by_slug["10-reasons-why-you-shouldn-t-read-this-list"].body_html.count("<li>"), 10)

    def test_import_excludes_confirmed_comment_without_dropping_short_articles(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, title, canonical, body in [
                ('response', 'My husband’s been married only once…',
                 'https://medium.com/@imajin/a-changed-title-585a1f5d093f',
                 'My husband’s been married only once. So proud. And so pissed off.'),
                ('article', 'Wait for it…', 'https://medium.com/@imajin/wait-for-it-123456abcdef',
                 'Wait for it. Then leave.'),
            ]:
                (root / f'{name}.html').write_text(
                    f'<title>{title}</title><time>May 8, 2023</time>'
                    f'<a href="{canonical}" class="p-canonical">Canonical link</a>'
                    f'<section data-field="body" class="e-content"><p>{body}</p></section><footer></footer>')
            imported = build_comedy.import_medium_posts(root)
            self.assertEqual([post.title for post in imported], ['Wait for it…'])
        self.assertFalse(any('585a1f5d093f' in post.canonical for post in build_comedy.load_medium_data()))

    def test_clean_body_removes_known_promo_but_not_last_or_single_section(self):
        article = ('<section class="section section--body section--first section--last"><p>single retained</p>'
                   '<div class="graf--mixtapeEmbed">follow this unrelated thing</div><p>Thanks to an editor.</p></section>')
        cleaned = build_comedy.clean_body(article)
        self.assertIn("single retained", cleaned)
        self.assertNotIn("unrelated thing", cleaned)
        self.assertIn("Thanks to an editor.", cleaned)

    def test_real_medium_follow_and_newsletter_tails_are_not_reintroduced(self):
        medium, _ = build_comedy.load_posts()
        by_slug = {post.slug: post for post in medium}
        self.assertNotIn("Wouldn’t you rather be laughing?", by_slug["i-would-hurt-a-fly"].body_html)
        self.assertNotIn("newsletter", by_slug["mug-shot-of-my-desk"].body_html.casefold())
        self.assertNotIn("This piece was first published", by_slug["welcome-to-the-fitfulness-gym"].body_html)

    def test_bad_data_has_clear_errors(self):
        good = json.loads(build_comedy.COMEDY_DATA_PATH.read_text())
        cases = {
            "empty": {"schema_version": 1, "posts": []},
            "duplicate": {**good, "posts": [good["posts"][0], good["posts"][0]]},
            "missing": {"schema_version": 1, "posts": [{"slug": "x"}]},
        }
        with tempfile.TemporaryDirectory() as directory:
            for name, data in cases.items():
                path = Path(directory) / f"{name}.json"
                path.write_text(json.dumps(data))
                with self.assertRaisesRegex(ValueError, name if name != "missing" else "required fields"):
                    build_comedy.load_medium_data(path)

    def test_rejects_html_empty_body_and_unsafe_slug(self):
        good = json.loads(build_comedy.COMEDY_DATA_PATH.read_text())
        with tempfile.TemporaryDirectory() as directory:
            for name, key, value, message in [
                ("empty-body", "body_html", "<p></p>", "empty comedy body"),
                ("unsafe-slug", "slug", "not/a/slug", "invalid comedy slug"),
            ]:
                data = {**good, "posts": [dict(good["posts"][0], **{key: value})]}
                path = Path(directory) / f"{name}.json"
                path.write_text(json.dumps(data))
                with self.assertRaisesRegex(ValueError, message):
                    build_comedy.load_medium_data(path)

    def test_empty_private_export_cannot_overwrite_data(self):
        with tempfile.TemporaryDirectory() as directory:
            data_path = Path(directory) / "comedy.json"
            data_path.write_text("keep this data")
            with self.assertRaisesRegex(ValueError, "refusing to replace"):
                build_comedy.import_medium_posts(Path(directory) / "missing-export")
            self.assertEqual(data_path.read_text(), "keep this data")

    def test_partial_refresh_refuses_removal_and_atomic_full_refresh_is_idempotent(self):
        posts = build_comedy.load_medium_data()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "comedy.json"
            build_comedy.write_medium_data(posts, path)
            before = path.read_text()
            with self.assertRaisesRegex(ValueError, "would remove 1 committed comedy posts"):
                build_comedy.write_medium_data(posts[:-1], path)
            self.assertEqual(path.read_text(), before)
            build_comedy.write_medium_data(posts, path)
            self.assertEqual(path.read_text(), before)
            build_comedy.write_medium_data(posts[:-1], path, allow_removals=True)
            self.assertEqual(len(build_comedy.load_medium_data(path)), len(posts) - 1)

    def test_medium_standalone_slug_collision_is_rejected(self):
        good = json.loads(build_comedy.COMEDY_DATA_PATH.read_text())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "_src"
            source.mkdir()
            (source / good["posts"][0]["slug"]).with_suffix(".md").write_text("---\ntitle: collision\n---\nbody")
            data = root / "comedy.json"
            data.write_text(json.dumps({**good, "posts": [good["posts"][0]]}))
            with patch.object(build_comedy, "COMEDY_DATA_PATH", data), patch.object(build_comedy, "COMEDY_SOURCE_ROOT", source):
                with self.assertRaisesRegex(ValueError, "slug collision"):
                    build_comedy.load_posts()

    def test_homunculus_regained_source_ending_is_present(self):
        medium, _ = build_comedy.load_posts()
        post = next(post for post in medium if post.slug == "homunculus-infection-rising-in-adult-population")
        self.assertIn("Infinite thanks to Andrew Rodwin", build_comedy.normalize_text(post.body_html))


if __name__ == "__main__":
    unittest.main()
