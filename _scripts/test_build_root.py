"""Source mutation checks for the generated homepage and publisher proof."""
import importlib.util
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


class HomeBuildTest(unittest.TestCase):
    def test_essay_add_remove_and_rejections(self):
        original = build_root.build_essays.load_posts()
        fixture = SimpleNamespace(slug="fixture-essay", title="A <new> essay", body_md="some words")
        with patch.object(build_root.build_essays, "load_posts", return_value=original + [fixture]):
            added = build_root.expected_root()
        self.assertIn('data-essay-slug="fixture-essay"', added)
        self.assertIn("A &lt;new&gt; essay", added)
        self.assertNotIn('data-essay-slug="fixture-essay"', build_root.expected_root())
        for invalid in [[], [fixture, fixture], [SimpleNamespace(slug="bad/slug", title="bad")]]:
            with self.assertRaises(home_catalog.CatalogError):
                home_catalog.essay_choices(invalid)

    def test_building_add_remove_and_malformed(self):
        source = build_root.BUILDING_INDEX_PATH.read_text()
        fixture = '<div class="project"><div class="project-head"><span class="project-name"><a href="/fixture/">Fixture</a></span><span class="project-status">live</span></div><p class="project-desc">A fixture project.</p></div>'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "building.html"
            path.write_text(source + fixture)
            added, count = home_catalog.render_building(path)
            self.assertIn('data-project-url="/fixture/"', added)
            expected_builds = sum(not c.collection for c in home_catalog.load_building_choices(build_root.BUILDING_INDEX_PATH)) + 1
            self.assertIn(f"{expected_builds:02d} pieces", count)
            path.write_text(source + fixture.replace("A fixture project.", "A <span>clear</span> description."))
            self.assertEqual(home_catalog.load_building_choices(path)[-1].description, "A clear description.")
            path.write_text(source)
            self.assertNotIn('data-project-url="/fixture/"', home_catalog.render_building(path)[0])
            for bad in ["", source + fixture + fixture, source + fixture.replace('class="project-desc"', 'class="wrong"'), source + fixture[:-6]]:
                path.write_text(bad)
                with self.assertRaises(home_catalog.CatalogError):
                    home_catalog.load_building_choices(path)

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

    def test_writing_publisher_refreshes_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(build_writes, "WRITES_ROOT", root / "writes"), patch.object(build_root, "INDEX_PATH", root / "index.html"):
                build_writes.main()
                build_root.check_home()

    def test_native_navigation_and_resolved_template(self):
        output = build_root.expected_root()
        self.assertNotIn("{{", output)
        self.assertIn('target="_self"', output)
        self.assertNotIn("localhost", output)

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
