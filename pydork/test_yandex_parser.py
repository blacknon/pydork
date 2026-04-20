#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from .engine_yandex import Yandex


class YandexParserTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = Yandex()

    def test_parses_text_results_with_modern_selectors(self):
        html = """
        <html>
          <body>
            <li class="serp-item">
              <a class="OrganicTitle-Link" href="https://example.com/page">
                <span class="OrganicTitleContentSpan">Example Result</span>
              </a>
              <div class="OrganicText">
                <span class="OrganicTextContentSpan">Example snippet</span>
              </div>
            </li>
          </body>
        </html>
        """

        links = self.engine.get_links('https://yandex.com/search/?text=linux', html, 'text')

        self.assertEqual(1, len(links))
        self.assertEqual('https://example.com/page', links[0]['link'])
        self.assertEqual('Example Result', links[0]['title'])
        self.assertEqual('Example snippet', links[0]['text'])

    def test_normalizes_relative_redirect_links(self):
        html = """
        <html>
          <body>
            <div class="Organic">
              <a class="OrganicTitle-Link" href="/clck/jsredir?url=https%3A%2F%2Fexample.com%2Ftarget">
                <span class="OrganicTitleContentSpan">Redirected Result</span>
              </a>
              <div class="OrganicText">Snippet</div>
            </div>
          </body>
        </html>
        """

        links = self.engine.get_links('https://yandex.com/search/?text=linux', html, 'text')

        self.assertEqual('https://example.com/target', links[0]['link'])

    def test_parses_image_results_from_data_bem(self):
        html = """
        <html>
          <body>
            <div class="serp-item" data-bem='{"serp-item":{"img_href":"https://img.example.com/cat.jpg","snippet":{"title":"Cat","url":"https://example.com/cat"}}}'></div>
          </body>
        </html>
        """

        links = self.engine.get_links('https://yandex.com/images/search?text=cat', html, 'image')

        self.assertEqual(1, len(links))
        self.assertEqual('https://img.example.com/cat.jpg', links[0]['link'])
        self.assertEqual('Cat', links[0]['title'])
        self.assertEqual('https://example.com/cat', links[0]['pagelink'])

    def test_parses_suggestions_from_json_array(self):
        suggests = self.engine.get_suggest_list({}, '', '["lin", ["linux", "linux mint"], []]')

        self.assertEqual(['linux', 'linux mint'], suggests[''])

    def test_returns_empty_for_unknown_suggest_payload(self):
        suggests = self.engine.get_suggest_list({}, '', 'not-json')

        self.assertEqual([], suggests[''])
