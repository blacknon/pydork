#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================

"""subcommand
    * pydorkをコマンドとして動作させる際の処理を記載しているモジュール
"""


import sys
import threading
import json

from .engine import SearchEngine, ENGINES
from .common import Color
from .common import Message


# サブコマンドの動作集約用関数
def run_subcommand(subcommand, args):
    """run_subcommand

    Args:
        subcommand (str): 使用するサブコマンド([search, suggest]).
        args (Namespace): argparseで取得した引数(Namespace).
    """

    target = None
    search_mode = ''
    if subcommand == 'search':
        # チェック処理
        if ((args.start is None and args.end is not None) or (args.start is not None and args.end is None)):
            print(
                Color.GRAY + "期間を指定する場合は--start, --endの両方を指定してください" + Color.END,
                file=sys.stderr
            )
            return
        target = search
        search_mode = 'text'

    elif subcommand == 'image':
        target = search
        search_mode = 'image'

    elif subcommand == 'suggest':
        target = suggest

    tasks = []
    lock = threading.Lock()
    for st in args.search_type:
        # if all
        if st == 'all':
            for engine in ENGINES:
                task = threading.Thread(
                    target=target, args=(engine, args, True, lock, search_mode))
                tasks.append(task)

            continue

        # if in searchengine
        if st in ENGINES:
            task = threading.Thread(
                target=target, args=(st, args, True, lock, search_mode))
            tasks.append(task)

            continue

    for task in tasks:
        task.start()

    for task in tasks:
        task.join()


# SearchEngineのオプション設定用関数
def set_se_options(se, args):
    """set_se_options

    Args:
        se (SearchEngine): argsの情報を元に、オプションを設定するSearchEngine.
        args (Namespace): argparseで取得した引数(Namespace).

    Returns:
        SearchEngine: オプションを設定したSearchEngine.
    """

    # set debug flag
    if 'debug' in args:
        se.set_is_debug(args.debug)

    # set is_command flag
    se.set_is_command(True)

    # set disable headless
    if 'disable_headless' in args:
        se.set_disable_headless(args.disable_headless)

    # proxy
    if args.proxy != '':
        se.set_proxy(args.proxy)

    # Selenium
    if args.selenium:
        # set default endpoint
        endpoint = None

        # if set browser-endpoint
        if args.browser_endpoint != "":
            endpoint = args.browser_endpoint

        # set selenium
        se.set_selenium(endpoint, args.browser)

    # Splush
    if args.splash:
        # set default endpoint
        endpoint = 'localhost:8050'

        # if set browser-endpoint
        if args.browser_endpoint != "":
            endpoint = args.browser_endpoint

        # set splash
        se.set_splash(endpoint)

    # useragent
    se.set_user_agent()

    # lang/country code
    se.set_lang(args.lang, args.country)

    # set cookie driver(last set)
    se.set_cookie_files(args.cookies)

    return se


# 検索
def search(engine, args, cmd=False, lock=None, mode='text'):
    """search

    Args:
        engine (str): 使用する検索エンジン(.engine.ENGINES).
        args (Namespace): argparseで取得した引数(Namespace).
        cmd (bool, optional): commandで実行しているか否か. Defaults to False.
        lock (threading.Lock): threadingのマルチスレッドで使用するLock.現在は未使用. Defaults to None.
        type (str, optional): 検索タイプ. `text` or `image`.
    """

    # start search engine class
    se = SearchEngine()

    # Set Engine
    se.set(engine)

    # Set SearchEngine options
    se = set_se_options(se, args)

    # Set lock
    se.set_lock(lock)

    # Set color
    if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
        se.set_is_color(True)

    # 検索タイプを設定(テキスト or 画像)
    search_type = mode

    # 検索を実行
    result = se.search(
        args.query, type=search_type,
        maximum=args.num
    )

    # sep
    sep = ': '
    if args.nullchar:
        sep = '\0'

    # debug
    se.ENGINE.MESSAGE.print_text(
        json.dumps(result),
        separator=sep,
        header=se.ENGINE.MESSAGE.HEADER + ': ' +
        Color.GRAY + '[DEBUG]: [Result]' + Color.END,
        mode="debug",
    )

    # title出力を行うか確認
    title_mode = False
    if 'title' in args:
        title_mode = args.title

    # pageurl出力を行うか確認
    pagelink_mode = False
    if 'pagelink' in args:
        pagelink_mode = args.pagelink

    # 検索結果を出力
    for d in result:
        data = []
        link = d['link']

        # 出力dataにlinkを追加
        data.insert(0, link)

        # pageurlの有無を確認
        if 'pagelink' in d and pagelink_mode:
            pagelink = d['pagelink']

            # pagelinkの色指定
            if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
                pagelink = Color.GRAY + Color.UNDERLINE + pagelink + Color.END

            data.insert(0, pagelink)

        # titleの有無を確認
        if 'title' in d and title_mode:
            title = d['title']

            # titleの色指定
            if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
                title = Color.GRAY + title + Color.END

            data.insert(0, title)

        se.ENGINE.MESSAGE.print_line(*data, separator=sep)


# サジェスト
def suggest(engine, args, cmd=False, lock=None, mode=''):
    """suggest

    Args:
        engine (str): 使用する検索エンジン(.engine.ENGINES).
        args (Namespace): argparseで取得した引数(Namespace).
        cmd (bool, optional): commandで実行しているか否か. Defaults to False.
        lock (threading.Lock): threadingのマルチスレッドで使用するLock.現在は未使用. Defaults to None.
        mode (str, optional): マルチスレッドでsearchとある程度共用で使えるようにするための引数. 利用していない. Defaults to ''.
    """

    # start search engine class
    se = SearchEngine()

    # Set Engine
    se.set(engine)

    # Set Message()
    msg = Message()
    msg.set_engine(se.ENGINE.NAME, se.ENGINE.COLOR)
    if 'debug' in args:
        msg.set_is_debug(args.debug)
    msg.set_is_command(True)

    # set msg to se
    se.ENGINE.set_messages(msg)

    # Set SearchEngine options
    se = set_se_options(se, args)

    # Set lock
    se.set_lock(lock)

    # Header
    header = '[${ENGINE_NAME}Suggest]'
    if args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty()):
        sc = Color(se.ENGINE.COLOR)
        header = sc.out(header)
    se.ENGINE.MESSAGE.set_header(header)

    # Suggestを取得
    result = se.suggest(
        args.query,
        jap=args.jap,
        alph=args.alph,
        num=args.num,
    )

    for words in result.values():
        for w in words:
            se.ENGINE.MESSAGE.print_line(w, separator=": ")
