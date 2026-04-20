#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

import pydork

from .engine import SearchEngine


class SearchEngineApiTestCase(unittest.TestCase):
    def test_search_accepts_legacy_type_keyword(self):
        search_engine = SearchEngine()
        search_engine.set('google')

        result = search_engine.search('Linux', type='image', maximum=0)

        self.assertEqual([], result)

    def test_search_rejects_unknown_keyword_arguments(self):
        search_engine = SearchEngine()
        search_engine.set('google')

        with self.assertRaises(TypeError):
            search_engine.search('Linux', unexpected=True)

    def test_search_rejects_unknown_search_type(self):
        search_engine = SearchEngine()
        search_engine.set('google')

        with self.assertRaises(ValueError):
            search_engine.search('Linux', search_type='video', maximum=0)

    def test_version_is_exposed(self):
        self.assertTrue(isinstance(pydork.__version__, str))
        self.assertNotEqual('', pydork.__version__)

    def test_set_ignore_ssl_delegates_to_engine(self):
        search_engine = SearchEngine()
        search_engine.set('google')

        self.assertFalse(search_engine.ENGINE.IGNORE_SSL_VERIFY)

        search_engine.set_ignore_ssl(True)

        self.assertTrue(search_engine.ENGINE.IGNORE_SSL_VERIFY)

    def test_set_rejects_unsupported_engine(self):
        search_engine = SearchEngine()

        with self.assertRaises(ValueError):
            search_engine.set('unsupported')

    def test_set_accepts_yandex_engine(self):
        search_engine = SearchEngine()

        search_engine.set('yandex')

        self.assertEqual('Yandex', search_engine.ENGINE.NAME)
