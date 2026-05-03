#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from unittest import mock

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

    def test_suggest_sets_message_before_session_creation(self):
        search_engine = SearchEngine()
        search_engine.set('google')

        observed = {}

        def fake_create_session():
            observed['has_message'] = hasattr(search_engine.ENGINE, 'MESSAGE')
            observed['header'] = search_engine.ENGINE.MESSAGE.HEADER

        def fake_close_session():
            return None

        with mock.patch.object(search_engine.ENGINE, 'create_session', fake_create_session):
            with mock.patch.object(search_engine.ENGINE, 'close_session', fake_close_session):
                with mock.patch.object(search_engine.ENGINE, 'get_result', return_value='[]'):
                    with mock.patch.object(
                        search_engine.ENGINE,
                        'get_suggest_list',
                        side_effect=lambda suggests, char, html: suggests,
                    ):
                        with mock.patch('pydork.engine.sleep', return_value=None):
                            result = search_engine.suggest('Linux')

        self.assertEqual({}, result)
        self.assertTrue(observed['has_message'])
        self.assertEqual('[${ENGINE_NAME}Search]', observed['header'])

    def test_ignore_ssl_adds_chrome_option_only_when_enabled(self):
        search_engine = SearchEngine()
        search_engine.set('google')
        search_engine.set_selenium(None, 'chrome')

        default_options = search_engine.ENGINE.create_selenium_options()
        self.assertNotIn('ignore-certificate-errors', default_options.arguments)

        search_engine.set_ignore_ssl(True)
        ignore_ssl_options = search_engine.ENGINE.create_selenium_options()
        self.assertIn('ignore-certificate-errors', ignore_ssl_options.arguments)
