#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import unittest

from .engine_bing import Bing, resolv_links


class BingParserTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = Bing()

    def test_parses_standard_b_algo_card(self):
        html = """
        <html><body>
          <ol class="b_results">
            <li class="b_algo">
              <h2><a href="https://example.com/a">Example A</a></h2>
              <div class="b_caption"><p>Snippet A</p></div>
            </li>
          </ol>
        </body></html>
        """

        links = self.engine.get_text_links_with_fallback("https://bing.test", html)

        self.assertEqual(1, len(links))
        self.assertEqual("https://example.com/a", links[0]["link"])
        self.assertEqual("Example A", links[0]["title"])
        self.assertEqual("Snippet A", links[0]["text"])

    def test_parses_minimal_result_card(self):
        html = """
        <html><body>
          <div class="b_algo">
            <a href="https://example.com/b"><h2>Example B</h2></a>
            <p>Snippet B</p>
          </div>
        </body></html>
        """

        links = self.engine.get_text_links_with_fallback("https://bing.test", html)

        self.assertEqual(1, len(links))
        self.assertEqual("https://example.com/b", links[0]["link"])
        self.assertEqual("Example B", links[0]["title"])
        self.assertEqual("Snippet B", links[0]["text"])

    def test_returns_empty_when_no_result_cards_exist(self):
        html = "<html><body><div>No results</div></body></html>"

        links = self.engine.get_text_links_with_fallback("https://bing.test", html)

        self.assertEqual([], links)

    def test_resolv_links_keeps_non_redirect_urls(self):
        loop = asyncio.new_event_loop()
        try:
            links = loop.run_until_complete(
                resolv_links(loop, None, ["https://example.com/a", "https://example.com/b"])
            )
        finally:
            loop.close()

        self.assertEqual(
            ["https://example.com/a", "https://example.com/b"],
            links,
        )
