#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================

"""subcommand
    * pydorkをコマンドとして動作させる際の処理を記載しているモジュール
"""


import sys
import threading
import json
import os

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

    # query及びfileがともに指定なしの場合、エラーにして返す
    if args.query == "" and args.file == "":
        print("Error: クエリもしくはファイルを指定してください.")
        return

    # args.fileのチェック
    if args.file != "":
        if not os.path.exists(args.file):
            print("Error: ファイルが存在しません.")
            return

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

    # create query_list
    query_list = list()

    # append query
    if args.query != "":
        query_list.append(args.query)

    # append query in file
    if args.file != "":
        with open(args.file) as f:
            file_querys = [s.strip() for s in f.readlines()]
            query_list.extend(file_querys)

    # engine_listへ、選択されているsearch engineを入れていく
    engine_list = []
    for search_type in args.search_type:
        # if all
        if search_type == 'all':
            for engine in ENGINES:
                engine_list.append(engine)
            continue

        # if in searchengine
        if search_type in ENGINES:
            engine_list.append(search_type)
            continue

    # engine_listから、重複したリストを削除
    engine_list = list(set(engine_list))

    tasks = []
    thread_result = dict()
    lock = threading.Lock()
    for engine in engine_list:
        task = threading.Thread(
            target=target, args=(engine, query_list, args, thread_result, True, lock, search_mode))
        tasks.append(task)

    for task in tasks:
        task.start()

    for task in tasks:
        task.join()

    # json出力が有効だった場合、json形式で出力
    if args.json:
        print(json.dumps(thread_result, ensure_ascii=False, indent=2))


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


# 検索結果を出力する
def print_search_result(result, args, message):
    """print_search_result


    Args:
        result : SearchEngine.searchのresult.
        args (Namespace): argparseで取得した引数(Namespace).
        message (common.Message): 出力用Class.
    """

    # 区切り文字を指定
    sep = ': '
    if args.nullchar:
        sep = '\0'

    # title出力を行うか確認
    title_mode = False
    if 'title' in args:
        title_mode = args.title

    # pageurl出力を行うか確認
    pagelink_mode = False
    if 'pagelink' in args:
        pagelink_mode = args.pagelink

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

        message.print_line(*data, separator=sep)


# 検索
def search(engine: str, query_list: list, args, thread_result: dict, cmd=False, lock=None, mode='text'):
    """search

    Args:
        engine (str): 使用する検索エンジン(.engine.ENGINES).
        query_list(list): 検索クエリのリスト.
        args (Namespace): argparseで取得した引数(Namespace).
        thread_result(dict): 結果を1箇所に集約するためのresult dict. json出力するときのみ使用.
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

    # 区切り文字を指定
    sep = ': '
    if args.nullchar:
        sep = '\0'

    # json出力時の変数を宣言
    all_result_json = list()

    # query_listの内容を順番に処理
    for query in query_list:
        # 検索を実行
        result = se.search(
            query, type=search_type,
            maximum=args.num
        )

        # debug
        se.ENGINE.MESSAGE.print_text(
            json.dumps(result),
            separator=sep,
            header=se.ENGINE.MESSAGE.HEADER + ': ' +
            Color.GRAY + '[DEBUG]: [Result]' + Color.END,
            mode="debug",
        )

        if args.json:
            # all_result_jsonへ組み込むためのjson方式へ加工.
            append_result = {
                'query': query,
                'result': result
            }
            all_result_json.append(append_result)

        else:
            print_search_result(result, args, se.ENGINE.MESSAGE)

    if args.json:
        thread_result[engine] = all_result_json


# サジェスト
def suggest(engine: str, query_list: list, args, thread_result: dict, cmd=False, lock=None, mode=''):
    """suggest

    Args:
        engine (str): 使用する検索エンジン(.engine.ENGINES).
        query_list(list): 検索クエリのリスト.
        args (Namespace): argparseで取得した引数(Namespace).
        thread_result(dict): 結果を1箇所に集約するためのresult dict. json出力するときのみ使用.
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

    # json出力時の変数を宣言
    all_result_json = list()

    # Suggestを取得
    for query in query_list:
        result = se.suggest(
            query,
            jap=args.jap,
            alph=args.alph,
            num=args.num,
        )

        for words in result.values():
            if args.json:
                append_result = {
                    'query': query,
                    'result': words
                }
                all_result_json.append(append_result)

            else:
                for w in words:
                    se.ENGINE.MESSAGE.print_line(w, separator=": ")

    if args.json:
        thread_result[engine] = all_result_json
