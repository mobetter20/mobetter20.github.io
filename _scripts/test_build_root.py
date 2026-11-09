"""Source mutation checks for the generated homepage and publisher proof."""
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import build_root
import build_essays
import build_writes
import home_catalog
import paper_site
import build_sections


class HomeBuildTest(unittest.TestCase):
    def test_essay_add_remove_and_rejections(self):
        original = build_essays.load_posts()
        baseline = build_root.expected_root()
        fixture = SimpleNamespace(slug="fixture-essay", title="A <new> essay", body_md="some words")
        with patch.object(build_essays, "load_posts", return_value=original + [fixture]):
            added = build_root.expected_root()
        self.assertEqual(added, baseline)
        with patch.object(build_essays, "load_posts", return_value=[]):
            self.assertEqual(build_root.expected_root(), baseline)
        self.assertEqual(home_catalog.essay_choices([]), [])   # essays may all be retracted
        for invalid in [[fixture, fixture], [SimpleNamespace(slug="bad/slug", title="bad")]]:
            with self.assertRaises(home_catalog.CatalogError):
                home_catalog.essay_choices(invalid)

    def test_building_add_remove_and_malformed(self):
        source = json.loads(paper_site.BUILDING_SOURCE.read_text())
        fixture = dict(title="Fixture", href="/fixture/", status="live", description="A new project.", collection=False, night=True)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "building.json"
            path.write_text(json.dumps(dict(source, projects=source['projects'] + [fixture])))
            with patch.object(paper_site, "BUILDING_SOURCE", path):
                added = paper_site.render_building()
                self.assertIn('href="/fixture/"', added)
                self.assertIn('data-room="night"', added)
                path.write_text(json.dumps(source))
                self.assertNotIn('href="/fixture/"', paper_site.render_building())
                for bad in [dict(source, projects=[]), dict(source, projects=source['projects'] + [fixture,fixture]),
                            dict(source, projects=[dict(fixture, description='')]), dict(source, projects=[dict(fixture, night='dark')])]:
                    path.write_text(json.dumps(bad))
                    with self.assertRaises(ValueError):
                        paper_site.render_building()

    def test_stats_and_stale_home(self):
        with tempfile.TemporaryDirectory() as directory:
            stats = Path(directory) / "stats.md"
            stats.write_text(re.sub(r"^total_km:.*$", "total_km: 80000", build_root.STATS_PATH.read_text(), flags=re.M))
            output = Path(directory) / "index.html"
            with patch.object(build_root, "STATS_PATH", stats), patch.object(build_root, "INDEX_PATH", output):
                build_root.build(root_only=True)
                self.assertIn("80,000", output.read_text())
                self.assertIn('--progress:20.812%', output.read_text())
                build_root.check_home()
                output.write_text(output.read_text() + "stale")
                with self.assertRaises(build_root.StatsError):
                    build_root.check_home()

    def test_distinct_home_with_running_below_the_work(self):
        output = build_root.expected_root()
        self.assertIn('class="home-page"', output)
        self.assertNotIn('is running</a>', output)
        self.assertEqual(output.count('href="/is/running/"'), 1)
        self.assertNotIn('href="/is/writing/bird-coo/"', output)
        self.assertNotIn('data-essay-slug', output)
        self.assertNotRegex(output, r'<a\b[^>]*href="/(?:writes|wrote)/')
        self.assertLess(output.index('id="writing-heading"'), output.index('id="building-heading"'))
        self.assertLess(output.index('</main>'), output.index('class="running"'))
        self.assertIn('href="/is/building/kenbaiki/"', output)
        self.assertNotIn('home-images.js', output)
        self.assertIn('href="/is/writing/austen-at-work/" target="_self"', output)
        self.assertNotIn('id="cartoon-dialog"', output)
        self.assertNotIn('Local mock', output)
        self.assertNotIn('content="noindex', output)
        running = build_root.parse_kv(build_root.require(build_root.parse_stats(build_root.STATS_PATH), "running"), "running")
        self.assertIn(build_root.as_of_label(running.get("as_of", "")), output)
        self.assertEqual(build_root.as_of_label("2026-07"), "to July 2026")
        with self.assertRaises(build_root.StatsError):
            build_root.as_of_label("July 2026")

    def test_daily_build_does_not_rewrite_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sections = root / 'is/writing/index.html'
            sections.parent.mkdir(parents=True)
            sections.write_text('untouched section')
            changes = {name:root / relative for name,relative in [
                ('INDEX_PATH','index.html'), ('RUNNING_INDEX_PATH','is/running/index.html'),
                ('READING_INDEX_PATH','is/reading/index.html'), ('LEARNING_INDEX_PATH','is/learning/index.html')]}
            with patch.multiple(build_root, **changes), patch.object(build_sections,'OUTPUT_ROOT',root):
                build_root.build()
            self.assertEqual(sections.read_text(), 'untouched section')
            self.assertEqual({str(p.relative_to(root)) for p in root.rglob('index.html')},
                {'index.html','is/running/index.html','is/reading/index.html','is/learning/index.html','is/writing/index.html'})

    def test_unified_archive_tracks_essay_registry(self):
        baseline = build_sections.expected_sections()['is/writing/index.html']
        image_count = len(paper_site.image_pieces.load_catalog()['pieces'])
        self.assertEqual(baseline.count('<li data-kind='), 50 + image_count + len(build_writes.collect_items()))
        fixture = SimpleNamespace(slug='new-essay', title='New essay', body_md='Words', date='2026', excerpt='A thought.', order=1)
        with patch.object(build_essays, 'load_posts', return_value=[fixture]):
            added = build_sections.expected_sections()['is/writing/index.html']
            home = build_root.expected_root()
        self.assertEqual(added.count('<li data-kind='), 51 + image_count)
        self.assertIn('href="/writes/new-essay/"', added)
        self.assertNotIn('/writes/new-essay/', home)
        self.assertNotIn('/writes/new-essay/', baseline)
        self.assertEqual(baseline.count('Browse all writing'),1)
        self.assertLess(baseline.index('Browse all writing'),baseline.index('class="edition-main"'))

    def test_archive_uses_full_publication_dates_and_editorial_exclusions(self):
        output = paper_site.render_writing([])
        archive = output.split('<ol id="writing-list"')[1].split('</ol>')[0]
        slugs = re.findall(r'href="/wrote/([^/]+)/"', archive)
        medium, standalone = paper_site.build_comedy.load_posts()
        expected = [post.slug for post in sorted(medium, key=lambda post: post.date, reverse=True)
                    if post.slug not in paper_site.UNLISTED_COMEDY_SLUGS]
        self.assertEqual(slugs, expected + [post.slug for post in standalone])
        self.assertNotIn('10-reasons-why-you-shouldn-t-read-this-list', archive)
        self.assertTrue((build_root.ROOT / 'wrote/10-reasons-why-you-shouldn-t-read-this-list/index.html').is_file())
        self.assertLess(archive.index('/is/writing/austen-at-work/'), archive.index('/wrote/'))
        self.assertLess(archive.index('/is/writing/cest-la-vie/'), archive.index('/wrote/'))
        self.assertLess(archive.index('/is/writing/thought-time-insight/'), archive.index('/wrote/'))
        catalog = paper_site.image_pieces.load_catalog()
        austen = next(piece for piece in catalog['pieces'] if piece['slug'] == 'austen-at-work')
        undated = {**austen, 'slug': 'undated-fixture', 'published_date': '',
                   'href': '/is/writing/undated-fixture/', 'featured': False}
        with patch.object(paper_site.image_pieces, 'load_catalog', return_value={
                **catalog, 'pieces': [*catalog['pieces'], undated]}):
            fixture_archive = paper_site.render_writing([]).split('<ol id="writing-list"')[1].split('</ol>')[0]
        self.assertEqual(re.findall(r'href="([^"]+)"', fixture_archive)[-1], undated['href'])
        essays = [dict(slug='older',title='A older',date='2024-02-10'),
                  dict(slug='year-only',title='B year',date='2024'),
                  dict(slug='newer',title='Z newer',date='2024-02-20')]
        with_essays = paper_site.render_writing(essays).split('<ol id="writing-list"')[1].split('</ol>')[0]
        self.assertLess(with_essays.index('/writes/newer/'),with_essays.index('/writes/older/'))
        self.assertLess(with_essays.index('/writes/older/'),with_essays.index('/writes/year-only/'))
        self.assertLess(with_essays.index('/writes/year-only/'),with_essays.index('/wrote/'))

    def test_building_curation_preserves_unlisted_route(self):
        output = paper_site.render_building()
        titles = [c.title for c in paper_site.load_building()]
        self.assertEqual(len(titles),9)
        self.assertEqual(titles[:4],['Bureau of Interior Conditions','Seoul Crushing','Instrument Bus','omen.ops'])
        self.assertLess(output.index('omen.ops/'),output.index('kenbaiki'))
        self.assertNotIn('/crossings/',output)
        self.assertTrue((build_root.ROOT / 'is/building/crossings/index.html').is_file())
        self.assertNotIn('machine-routes',output)
        footer = output.split('<footer')[1]
        self.assertNotIn('href="/"',footer)

    def test_writing_publisher_refreshes_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(build_writes, "WRITES_ROOT", root / "writes"), patch.object(build_root, "INDEX_PATH", root / "index.html"), patch.object(build_sections, "OUTPUT_ROOT", root):
                build_writes.main()
                build_root.check_home()

    def test_native_navigation_and_resolved_template(self):
        output = build_root.expected_root()
        self.assertNotIn("{{", output)
        self.assertIn('target="_self"', output)
        self.assertNotIn("localhost", output)
        preview = re.search(r'property="og:image" content="https://ajin.im([^"]+)"', output)
        self.assertIsNotNone(preview)
        self.assertTrue((build_root.ROOT / preview.group(1).lstrip('/')).is_file())

    def test_publisher_requires_pushed_archive_source_and_reader(self):
        spec = importlib.util.spec_from_file_location("watcher", Path(__file__).parent / "writes_publisher/publish_watcher.py")
        watcher = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = watcher
        spec.loader.exec_module(watcher)
        def git(*args, **kwargs):
            value = "source" if args[:1] == ("show",) else ""
            if args == ("show", "HEAD:is/writing/index.html"):
                value = self.writing
            return subprocess.CompletedProcess(args, 1 if args == self.failure else 0, value, "")
        with patch.object(watcher, "git", git):
            self.failure = None
            teaser = '<a href="/writes/fixture/">Fixture</a>'
            self.writing = teaser
            self.assertIn("Writing archive entry", watcher.verify_published({"fixture": "source"}))
            self.writing = teaser + '<ol id="writing-list"><li>' + teaser + '</li></ol>'
            self.assertIsNone(watcher.verify_published({"fixture": "source"}))
            self.assertIn('source is not', watcher.verify_published({"fixture": "edited source"}))
            self.failure = ('cat-file', '-e', 'HEAD:writes/fixture/index.html')
            self.assertIn('page was not generated', watcher.verify_published({"fixture": "source"}))
            self.failure = ('merge-base', '--is-ancestor', 'HEAD', 'origin/master')
            self.assertIn('not on origin', watcher.verify_published({"fixture": "source"}))


if __name__ == "__main__":
    unittest.main()
