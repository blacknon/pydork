#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import unittest

from .engine_baidu import Baidu, resolv_links


class BaiduParserTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = Baidu()

    def test_parses_text_results_with_fallback(self):
        html = """
        <html><body>
          <div class="result">
            <div class="tts-title"><a href="https://www.baidu.com/link?url=abc">Example A</a></div>
            <div class="c-gap-top-small">Snippet A</div>
          </div>
        </body></html>
        """

        original = self.engine.processings_elist
        self.engine.processings_elist = lambda elinks, etitles, etexts: (
            ["https://example.com/a"], etitles, etexts
        )
        try:
            links = self.engine.get_text_links_with_fallback("https://baidu.test", html)
        finally:
            self.engine.processings_elist = original

        self.assertEqual(1, len(links))
        self.assertEqual("https://example.com/a", links[0]["link"])
        self.assertEqual("Example A", links[0]["title"])
        self.assertEqual("Snippet A", links[0]["text"])

    def test_resolv_links_keeps_original_url_when_resolution_fails(self):
        class BrokenSession:
            def head(self, url, allow_redirects=False):
                raise RuntimeError("boom")

        loop = asyncio.new_event_loop()
        try:
            links = loop.run_until_complete(
                resolv_links(loop, BrokenSession(), ["https://www.baidu.com/link?url=abc"])
            )
        finally:
            loop.close()

        self.assertEqual(["https://www.baidu.com/link?url=abc"], links)

    def test_returns_empty_for_unparseable_suggest_body(self):
        suggests = self.engine.get_suggest_list({}, '', '<html><body></body></html>')

        self.assertEqual({}, suggests)
