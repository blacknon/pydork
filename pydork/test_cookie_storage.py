#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pickle
import tempfile
import unittest
from types import SimpleNamespace

from requests.cookies import RequestsCookieJar

from .engine_common import CommonEngine


class CookieStorageTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = CommonEngine()
        self.engine.NAME = 'TestEngine'

    def test_serialize_requests_cookiejar_to_json_compatible_list(self):
        jar = RequestsCookieJar()
        jar.set('sid', 'abc', domain='example.com', path='/')

        cookies = self.engine._serialize_cookies(jar)

        self.assertEqual(1, len(cookies))
        self.assertEqual('sid', cookies[0]['name'])
        self.assertEqual('abc', cookies[0]['value'])

    def test_loads_json_cookie_file(self):
        cookie_data = [{'name': 'sid', 'value': 'abc', 'domain': 'example.com', 'path': '/'}]

        with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False) as f:
            json.dump(cookie_data, f)
            self.engine.COOKIE_FILE = f.name

        self.assertEqual(cookie_data, self.engine._load_cookies_from_file())

    def test_loads_legacy_pickle_cookie_file(self):
        cookie_data = [{'name': 'sid', 'value': 'abc', 'domain': 'example.com', 'path': '/'}]

        with tempfile.NamedTemporaryFile('wb', delete=False) as f:
            pickle.dump(cookie_data, f)
            self.engine.COOKIE_FILE = f.name

        self.assertEqual(cookie_data, self.engine._load_cookies_from_file())

    def test_write_cookies_persists_json(self):
        jar = RequestsCookieJar()
        jar.set('sid', 'abc', domain='example.com', path='/')

        with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False) as f:
            self.engine.COOKIE_FILE = f.name

        self.engine.session = SimpleNamespace(cookies=jar)
        self.engine.write_cookies()

        with open(self.engine.COOKIE_FILE, 'r', encoding='utf-8') as f:
            cookie_data = json.load(f)

        self.assertEqual('sid', cookie_data[0]['name'])
        self.assertEqual('abc', cookie_data[0]['value'])
