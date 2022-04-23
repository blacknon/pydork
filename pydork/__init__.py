#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================


import argparse
import copy

from datetime import datetime
from pkg_resources import get_distribution

from .engine import ENGINES
from .subcommands import run_subcommand


# version (setup.pyから取得してくる)
__version__ = get_distribution('pydork').version


# main
def main():
    # parserの作成
    parser = argparse.ArgumentParser(
        description='各種検索エンジンから指定したクエリの結果(url)およびSuggestを取得するスクリプト')
    subparsers = parser.add_subparsers()

    # ENGINESに`all`を追加
    engines_list = copy.deepcopy(ENGINES)
    engines_list.append('all')

    # サブコマンド共通の引数
    common_args_map = [
        {
            "args": ["query"],
            "action": "store",
            "type": str,
            "nargs": "?",
            "default": "",
            "help": "検索文字列(クエリ)",
        },
        {
            "args": ["-f", "--file"],
            "action": "store",
            "type": str,
            "default": "",
            "help": "検索文字列(クエリ)が書かれているファイル",
        },
        {
            "args": ["-t", "--search_type"],
            "default": ["google"],
            "choices": engines_list,
            "nargs": "+",
            "type": str,
            "help": "使用する検索エンジンを指定",
        },
        {
            "args": ["-l", "--lang"],
            "default": "ja",
            "choices": ["ja", "en"],
            "type": str,
            "help": "言語を指定",
        },
        {
            "args": ["-c", "--country"],
            "default": "JP",
            "choices": ["JP", "US"],
            "type": str,
            "help": "国を指定",
        },
        {
            "args": ["-P", "--proxy"],
            "default": "",
            "type": str,
            "help": "プロキシサーバーを指定(例:socks5://hogehoge:8080, https://fugafuga:18080)",
        },
        {
            "args": ["-j", "--json"],
            "action": "store_true",
            "help": "json形式で出力する",
        },
        {
            "args": ["-s", "--selenium"],
            "action": "store_true",
            "help": "Selenium(headless browser)を使用する(排他: Splashより優先)",
        },
        {
            "args": ["-S", "--splash"],
            "action": "store_true",
            "help": "Splash(headless browser)を使用する(排他: Seleniumの方が優先)",
        },
        {
            "args": ["-b", "--browser-endpoint"],
            "default": "",
            "type": str,
            "help": "Selenium/Splash等のヘッドレスブラウザのエンドポイントを指定(例: localhost:8050)",
        },
        {
            "args": ["-B", "--browser"],
            "default": "firefox",
            "choices": ["chrome", "firefox"],
            "type": str,
            "help": "Seleniumで使用するBrowserを指定",
        },
        {
            "args": ["--color"],
            "default": "auto",
            "choices": ["auto", "none", "always"],
            "type": str,
            "help": "color出力の切り替え"
        },
        {
            "args": ["--cookies"],
            "default": "~/.pydork_cookies",
            "type": str,
            "help": "使用するcookieファイルの格納先ディレクトリのPATH(各検索エンジンごとでcookieファイルを個別保存)"
        },
    ]

    # サブコマンド `search` の引数
    search_args_map = [
        {
            "args": ["-T", "--title"],
            "action": "store_true",
            "help": "検索結果のタイトルをセットで出力する",
        },
        {
            "args": ["-0", "--nullchar"],
            "action": "store_true",
            "help": "null characterを区切り文字として使用する",
        },
        {
            "args": ["-n", "--num"],
            "default": 300,
            "type": int,
            "help": "検索結果の取得数を指定する",
        },
        {
            "args": ["--start"],
            "type": lambda s: datetime.strptime(s, '%Y-%m-%d'),
            "help": "期間指定(開始)",
        },
        {
            "args": ["--end"],
            "type": lambda s: datetime.strptime(s, '%Y-%m-%d'),
            "help": "期間指定(終了)",
        },
        {
            "args": ["--debug"],
            "action": "store_true",
            "help": "debugモードを有効にする",
        },
        {
            "args": ["--disable-headless"],
            "action": "store_true",
            "help": "Seleniumでheadlessモードを無効化する(手動でのReCaptcha対応時に必要)",
        },
    ]
    search_args_map.extend(copy.deepcopy(common_args_map))

    # サブコマンド `image` の引数
    image_args_map = [
        {
            "args": ["-T", "--title"],
            "action": "store_true",
            "help": "検索結果のタイトルをセットで出力する",
        },
        {
            "args": ["-p", "--pagelink"],
            "action": "store_true",
            "help": "画像ファイルがあるhtmlのURLも出力する",
        },
        {
            "args": ["-0", "--nullchar"],
            "action": "store_true",
            "help": "null characterを区切り文字として使用する",
        },
        {
            "args": ["-n", "--num"],
            "default": 300,
            "type": int,
            "help": "検索結果の取得数を指定する",
        },
        # {
        #     "args": ["--start"],
        #     "type": lambda s: datetime.strptime(s, '%Y-%m-%d'),
        #     "help": "期間指定(開始)",
        # },
        # {
        #     "args": ["--end"],
        #     "type": lambda s: datetime.strptime(s, '%Y-%m-%d'),
        #     "help": "期間指定(終了)",
        # },
        {
            "args": ["--debug"],
            "action": "store_true",
            "help": "debugモードを有効にする",
        },
        {
            "args": ["--disable-headless"],
            "action": "store_true",
            "help": "Seleniumでheadlessモードを無効化する(手動でのReCaptcha対応時に必要)",
        },
    ]
    image_args_map.extend(copy.deepcopy(common_args_map))

    # サブコマンド `suggest` の引数
    suggest_args_map = [
        {
            "args": ["--jap"],
            "action": "store_true",
            "help": "日本語の文字を検索キーワードに追加してサジェストを取得"
        },
        {
            "args": ["--alph"],
            "action": "store_true",
            "help": "アルファベット文字を検索キーワードに追加してサジェストを取得"
        },
        {
            "args": ["--num"],
            "action": "store_true",
            "help": "数字を検索キーワードに追加してサジェストを取得"
        },
    ]
    suggest_args_map.extend(copy.deepcopy(common_args_map))

    # search
    # ----------
    parser_search = subparsers.add_parser(
        'search',
        help='search mode. see `search -h`'
    )

    # add_argument
    for element in search_args_map:
        args = element['args']
        element.pop('args')
        parser_search.add_argument(*args, **element)

    # set parser_search
    parser_search.set_defaults(handler=run_subcommand, subcommand="search")

    # image
    # ----------
    # TODO: image検索をサブコマンドとして追加する
    parser_image = subparsers.add_parser(
        'image',
        help='search mode. see `search -h`'
    )

    # add_argument
    for element in image_args_map:
        args = element['args']
        element.pop('args')
        parser_image.add_argument(*args, **element)

    # set parser_image
    parser_image.set_defaults(handler=run_subcommand, subcommand="image")

    # suggest
    # ----------
    parser_suggest = subparsers.add_parser(
        'suggest',
        help='suggest mode. see `suggest -h`'
    )

    # add_argument
    for element in suggest_args_map:
        args = element['args']
        element.pop('args')
        parser_suggest.add_argument(*args, **element)

    parser_suggest.set_defaults(handler=run_subcommand, subcommand="suggest")

    # --version(-v)オプションのparser定義
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s version:{version}'.format(version=__version__)
    )

    args = parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args.subcommand, args)
    else:
        # 未知のサブコマンドの場合はヘルプを表示
        parser.print_help()


if __name__ == '__main__':
    main()
