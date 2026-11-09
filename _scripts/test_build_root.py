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
import build_writes
import home_catalog
import paper_site
import build_sections


class HomeBuildTest(unittest.TestCase):
    def test_essay_add_remove_and_rejections(self):
        original = build_root.build_essays.load_posts()
        fixture = SimpleNamespace(slug="fixture-essay", title="A <new> essay", body_md="some words")
        with patch.object(build_root.build_essays, "load_posts", return_value=original + [fixture]):
            added = build_root.expected_root()
        self.assertIn('data-essay-slug="fixture-essay"', added)
        self.assertIn("A &lt;new&gt; essay", added)
        self.assertNotIn('data-essay-slug="fixture-essay"', build_root.expected_root())
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
                build_root.check_home()
                output.write_text(output.read_text() + "stale")
                with self.assertRaises(build_root.StatsError):
                    build_root.check_home()

    def test_newspaper_navigation_and_mileage(self):
        output = build_root.expected_root()
        self.assertIn('class="paper-page page-home"', output)
        self.assertNotIn('is running</a>', output)
        self.assertEqual(output.count('href="/is/running/"'), 1)
        self.assertIn('href="/is/writing/bird-coo/"', output)
        self.assertIn('data-cartoon-view', output)
        self.assertIn('id="cartoon-dialog"', output)
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
        self.assertEqual(baseline.count('<li data-kind='), 53 + len(build_writes.collect_items()))
        fixture = SimpleNamespace(slug='new-essay', title='New essay', body_md='Words', date='2026', excerpt='A thought.', order=1)
        with patch.object(build_root.build_essays, 'load_posts', return_value=[fixture]):
            added = build_sections.expected_sections()['is/writing/index.html']
            home = build_root.expected_root()
        self.assertEqual(added.count('<li data-kind='), 54)
        self.assertIn('href="/writes/new-essay/"', added)
        self.assertIn('data-essay-slug="new-essay"', home)
        self.assertIn('href="/writes/new-essay/?from=machine"', home)
        self.assertNotIn('/writes/new-essay/', baseline)
        self.assertEqual(baseline.count('Browse all writing'),1)
        self.assertLess(baseline.index('Browse all writing'),baseline.index('class="edition-main"'))

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

    def test_publisher_rejects_missing_home_control(self):
        spec = importlib.util.spec_from_file_location("watcher", Path(__file__).parent / "writes_publisher/publish_watcher.py")
        watcher = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = watcher
        spec.loader.exec_module(watcher)
        def git(*args, **kwargs):
            value = "source" if args[:1] == ("show",) else ""
            if args == ("show", "HEAD:index.html"):
                value = self.home
            return subprocess.CompletedProcess(args, 0, value, "")
        with patch.object(watcher, "git", git):
            self.home = "<html></html>"
            self.assertIn("homepage control", watcher.verify_published({"fixture": "source"}))
            self.home = '<a data-essay-slug="fixture" href="/writes/fixture/?from=machine">Fixture</a>'
            self.assertIsNone(watcher.verify_published({"fixture": "source"}))


if __name__ == "__main__":
    unittest.main()
