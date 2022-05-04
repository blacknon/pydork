#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================


"""engine_duckduckgo
    * DuckDuckGo用の検索用Classを持つモジュール.
"""


import json
import re
import sys

from time import sleep
from urllib import parse
from bs4 import BeautifulSoup

from .common import Color
from .engine_common import CommonEngine


class DuckDuckGo(CommonEngine):
    """DuckDuckGo

    DuckDuckGo用の検索エンジン用Class.
    """

    def __init__(self):
        # CommonEngineの処理を呼出し
        super().__init__()

        self.NAME = 'DuckDuckGo'
        self.COLOR = Color.BLUE
        self.COLOR_NAME = self.COLOR + self.NAME + Color.END

        # リクエスト先のURLを指定
        self.PRE_URL = 'https://duckduckgo.com/'
        self.ENGINE_TOP_URL = 'https://duckduckgo.com/'
        self.SEARCH_URL = 'https://links.duckduckgo.com/d.js'
        self.IMAGE_URL = 'https://duckduckgo.com/i.js'
        self.SUGGEST_URL = 'https://duckduckgo.com/ac/'

    def request_selenium(self, url: str, method='GET', data=None):
        if self.SUGGEST_URL in url:
            # 最初にTOPページを表示
            self.driver.get(self.ENGINE_TOP_URL)

            self.driver.implicitly_wait(3)

            # javascriptからリクエストを投げてjsonを取得
            exec_java_script = 'return fetch("{}").then(response=>response.json())'.format(
                url)
            result = self.driver.execute_script(exec_java_script)

            result = json.dumps(result)

        else:
            result = super().request_selenium(url, method, data)

        return result

    def gen_search_url(self, keyword: str, type: str):
        """gen_search_url

        検索用のurlを生成する.

        Args:
            keyword (str): 検索クエリ.
            type (str): 検索タイプ.

        Returns:
            dict: 検索用url
        """

        # 前処理リクエスト用パラメータの設定
        pre_param = {
            'q': keyword,  # 検索キーワード
            't': 'h_'
        }

        try:
            # 前処理リクエスのセッションを生成する
            pre_params = parse.urlencode(pre_param)
            pre_url = self.PRE_URL + '?' + pre_params

            # 前処理リクエスト1を実行
            self.get_result('https://duckduckgo.com/?t=h_')

            # 待機時間を入れる
            sleep(1)

            # 前処理リクエスト2を実行
            pre_html = self.get_result(pre_url)
            sleep(1)

            r = re.findall(
                r"(?<=vqd\=)[0-9-]+", pre_html
            )

            # get vqd
            vqd = r[0]

        except Exception:
            return

        if type == 'text':
            # 検索urlを指定
            search_url = self.SEARCH_URL

            # 検索パラメータの設定
            url_param = {
                'q': keyword,  # 検索キーワード
                's': 0,  # 取得開始件数
                'vqd': vqd
            }

            # lang/localeが設定されている場合
            if self.LANG != '' and self.LOCALE != '':
                url_param['l'] = self.LANG + '_' + self.LOCALE

            # rangeが設定されている場合(DuckDuckGoにはレンジ指定がないらしいので、追加されたら記述する)

        elif type == 'image':
            # 検索urlを指定
            search_url = self.IMAGE_URL

            # 検索パラメータの設定
            url_param = {
                'q': keyword,  # 検索キーワード
                'o': 'json',  # output format
                'p': 1,
                's': 0,  # 取得開始件数
                'u': 'bing',  # TODO: 利用する検索エンジン(おそらく).後でオプションで指定できるようにする.
                'f': ',,,,,',
                'vqd': vqd
            }

            # lang/localeが設定されている場合
            if self.LANG != '' and self.LOCALE != '':
                url_param['l'] = self.LANG + '-' + self.LANG

        # set next_url
        params = parse.urlencode(url_param)
        self.next_url = search_url + '?' + params

        # while loop
        page = 0
        while True:
            if self.next_url == "":
                break

            # get next_url
            target_url = self.next_url

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
            'q': keyword,  # 検索キーワード
            'kl': 'wt-wt'
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
        links = list()

        # next_url用のurl
        url = ""
        vqd = ""

        if type == 'text':
            # 加工してdictとして扱えるようにする
            r = re.findall(
                r"DDG\.pageLayout\.load\(\'d\',(.+)\]\)\;", html
            )

            try:
                r_dict = json.loads(r[0] + "]")
            except Exception:
                return links

            for r_data in r_dict:
                if "u" in r_data and "s" in r_data:
                    d = {
                        "link": r_data["u"],
                        "title": BeautifulSoup(
                            r_data["t"], "lxml").text,
                        "text": BeautifulSoup(
                            r_data["a"], "lxml").text
                    }
                    links.append(d)

                elif "n" in r_data:
                    base_uri = '{uri.scheme}://{uri.netloc}'.format(
                        uri=parse.urlparse(self.SEARCH_URL)
                    )
                    url = base_uri + r_data["n"]

        elif type == 'image':
            # seleniumを使用している場合、htmlを上書き
            if self.USE_SELENIUM or self.USE_SPLASH:
                soup = BeautifulSoup(html, "lxml")
                selected_one = soup.select_one('html > body > pre')
                html = selected_one.text

            # jsonとして読み込む
            try:
                data = json.loads(html)
            except Exception as e:
                print(e, file=sys.stderr)
                return links

            if 'results' in data:
                results = data['results']

                for r in results:
                    d = {
                        'link': r['image'],
                        'title': r['title'],
                        'pagelink': r['url']
                    }
                    links.append(d)

            if 'vqd' in data:
                vqd = list(data['vqd'].values())[0]

            # next_url用のurlを取得する
            if 'next' in data:
                next_path = data['next']
                next_path = next_path + '&vqd=' + vqd
                base_url = '{uri.scheme}://{uri.netloc}/'.format(
                    uri=parse.urlparse(self.IMAGE_URL)
                )
                url = base_url + next_path

        if url != "":
            self.next_url = url

        return links

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

        data = json.loads(html)
        suggests[char if char == '' else char[-1]] = [e['phrase']
                                                      for e in data]

        return suggests
