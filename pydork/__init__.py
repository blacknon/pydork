#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

from .sub_commands import run_subcommand
from .engine import ENGINES
from . import messages

from pkg_resources import get_distribution
from datetime import datetime

import copy
import argparse

# TODO: returnではなくyieldに切り替えて、返り値をgeneratorにすることである程度途中状態でも状況を見れるような仕組みとする


# version (setup.pyから取得してくる)
__version__ = get_distribution('pydork').version


# main
def main():
    # parserの作成
    parser = argparse.ArgumentParser(
        description=messages.description)
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
            "help": messages.help_message_query,
        },
        {
            "args": ["-f", "--file"],
            "action": "store",
            "type": str,
            "default": "",
            "help": messages.help_message_op_file,
        },
        {
            "args": ["-F", "--template_file"],
            "action": "store",
            "type": str,
            "default": "",
            "help": messages.help_message_op_template_file,
        },
        {
            "args": ["-V", "--template_variable"],
            "action": "store",
            "type": str,
            "default": "",
            "help": messages.help_message_op_template_variable,
        },
        {
            "args": ["-t", "--search_type"],
            "default": ["google"],
            "choices": engines_list,
            "nargs": "+",
            "type": str,
            "help": messages.help_message_op_search_type,
        },
        {
            "args": ["-l", "--lang"],
            "default": "ja",
            "choices": ["ja", "en"],
            "type": str,
            "help": messages.help_message_op_lang,
        },
        {
            "args": ["-c", "--country"],
            "default": "JP",
            "choices": ["JP", "US"],
            "type": str,
            "help": messages.help_message_op_country,
        },
        {
            "args": ["-P", "--proxy"],
            "default": "",
            "type": str,
            "help": messages.help_message_op_proxy_server,
        },
        {
            "args": ["-j", "--json"],
            "action": "store_true",
            "help": messages.help_message_op_json,
        },
        {
            "args": ["-k", "--insecure"],
            "action": "store_true",
            "help": messages.help_message_op_insecure,
        },
        {
            "args": ["-s", "--selenium"],
            "action": "store_true",
            "help": messages.help_message_op_selenium,
        },
        {
            "args": ["-S", "--splash"],
            "action": "store_true",
            "help": messages.help_message_op_splash,
        },
        {
            "args": ["-b", "--browser-endpoint"],
            "default": "",
            "type": str,
            "help": messages.help_message_op_browser_endpoint,
        },
        {
            "args": ["-B", "--browser"],
            "default": "firefox",
            "choices": ["chrome", "firefox"],
            "type": str,
            "help": messages.help_message_op_browser,
        },
        {
            "args": ["--color"],
            "default": "auto",
            "choices": ["auto", "none", "always"],
            "type": str,
            "help": messages.help_message_op_color,
        },
        {
            "args": ["--cookies"],
            "default": "~/.pydork_cookies",
            "type": str,
            "help": messages.help_message_op_cookies_dir,
        },
        {
            "args": ["--delete-cookies"],
            "action": "store_true",
            "help": messages.help_message_op_delete_cookies,
        },
    ]

    # サブコマンド `search` の引数
    search_args_map = [
        {
            "args": ["-T", "--title"],
            "action": "store_true",
            "help": messages.help_message_op_title,
        },
        {
            "args": ["-0", "--nullchar"],
            "action": "store_true",
            "help": messages.help_message_op_null_char,
        },
        {
            "args": ["-n", "--num"],
            "default": 300,
            "type": int,
            "help": messages.help_message_op_num,
        },
        {
            "args": ["--start"],
            "type": lambda s: datetime.strptime(s, '%Y-%m-%d'),
            "help": messages.help_message_op_start,
        },
        {
            "args": ["--end"],
            "type": lambda s: datetime.strptime(s, '%Y-%m-%d'),
            "help": messages.help_message_op_end,
        },
        {
            "args": ["--debug"],
            "action": "store_true",
            "help": messages.help_message_op_debug,
        },
        {
            "args": ["--disable-headless"],
            "action": "store_true",
            "help": messages.help_message_op_disable_headless,
        },
    ]
    search_args_map.extend(copy.deepcopy(common_args_map))

    # サブコマンド `image` の引数
    image_args_map = [
        {
            "args": ["-T", "--title"],
            "action": "store_true",
            "help": messages.help_message_op_title,
        },
        {
            "args": ["-p", "--pagelink"],
            "action": "store_true",
            "help": messages.help_message_op_image_pagelink,
        },
        {
            "args": ["-0", "--nullchar"],
            "action": "store_true",
            "help": messages.help_message_op_null_char,
        },
        {
            "args": ["-n", "--num"],
            "default": 300,
            "type": int,
            "help": messages.help_message_op_num,
        },
        # {
        #     "args": ["--start"],
        #     "type": lambda s: datetime.strptime(s, '%Y-%m-%d'),
        #     "help": messages.help_message_op_start,
        # },
        # {
        #     "args": ["--end"],
        #     "type": lambda s: datetime.strptime(s, '%Y-%m-%d'),
        #     "help": messages.help_message_op_end,
        # },
        {
            "args": ["--debug"],
            "action": "store_true",
            "help": messages.help_message_op_debug,
        },
        {
            "args": ["--disable-headless"],
            "action": "store_true",
            "help": messages.help_message_op_disable_headless,
        },
    ]
    image_args_map.extend(copy.deepcopy(common_args_map))

    # サブコマンド `suggest` の引数
    suggest_args_map = [
        {
            "args": ["--jap"],
            "action": "store_true",
            "help": messages.help_message_op_suggest_jap
        },
        {
            "args": ["--alph"],
            "action": "store_true",
            "help": messages.help_message_op_suggest_alph
        },
        {
            "args": ["--num"],
            "action": "store_true",
            "help": messages.help_message_op_suggest_num
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
