#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from .engine_duckduckgo import DuckDuckGo


class DuckDuckGoParserTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = DuckDuckGo()

    def test_extract_vqd_from_inline_assignment(self):
        html = "<html><script>var vqd='12345-67890';</script></html>"

        self.assertEqual('12345-67890', self.engine.extract_vqd(html))

    def test_extract_vqd_from_query_style_assignment(self):
        html = "<html>something?vqd=54321-9876&other=1</html>"

        self.assertEqual('54321-9876', self.engine.extract_vqd(html))

    def test_parses_text_results_and_updates_next_url(self):
        html = """
        DDG.pageLayout.load('d',[
          {"u":"https://example.com/a","t":"Example A","a":"Snippet A","s":"result"},
          {"n":"/d.js?q=test&s=30"}
        ]);
        """

        links = self.engine.get_text_links_with_fallback("https://duck.test", html)

        self.assertEqual(1, len(links))
        self.assertEqual("https://example.com/a", links[0]["link"])
        self.assertEqual("Example A", links[0]["title"])
        self.assertEqual("Snippet A", links[0]["text"])
        self.assertEqual("https://links.duckduckgo.com/d.js?q=test&s=30", self.engine.next_url)

    def test_returns_empty_for_unparseable_text_results(self):
        html = "<html><body>No DDG payload</body></html>"

        self.assertEqual([], self.engine.get_text_links_with_fallback("https://duck.test", html))
