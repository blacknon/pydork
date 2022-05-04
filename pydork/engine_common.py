#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================


"""engine_common
    * SearchEngine Classから呼び出す、各検索エンジンで共通の処理を保持させる継承用Classである `CommonEngine` を持つモジュール.
"""


import requests
import os
import pickle

# selenium driver auto install packages
import chromedriver_autoinstaller
import geckodriver_autoinstaller

# seleniumrequests
from seleniumrequests import Chrome, Firefox

# selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from urllib import parse
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from datetime import datetime

from .common import Color, Message


# 各検索エンジン用class共通の処理を記述した継承用class
class CommonEngine:
    """CommonEngine

    検索エンジンごとの処理を記述するClassのための、継承用Class.
    """

    # Class作成時の処理
    def __init__(self):
        # headless browserの利用有無フラグ(デフォルト: False)
        self.USE_SELENIUM = False
        self.USE_SPLASH = False

        # 初期値の作成
        self.LOCK = None
        self.COOKIE_FILE = ''
        self.SPLASH_URI = ''
        self.PROXY = ''
        self.USER_AGENT = ''
        self.LANG = ''
        self.LOCALE = ''
        self.IS_DEBUG = False
        self.IS_COMMAND = False
        self.IS_DISABLE_HEADLESS = False
        self.MESSAGE = False

        # ReCaptcha画面かどうかの識別用(初期値(ブランク))
        self.RECAPTCHA_SITEKEY = ''
        self.SOUP_RECAPTCHA_TAG = ''
        self.SOUP_RECAPTCHA_SITEKEY = ''

    # 検索エンジンにわたす言語・国の設定を受け付ける
    def set_lang(self, lang: str, locale: str):
        """set_lang

        検索エンジンで指定する言語・国の設定を行う関数

        Args:
            lang (str): 検索エンジンのパラメータで指定する言語を指定する([ja,en])
            locale (str): 検索エンジンのパラメータで指定する国を指定する([JP,US])
        """

        self.LANG = lang
        self.LOCALE = locale

    # 検索時の日時範囲を指定
    def set_range(self, start: datetime, end: datetime):
        """set_range

        検索エンジンで指定する日付範囲を指定する

        Args:
            start (datetime): 検索対象ページの対象範囲開始日時(datetime)
            end (datetime): 検索対象ページの対象範囲終了日時(datetime)
        """
        self.RANGE_START = start
        self.RANGE_END = end

    # user_agentの設定値を受け付ける(引数がない場合はランダム。Seleniumの際は自動的に使用したbrowserのagentを指定)
    def set_user_agent(self, user_agent: str = None, browser: str = None):
        """set_user_agent

        user_agentの値を受け付ける.
        user_agentの指定がない場合、 Chromeを使用したものとする.
        また、もし`browser`が指定されている場合はそのブラウザのUser Agentを指定する.

        注) seleniumを利用する場合、事前に有効にする必要がある。

        Args:
            user_agent (str, optional): User Agentを指定する. Defaults to None.
            browser (str, optional): Seleniumで使用するBrowserを指定する([chrome, firefox]). Defaults to None.
        """

        if user_agent is None:
            # seleniumが有効になっている場合、そのままSeleniumで利用するブラウザのUAを使用する
            if self.USE_SELENIUM:
                user_agent = ''
            else:
                try:
                    ua = UserAgent(verify_ssl=False, use_cache_server=True)
                    if user_agent is None:
                        if browser is None:
                            user_agent = ua.firefox

                        elif browser == 'chrome':
                            user_agent = ua.chrome

                        elif browser == 'firefox':
                            user_agent = ua.chrome

                except Exception:
                    user_agent = 'Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36.'

        self.USER_AGENT = user_agent

    # seleniumを有効にする
    #   - splashより優先
    #   - host, browserは、指定がない場合はそれぞれデフォルト設定(hostは指定なし、browserはchrome)での動作
    #   - browserは `chrome` or `firefox` のみ受け付ける
    def set_selenium(self, uri: str = None, browser: str = None):
        """set_selenium

        検索時にSelenium経由で通信を行う.
        他のHeadless Browserと比較して最優先(Splash等が有効でもこちらが優先される).

        Args:
            uri (str, optional): APIのURIを指定(localhost:4444). Defaults to None.
            browser (str, optional): 使用するブラウザを指定([chrome, firefox]). Defaults to None.
        """

        # 入力値検証(browser: chrome or firefox)
        if browser is None:
            browser = 'chrome'

        # USE_SELENIUM to True
        self.USE_SELENIUM = True
        self.SELENIUM_URI = uri
        self.SELENIUM_BROWSER = browser

    # proxyの設定を受け付ける
    def set_proxy(self, proxy: str):
        """set_proxy

        検索時に使用するProxyを指定する(uri指定)

        Args:
            proxy (str): ProxyのURIを指定する(socks5://localhost:11080, http://hogehoge:8080)
        """

        self.PROXY = proxy

    # splash urlの値を受け付ける
    def set_splash(self, splash_url: str):
        """set_splash

        検索時にSplashを有効にする.
        (Seleniumと同時に有効化されている場合、Seleniumを優先する)

        Args:
            splash_url (str): Splashのアクセス先URIを指定する(ex: `localhost:8050`)
        """

        self.USE_SPLASH = True
        self.SPLASH_URI = splash_url

    # common.Messageを受け付ける
    def set_messages(self, message: Message):
        self.MESSAGE = message

    # cookieをcookiefileから取得する
    def read_cookies(self):
        """read_cookies

        `self.COOKIE_FILE` からcookieを読み込む.
        現時点ではSeleniumでのみ動作.
        """

        # cookieファイルのサイズを取得
        file_size = os.path.getsize(self.COOKIE_FILE)

        # cookieファイルのサイズが0以上の場合
        if file_size > 0:
            # cookie fileからcookieの取得
            cookies = pickle.load(open(self.COOKIE_FILE, "rb"))

            # seleniumを使う場合
            if self.USE_SELENIUM:
                # 事前アクセスが必要になるため、検索対象ドメインのTOPページにアクセスしておく
                self.driver.get(self.ENGINE_TOP_URL)

                # cookieを設定していく
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception:
                        pass

            # splashを使う場合
            elif self.USE_SPLASH:
                # NOTE: 動作しないためコメントアウト
                # TODO: 確認して修正
                # self.session.cookies.update(cookies)
                None

            # requestを使う場合
            else:
                # NOTE: 動作しないためコメントアウト
                # TODO: 確認して修正
                # self.session.cookies.update(cookies)
                None

    # cookieをcookiefileに書き込む
    def write_cookies(self):
        """write_cookies

        cookiesを `self.COOKIE_FILE` に書き込む.

        """

        cookies = None

        # seleniumを使う場合
        if self.USE_SELENIUM:
            cookies = self.driver.get_cookies()

        # splashを使う場合
        elif self.USE_SPLASH:
            cookies = self.session.cookies

        # requestを使う場合
        else:
            cookies = self.session.cookies

        # cookieを書き込み
        with open(self.COOKIE_FILE, 'wb') as f:
            pickle.dump(cookies, f)

    # seleniumのOptionsを作成
    def create_selenium_options(self):
        """create_selenium_options

        Seleniumのoptionsを生成して返す.

        Returns:
            Options: 指定されたブラウザに応じたSeleniumのOptionsを返す.
        """

        if self.SELENIUM_BROWSER == 'chrome':
            options = ChromeOptions()

        elif self.SELENIUM_BROWSER == 'firefox':
            options = FirefoxOptions()

        # set headless option
        if not self.IS_DISABLE_HEADLESS:
            options.add_argument('--headless')

        # set user_agent option
        if self.USER_AGENT != '':
            options.add_argument('--user-agent=%s' % self.USER_AGENT)

        return options

    # selenium driverの作成
    def create_selenium_driver(self):
        """create_selenium_driver

        Seleniumで使用するDriverを作成する関数.
        Optionsもこの関数で作成する.
        """

        # optionsを取得する
        options = self.create_selenium_options()

        # proxyを追加
        if self.PROXY != '':
            options.add_argument('--proxy-server=%s' % self.PROXY)
            # debug: 投げてるリクエストの調査のため
            # options.add_argument('--proxy-server=%s' % 'http://localhost:8080')

        # browserに応じてdriverを作成していく
        if self.SELENIUM_BROWSER == 'chrome':
            chromedriver_autoinstaller.install()
            self.driver = Chrome(options=options)

        elif self.SELENIUM_BROWSER == 'firefox':
            # profileを作成する
            profile = webdriver.FirefoxProfile()
            profile.set_preference('devtools.jsonview.enabled', False)
            profile.set_preference('plain_text.wrap_long_lines', False)
            profile.set_preference('view_source.wrap_long_lines', False)

            # debug comment out.
            # capabilities = webdriver.DesiredCapabilities().FIREFOX
            # capabilities['acceptSslCerts'] = True

            geckodriver_autoinstaller.install()
            self.driver = Firefox(options=options, firefox_profile=profile)

        # NOTE:
        #   User Agentを確認する場合、↓の処理で実施可能(Chrome/Firefoxともに)。
        # ```python
        # user_agent = self.driver.execute_script("return navigator.userAgent")
        # print(user_agent)
        # ```

        return

    # selenium経由でリクエストを送信する
    def request_selenium(self, url: str, method='GET', data=None):
        """[summary]

        Selenium経由でGETリクエストを投げて、その結果をhtml(文字列)で返す.

        Args:
            url (str):    リクエストを投げるurl.
            method (str): リクエストメソッド.
            data (str):   POSTメソッド時に利用するdata.

        Returns:
            str: htmlの文字列.
        """

        if method == 'GET':
            response = self.driver.get(url)

            # wait all elements
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located)

            # wait 5 seconds(wait DOM)
            if self.NAME in ('Bing', 'Baidu', 'DuckDuckGo'):
                self.driver.implicitly_wait(20)

            # get result
            result = self.driver.page_source

        elif method == 'POST':
            response = self.driver.request('POST', url, data=data)

            # wait all elements
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located)

            # wait 5 seconds(wait DOM)
            if self.NAME in ('Bing', 'Baidu', 'DuckDuckGo'):
                self.driver.implicitly_wait(20)

            # get result
            result = response.text

        return result

    # splash経由でのリクエストを送信する
    def request_splash(self, url: str, method='GET', data=None):
        """request_splash

        Splash経由でGETリクエストを投げて、その結果をhtml(文字列)で返す.

        Args:
            url (str):    リクエストを投げるurl.
            method (str): リクエストメソッド.
            data (str):   POSTメソッド時に利用するdata.

        Returns:
            str: htmlの文字列.
        """

        # urlを生成する
        splash_url = 'http://' + self.SPLASH_URI + '/render.html'

        # param
        params = {
            'url': url
        }

        # Proxy指定をする場合
        if self.PROXY != '':
            params['proxy'] = self.PROXY

        # リクエストを投げてレスポンスを取得する
        if method == 'GET':
            result = self.session.get(splash_url, params=params).text

        # NOTE: Googleの画像検索のPOSTがSplashではレンダリングできないので、特例対応でrequestsを使用する.
        # TODO: Splashでもレンダリングできるようになったら書き換える.
        elif method == 'POST' and self.NAME == 'Google' and self.IMAGE_URL in url:
            # create session
            session = requests.session()

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

            result = session.post(url, data=data).text

        elif method == 'POST':
            headers = {'Content-Type': 'application/json'}
            params['http_method'] = 'POST'
            params['body'] = parse.urlencode(data)

            result = self.session.post(
                splash_url,
                headers=headers,
                json=params
            ).text

        return result

    # seleniumやsplushなどのヘッドレスブラウザ、request.sessionの作成・設定、cookieの読み込みを行う
    def create_session(self):
        """create_session

        指定された接続方式(Seleniumなどのヘッドレスブラウザの有無)に応じて、driverやsessionを作成する.
        cookiesの読み込みやproxyの設定が必要な場合、この関数内で処理を行う.
        """

        # seleniumを使う場合
        if self.USE_SELENIUM:
            self.create_selenium_driver()

        # splashを使う場合
        elif self.USE_SPLASH:
            # create session
            self.session = requests.session()

            # user-agentを設定
            if self.USER_AGENT != '':
                self.session.headers.update(
                    {
                        'User-Agent': self.USER_AGENT,
                        'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3'
                    }
                )

        # requestを使う場合
        else:
            # create session
            self.session = requests.session()

            # リダイレクトの上限を60にしておく(baidu対策)
            self.session.max_redirects = 60

            # proxyを設定
            if self.PROXY != '':
                proxies = {
                    'http': self.PROXY,
                    'https': self.PROXY
                }
                self.session.proxies = proxies

            # user-agentを設定
            if self.USER_AGENT != '':
                self.session.headers.update(
                    {
                        'User-Agent': self.USER_AGENT,
                        'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3'
                    }
                )

        # cookiefileが指定されている場合、読み込みを行う
        if self.COOKIE_FILE != '':
            self.read_cookies()

        return

    # sessionをcloseする
    def close_session(self):
        if self.USE_SELENIUM:
            self.driver.quit()
        else:
            self.session.close()

    # リクエストを投げてhtmlを取得する(selenium/splash/requestで分岐してリクエストを投げるwrapperとして動作させる)
    def get_result(self, url: str, method='GET', data=None):
        """get_result

        接続方式に応じて、urlへGETリクエストを投げてhtmlを文字列で返す関数.

        Args:
            url (str):    リクエストを投げるurl.
            method (str): リクエストメソッド.
            data (str):   POSTメソッド時に利用するdata.

        Returns:
            str: htmlの文字列.
        """

        # 優先度1: Selenium経由でのアクセス
        if self.USE_SELENIUM:
            result = self.request_selenium(url, method=method, data=data)

        # 優先度2: Splash経由でのアクセス(Seleniumが有効になってない場合はこちら)
        elif self.USE_SPLASH:
            # create splash url
            result = self.request_splash(url, method=method, data=data)

        # 優先度3: request.sessionからのリクエスト(SeleniumもSplashも有効でない場合)
        else:
            if method == 'GET':
                result = self.session.get(url).text
            elif method == 'POST':
                result = self.session.post(url, data=data).text

        return result

    # 検索用のurlを生成
    def gen_search_url(self, keyword: str, type: str):
        """gen_search_url

        検索用のurlを生成する.
        各検索エンジンで上書きする用の関数.

        Args:
            keyword (str): 検索クエリ.
            type (str): 検索タイプ.

        Returns:
            dict: method
            dict: 検索用url
            dict: data
        """

        result = {}
        return 'GET', result, None

    # テキスト、画像検索の結果からlinksを取得するための集約function
    def get_links(self, html: str, type: str):
        """get_links

        受け付けたhtmlを解析し、検索結果をlistに加工して返す関数.

        Args:
            html (str): 解析する検索結果のhtml.
            type (str): 検索タイプ([text, image]).現時点ではtextのみ対応.

        Returns:
            list: 検索結果(`[{'title': 'title...', 'link': 'https://hogehoge....'}, {...}]`)
        """

        # BeautifulSoupでの解析を実施
        soup = BeautifulSoup(html, 'lxml')

        if type == 'text':
            # link, titleの組み合わせを取得する
            elinks, etitles, etexts = self.get_text_links(soup)

            # before processing elists
            self.MESSAGE.print_text(
                ','.join(elinks),
                header=self.MESSAGE.HEADER + ': ' + Color.BLUE +
                '[BeforeProcessing elinks]' + Color.END,
                separator=" :",
                mode="debug",
            )

            # before processing etitles
            self.MESSAGE.print_text(
                ','.join(etitles),
                header=self.MESSAGE.HEADER + ': ' +
                Color.BLUE + '[BeforeProcessing etitles]' + Color.END,
                separator=" :",
                mode="debug",
            )

            # 加工処理を行う関数に渡す(各エンジンで独自対応)
            elinks, etitles, etexts = self.processings_elist(
                elinks, etitles, etexts)

            # after processing elists
            self.MESSAGE.print_text(
                ','.join(elinks),
                header=self.MESSAGE.HEADER + ': ' +
                Color.GREEN + '[AfterProcessing elinks]' + Color.END,
                separator=" :",
                mode="debug",
            )

            # after processing etitles
            self.MESSAGE.print_text(
                ','.join(etitles),
                header=self.MESSAGE.HEADER + ': ' +
                Color.GREEN + '[AfterProcessing etitles]' + Color.END,
                separator=" :",
                mode="debug",
            )

            # dictに加工してリスト化する
            # [{'title': 'title...', 'link': 'https://hogehoge....'}, {...}]
            links = self.create_text_links(elinks, etitles, etexts)

            return links

        elif type == 'image':
            links = self.get_image_links(soup)

            return links

    # テキスト検索ページの検索結果(links([{link: ..., title: ...},...]))を生成するfunction
    def get_text_links(self, soup: BeautifulSoup):
        """get_text_links

        BeautifulSoupからテキスト検索ページを解析して結果を返す関数.

        Args:
            soup (BeautifulSoup): 解析するBeautifulSoupオブジェクト.

        Returns:
            list: linkの検索結果([xxx,xxx,xxx...)
            list: titleの検索結果([xxx,xxx,xxx...)
        """
        # linkのurlを取得する
        elements = soup.select(self.SOUP_SELECT_URL)
        elinks = [e['href'] for e in elements]

        # linkのtitleを取得する
        elements = soup.select(self.SOUP_SELECT_TITLE)
        etitles = [e.text for e in elements]

        # linkのtextを取得する
        elements = soup.select(self.SOUP_SELECT_TEXT)
        etext = [e.text for e in elements]

        return elinks, etitles, etext

    # 画像検索ページの検索結果(links(list()))を生成するfunction
    def get_image_links(self, soup: BeautifulSoup):
        """get_image_links
        BeautifulSoupから画像検索ページを解析して結果を返す関数.
        (実際の処理は各検索エンジンごとの関数で実施).

        Args:
            soup (BeautifulSoup): 解析するBeautifulSoupオブジェクト.

        Returns:
            list: 検索結果(`[{'title': 'title...', 'link': 'https://hogehoge....'}, {...}]`)
        """

        links = []

        return links

    # elist, etitle生成時の追加編集処理用function
    def processings_elist(self, elinks, etitles, etexts: list):
        """processings_elist

        self.get_links 内で、取得直後のelinks, etitlesに加工を加えるための関数.
        必要に応じて各検索エンジンのClassで上書きする.

        Args:
            elinks (list): elinks(検索結果のlink)の配列
            etitles (list): etitles(検索結果のtitle)の配列
            etexts (list): etexts(検索結果のtext)の配列

        Returns:
            elinks (list): elinks(検索結果のlink)の配列
            etitles (list): etitles(検索結果のtitle)の配列
            etexts (list): etexts(検索結果のtext)の配列
        """

        return elinks, etitles, etexts

    # テキスト検索の1ページごとの検索結果から、links(links([{link: ..., title: ...},...]))を生成するfunction
    def create_text_links(self, elinks, etitles, etext: list):
        """create_text_links

        elinks, etitlesからlinks(get_linksのデータ)を返す関数.

        Args:
            elinks (list): elinks(検索結果のlink)の配列
            etitles (list): etitles(検索結果のtitle)の配列
            etext (list): etext(検索結果のテキスト)の配列

        Returns:
            list: 検索結果(`[{'title': 'title...', 'url': 'https://hogehoge....', 'text': 'hogehoge fugafuga...'}, {...}]`)を返す。
        """

        links = list()
        n = 0
        before_link = ""
        for link in elinks:
            d = dict()
            d['link'] = link

            # etitle(urlのtitle)をdictに追加する
            if len(etitles) > n:
                d['title'] = etitles[n]

            # etext(urlに対応する検索結果のテキスト文)をdictに追加する
            if len(etext) > n:
                d['text'] = etext[n]

            if before_link != link:
                links.append(d)

            before_link = link
            n += 1
        return links

    # サジェスト取得用のurlを生成
    def gen_suggest_url(self, keyword: str):
        """gen_suggest_url

        サジェスト取得用のurlを生成する.
        各検索エンジンで上書きする用の関数.

        Args:
            keyword (str): 検索クエリ.

        Returns:
            dict: サジェスト取得用url
        """

        result = {}
        return result

    # サジェストの取得
    def get_suggest_list(self, suggests: list, char: str, html: str):
        """get_suggest_list

        htmlからsuggestを配列で取得する関数.
        実際の処理は各検索エンジンClassで上書きする.

        Args:
            suggests (list): suggestを追加するための大本のlist.
            char (str): サジェストの文字列.
            html (str): 解析を行うhtml.

        Returns:
            dict: サジェスト配列
        """
        result = {}
        return result

    # ReCaptcha画面かどうかを識別するための関数
    def check_recaptcha(self, html: str):
        """[summary]

        `self.SOUP_RECAPTCHA_TAG` を元に、htmlがReCaptcha画面かどうかを識別する.

        Args:
            html (str): 識別するページのhtml

        Returns:
            bool: ReCaptcha画面かどうか(ReCaptcha画面の場合はTrue)
        """

        result = False

        # BeautifulSoupでの識別を実施
        soup = BeautifulSoup(html, 'lxml')

        # 要素が存在するかを確認
        if self.SOUP_RECAPTCHA_TAG != '':
            elements = soup.select(self.SOUP_RECAPTCHA_TAG)

            # 要素のチェック
            if len(elements) > 0:
                result = True

        return result

    # ReCaptchaをBypassする処理(wrapper)
    def bypass_recaptcha(self, url: str, html: str):
        """bypass_recaptcha

        ReCaptcha画面をBypassするための関数.
        実際の処理は Selenium/Splash 各ブラウザに応じて処理させる関数に行わせる.

        Args:
            url (str): ReCaptcha画面が表示されてしまったリクエストのurl
            html (str): ReCaptcha画面のhtml

        Returns:
            str: ReCaptchaを突破後のurlのhtml
        """

        # seleniumを使う場合
        if self.USE_SELENIUM:
            html = self.bypass_recaptcha_selenium(url, html)

        # splashを使う場合
        elif self.USE_SPLASH:
            html = self.bypass_recaptcha_splash(url, html)

        return html

    # ReCaptchaをSeleniumでBypassする処理
    def bypass_recaptcha_selenium(self, url: str, html: str):
        """bypass_recaptcha_selenium

        SeleniumでReCaptchaを突破する関数.
        実際の処理は各検索エンジンのClassで実装.

        Args:
            url (str): ReCaptcha画面が表示されてしまったリクエストのurl
            html (str): ReCaptcha画面のhtml

        Returns:
            str: ReCaptchaを突破後のurlのhtml
        """

        return html

    # ReCaptchaをSplashでBypassする処理
    def bypass_recaptcha_splash(self, url: str, html: str):
        """bypass_recaptcha_splash

        SplashでReCaptchaを突破する関数.
        実際の処理は各検索エンジンのClassで実装.

        Args:
            url (str): ReCaptcha画面が表示されてしまったリクエストのurl
            html (str): ReCaptcha画面のhtml

        Returns:
            str: ReCaptchaを突破後のurlのhtml
        """

        return html
