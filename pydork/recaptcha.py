#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================

"""engine
    * ReCaptcha関連のClassを集約するモジュールファイル
"""

import json
import requests

from urllib import parse
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from time import sleep

from .common import Color, Message


# 2CaptchaのAPIへPOSTするためのClass
class TwoCaptcha:
    """TwoCaptcha

    2CaptchaのAPIへPOSTし、ReCaptchaを突破するためのClass.

    Note:
        公式ライブラリ側でCookieのPOSTに対応していなかったため作成.


    """

    def __init__(self, apikey: str):
        """__init__

        Args:
            apikey (str): 2CaptchaのAPI Key.
        """

        # apiへリクエストを投げるためのsession
        self.session = requests.Session()

        # api_url
        self.api_in_url = 'https://2captcha.com/in.php'
        self.api_res_url = 'https://2captcha.com/res.php'

        # api_key
        self.api_key = apikey

        # proxy
        self.proxy = None
        self.user_agent = None

        # flag
        self.IS_DEBUG = False
        self.IS_COMMAND = False

        # Message
        self.MESSAGE = None

    def set_debug(self, is_debug: bool):
        """set_debug

        Args:
            is_debug (bool): debug modeが有効ならTrue
        """

        self.IS_DEBUG = is_debug

    def set_command(self, is_command: bool):
        """set_command

        Args:
            is_command (bool): command modeが有効ならTrue
        """

        self.IS_COMMAND = is_command

    def set_user_agent(self, user_agent: str):
        """set_user_agent

        Args:
            user_agent (str): 2Captchaに送るUser Agent
        """

        self.user_agent = user_agent

    def set_messages(self, message: Message):
        """set_message

        Args:
            message (Message): 利用するcommon.Messageを指定
        """

        self.MESSAGE = message

    # googleのReCaptcha画面からデータを抽出する
    def get_google_recaptcha_data(self, html: str):
        """get_google_recaptcha_data

        ReCapthcaのhtmlからsitekey, data-sの値を抽出する.


        Args:
            html (str): 解析するReCaptcha画面のhtmlデータ

        Returns:
            sitekey (str): 2Captchaへ送るsitekey
            data-s (str): 2Captchaへ送るdata-s
        """

        # resultの初期値設定
        sitekey = None
        data_s = None

        # ReCaptchaのタグ・要素データを宣言
        recaptcha_tag = '#captcha-form > #recaptcha'
        sitekey_el_name = 'data-sitekey'
        data_s_el_name = 'data-s'

        # htmlをBeautifulSoupで解析する
        soup = BeautifulSoup(html, 'lxml')

        # 要素を抽出する
        if recaptcha_tag != '':
            elements = soup.select(recaptcha_tag)

            # 要素のチェック
            if len(elements) > 0:
                el = elements[0]

                try:
                    sitekey = el[sitekey_el_name]
                    data_s = el[data_s_el_name]

                    return sitekey, data_s

                except AttributeError:
                    None

        return sitekey, data_s

    def in_php(self, data: dict):
        """in_php

        Args:
            data (dict): in.phpにpostするデータ(dict)

        Returns:
            bool: 処理が正常終了か否か
            str: request_code
        """

        res = self.session.post(self.api_in_url, data=data)

        if self.MESSAGE is not None:
            self.MESSAGE.print_text(
                '2Captcha Response in.php from `{}`: {}'.format(
                    self.api_in_url, res.text),
                mode='debug',
                header=self.MESSAGE.HEADER + ': ' + Color.GRAY +
                '[DEBUG]: [2CaptchaIn]' + Color.END,
                separator=": "
            )

        # status codeを確認
        if res.status_code == 200:
            d = json.loads(res.text)
            if d['status'] == 1:
                request_id = d['request']

                return True, request_id

        # request codeを取得できなかった場合、
        return False, None

    def res_php(self, request_id: str):
        """res_php

        Args:
            request_id (str): 2Captchaのres.php(2Captchaの突破状況確認するpath)で利用するrequest_id.

        Returns:
            (str): res.phpからのresponse結果を返す
        """

        url_param = {
            'key': self.api_key,
            'action': 'get',
            'json': 1,
            'id': request_id
        }
        params = parse.urlencode(url_param)
        target_url = self.api_res_url + '?' + params

        result = self.session.get(target_url)

        if self.MESSAGE is not None:
            self.MESSAGE.print_text(
                '2Captcha res.php Response from `{}`: {}'.format(
                    target_url, result.text),
                mode='debug',
                header=self.MESSAGE.HEADER + ': ' + Color.GRAY +
                '[DEBUG]: [2CaptchaRes]' + Color.END,
                separator=": "
            )

        return result

    # 解析結果を渡す
    def google_recaptcha(self, html: str, url: str, cookies: list, proxy: str):
        """[summary]

        Args:
            sitekey (str): ReCaptchaのhtml.
            url (str): ReCaptchaが表示されてしまったurl(元のurl)
            cookie (list): cookiesを渡す.
            proxy (str): proxyをuriで渡す.

        Returns:
            (str): Google ReCaptchaで使用するcodeを返す.
        """

        # code
        code = None
        result = None

        # set proxy
        self.proxy = proxy

        # sitekey, data-sを取得する
        sitekey, data_s = self.get_google_recaptcha_data(html)

        # proxyをuriから整形する
        proxy_parse = urlparse(proxy)
        proxy_type = proxy_parse.scheme.upper()
        proxy_uri = proxy_parse.netloc

        # cookieを整形する
        cookie_elements = []
        for cookie in cookies:
            cookie_element = cookie['name'] + ':' + cookie['value']
            cookie_elements.append(cookie_element)

        cookie_data = ';'.join(cookie_elements)

        # postリクエストで使用するデータを生成する
        payload = {
            'key': self.api_key,
            'pageurl': url,
            'method': 'userrecaptcha',
            'json': 1,
            'googlekey': sitekey,
            'data-s': data_s,
            'proxytype': proxy_type,
            'proxy': proxy_uri,
            'cookies': cookie_data,
            'callback': 'submitCallback',
        }

        if self.user_agent is not None:
            payload['userAgent'] = self.user_agent

        while True:
            # debug message
            if self.MESSAGE is not None:
                self.MESSAGE.print_text(
                    'Send ReCaptcha Data to `{}`.'.format(
                        self.api_in_url),
                    mode='info',
                    header=self.MESSAGE.HEADER + ': ' + Color.GRAY +
                    '[DEBUG]: [ReCaptcha]' + Color.END,
                    separator=": "
                )

            # リクエストを送信
            ok, request_id = self.in_php(payload)

            if not ok:
                # debug message
                if self.MESSAGE is not None:
                    self.MESSAGE.print_text(
                        'Failed Send ReCaptcha Data. data: {}'.format(
                            payload),
                        mode='warn',
                        header=self.MESSAGE.HEADER + ': ' + Color.GRAY +
                        '[DEBUG]: [ReCaptcha]' + Color.END,
                        separator=": "
                    )

                break

            # message
            if self.MESSAGE is not None:
                self.MESSAGE.print_text(
                    'Get request_id: {}'.format(request_id),
                    mode='info',
                    header=self.MESSAGE.HEADER + ': ' + Color.GRAY +
                    '[DEBUG]: [2Captcha]' + Color.END,
                    separator=": "
                )

                self.MESSAGE.print_text(
                    'Check ReCaptcha Rsponse Status from: {}'.format(
                        self.api_res_url),
                    mode='info',
                    header=self.MESSAGE.HEADER + ': ' + Color.GRAY +
                    '[DEBUG]: [2Captcha]' + Color.END,
                    separator=": "
                )

            # res_phpのチェックループ
            while True:
                res = self.res_php(request_id)

                # レスポンス(json)から読み込む
                data = json.loads(res.text)

                # codeを取得
                code = data['request']

                if data['status'] == 1:
                    result = code
                    return result

                if code != 'CAPCHA_NOT_READY':
                    break

                sleep(30)

        if code is None:
            code = 'None'

        # debug messages
        if self.MESSAGE is not None:
            self.MESSAGE.print_text(
                'Bypass NG ReCaptcha Data. code: {}'.format(code),
                mode='warn',
                header=self.MESSAGE.HEADER + ': ' + Color.GRAY +
                '[DEBUG]: [2Captcha]' + Color.END,
                separator=": "
            )

        return result
