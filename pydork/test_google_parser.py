#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from .engine_google import Google


class GoogleParserTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = Google()

    def test_parses_modern_desktop_layout(self):
        html = """
        <html><body>
          <div class="MjjYud">
            <div class="yuRUbf"><a href="https://example.com/a"><h3>Example A</h3></a></div>
            <div class="VwiC3b">Snippet A</div>
          </div>
        </body></html>
        """

        links = self.engine.get_text_links_with_fallback("https://google.test", html)

        self.assertEqual(1, len(links))
        self.assertEqual("https://example.com/a", links[0]["link"])
        self.assertEqual("Example A", links[0]["title"])
        self.assertEqual("Snippet A", links[0]["text"])

    def test_parses_legacy_mobile_layout_and_normalizes_redirect_url(self):
        html = """
        <html><body>
          <div class="Gx5Zad">
            <a href="/url?q=https://example.com/b&sa=U&ved=2ah">
              <h3>Example B</h3>
            </a>
            <div class="BNeawe s3v9rd AP7Wnd">Snippet B</div>
          </div>
        </body></html>
        """

        links = self.engine.get_text_links_with_fallback("https://google.test", html)

        self.assertEqual(1, len(links))
        self.assertEqual("https://example.com/b", links[0]["link"])
        self.assertEqual("Example B", links[0]["title"])
        self.assertEqual("Snippet B", links[0]["text"])

    def test_returns_empty_when_no_result_cards_exist(self):
        html = "<html><body><div>No search results here</div></body></html>"

        links = self.engine.get_text_links_with_fallback("https://google.test", html)

        self.assertEqual([], links)

    def test_extracts_next_page_url_from_modern_pagination(self):
        html = """
        <html><body>
          <a id="pnnext" href="/search?q=linux&start=100&sca_esv=1">Next</a>
        </body></html>
        """

        next_url = self.engine.get_nextpage_url(
            "https://www.google.com/search?q=linux&start=0", html
        )

        self.assertEqual(
            "https://www.google.com/search?q=linux&start=100&sca_esv=1",
            next_url,
        )

    def test_extracts_next_page_url_from_legacy_pagination(self):
        html = """
        <html><body>
          <div class="AaVjTc">
            <table><tbody><tr><td><a href="/search?q=linux&start=100">2</a></td></tr></tbody></table>
          </div>
        </body></html>
        """

        next_url = self.engine.get_nextpage_url(
            "https://www.google.com/search?q=linux&start=0", html
        )

        self.assertEqual(
            "https://www.google.com/search?q=linux&start=100",
            next_url,
        )
