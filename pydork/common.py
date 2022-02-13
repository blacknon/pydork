#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================


"""common
    * 共通系や雑多な処理を詰め合わせたバルクモジュール.

"""

import sys
import datetime

from string import Template


# コンソール出力時に色付をするためのClass
class Color:
    """Color

    コンソール出力時に色付をするための文字列を変数にして保持しているClass.

    Examples:
        c = Color()
        c.set(c.BLUE)
        print(c.out('hogehoge'))
    """
    # color_code
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[1;30m'

    # 文字効果
    BOLD = '\038[1m'
    ITALIC = '\038[3m'
    UNDERLINE = '\033[4m'
    INVISIBLE = '\033[08m'
    REVERCE = '\033[07m'

    # 効果を終了
    END = '\033[0m'

    def __init__(self, color_code: str):
        """[summary]

        Args:
            color_code (str): 使用するカラーコード

        """
        self.COLOR_CODE = color_code

    def out(self, text: str, is_bold=False, is_underline=False, is_reverse=False, is_italic=False):
        # textを囲む
        text = self.COLOR_CODE + text + self.END

        # is_boldが有効な場合、太字にする
        if is_bold:
            text = self.BOLD + text + self.END

        # is_underlineが有効な場合、下線を入れる
        if is_underline:
            text = self.UNDERLINE + text + self.END

        # is_reverseが有効な場合、色の反転をする
        if is_reverse:
            text = self.REVERCE + text + self.END

        # is_italicが有効な場合、Italicにする
        if is_italic:
            text = self.ITALIC + text + self.END

        return text


# Message関連の制御用Class
class Message:
    """Message

    メッセージの出力を簡易化するためのClass(未完成...).

    Examples:

    """

    def __init__(self):
        # command flag
        self.IS_COMMAND = False

        # debug flag
        self.IS_DEBUG = False

        # timestamp flag
        self.IS_TIMESTAMP = False

        # engine data
        self.ENGINE_COLOR = Color('')
        self.ENGINE_NAME = ''
        self.ENGINE = ''

        # header
        self.HEADER = ''

    def set_is_command(self, is_command: bool):
        self.IS_COMMAND = is_command

    def set_is_debug(self, is_debug: bool):
        self.IS_DEBUG = is_debug

    def set_engine(self, engine: str, color: str):
        self.ENGINE_COLOR = Color(color)
        self.ENGINE_NAME = engine
        self.ENGINE = self.ENGINE_COLOR.out(engine)

    def set_header(self, text):
        self.HEADER = text

    def replace(self, text):
        """replace

        テンプレートテキストの変数をself変数や時刻に置換して返す

        Args:
            text (str): 置換処理をするテンプレート用テキスト
        """

        # 現在時刻を取得
        dt_now = datetime.datetime.now()

        # 置換用のdictを生成
        data = {
            # 時刻情報
            'YEAR': dt_now.year,
            'MONTH': dt_now.month,
            'DAY': dt_now.day,
            'HOUR': dt_now.hour,
            'MINUTE': dt_now.minute,
            'SECOND': dt_now.second,

            # 検索エンジン(color)
            'ENGINE': self.ENGINE,  # 色付き
            'ENGINE_NAME': self.ENGINE_NAME,  # 色なし
        }

        # テンプレートを作成
        template = Template(text)

        # 置換処理を実行
        result = template.safe_substitute(data)

        return result

    def print_line(self, *text, use_header=True, separator=' ', file=sys.stdout, header=None):
        # headerの生成
        if header is None:
            header = self.HEADER

        header = self.replace(header)

        # テキストを出力
        if use_header:
            print(header, *text, sep=separator, file=file)
        else:
            print(*text, sep=separator, file=file)

    def print_text(self, text, mode='message', use_header=True, separator=' ', file=sys.stdout, header=None):
        # is_commandが有効のときのみ出力させる
        if not self.IS_COMMAND:
            return

        # debug, infoのときは、self.is_debugが有効のときのみ出力
        if mode in ('info', 'debug'):
            # self.is_debugでない場合は出力しない
            if not self.IS_DEBUG:
                return

        # 出力テキストの生成
        text = self.replace(text)

        # case
        if mode == 'message':  # modeが `message` のとき
            text_color = Color(Color.WHITE)

        elif mode == 'error':
            text_color = Color(Color.RED)
            file = sys.stderr

        elif mode == 'warn':
            text_color = Color(Color.YELLOW)
            file = sys.stderr

        elif mode == 'info':
            text_color = Color(Color.GREEN)
            file = sys.stderr

        elif mode == 'debug':
            text_color = Color(Color.GRAY)
            file = sys.stderr

        # default headerの定義
        if mode in ('info', 'debug'):
            if header is None:
                header = self.HEADER

            header = Color.REVERCE + \
                self.replace(header) + Color.END

        # TODO: 正規表現で、付きの箇所を抜き出すような処理を追加で入れる

        # テキストの出力
        for line in text.splitlines():
            self.print_line(text_color.out(line),
                            separator=separator, use_header=use_header, file=file, header=header)

        return
