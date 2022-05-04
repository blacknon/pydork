#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================


"""test_engine_google
    * SearchEngine Classのテストコード.
    * 各検索エンジンの動作テストを行う
"""

# TODO: splash/selenium経由での通信のテストも追加する(dockerでのコンテナ環境が前提になると思われる)


import unittest

from .engine import SearchEngine

# 変数
SEARCH_TEXT = 'Linux'


class SearchEngineTestCaseWithSelenium(unittest.TestCase):
    def setUp(self):
        """setUp

        テストメソッド実行前処理.
        """
        # SearchEngine
        self.search_engine = SearchEngine()

        print("setUp!!")

    def tearDown(self):
        """tearDown

        テストメソッド実行後処理
        """

        print("tearDown!!")

    def common_settings(self):
        # command modeを有効化
        self.search_engine.set_is_command(True)

        # debug modeを有効化
        self.search_engine.set_is_debug(True)

        # seleniumを有効化
        self.search_engine.set_selenium(None, 'chrome')

        # user agentを定義
        self.search_engine.set_user_agent()

    # ==========
    # Baidu
    # ==========
    def test_baidu_text_search(self):
        print('Test Baidu text search.')

        # 検索エンジンを指定(ここではBaiduを使用)
        self.search_engine.set('baidu')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.search(SEARCH_TEXT, maximum=30)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))

    def test_baidu_image_search(self):
        print('Test Baidu image search.')

        # 検索エンジンを指定(ここではBaiduを使用)
        self.search_engine.set('baidu')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.search(SEARCH_TEXT, type='image', maximum=30)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))

    def test_baidu_suggest(self):
        print('Test Baidu text suggest.')

        # 検索エンジンを指定(ここではBaiduを使用)
        self.search_engine.set('baidu')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))

    def test_baidu_suggest_with_alph(self):
        print('Test Baidu text suggest with alph.')

        # 検索エンジンを指定(ここではBaiduを使用)
        self.search_engine.set('baidu')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT, alph=True)

        self.assertNotEqual(0, len(data))

    def test_baidu_suggest_with_num(self):
        print('Test Baidu text suggest with num.')

        # 検索エンジンを指定(ここではBaiduを使用)
        self.search_engine.set('baidu')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT, num=True)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))

    # ==========
    # Bing
    # ==========
    def test_bing_text_search(self):
        print('Test Bing text search.')

        # 検索エンジンを指定(ここではBingを使用)
        self.search_engine.set('bing')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.search(SEARCH_TEXT, maximum=30)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))

    def test_bing_image_search(self):
        print('Test Bing image search.')

        # 検索エンジンを指定(ここではBingを使用)
        self.search_engine.set('bing')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.search(SEARCH_TEXT, type='image', maximum=30)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))

    def test_bing_suggest(self):
        print('Test Bing text suggest.')

        # 検索エンジンを指定(ここではBingを使用)
        self.search_engine.set('bing')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))

    def test_bing_suggest_with_jap(self):
        print('Test Bing text suggest with jap.')

        # 検索エンジンを指定(ここではBingを使用)
        self.search_engine.set('bing')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT, jap=True)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))

    def test_bing_suggest_with_alph(self):
        print('Test Bing text suggest with alph.')

        # 検索エンジンを指定(ここではBingを使用)
        self.search_engine.set('bing')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT, alph=True)

        self.assertNotEqual(0, len(data))

    def test_bing_suggest_with_num(self):
        print('Test Bing text suggest with num.')

        # 検索エンジンを指定(ここではBingを使用)
        self.search_engine.set('bing')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT, num=True)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))

    # ==========
    # DuckDuckGo
    # ==========
    def test_duckduckgo_text_search(self):
        print('Test DuckDuckGo text search.')

        # 検索エンジンを指定(ここではDuckDuckGoを使用)
        self.search_engine.set('duckduckgo')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.search(SEARCH_TEXT, maximum=30)

        print("{} count.".format(len(data)))
        self.assertEqual(30, len(data))

    def test_duckduckgo_image_search(self):
        print('Test DuckDuckGo image search.')

        # 検索エンジンを指定(ここではDuckDuckGoを使用)
        self.search_engine.set('duckduckgo')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.search(SEARCH_TEXT, type='image', maximum=30)

        print("{} count.".format(len(data)))
        self.assertEqual(30, len(data))

    def test_duckduckgo_suggest(self):
        print('Test DuckDuckGo text suggest.')

        # 検索エンジンを指定(ここではDuckDuckGoを使用)
        self.search_engine.set('duckduckgo')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))

    def test_duckduckgo_suggest_with_jap(self):
        print('Test DuckDuckGo text suggest with jap.')

        # 検索エンジンを指定(ここではDuckDuckGoを使用)
        self.search_engine.set('duckduckgo')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT, jap=True)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))

    def test_duckduckgo_suggest_with_alph(self):
        print('Test DuckDuckGo text suggest with alph.')

        # 検索エンジンを指定(ここではDuckDuckGoを使用)
        self.search_engine.set('duckduckgo')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT, alph=True)

        self.assertNotEqual(0, len(data))

    def test_duckduckgo_suggest_with_num(self):
        print('Test DuckDuckGo text suggest with num.')

        # 検索エンジンを指定(ここではDuckDuckGoを使用)
        self.search_engine.set('duckduckgo')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT, num=True)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))

    # ==========
    # Google
    # ==========
    def test_google_text_search(self):
        print('Test Google text search.')

        # 検索エンジンを指定(ここではGoogleを使用)
        self.search_engine.set('google')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.search(SEARCH_TEXT, maximum=30)

        print("{} count.".format(len(data)))
        self.assertEqual(30, len(data))

    def test_google_image_search(self):
        print('Test Google image search.')

        # 検索エンジンを指定(ここではGoogleを使用)
        self.search_engine.set('google')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.search(SEARCH_TEXT, type='image', maximum=30)

        print("{} count.".format(len(data)))
        self.assertEqual(30, len(data))

    def test_google_suggest(self):
        print('Test Google text suggest.')

        # 検索エンジンを指定(ここではGoogleを使用)
        self.search_engine.set('google')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))

    def test_google_suggest_with_jap(self):
        print('Test Google text suggest with jap.')

        # 検索エンジンを指定(ここではGoogleを使用)
        self.search_engine.set('google')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT, jap=True)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))

    def test_google_suggest_with_alph(self):
        print('Test Google text suggest with alph.')

        # 検索エンジンを指定(ここではGoogleを使用)
        self.search_engine.set('google')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT, alph=True)

        self.assertNotEqual(0, len(data))

    def test_google_suggest_with_num(self):
        print('Test Google text suggest with num.')

        # 検索エンジンを指定(ここではGoogleを使用)
        self.search_engine.set('google')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT, num=True)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))

    # ==========
    # Yahoo
    # ==========
    def test_yahoo_text_search(self):
        print('Test Yahoo text search.')

        # 検索エンジンを指定(ここではYahooを使用)
        self.search_engine.set('yahoo')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.search(SEARCH_TEXT, maximum=30)

        print("{} count.".format(len(data)))
        self.assertEqual(30, len(data))

    def test_yahoo_image_search(self):
        print('Test Yahoo image search.')

        # 検索エンジンを指定(ここではYahooを使用)
        self.search_engine.set('yahoo')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.search(SEARCH_TEXT, type='image', maximum=30)

        print("{} count.".format(len(data)))
        self.assertEqual(30, len(data))

    def test_yahoo_suggest(self):
        print('Test Yahoo text suggest.')

        # 検索エンジンを指定(ここではYahooを使用)
        self.search_engine.set('yahoo')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))

    def test_yahoo_suggest_with_jap(self):
        print('Test Yahoo text suggest with jap.')

        # 検索エンジンを指定(ここではYahooを使用)
        self.search_engine.set('yahoo')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT, jap=True)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))

    def test_yahoo_suggest_with_alph(self):
        print('Test Yahoo text suggest with alph.')

        # 検索エンジンを指定(ここではYahooを使用)
        self.search_engine.set('yahoo')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT, alph=True)

        self.assertNotEqual(0, len(data))

    def test_yahoo_suggest_with_num(self):
        print('Test Yahoo text suggest with num.')

        # 検索エンジンを指定(ここではYahooを使用)
        self.search_engine.set('yahoo')

        # 共通系の中間前処理を実行
        self.common_settings()

        # 検索を実行
        data = self.search_engine.suggest(
            SEARCH_TEXT, num=True)

        print("{} count.".format(len(data)))
        self.assertNotEqual(0, len(data))
