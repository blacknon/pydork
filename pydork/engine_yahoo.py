#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
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

    def get_links(self, url: str, html: str, type: str):
        """get_links

        受け付けたhtmlを解析し、検索結果をlistに加工して返す関数.

        Args:
            url  (str): 解析する検索結果のurl.
            html (str): 解析する検索結果のhtml.
            type (str): 検索タイプ([text, image]).現時点ではtextのみ対応.

        Returns:
            list: 検索結果(`[{'title': 'title...', 'url': 'https://hogehoge....'}, {...}]`)
        """

        if type == 'text':
            if self.USE_SPLASH or self.USE_SELENIUM:
                links = self.get_text_links_from_next_data(url, html)

                if not links:
                    links = self.get_text_links_from_html(url, html)

            else:
                links = self.get_text_links_from_html(url, html)

        elif type == 'image':
            # CommonEngineの処理を呼び出す
            links = super().get_links(url, html, type)

        return links

    def get_text_links_from_next_data(self, source_url: str, html: str):
        soup = BeautifulSoup(html, 'lxml')
        element = soup.select_one('#__NEXT_DATA__')
        if element is None or element.string is None:
            return []

        if self.IS_DEBUG:
            print(Color.PURPLE + '[JsonElement]' + Color.END, file=sys.stderr)
            print(Color.PURPLE + element.string + Color.END, file=sys.stderr)

        try:
            data = json.loads(element.string)
        except json.JSONDecodeError:
            return []

        if self.IS_DEBUG:
            print(Color.PURPLE + '[Json]' + Color.END, file=sys.stderr)
            print(Color.PURPLE + json.dumps(data) + Color.END, file=sys.stderr)

        records = self.extract_next_data_algos(data)
        if not records:
            return []

        elinks = [entry['url'] for entry in records if 'url' in entry]
        etitles = [entry['title'] for entry in records if 'title' in entry]
        etexts = [entry.get('description', '') for entry in records if 'url' in entry]

        return self.create_text_links(source_url, elinks, etitles, etexts)

    def extract_next_data_algos(self, data: dict):
        try:
            return data['props']['initialProps']['pageProps']['pageData']['algos']
        except KeyError:
            return []

    def get_text_links_from_html(self, source_url: str, html: str):
        soup = BeautifulSoup(html, 'lxml')
        elinks = [e.get('href', '').strip() for e in soup.select('.sw-Card__headerSpace > .sw-Card__title > a')]
        elinks = [href for href in elinks if href]
        etitles = [e.get_text(" ", strip=True) for e in soup.select('.sw-Card__headerSpace > .sw-Card__title > a > h3')]
        etexts = [e.get_text(" ", strip=True) for e in soup.select('.sw-Card__floatContainer > .sw-Card__summary')]

        if elinks:
            return self.create_text_links(source_url, elinks, etitles, etexts)

        result_selectors = [
            '.sw-Card',
            '.algo',
        ]
        title_selectors = [
            '.sw-Card__title h3',
            'h3',
        ]
        link_selectors = [
            '.sw-Card__title a',
            'a[href]',
        ]
        snippet_selectors = [
            '.sw-Card__summary',
            '.sw-Card__floatContainer',
            'p',
        ]

        links = []
        seen = set()
        for selector in result_selectors:
            blocks = soup.select(selector)
            for block in blocks:
                title = self._extract_first_text(block, title_selectors)
                href = self._extract_first_href(block, link_selectors)
                text = self._extract_first_text(block, snippet_selectors)

                if not title or not href:
                    continue

                key = (href, title)
                if key in seen:
                    continue

                seen.add(key)
                links.append(
                    {
                        'link': href,
                        'title': title,
                        'text': text,
                        'source_url': source_url,
                    }
                )

            if links:
                break

        return links

    def _extract_first_text(self, block, selectors: list):
        for selector in selectors:
            element = block.select_one(selector)
            if element is None:
                continue

            text = element.get_text(" ", strip=True)
            if text:
                return text

        return ''

    def _extract_first_href(self, block, selectors: list):
        for selector in selectors:
            element = block.select_one(selector)
            if element is None:
                continue

            href = element.get('href', '').strip()
            if href:
                return href

        return ''

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
        except json.JSONDecodeError:
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
        suggests[char if char == '' else char[-1]] = [e['key']  # type: ignore
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
