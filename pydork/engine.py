#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================

"""engine
    * Module for performing searches with SearchEngine
"""


import os
import pathlib
import sys

from time import sleep
from string import ascii_lowercase, digits
from datetime import datetime

from .common import Color
from .common import Message
from .engine_baidu import Baidu
from .engine_bing import Bing
from .engine_duckduckgo import DuckDuckGo
from .engine_google import Google
from .engine_yahoo import Yahoo


# 対応する検索エンジンのリスト
ENGINES = ['baidu', 'bing', 'duckduckgo', 'google', 'yahoo']


# 各種SearchEngineへの処理をまとめるWrapper用Class
class SearchEngine:
    """SearchEngine

    Class for Wrapper to perform a search against the specified search engine.

    Examples:
        >>> search_engine = SearchEngine()
        >>> search_engine.set('google')
        >>>
        >>> # Text search in the accepted query
        >>> search_result = search_engine.search('zelda')
        >>>
        >>> # Image search in the accepted query
        >>> search_result = search_engine.search('zelda', type='image')
        >>>
        >>> # Get Suggest in the accepted query
        >>> search_result = search_engine.suggest('zelda')
    """

    def __init__(self):
        None

    # どの検索エンジンを使用するか指定する関数
    def set(self, engine: str):
        """set

        A function that specifies which search engine to use.

        Args:
            engine (str): Specify the search engine to use for the search (see const ENGINES)
        """

        # TODO: 値チェックして、許可した値以外はエラーにする
        if engine == 'baidu':
            self.ENGINE = Baidu()

        elif engine == 'bing':
            self.ENGINE = Bing()

        elif engine == 'duckduckgo':
            self.ENGINE = DuckDuckGo()

        elif engine == 'google':
            self.ENGINE = Google()

        elif engine == 'yahoo':
            self.ENGINE = Yahoo()

        else:
            raise Exception('Error!')

        self.IS_COLOR = False

        # Messageを定義
        self.MESSAGE = Message()
        self.MESSAGE.set_engine(self.ENGINE.NAME, self.ENGINE.COLOR)

    # multithreading用のlockを渡すための関数(現在未使用？)
    def set_lock(self, lock):
        """set_lock

        Function to pass lock for multithreading

        Args:
            lock (threading.Lock): multithreading lock object
        """
        self.ENGINE.LOCK = lock

    # debugフラグを有効化する関数
    def set_is_debug(self, is_debug: bool):
        """set_debug

        set debug flag

        Args:
            debug (bool): debug flag(Enable debug with `True`).
        """

        self.ENGINE.IS_DEBUG = is_debug

    # commandフラグ(コマンドモードでの実行)を有効化する関数
    def set_is_command(self, is_command: bool):
        """set_is_command

        set command flag.
        When the command flag is enabled, the contents used in the command will be output to the console.

        Args:
            is_command (bool): command flag(Enable command mode with `True`).
        """
        self.ENGINE.IS_COMMAND = is_command

    # color出力が有効か否か
    def set_is_color(self, is_color: bool = False):
        """set_is_color

        Specifies whether to display the output in color.

        Args:
            is_color (bool): color flag(Enable color mode with `True`).
        """
        self.IS_COLOR = is_color

    # disable-headlessフラグ(Seleniumをheadlessで起動)を有効化する関数
    def set_disable_headless(self, disable_headless: bool):
        """set_disable_headless

        Function to Disable Selenium's headless option.
        Used when manually bypassing ReCaptcha or when debugging.

        Args:
            disable_headless (bool): Disable Selenium headless option (disable with True)

        Examples:
            >>> search_engine = SearchEngine()
            >>> search_engine.set('google')
            >>>
            >>> # Set Selenium
            >>> search_engine.set_selenium()
            >>>
            >>> # Disable headless mode
            >>> search_engine.set_disable_headless(True)
            >>>
            >>> # Open browser and search query
            >>> search_engine.search('mario')

        """

        self.ENGINE.IS_DISABLE_HEADLESS = disable_headless

    # cookieファイルを入れているディレクトリを渡して、使用するcookieファイルを取得する関数
    def set_cookie_files(self, cookie_dir: str):
        """set_cookie_files

        Function to specify and generate the cookie file name to be used by passing the directory to put the cookie file.
        Currently, cookie files are only used with Selenium.

        Args:
            cookie_dir (str): Directory path where cookie files are placed.
        """

        # フルパスに変換
        cookie_dir = pathlib.Path(cookie_dir).expanduser()
        cookie_dir = pathlib.Path(cookie_dir).resolve()

        # 存在チェックをして、ディレクトリがない場合は新規作成
        if not os.path.exists(cookie_dir):
            # TODO: ディレクトリではなく、ファイルが存在していた場合はエラー処理をする

            # ディレクトリを作成
            os.mkdir(cookie_dir)

        # 使用する方式に応じてpostfixを切り替え
        postfix = ''
        if self.ENGINE.USE_SELENIUM:
            postfix = '_selenium'
        elif self.ENGINE.USE_SPLASH:
            postfix = '_splash'
        else:
            postfix = '_requests'

        # Prefixを付与してPATHを生成
        cookie_file = os.path.join(
            cookie_dir, '.cookie_' + self.ENGINE.NAME.lower() + postfix)

        # 存在チェックをして、ファイルがない場合は新規作成
        if not os.path.exists(cookie_file):
            open(cookie_file, 'a').close()

        # ENGINEのself変数にセットする
        self.ENGINE.COOKIE_FILE = cookie_file

    # 検索エンジンにわたす言語・国の設定を受け付ける
    def set_lang(self, lang: str = "ja", locale: str = "JP"):
        """set_lang

        Function to set the language / country specified by the search engine.

        Args:
            lang (str): Language ([ja,en])
            locale (str): Locale ([JP,US])
        """
        self.ENGINE.set_lang(lang, locale)

    # 検索時の日時範囲を指定
    def set_range(self, start: datetime, end: datetime):
        """set_range

        Specify the date of the search range.

        Args:
            start (datetime): start time(datetime)
            end (datetime): end time(datetime)
        """

        self.ENGINE.set_range(start, end)

    # proxyの設定を受け付ける
    def set_proxy(self, proxy: str):
        """set_proxy

        Set the proxy server to be used when searching.

        Args:
            proxy (str): proxy uri(ex. socks5://localhost:11080, http://hogehoge:8080)
        """
        self.ENGINE.set_proxy(proxy)

    # seleniumを有効にする
    def set_selenium(self, uri: str = None, browser: str = None):
        """set_selenium

        Use Selenium (priority over Splash).

        Args:
            uri (str, optional): Specify the `host:port` of Selenium  (used when Selenium is started by docker etc.). Defaults to None.
            browser (str, optional): Specify Browser to use with Selenium ([chrome, firefox]). Defaults to None.
        """

        self.ENGINE.set_selenium(uri, browser)

    # splashを有効にする
    def set_splash(self, splash_url: str):
        """set_splash

        Use Splash (Selenium has priority).

        Args:
            splash_url (str): Splash uri(ex: `localhost:8050`)
        """

        self.ENGINE.set_splash(splash_url)

    # user_agentの設定値を受け付ける
    def set_user_agent(self, useragent: str = None):
        """set_user_agent

        Specify the UserAgent.
        If not specified, FakeUA or hard-coded UserAgent will be used.


        Args:
            useragent (str, optional): useragent. Defaults to None.
        """

        self.ENGINE.set_user_agent(useragent)

    # 検索を行う
    def search(self, keyword: str, type='text', maximum=100):
        """search

        Search with a search engine.

        Args:
            keyword (str): query.
            type (str, optional): search type. text or image. Defaults to 'text'.
            maximum (int, optional): Max count of searches. Defaults to 100.

        Returns:
            [list]: [{'link', 'http://...', 'title': 'hogehoge...'}, {'link': '...', 'title': '...'}, ... ]
        """

        # ENGINE.MESSAGEへis_command/is_debugを渡す
        self.MESSAGE.set_is_command(self.ENGINE.IS_COMMAND)
        self.MESSAGE.set_is_debug(self.ENGINE.IS_DEBUG)

        # Set header
        header = '[${ENGINE_NAME}Search]'
        if self.IS_COLOR:
            sc = Color(self.ENGINE.COLOR)
            header = sc.out(header)
        self.MESSAGE.set_header(header)

        # ENGINEへMessage()を渡す
        self.ENGINE.set_messages(self.MESSAGE)

        if self.ENGINE.LANG != "" or self.ENGINE.LOCALE != "":
            self.set_lang()

        # メッセージ出力（コマンド実行時のみ）
        colored_keyword = self.ENGINE.MESSAGE.ENGINE_COLOR.out(keyword)
        self.ENGINE.MESSAGE.print_text(
            "$ENGINE: {} Search: {}".format(
                type.capitalize(), colored_keyword),
            use_header=False,
            file=sys.stderr

        )
        result, total = [], 0

        # maximumが0の場合、返す値は0個になるのでこのままreturn
        if maximum == 0:
            return result

        # ENGINEのproxyやブラウザオプションを、各接続方式(Selenium, Splash, requests)に応じてセットし、ブラウザ(session)を作成する
        self.ENGINE.create_session()

        # 検索処理の開始
        gen_url = self.ENGINE.gen_search_url(keyword, type)
        while True:
            # リクエスト先のurlを取得
            try:
                method, url, data = next(gen_url)
            except Exception:
                break

            # debug
            self.ENGINE.MESSAGE.print_text(
                url,
                mode='debug',
                separator=": ",
                header=self.ENGINE.MESSAGE.HEADER + ': ' +
                Color.GRAY + '[DEBUG]: [TargetURL]' + Color.END
            )

            # debug
            self.ENGINE.MESSAGE.print_text(
                self.ENGINE.USER_AGENT,
                mode='debug',
                separator=": ",
                header=self.ENGINE.MESSAGE.HEADER + ': ' +
                Color.GRAY + '[DEBUG]: [UserAgent]' + Color.END
            )

            # 検索結果の取得
            html = self.ENGINE.get_result(url, method=method, data=data)

            # debug
            self.ENGINE.MESSAGE.print_text(
                html,
                mode='debug',
                separator=": ",
                header=self.ENGINE.MESSAGE.HEADER + ': ' +
                Color.GRAY + '[DEBUG]: [Response]' + Color.END
            )

            while True:
                # ReCaptchaページかどうかを識別
                if html is not None:
                    is_recaptcha = self.ENGINE.check_recaptcha(html)
                else:
                    break

                if is_recaptcha:
                    # commandの場合の出力処理
                    self.ENGINE.MESSAGE.print_text(
                        'Oh, Redirect to ReCaptcha Window.',
                        mode='warn',
                        header=self.ENGINE.MESSAGE.ENGINE,
                        separator=": "
                    )

                    # headless browserを使っている場合
                    if self.ENGINE.USE_SELENIUM or self.ENGINE.USE_SPLASH:
                        # byass用の関数にわたす
                        html = self.ENGINE.bypass_recaptcha(url, html)

                        if html is not None:
                            # debug
                            self.ENGINE.MESSAGE.print_text(
                                html,
                                mode='debug',
                                header=self.ENGINE.MESSAGE.HEADER + ': ' + Color.GRAY +
                                '[DEBUG]: [ReCaptchaedResponse]' + Color.END,
                                separator=": "
                            )

                    else:
                        # headless browserが無い場合、Recaptchaには対応していない旨のエラーメッセージを出力する
                        None

                else:  # is_recaptchaがFalseの場合、whileを抜ける
                    break

            # htmlがNone、かつReCaptchaチェックでTrueであった場合
            if html is None and is_recaptcha:
                # commandの場合の出力処理
                self.ENGINE.MESSAGE.print_text(
                    'FAiled ReCaptcha. exit process.',
                    mode='warn',
                    header=self.ENGINE.MESSAGE.ENGINE,
                    separator=": "
                )

                break

            # TODO: resultも関数に渡して重複チェックを行わせる
            # 検索結果をパースしてurlリストを取得する
            links = self.ENGINE.get_links(html, type)

            # linksの件数に応じて処理を実施
            if not len(links):
                # commandの場合の出力処理
                self.ENGINE.MESSAGE.print_text(
                    'No more links.',
                    header=self.ENGINE.MESSAGE.ENGINE,
                    separator=": ",
                    file=sys.stderr,
                )

                # loopを抜ける
                break

            # maximumで指定した件数を超える場合、その件数までを追加してloopを抜ける
            elif len(links) > maximum - total:
                result += links[:maximum - total]
                break

            # TODO: bingのときだけ追加する処理として外だしする方法を考える
            elif len(links) < 10 and self.ENGINE.NAME == "Bing":
                # Bingの場合、件数以下でも次のページが表示されてしまうため件数でbreak
                result += links[:maximum - total]
                break

            else:
                result += links
                total += len(links)

            # 連続でアクセスすると問題があるため、3秒待機
            sleep(3)

        # commandの場合の出力処理
        self.ENGINE.MESSAGE.print_text(
            'Finally got ' + self.ENGINE.COLOR +
            str(len(result)) + Color.END + ' links.',
            header=self.ENGINE.MESSAGE.ENGINE,
            separator=": ",
            file=sys.stderr,
        )

        # save cookies
        if self.ENGINE.COOKIE_FILE != '':
            self.ENGINE.write_cookies()

        # sessionを終了
        self.ENGINE.close_session()

        return result

    # suggestを取得する
    def suggest(self, keyword: str, jap=False, alph=False, num=False):
        """suggest

        get suggest with a search engine.

        Args:
            keyword (str): query
            jap (bool, optional): with japanese char. Defaults to False.
            alph (bool, optional): with alphabet char. Defaults to False.
            num (bool, optional): with number. Defaults to False.

        Returns:
            [list]: {'with char': ['suggest1', 'suggest2' ...]}
        """

        # ENGINEのproxyやブラウザオプションを、各接続方式(Selenium, Splash, requests)に応じてセットし、ブラウザ(session)を作成する
        self.ENGINE.create_session()

        # 文字リスト作成
        chars = ['', ' ']

        # japフラグが有効な場合、キーワードに日本語を含めてサジェストを検索
        chars += [' ' + chr(i) for i in range(12353, 12436)] if jap else[]

        # alphフラグが有効な場合、キーワードにアルファベットを含めてサジェストを検索
        chars += [' ' + char for char in ascii_lowercase] if alph else[]

        # numフラグが有効な場合、キーワードに数字を含めてサジェストを検索
        chars += [' ' + char for char in digits] if num else []

        # サジェスト取得
        suggests = {}
        for char in chars:
            word = keyword + char
            url = self.ENGINE.gen_suggest_url(word)
            html = self.ENGINE.get_result(url)

            # TODO: 各エンジンでjson/textの変換処理を別途実装する必要がある
            suggests = self.ENGINE.get_suggest_list(suggests, char, html)

            sleep(0.5)

        # sessionを終了
        self.ENGINE.close_session()

        return suggests
