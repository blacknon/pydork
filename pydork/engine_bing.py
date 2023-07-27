#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================


"""engine_bing
    * Bing用の検索用Classを持つモジュール.
"""

import requests
import datetime
import json
import asyncio
import re

from urllib import parse
from bs4 import BeautifulSoup

from .common import Color
from .engine_common import CommonEngine


class Bing(CommonEngine):
    """Bing

    Bing用の検索エンジン用Class.
    """

    def __init__(self):
        # CommonEngineの処理を呼出し
        super().__init__()

        self.NAME = 'Bing'
        self.COLOR = Color.CYAN
        self.COLOR_NAME = self.COLOR + self.NAME + Color.END

        # リクエスト先のURLを指定
        self.ENGINE_TOP_URL = 'https://www.bing.com/'
        self.SEARCH_URL = 'https://www.bing.com/search'
        self.IMAGE_URL = 'https://www.bing.com/images/async'
        self.SUGGEST_URL = 'https://www.bing.com/AS/Suggestions'

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
                'q': keyword,    # 検索キーワード
                'count': '100',  # 1ページごとの表示件数
                'go': '検索',
                'qs': 'ds',
                'from': 'QBRE',
                'filters': '',   # 期間含めフィルターとして指定するパラメータ
                'first': ''      # 開始位置
            }

            # lang/localeが設定されている場合
            if self.LANG != '' and self.LOCALE != '':
                url_param['mkt'] = self.LANG + '-' + self.LOCALE

            # rangeが設定されている場合
            try:
                start = self.RANGE_START
                end = self.RANGE_END

                unix_day = datetime.strptime('1970-01-01', "%Y-%m-%d")
                cd_min = (start - unix_day).days
                cd_max = (end - unix_day).days

                # GETパラメータに日時データを追加
                url_param['filters'] = 'ex1:"ez5_{0}_{1}"'.format(
                    cd_min, cd_max)

            except AttributeError:
                None

        # 検索タイプがimageの場合
        elif type == 'image':
            # 検索urlを指定
            search_url = self.IMAGE_URL

            # 検索パラメータの設定
            url_param = {
                'q': keyword,    # 検索キーワード
                'count': '100',  # 1回ごとの件数
                'first': '',     # 検索位置
                'tsc': 'ImageBasicHover',
                'layout': 'RowBased',
            }

            # rangeが指定されている場合
            # TODO: 日時パラメータを追加(ex: `qft=+filterui%3aage-lt43200`)

        page = 0
        while True:
            # parameterにページを開始する番号を指定
            url_param['first'] = str(page * 100)
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
            'qry': keyword,  # 検索キーワード
            'cvid': 'F5F47E4155E44D86A86690B49023B0EF'
        }

        params = parse.urlencode(url_param)
        url = self.SUGGEST_URL + '?' + params

        return url

    def get_links(self, url: str, html: str, type: str):
        """get_links

        受け付けたhtmlを解析し、検索結果をlistに加工して返す関数.

        Args:
            html (str): 解析する検索結果のhtml.
            type (str): 検索タイプ([text, image]).現時点ではtextのみ対応.

        Returns:
            list: 検索結果(`[{'title': 'title...', 'url': 'https://hogehoge....'}, {...}]`)
        """

        if type == 'text':
            self.SOUP_SELECT_URL = 'h2 > a'
            self.SOUP_SELECT_TITLE = 'h2 > a'
            self.SOUP_SELECT_TEXT = 'li > div > p'

        elif type == 'image':
            self.SOUP_SELECT_URL = '.imgpt > .iusc'

        # CommonEngineの処理を呼び出す
        links = super().get_links(url, html, type)

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

        elements = soup.select(self.SOUP_SELECT_URL)
        edata = [e['m'] for e in elements]

        result = []  # image url
        for e in edata:
            # json化
            je = json.loads(e)

            etitle = je['t']
            elink = je['purl']
            eimage = je['murl']

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
        soup = BeautifulSoup(html, 'lxml')
        elements = soup.select('ul > li')
        suggests[char if char == '' else char[-1]] = [e['query']
                                                      for e in elements]
        return suggests

    def processings_elist(self, elinks, etitles, etexts: list):
        """processings_elist

        self.get_links 内で、取得直後のelinks, etitlesに加工を加えるための関数.
        requestsを用いて、リダイレクトリンクから遷移先urlを取得していく.

        Args:
            elinks (list): elinks(検索結果のlink)の配列
            etitles (list): etitles(検索結果のtitle)の配列
            etexts (list): etexts(検索結果のtext)の配列

        Returns:
            elinks (list): elinks(検索結果のlink)の配列
            etitles (list): etitles(検索結果のtitle)の配列
            etexts (list): etexts(検索結果のtext)の配列
        """

        # 通常のスクレイピングとは別にセッションを作成
        session = requests.session()

        # pool sizeを調整
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=100, pool_maxsize=100)
        session.mount('https://', adapter)

        # proxyを設定
        if self.PROXY != '':
            proxies = {
                'http': self.PROXY,
                'https': self.PROXY
            }
            session.proxies = proxies

        # user-agentを設定
        if self.USER_AGENT != '':
            session.headers.update(
                {
                    'User-Agent': self.USER_AGENT,
                    'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3'
                }
            )

        # asyncio loopを作成
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # リダイレクト先のurlに置き換え
        elinks = loop.run_until_complete(
            resolv_links(loop, session, elinks))
        loop.close()

        return elinks, etitles, etexts


async def resolv_links(loop: asyncio.AbstractEventLoop, session: requests.Session, links: list):
    """resolv_links

    リダイレクト先のurlをパラレルで取得する(Baiduで使用)

    Args:
        loop (asyncio.AbstractEventLoop): loop
        session (requests.Session): 使用するSession
        links (list): リダイレクト先を取得するurlのリスト

    Returns:
        data (list): リダイレクト先を取得したurlのリスト
    """

    async def req(session: requests.Session, url: str):
        task = await loop.run_in_executor(None, resolv_url, session, url)
        return task

    tasks = []
    for link in links:
        # urlをパース
        url = parse.urlparse(link)

        # bingの遷移ページの場合はリダイレクトして処理
        if url.netloc == 'www.bing.com' and url.path == '/ck/a':
            task = req(session, link)
            tasks.append(task)

    data = await asyncio.gather(*tasks)

    return data


def resolv_url(session: requests.Session, url: str):
    """resolv_url
    リダイレクト先のurlを取得する(Baiduで使用)
    Args:
        session (request.Session): リダイレクト先を取得する際に使用するSession
        url (str): リダイレクト先を取得するurl
    Returns:
        url (str): リダイレクト先のurl
    """

    while True:
        try:
            # リダイレクト先のbodyを取得する
            res = session.get(url).text

        except requests.RequestException:
            continue
        except ConnectionError:
            continue
        else:
            # resから１行ずつチェック
            for line in res.splitlines():
                if re.match('^ +var u', line):
                    text = re.findall('"([^"]*)"', line)
                    url = text[0]
                    break
            break

    return url
