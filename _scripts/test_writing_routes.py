"""Contracts for durable writing readers and retired archive indexes."""

from pathlib import Path
import unittest

import build_essays
import build_writes
import build_wrote
import writes_common


class WritingRouteTest(unittest.TestCase):
    def test_reader_uses_paper_system_and_unified_backlink(self):
        page = writes_common.reading_page(
            title="A piece",
            body_html="        <p>Words.</p>",
            canonical="https://ajin.im/writes/a-piece/",
            description="Words.",
            kicker="a thought",
            back_href="/is/writing/#all",
            back_label="← All writing",
            feed_url="/writes/feed.xml",
        )
        self.assertIn("EB+Garamond", page)
        self.assertIn("IBM+Plex+Mono", page)
        self.assertIn('/writes.css?v=paper-r12', page)
        self.assertIn('href="/is/writing/#all" target="_self"', page)
        self.assertIn('rel="alternate" type="application/atom+xml"', page)
        self.assertIn('href="https://ajin.im/writes/a-piece/"', page)

    def test_reader_styles_are_the_paper_palette_and_single_column(self):
        css = (Path(__file__).resolve().parents[1] / "writes.css").read_text()
        for token in ("#fffef8", "#101b33", "#1c4286", '"EB Garamond"', '"IBM Plex Mono"'):
            self.assertIn(token, css)
        self.assertIn(".read-page .shell { max-width: 38rem", css)
        self.assertNotIn("Newsreader", css)
        self.assertNotIn("DM Mono", css)

    def test_legacy_indexes_have_one_crawl_safe_destination(self):
        for page in (build_writes.render_index(), build_wrote.render_index()):
            self.assertIn('content="noindex,follow"', page)
            self.assertIn('content="0; url=/is/writing/#all"', page)
            self.assertIn('href="https://ajin.im/is/writing/#all"', page)
            self.assertIn('href="/is/writing/#all" target="_self"', page)
            self.assertNotIn('class="log"', page)

    def test_essay_reader_and_feed_contract_survive_unification(self):
        post = build_essays.EssayPost(
            source=Path("fixture.md"), title="Fixture", order=1, body_md="Words.",
            excerpt="Words.", slug="fixture", date="2026",
        )
        page = build_essays.build_post_page(post)
        self.assertIn('href="/is/writing/#all" target="_self"', page)
        self.assertIn('href="/writes/feed.xml"', page)
        feed = build_essays.render_feed([post])
        self.assertIn('<link rel="alternate" href="https://ajin.im/writes/"/>', feed)
        self.assertIn('<link rel="self" href="https://ajin.im/writes/feed.xml"/>', feed)
        self.assertIn('https://ajin.im/writes/fixture/', feed)


if __name__ == "__main__":
    unittest.main()
