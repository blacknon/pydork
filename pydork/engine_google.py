#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================


"""engine_google
    * Google用の検索用Classを持つモジュール.
"""


import json
import os

from time import sleep
from json.decoder import JSONDecodeError
from urllib import parse
from lxml import etree

from .common import Color
from .recaptcha import TwoCaptcha
from .engine_common import CommonEngine


# Google画像検索で使用するパラメータID
RPC_ID = "HoAMBc"


class Google(CommonEngine):
    """Google

    Google用の検索エンジン用Class.
    """

    def __init__(self):
        # CommonEngineの処理を呼出し
        super().__init__()

        self.NAME = 'Google'
        self.COLOR = Color.PURPLE
        self.COLOR_NAME = self.COLOR + self.NAME + Color.END

        # リクエスト先のURLを指定
        self.ENGINE_TOP_URL = 'https://www.google.com/'
        self.SEARCH_URL = 'https://www.google.com/search'
        self.IMAGE_URL = 'https://www.google.com/_/VisualFrontendUi/data/batchexecute'
        self.SUGGEST_URL = 'http://www.google.com/complete/search'

        # ReCaptcha画面かどうかの識別用
        self.SOUP_RECAPTCHA_TAG = '#captcha-form > #recaptcha'

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

        if type == 'text':
            # 検索用urlを指定
            search_url = self.SEARCH_URL

            # 検索パラメータの設定
            url_param = {
                'q': keyword,   # 検索キーワード
                'oq': keyword,  # 検索キーワード
                'num': '100',   # 1ページごとの表示件数
                'filter': '0',  # 類似ページのフィルタリング(0...無効, 1...有効)
                'start': '',    # 開始位置
                'tbs': '',      # 期間
                'nfpr': '1'     # もしかして検索(Escape hatch)を無効化
            }

            # lang/localeが設定されている場合
            if self.LANG != '' and self.LOCALE != '':
                url_param['hl'] = self.LANG
                url_param['gl'] = self.LOCALE

            # rangeが設定されている場合
            try:
                start = self.RANGE_START
                end = self.RANGE_END

                cd_min = start.strftime("%m/%d/%Y")
                cd_max = end.strftime("%m/%d/%Y")

                # GETパラメータに日時データを追加
                url_param['tbs'] = "cdr:1,cd_min:{0},cd_max:{1}".format(
                    cd_min, cd_max)

            except AttributeError:
                None

            page = 0
            while True:
                # parameterにページを開始する番号を指定
                url_param['start'] = str(page * 100)
                params = parse.urlencode(url_param)

                target_url = search_url + '?' + params

                yield 'GET', target_url, None

                page += 1

        elif type == 'image':
            # 検索用urlを指定
            search_url = self.IMAGE_URL

            # Refererの設定
            if not self.USE_SELENIUM:
                self.session.headers.update(
                    {"Referer": "https://www.google.com/"}
                )

            # 検索パラメータの設定
            url_param = {
                'rpcids': 'HoAMBc',
                'hl': 'id',
                'authuser': '0',
                'soc-app': '162',
                'soc-platform': '1',
                'soc-device': '1',
                'rt': 'c'
            }

            # 画像のカーソル位置指定パラメータを作成
            self.image_next_cursor = None
            self.image_cursor = []

            page = 0
            while True:
                # post dataを生成
                data = {
                    "f.req": build_rpc_request(keyword, (self.image_cursor, self.image_next_cursor), page),
                    "at": "ABrGKkQnVYg89U_cdKuhNZ5hM4vx:1616119655028",
                    # "": "",
                }

                params = parse.urlencode(url_param)
                target_url = search_url + '?' + params

                yield 'POST', target_url, data

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
            'output': 'toolbar',
            'ie': 'utf-8',
            'oe': 'utf-8',
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

        # テキスト検索の場合
        if type == 'text':
            # request or seleniumの定義
            self.SOUP_SELECT_URL = '#main > div > div > .kCrYT > a'
            self.SOUP_SELECT_TITLE = '#main > div > div > .kCrYT > a > h3 > div'
            self.SOUP_SELECT_TEXT = '#main > div > div > .kCrYT > div > div > div > div > div'

            # Selenium経由、かつFirefoxを使っている場合
            if self.USE_SELENIUM and self.SELENIUM_BROWSER == 'firefox':
                self.SOUP_SELECT_URL = '.jtfYYd > div > .yuRUbf > a'
                self.SOUP_SELECT_TITLE = '.jtfYYd > div > .yuRUbf > a > .LC20lb'
                self.SOUP_SELECT_TEXT = '.jtfYYd > div > div'

            # Splash経由で通信している場合
            elif self.USE_SPLASH:
                self.SOUP_SELECT_URL = '.yuRUbf > a'
                self.SOUP_SELECT_TITLE = '.yuRUbf > a > .LC20lb'
                self.SOUP_SELECT_TEXT = '.jtfYYd > div > div'

            # CommonEngineの処理を呼び出す
            links = super().get_links(html, type)

        # イメージ検索の場合
        elif type == 'image':
            links = self.get_image_links(html)

        return links

    # 画像検索ページの検索結果(links(list()))を生成するfunction
    def get_image_links(self, html: str):
        """get_image_links

        BeautifulSoupから画像検索ページを解析して結果を返す関数.
        Seleniumを利用し、自動的にページ末尾まで移動して続きを取得する.
        クリック等が発生するため、抽出にかなり時間がかかる.

        Args:
            html (str): 解析する検索結果のhtml.

        Returns:
            list: 検索結果(`[{'title': 'title...', 'link': 'https://hogehoge....'}, {...}]`)

        参考:
            - https://github.com/Wikidepia/py-googleimages/blob/b781b79e9bf40d29cf6fcbdcf625303abf3718bd/googleimages/client.py
        """

        links = list()

        # 改行区切りでloop
        for line in html.split("\n"):
            if RPC_ID not in line:
                continue

            # Make it json readable
            line_cl = line.replace("\\n", "")  # Remove \n

        lineson = json.loads(line_cl)

        data = pjson_loads(lineson[0][2])

        # 画像のカーソル位置を更新
        self.image_next_cursor = data[-2]
        self.image_img_cursor = data[31][0][12][11][5]

        for img in data[31][0][12][2]:
            # imgの値をチェック
            if img[1] is None:
                continue

            link = img[1][3][0]  # 画像ファイルのurl
            title = img[1][9]['2003'][3]  # 画像ファイルのあるページのtitle
            pagelink = img[1][9]['2003'][2]  # 画像ファイルのあるページのurl
            links.append(
                {
                    "link": link,
                    "title": title,
                    "pagelink": pagelink,
                }
            )

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

        sug_root = etree.XML(html)
        sug_data = sug_root.xpath("//suggestion")
        data = [s.get("data") for s in sug_data]

        suggests[char if char == '' else char[-1]] = data

        return suggests

    def processings_elist(self, elinks, etitles, etexts: list):
        """processings_elist

        self.get_links 内で、取得直後のelinks, etitlesに加工を加えるための関数.

        Args:
            elinks (list): elinks(検索結果のlink)の配列
            etitles (list): etitles(検索結果のtitle)の配列
            etexts (list): etexts(検索結果のtext)の配列

        Returns:
            elinks (list): elinks(検索結果のlink)の配列
            etitles (list): etitles(検索結果のtitle)の配列
            etexts (list): etexts(検索結果のtext)の配列
        """

        # seleniumでfirefoxを使っていない、かつsplashを使っていない場合
        new_elinks = []
        for elink in elinks:
            parsed = parse.urlparse(elink)
            parsed_query = parse.parse_qs(parsed.query)

            if 'url' in parsed_query and elink[0] == '/':
                parsed_q = parsed_query['url']
                if len(parsed_q) > 0:
                    new_elink = parsed_q[0]
                    new_elinks.append(new_elink)
            else:
                new_elinks.append(elink)
        elinks = list(dict.fromkeys(new_elinks))

        return elinks, etitles, etexts

    def bypass_recaptcha_selenium(self, url: str, html: str):
        """bypass_recaptcha_selenium

        SeleniumでReCaptchaを突破する関数.
        2Captchaでの自動突破の場合、CookieとProxyが必要となる.

        Args:
            url (str): ReCaptcha画面が表示されてしまったリクエストのurl
            html (str): ReCaptcha画面のhtml

        Returns:
            str: ReCaptchaを突破後のurlのhtml
        """

        # resultを定義しておく
        result = None

        # 環境変数を取得
        TC_API_KEY = os.getenv('API_KEY_2CAPTCHA')

        # Seleniumの場合、手動でBypassが行えるようにする
        if self.IS_DISABLE_HEADLESS:
            while True:
                # 現在のSeleniumのurlを取得する
                current_url = self.driver.current_url
                current_url_parse = parse.urlparse(current_url)

                # current_urlのpathが `/sorry/index` か識別する
                current_url_path = current_url_parse.path
                if current_url_path != '/sorry/index':
                    break

                # 待機
                sleep(1)

            sleep(5)

            # 現在のページ(ReCaptchaから移動したページ)のhtmlを取得する
            result = self.driver.page_source

        # self.IS_DISABLE_HEADLESS がFalseで、かつ`API_KEY_2CAPTCHA`が定義されている場合
        elif TC_API_KEY is not None:
            # solverを作成
            solver = TwoCaptcha(TC_API_KEY)

            # flag set
            solver.set_debug(self.IS_DEBUG)
            solver.set_command(self.IS_COMMAND)
            solver.set_user_agent(self.USER_AGENT)
            solver.set_messages(self.MESSAGE)

            # solverからのレスポンスを取得する
            code = solver.google_recaptcha(
                html=html,
                url=url,
                cookies=self.driver.get_cookies(),
                proxy=self.PROXY,

            )

            # ReCaptchaの解除に失敗した場合
            if code is None:
                return result

            # 解除コードを所定のtextareaに入力
            self.driver.execute_script("""
              document.getElementById(
                  "g-recaptcha-response").innerHTML = arguments[0]
            """, code)

            # ボタンクリック
            self.driver.execute_script(
                'var element=document.getElementById("g-recaptcha-response"); element.style.display="none";')

            self.driver.execute_script('submitCallback()')

            sleep(10)

            # 結果を取得する
            result = self.driver.page_source

        return result


def build_rpc_request(keyword: str, cursor: list, page: int):
    """build_rpc_request

    画像検索で使用するrpcデータの生成用関数.

    Original:
        https://github.com/Wikidepia/py-googleimages/blob/b781b79e9bf40d29cf6fcbdcf625303abf3718bd/googleimages/utils.py

    Args:
        keyword (str): [description]
        cursor (list): [description]
        page (int): [description]

    Returns:
        [type]: [description]
    """

    RPC_ID = "HoAMBc"

    return json.dumps(
        [
            [
                [
                    RPC_ID,
                    json.dumps(
                        [
                            None,
                            None,
                            [
                                1,
                                None,
                                450,
                                1,
                                1280,
                                cursor[0],
                                [],
                                [],
                                None,
                                None,
                                None,
                                0,
                                310,
                                [],
                            ],
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            [
                                keyword,
                                None,
                                None,
                                "strict",
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                "lnms",
                            ],
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            [
                                cursor[1],
                                "CAM=",
                                "CgtHUklEX1NUQVRFMBAaIAA=",
                            ],
                        ],
                        separators=(",", ":"),
                    ),
                    None,
                    "generic",
                ],
            ]
        ],
        separators=(",", ":"),
    )


def pjson_loads(text):
    """pjson_loads

    画像検索で使用するデータの生成用関数.

    Original:
        https://github.com/Wikidepia/py-googleimages/blob/b781b79e9bf40d29cf6fcbdcf625303abf3718bd/googleimages/utils.py

    Args:
        text ([type]): [description]

    Returns:
        [type]: [description]
    """
    while True:
        try:
            data = json.loads(text, strict=False)
        except JSONDecodeError as exc:
            if exc.msg == "Invalid \\escape":
                text = text[: exc.pos] + "\\" + text[exc.pos:]
            else:
                raise
        else:
            return data
