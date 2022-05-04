#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================


"""engine_yahoo
    * Yahoo(yahoo.co.jp)用の検索用Classを持つモジュール.
"""


import json
import re
import sys

from urllib import parse
from bs4 import BeautifulSoup

from .common import Color
from .engine_common import CommonEngine


class Yahoo(CommonEngine):
    """Yahoo

    Yahoo(yahoo.co.jp)用の検索エンジン用Class.
    """

    def __init__(self):
        # CommonEngineの処理を呼出し
        super().__init__()

        self.NAME = 'Yahoo'
        self.COLOR = Color.YELLOW
        self.COLOR_NAME = self.COLOR + self.NAME + Color.END

        # リクエスト先のURLを指定
        self.ENGINE_TOP_URL = 'https://www.yahoo.co.jp/'
        self.SEARCH_URL = 'https://search.yahoo.co.jp/search'
        self.IMAGE_PRE_URL = 'https://search.yahoo.co.jp/image/search'
        self.IMAGE_URL = 'https://search.yahoo.co.jp/image/api/search'
        self.SUGGEST_URL = 'https://ff.search.yahoo.com/gossip'

    def gen_search_url(self, keyword: str, type: str):
        """gen_search_url

        検索用のurlを生成する.

        Args:
            keyword (str): 検索クエリ.
            type (str): 検索タイプ.

        Returns:
            dict: 検索用url
        """
        search_url = ''

        # 検索タイプがtextの場合
        if type == 'text':
            # 検索urlを指定
            search_url = self.SEARCH_URL

            # 検索パラメータの設定
            url_param = {
                'p': keyword,         # 検索キーワード
                'num': '100',    # 指定不可(削除)
                'day_from': '',  # 開始日時(yyyy/mm/dd)
                'day_to': '',    # 終了日時(yyyy/mm/dd)
                'b': '',         # 開始位置
                'nfpr': '1',     # もしかして検索(Escape hatch)の無効化
                'qrw': '0'       # もしかして検索(Escape hatch)の無効化
            }

            # lang/localeが設定されている場合
            if self.LANG != '' and self.LOCALE != '':
                url_param['hl'] = self.LANG
                url_param['gl'] = self.LOCALE

            # rangeが設定されている場合
            try:
                start = self.RANGE_START
                end = self.RANGE_END

                # ex.) day_from=2019/09/01&day_to=2019/09/30
                # パラメータが2つ存在している
                day_from = start.strftime("%Y/%m/%d")
                day_to = end.strftime("%Y/%m/%d")

                # GETパラメータに日時データを追加
                url_param['day_from'] = day_from
                url_param['day_to'] = day_to

            except AttributeError:
                None

        # 検索タイプがimageの場合
        elif type == 'image':
            # 前処理(パラメータ`cr`の取得)を実行
            cr = self.get_image_search_cr(keyword)

            # 検索urlを指定
            search_url = self.IMAGE_URL

            # 検索パラメータの設定
            url_param = {
                'p': keyword,  # 検索キーワード
                'fr': 'top_ga1_sa',
                'ei': 'UTF-8',
                'aq': '-1',
                'n': '20',  # 指定不可(削除)
                'vm': 'i',
                'se': '0',
                'ue': '0',
                'cr': cr,
                # 'day_from': '',  # 開始日時(yyyy/mm/dd)
                # 'day_to': '',    # 終了日時(yyyy/mm/dd)
                'b': '',         # 開始位置
                'nfpr': '1',     # もしかして検索(Escape hatch)の無効化
                'qrw': '0'       # もしかして検索(Escape hatch)の無効化
            }

        page = 0
        while True:
            # parameterにページを開始する番号を指定
            if type == 'text':
                url_param['b'] = str(page * 10)
            elif type == 'image':
                url_param['b'] = str(page * 10)

            # パラメータをセット
            params = parse.urlencode(url_param)

            target_url = search_url + '?' + params

            yield 'GET', target_url, None

            page += 1

    def gen_suggest_url(self, keyword: str):
        """gen_suggest_url

        サジェスト取得用のurlを生成する.

        Args:
            keyword (str): 検索クエリ.

        Returns:
            dict: サジェスト取得用url
        """
        url_param = {
            'command': keyword,   # 検索キーワード
            'output': 'json',
        }

        params = parse.urlencode(url_param)
        url = self.SUGGEST_URL + '?' + params

        return url

    def get_links(self, html: str, type: str):
        """get_links

        受け付けたhtmlを解析し、検索結果をlistに加工して返す関数.

        Args:
            html (str): 解析する検索結果のhtml.
            type (str): 検索タイプ([text, image]).現時点ではtextのみ対応.

        Returns:
            list: 検索結果(`[{'title': 'title...', 'url': 'https://hogehoge....'}, {...}]`)
        """

        if type == 'text':
            if self.USE_SPLASH or self.USE_SELENIUM:
                self.SOUP_SELECT_JSON = '#__NEXT_DATA__'
                self.SOUP_SELECT_IMAGE = '.rg_meta.notranslate'
                self.SOUP_SELECT_TEXT = ''

                # Yahooの場合、jsonから検索結果を取得する
                soup = BeautifulSoup(html, 'lxml')
                elements = soup.select(self.SOUP_SELECT_JSON)
                element = elements[0].string

                # debug
                if self.IS_DEBUG:
                    print(Color.PURPLE + '[JsonElement]' + Color.END,
                          file=sys.stderr)
                    print(Color.PURPLE + element + Color.END, file=sys.stderr)

                # jsonからデータを抽出　
                j = json.loads(element)

                # debug
                if self.IS_DEBUG:
                    print(Color.PURPLE + '[Json]' + Color.END, file=sys.stderr)
                    print(Color.PURPLE + json.dumps(j) + Color.END,
                          file=sys.stderr)

                jd = j['props']['initialProps']['pageProps']['pageData']['algos']

                elinks = [e['url'] for e in jd]
                etitles = [e['title'] for e in jd]
                etexts = [e['description'] for e in jd]

                links = self.create_text_links(elinks, etitles, etexts)

            else:
                self.SOUP_SELECT_URL = '.sw-Card__headerSpace > .sw-Card__title > a'
                self.SOUP_SELECT_TITLE = '.sw-Card__headerSpace > .sw-Card__title > a > h3'
                self.SOUP_SELECT_TEXT = '.sw-Card__floatContainer > .sw-Card__summary'

                # CommonEngineの処理を呼び出す
                links = super().get_links(html, type)

        elif type == 'image':
            # CommonEngineの処理を呼び出す
            links = super().get_links(html, type)

        return links

    # 画像検索ページの検索結果(links(list()))を生成するfunction
    def get_image_links(self, soup: BeautifulSoup):
        """get_image_links
        BeautifulSoupから画像検索ページを解析して結果を返す関数.

        Args:
            soup (BeautifulSoup): 解析するBeautifulSoupオブジェクト.

        Returns:
            list: 検索結果(`[{'title': 'title...', 'link': 'https://hogehoge....'}, {...}]`)
        """

        result = []  # image url

        try:
            data = json.loads(soup.text)
        except Exception:
            return result

        for d in data['algos']:
            etitle = d['title']
            elink = d['refererUrl']
            eimage = d['original']['url']

            el = {
                'title': etitle,
                'pagelink': elink,
                'link': eimage,
            }

            result.append(el)

        return result

    def get_suggest_list(self, suggests: list, char: str, html: str):
        """get_suggest_list

        htmlからsuggestを配列で取得する関数.

        Args:
            suggests (list): suggestを追加するための大本のlist.
            char (str): サジェストの文字列.
            html (str): 解析を行うhtml.

        Returns:
            dict: サジェスト配列
        """
        if self.USE_SELENIUM and self.SELENIUM_BROWSER == 'firefox':
            soup = BeautifulSoup(html, features="lxml")
            html = soup.find("pre").text
        data = json.loads(html)
        suggests[char if char == '' else char[-1]] = [e['key']
                                                      for e in data['gossip']['results']]

        return suggests

    def get_image_search_cr(self, keyword: str):
        """get_image_search_cr

        Yahooの画像検索時に必要になるcrumb(cr)パラメータを取得するための前処理リクエストを行う関数

        Args:
            keyword (str): 検索キーワード

        Returns:
            str: crumbパラメータの値
        """

        result = ''

        # urlパラメータを設定
        url_param = {
            'p': keyword,
            'fr': 'top_ga1_sa',
            'ei': 'UTF-8',
            'aq': '-1',
        }
        params = parse.urlencode(url_param)

        # 前処理リクエストを投げる
        pre_result = self.get_result(self.IMAGE_PRE_URL + '?' + params)

        # 前処理リクエストから、crumbパラメータの値を取得する(正規表現)
        pattern = r'{ *"crumb": *"[^"]+" *}'
        data = re.findall(pattern, pre_result)

        if len(data) > 0:
            d = data[0]
            jd = json.loads(d)

            result = jd['crumb']

        return result
