#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

"""common
    * commandでのhelp messageを英語・日本語対応させるためのテキストデータを持つモジュール.
"""

import os

lang = os.getenv('LANG')

if lang == 'ja_JP.UTF-8':
    description = "各種検索エンジンから指定したクエリの結果(url)およびSuggestを取得する"

    # common_args_map
    help_message_query = "検索文字列(クエリ)"
    help_message_op_file = "検索文字列(クエリ)が書かれているファイル"
    help_message_op_template_file = "検索文字列(クエリ)が書かれているテンプレートファイル(jinja2)"
    help_message_op_template_variable = "テンプレートファイル(jinja2)で使用する変数セット(json)"
    help_message_op_search_type = "使用する検索エンジンを指定"
    help_message_op_lang = "言語を指定"
    help_message_op_country = "国を指定"
    help_message_op_proxy_server = "プロキシサーバーを指定(例:socks5://hogehoge:8080, https://fugafuga:18080)"
    help_message_op_json = "json形式で出力する"
    help_message_op_insecure = "sslエラーを無視する"
    help_message_op_selenium = "Selenium(headless browser)を使用する(排他: Splashより優先)"
    help_message_op_splash = "Splash(headless browser)を使用する(排他: Seleniumの方が優先)"
    help_message_op_browser_endpoint = "Selenium/Splash等のヘッドレスブラウザのエンドポイントを指定(例: localhost:8050)"
    help_message_op_browser = "Seleniumで使用するBrowserを指定"
    help_message_op_color = "color出力の切り替え"
    help_message_op_cookies_dir = "使用するcookieファイルの格納先ディレクトリのPATH(各検索エンジンごとでcookieファイルを個別保存)"
    help_message_op_delete_cookies = "検索クエリ実行ごとにCookieを削除する"

    # other_map
    help_message_op_title = "検索結果のタイトルをセットで出力する"
    help_message_op_null_char = "null characterを区切り文字として使用する"
    help_message_op_num = "検索結果の取得数を指定する"
    help_message_op_debug = "debugモードを有効にする"
    help_message_op_disable_headless = "Seleniumでheadlessモードを無効化する(手動でのReCaptcha対応時に必要)"
    help_message_op_start = "期間指定(開始)"
    help_message_op_end = "期間指定(終了)"
    help_message_op_image_pagelink = "画像ファイルがあるhtmlのURLも出力する"

    # suggest_map
    help_message_op_suggest_jap = "日本語の文字を検索キーワードに追加してサジェストを取得"
    help_message_op_suggest_alph = "アルファベット文字を検索キーワードに追加してサジェストを取得"
    help_message_op_suggest_num = "数字を検索キーワードに追加してサジェストを取得"


else:
    description = "Obtain results (url) and Suggest for a specified query from various search engines"

    # common_args_map
    help_message_query = "search string(query)"
    help_message_op_file = "File containing search strings(queries)"
    help_message_op_template_file = "Template file (jinja2) containing search strings (queries)"
    help_message_op_template_variable = "Variable set (json) used in template file (jinja2)"
    help_message_op_search_type = "Specify which search engine to use"
    help_message_op_lang = "Specify language"
    help_message_op_country = "Specify country"
    help_message_op_proxy_server = "Specify proxy server(example: socks5://hogehoge:8080, https://fugafuga:18080)"
    help_message_op_json = "Output in json format"
    help_message_op_insecure = "ignore ssl errors"
    help_message_op_selenium = "Use Selenium (headless browser). (exclusive: takes precedence over Splash)"
    help_message_op_splash = "Use Splash (headless browser) (exclusive: Selenium is preferred)"
    help_message_op_browser_endpoint = "Specify the endpoint for headless browsers such as Selenium/Splash (example: localhost:8050)"
    help_message_op_browser = "Specify Browser to use with Selenium"
    help_message_op_color = "Switching color output"
    help_message_op_cookies_dir = "PATH of the directory where the cookie files to be used are stored (cookie files are stored separately for each search engine)"
    help_message_op_delete_cookies = "Delete cookies on every search query execution"

    # other_map
    help_message_op_title = "Output a set of search result titles"
    help_message_op_null_char = "Use null character as delimiter"
    help_message_op_num = "Specify the number of search results to retrieve"
    help_message_op_debug = "Enable debug mode"
    help_message_op_disable_headless = "Disable headless mode in Selenium (required for manual ReCaptcha support)"
    help_message_op_start = "Search period (start)"
    help_message_op_end = "Search period (end)"
    help_message_op_image_pagelink = "Also output the html URL where the image files are located."

    # suggest_map
    help_message_op_suggest_jap = "Add Japanese characters to search keywords to get suggestions"
    help_message_op_suggest_alph = "Add alphabetic characters to search keywords to get suggestions"
    help_message_op_suggest_num = "Add numbers to search keywords to get suggestions"
