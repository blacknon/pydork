#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================


"""engine_baidu
    * Baidu用の検索用Classを持つモジュール.
"""

import requests
import json
import asyncio
import sys

from urllib import parse
from bs4 import BeautifulSoup

from .engine_common import CommonEngine
from .common import Color


class Baidu(CommonEngine):
    """Baidu

    Baidu用の検索エンジン用Class.

    Note:
        検索結果に直接urlが記載されておらず、リンクを踏んで移動先のurlを取得する必要がある。
        そのため、検索結果を取得してからパラレルで検索結果urlからリンク先urlを取得している。
        なお、その際のリクエストはSelenium/Splashを使用している場合でもrequestsを使っている。
    """

    def __init__(self):
        # CommonEngineの処理を呼出し
        super().__init__()

        self.NAME = 'Baidu'
        self.COLOR = Color.RED
        self.COLOR_NAME = self.COLOR + self.NAME + Color.END

        # リクエスト先のURLを指定
        self.ENGINE_TOP_URL = 'https://www.baidu.com/'
        self.SEARCH_URL = 'https://www.baidu.com/s'
        self.IMAGE_URL = 'https://image.baidu.com/search/acjson'
        self.SUGGEST_URL = 'https://www.baidu.com/sugrec'

    def gen_search_url(self, keyword: str, type: str):
        """gen_search_url

        検索用のurlを生成する.

        Args:
            keyword (str): 検索クエリ.
            type (str): 検索タイプ.

        Returns:
            dict: 検索用url
        """

        if type == 'text':
            # 1ページごとの表示件数
            view_num = 50

            # 検索urlを指定
            search_url = self.SEARCH_URL

            # 検索パラメータの設定
            url_param = {
                'wd': keyword,  # 検索キーワード
                'rn': view_num,     # 1ページごとの表示件数
                'filter': '0',  # aaa
                'ia': 'web',    #
                'pn': ''        # 開始位置
            }

        elif type == 'image':
            # 1ページごとの表示件数
            view_num = 30

            # example:
            #   'https://image.baidu.com/search/acjson?tn=resultjson_com&logid=10696586825489113064&ipn=rj&ct=201326592&is=&fp=result&queryWord=poop&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=&z=&ic=&hd=&latest=&copyright=&word=poop&s=&se=&tab=&width=&height=&face=&istype=&qc=&nc=1&fr=&expermode=&force=&pn=30&rn=30&gsm=1e&1617708591950='
            #   'https://image.baidu.com/search/acjson?tn=resultjson_com&logid=11967476791890431299&ipn=rj&ct=201326592&is=&fp=result&queryWord=poop&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=&z=&ic=&hd=&latest=&copyright=&word=poop&s=&se=&tab=&width=&height=&face=&istype=&qc=&nc=1&fr=&expermode=&nojc=&pn=60&rn=30&gsm=3c&1629026924429='

            # 検索urlを指定
            search_url = self.IMAGE_URL

            # 検索パラメータの設定
            url_param = {
                'tn': 'resultjson_com',
                'fp': 'result',
                'queryWord': keyword,
                'word': keyword,
                'logid': '12399428100030957064',
                'ipn': 'rj',
                'ct': '201326592',
                'lm': '-1',
                'cl': 2,
                'ie': 'utf-8',
                'nc': 1,
                'pn': 0,  # 開始位置
                'rn': view_num,
                'gsm': '3c',
            }

        page = 0
        while True:
            # parameterにページを開始する番号を指定
            url_param['pn'] = str(page * view_num)
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
            'wd': keyword,  # 検索キーワード
            'prod': 'pc'   #
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

        links = []

        if type == 'text':
            links = self.get_text_links_with_fallback(url, html)
            if links:
                return links

            # Splash経由で通信している場合
            self.SOUP_SELECT_URL = '.tts-title > a'
            self.SOUP_SELECT_TITLE = '.tts-title > a'
            self.SOUP_SELECT_TEXT = '.c-gap-top-small > span'

            # CommonEngineの処理を呼び出す
            links = super().get_links(url, html, type)

        elif type == 'image':
            # unicode escape
            # html = html.encode().decode("unicode-escape")
            html = html.replace("\\'", "'")

            # seleniumを使用している場合、htmlで返ってくるためjson要素のみを抽出する
            if self.USE_SELENIUM:
                html_text = ""
                soup = BeautifulSoup(html, "lxml")

                for text in soup.find_all(text=True):
                    if text.strip():
                        html_text += text

                html = html_text

            # json load
            try:
                json_data = json.loads(html, strict=False)
            except json.JSONDecodeError as e:
                print(e, file=sys.stderr)
                return links

            if 'data' in json_data:
                data = json_data['data']

                for d in data:
                    if 'replaceUrl' in d:
                        result = dict()

                        # 画像ファイルのurlをパラメータに持つvalueを取得する
                        replace_url = d['replaceUrl'][0]['ObjURL']
                        replace_url = replace_url.replace(
                            'image_search/', 'image_search/?')

                        # url valueをparse
                        replace_url_query = parse.urlparse(replace_url).query

                        # パラメータを取得
                        replace_url_query_dict = parse.parse_qs(
                            replace_url_query)

                        if 'src' not in replace_url_query_dict:
                            continue

                        # 画像urlを取得
                        result['link'] = replace_url_query_dict['src'][0]

                        if 'fromPageTitle' in d:
                            result['title'] = d['fromPageTitle']

                        links.append(result)

        return links

    def get_text_links_with_fallback(self, source_url: str, html: str):
        soup = BeautifulSoup(html, 'lxml')

        result_selectors = [
            '.result',
            '.c-container',
            '.xpath-log',
        ]
        title_selectors = [
            '.tts-title',
            'h3',
            'h3 a',
        ]
        link_selectors = [
            '.tts-title a',
            'h3 a',
            'a[href]',
        ]
        snippet_selectors = [
            '.c-gap-top-small',
            '.content-right_8Zs40',
            '.c-span-last p',
            '.c-color-text',
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

        if not links:
            return links

        raw_links = [item['link'] for item in links]
        raw_titles = [item['title'] for item in links]
        raw_texts = [item.get('text', '') for item in links]
        raw_links, raw_titles, raw_texts = self.processings_elist(
            raw_links, raw_titles, raw_texts
        )

        return self.create_text_links(source_url, raw_links, raw_titles, raw_texts)

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

        try:
            data = json.loads(html)
        except json.JSONDecodeError:
            soup = BeautifulSoup(html, "lxml")
            json_data = soup.select_one('html > body')
            if json_data is None or json_data.text is None or json_data.text.strip() == '':
                return suggests
            try:
                data = json.loads(json_data.text)
            except json.JSONDecodeError:
                return suggests

        if 'g' in data:
            suggests[char if char == '' else char[-1]
                     ] = [e['q']
                          for e in data['g']]
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
        session.mount('http://', adapter)

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
    indexes = []
    resolved_links = list(links)

    for index, link in enumerate(links):
        task = req(session, link)
        tasks.append(task)
        indexes.append(index)

    if not tasks:
        return resolved_links

    data = await asyncio.gather(*tasks)

    for task_index, index in enumerate(indexes):
        if data[task_index]:
            resolved_links[index] = data[task_index]

    return resolved_links


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
            res_header = session.head(url, allow_redirects=False).headers
        except requests.RequestException:
            return url
        except ConnectionError:
            return url
        except Exception:
            return url
        else:
            url = res_header.get('Location', url)
            break

    return url
