#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================


"""engine_yandex
    * Yandex用の検索用Classを持つモジュール.
"""

import json
import re

from urllib import parse
from bs4 import BeautifulSoup

from .common import Color
from .engine_common import CommonEngine


class Yandex(CommonEngine):
    """Yandex

    Yandex用の検索エンジン用Class.
    """

    def __init__(self):
        super().__init__()

        self.NAME = 'Yandex'
        self.COLOR = Color.RED
        self.COLOR_NAME = self.COLOR + self.NAME + Color.END

        self.ENGINE_TOP_URL = 'https://yandex.com/'
        self.SEARCH_URL = 'https://yandex.com/search/'
        self.IMAGE_URL = 'https://yandex.com/images/search'
        self.SUGGEST_URL = 'https://yandex.com/suggest/suggest-ya.cgi'

    def gen_search_url(self, keyword: str, type: str):
        """gen_search_url

        検索用のurlを生成する.
        """

        if type == 'text':
            search_url = self.SEARCH_URL
            url_param = {
                'text': keyword,
                'p': '',
            }
        elif type == 'image':
            search_url = self.IMAGE_URL
            url_param = {
                'text': keyword,
                'p': '',
            }
        else:
            return

        page = 0
        while True:
            url_param['p'] = str(page)
            params = parse.urlencode(url_param)
            target_url = search_url + '?' + params

            yield 'GET', target_url, None

            page += 1

    def gen_suggest_url(self, keyword: str):
        """gen_suggest_url

        サジェスト取得用のurlを生成する.
        """

        url_param = {
            'v': '4',
            'part': keyword,
            'uil': self.LANG if self.LANG != '' else 'en',
        }

        params = parse.urlencode(url_param)
        return self.SUGGEST_URL + '?' + params

    def get_links(self, url: str, html: str, type: str):
        """get_links

        受け付けたhtmlを解析し、検索結果をlistに加工して返す関数.
        """

        if type == 'text':
            return self.get_text_links_with_fallback(url, html)

        if type == 'image':
            return self.get_image_links(url, html)

        return []

    def get_text_links_with_fallback(self, source_url: str, html: str):
        soup = BeautifulSoup(html, 'lxml')

        result_selectors = [
            'li.serp-item',
            'div.serp-item',
            '.Organic',
            '.VanillaReact',
        ]
        title_selectors = [
            '.OrganicTitleContentSpan',
            '.OrganicTitle-Link',
            '.Link_theme_normal',
            'h2',
            'h3',
        ]
        link_selectors = [
            'a.OrganicTitle-Link',
            'a.Link[href]',
            'h2 a',
            'a[href]',
        ]
        snippet_selectors = [
            '.OrganicTextContentSpan',
            '.OrganicText',
            '.text-container',
            'p',
        ]

        links = []
        seen = set()
        for selector in result_selectors:
            blocks = soup.select(selector)
            for block in blocks:
                title = self._extract_first_text(block, title_selectors)
                href = self._extract_first_href(block, link_selectors)
                text = self._extract_first_text(block, snippet_selectors)

                if not title or not href:
                    continue

                key = (href, title)
                if key in seen:
                    continue

                seen.add(key)
                links.append(
                    {
                        'link': href,
                        'title': title,
                        'text': text,
                        'source_url': source_url,
                    }
                )

            if links:
                break

        if not links:
            return links

        raw_links = [item['link'] for item in links]
        raw_titles = [item['title'] for item in links]
        raw_texts = [item.get('text', '') for item in links]
        raw_links, raw_titles, raw_texts = self.processings_elist(
            raw_links, raw_titles, raw_texts
        )

        return self.create_text_links(source_url, raw_links, raw_titles, raw_texts)

    def get_image_links(self, source_url: str, html: str):
        soup = BeautifulSoup(html, 'lxml')

        links = []
        seen = set()
        blocks = soup.select('.serp-item, .ImagesContentImage')
        for block in blocks:
            payload = self._load_embedded_json(
                block.get('data-bem', '') or block.get('data-state', '')
            )
            image_url = self._find_first_value(
                payload,
                {
                    'img_href',
                    'serp-item.img_href',
                    'origin.url',
                    'serp-item.origin.url',
                    'preview.url',
                    'serp-item.preview.url',
                    'dups[0].url',
                    'serp-item.dups[0].url',
                    'url',
                },
            )
            title = self._find_first_value(
                payload,
                {
                    'snippet.title',
                    'serp-item.snippet.title',
                    'title',
                    'text',
                },
            )
            page_link = self._find_first_value(
                payload,
                {
                    'snippet.url',
                    'serp-item.snippet.url',
                    'origin.pageUrl',
                    'serp-item.origin.pageUrl',
                    'pageUrl',
                    'url',
                },
            )

            if not image_url:
                image_url = self._extract_image_href_from_block(block)
            if not title:
                title = self._extract_first_text(block, ['img[alt]', '.serp-item__title', '.Title'])
            if not page_link:
                page_link = self._extract_first_href(block, ['a[href]'])

            image_url = self._normalize_link(image_url)
            page_link = self._normalize_link(page_link)

            if not image_url or image_url in seen:
                continue

            seen.add(image_url)
            link = {
                'link': image_url,
                'title': title,
                'source_url': source_url,
            }
            if page_link:
                link['pagelink'] = page_link
            links.append(link)

        return links

    def get_suggest_list(self, suggests: list, char: str, html: str):
        """get_suggest_list

        htmlからsuggestを配列で取得する関数.
        """

        data = self._load_suggest_payload(html)
        suggests[char if char == '' else char[-1]] = self._extract_suggestions(data)

        return suggests

    def processings_elist(self, elinks, etitles, etexts: list):
        """processings_elist

        Yandexの相対URLやリダイレクトURLを補正する.
        """

        normalized_links = []
        for link in elinks:
            normalized_links.append(self._normalize_link(link))

        return normalized_links, etitles, etexts

    def _extract_first_text(self, block, selectors: list):
        for selector in selectors:
            element = block.select_one(selector)
            if element is None:
                continue

            text = element.get_text(' ', strip=True)
            if text:
                return text

            alt = element.get('alt', '').strip()
            if alt:
                return alt

        return ''

    def _extract_first_href(self, block, selectors: list):
        for selector in selectors:
            element = block.select_one(selector)
            if element is None:
                continue

            href = element.get('href', '').strip()
            href = self._normalize_link(href)
            if href:
                return href

        return ''

    def _extract_image_href_from_block(self, block):
        for selector in ['img[src]', 'img[data-src]', 'source[srcset]']:
            element = block.select_one(selector)
            if element is None:
                continue

            href = element.get('src', '').strip() or element.get('data-src', '').strip()
            if not href and element.has_attr('srcset'):
                href = element['srcset'].split(' ')[0].strip()

            if href:
                return href

        return ''

    def _load_embedded_json(self, value: str):
        if not value:
            return {}

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {}

    def _load_suggest_payload(self, html: str):
        html = html.strip()
        if not html:
            return []

        try:
            return json.loads(html)
        except json.JSONDecodeError:
            pass

        matched = re.search(r'^[^(]+\((.*)\)\s*;?\s*$', html, re.DOTALL)
        if matched is not None:
            try:
                return json.loads(matched.group(1))
            except json.JSONDecodeError:
                return []

        return []

    def _extract_suggestions(self, data):
        if isinstance(data, list):
            if len(data) > 1 and isinstance(data[1], list):
                return [item for item in data[1] if isinstance(item, str)]

            if all(isinstance(item, str) for item in data):
                return data

            result = []
            for item in data:
                if isinstance(item, dict):
                    suggestion = item.get('text') or item.get('value')
                    if isinstance(suggestion, str):
                        result.append(suggestion)
            return result

        if isinstance(data, dict):
            for key in ('suggests', 'items', 'results'):
                values = data.get(key)
                if isinstance(values, list):
                    result = []
                    for item in values:
                        if isinstance(item, str):
                            result.append(item)
                        elif isinstance(item, dict):
                            suggestion = item.get('text') or item.get('value')
                            if isinstance(suggestion, str):
                                result.append(suggestion)
                    return result

        return []

    def _normalize_link(self, link: str):
        if not link:
            return ''

        link = link.strip()
        if link.startswith('//'):
            return 'https:' + link

        parsed = parse.urlparse(link)
        query = parse.parse_qs(parsed.query)
        for key in ('url', 'target'):
            values = query.get(key, [])
            if values:
                return values[0]

        if link.startswith('/'):
            base_uri = '{uri.scheme}://{uri.netloc}'.format(
                uri=parse.urlparse(self.SEARCH_URL)
            )
            return parse.urljoin(base_uri, link)

        return link

    def _find_first_value(self, data, candidates: set):
        for candidate in candidates:
            value = self._walk_path(data, candidate)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ''

    def _walk_path(self, data, path: str):
        current = data
        for chunk in path.split('.'):
            if '[' in chunk and chunk.endswith(']'):
                key, index = chunk[:-1].split('[', 1)
                if key:
                    if not isinstance(current, dict) or key not in current:
                        return None
                    current = current[key]
                if not isinstance(current, list):
                    return None
                idx = int(index)
                if idx >= len(current):
                    return None
                current = current[idx]
            else:
                if not isinstance(current, dict) or chunk not in current:
                    return None
                current = current[chunk]
        return current
