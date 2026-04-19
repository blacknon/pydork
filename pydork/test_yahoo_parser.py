#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import unittest

from .engine_yahoo import Yahoo


class YahooParserTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = Yahoo()

    def test_extracts_links_from_next_data(self):
        payload = {
            "props": {
                "initialProps": {
                    "pageProps": {
                        "pageData": {
                            "algos": [
                                {
                                    "url": "https://example.com/a",
                                    "title": "Example A",
                                    "description": "Snippet A",
                                }
                            ]
                        }
                    }
                }
            }
        }
        html = '<html><body><script id="__NEXT_DATA__" type="application/json">{}</script></body></html>'.format(
            json.dumps(payload)
        )

        links = self.engine.get_text_links_from_next_data("https://yahoo.test", html)

        self.assertEqual(1, len(links))
        self.assertEqual("https://example.com/a", links[0]["link"])
        self.assertEqual("Example A", links[0]["title"])
        self.assertEqual("Snippet A", links[0]["text"])

    def test_extracts_links_from_html_fallback(self):
        html = """
        <html><body>
          <div class="sw-Card">
            <div class="sw-Card__headerSpace">
              <div class="sw-Card__title">
                <a href="https://example.com/b"><h3>Example B</h3></a>
              </div>
            </div>
            <div class="sw-Card__floatContainer">
              <div class="sw-Card__summary">Snippet B</div>
            </div>
          </div>
        </body></html>
        """

        links = self.engine.get_text_links_from_html("https://yahoo.test", html)

        self.assertEqual(1, len(links))
        self.assertEqual("https://example.com/b", links[0]["link"])
        self.assertEqual("Example B", links[0]["title"])
        self.assertEqual("Snippet B", links[0]["text"])

    def test_returns_empty_for_missing_next_data(self):
        html = "<html><body>No next data</body></html>"

        self.assertEqual([], self.engine.get_text_links_from_next_data("https://yahoo.test", html))
