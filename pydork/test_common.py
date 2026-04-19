#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from .common import Color


class ColorTestCase(unittest.TestCase):
    def test_bold_uses_standard_escape_sequence(self):
        rendered = Color(Color.GREEN).out('x', is_bold=True)

        self.assertIn('\033[1m', rendered)

    def test_reverse_uses_standard_escape_sequence(self):
        rendered = Color(Color.GREEN).out('x', is_reverse=True)

        self.assertIn('\033[07m', rendered)
