from functools import lru_cache
import json
import logging
from typing import cast, Tuple
from urllib.request import Request, urlopen

from cachetools.func import ttl_cache
from feedgen.feed import FeedGenerator
from hext import Html, Rule
from humanize import naturalsize
from lxml.etree import CDATA
from more_itertools import unique_everseen

from pwc import config

config.configure_logging()

log = logging.getLogger(__name__)


class Feed:

    def __init__(self, feed_type: str):
        html_url_suffix = feed_type if feed_type != "trending" else ''
        html_urls = [f'{config.HTML_URL_BASE}{html_url_suffix}?page={page_num}' for page_num in
                     range(1, config.NUM_PAGES_READ[feed_type] + 1)]
        self._html_requests = [Request(html_url, headers={'User-Agent': config.USER_AGENT}) for html_url in html_urls]

        self._feed_type = feed_type
        self._feed_type_desc = f'for "{self._feed_type}"'
        self._feed_title = config.FEED_TITLE_TEMPLATE.format(feed_type=self._feed_type.title())

        self._hext_rule_extract = Rule(config.HTML_HEXT).extract
        self._is_debug_logged = log.isEnabledFor(logging.DEBUG)

        self._output = lru_cache(maxsize=1)(self._output)  # type: ignore  # Instance level cache
        self.feed = ttl_cache(maxsize=1, ttl=config.CACHE_TTL)(self.feed)  # type: ignore  # Instance level cache

    def _init_feed(self) -> FeedGenerator:
        feed = FeedGenerator()
        feed.title(self._feed_title)
        feed.link(href=config.REPO_URL, rel='self')
        feed.description(config.FEED_DESCRIPTION)
        return feed

    def _output(self, texts: Tuple[bytes, ...]) -> bytes:
        feed_type_desc = self._feed_type_desc
        items = [item for text in texts for item in self._hext_rule_extract(Html(text.decode()))]
        items = list(unique_everseen(items, json.dumps))
        log.info('HTML inputs %s have %s items in all.', feed_type_desc, len(items))

        feed = self._init_feed()
        is_debug_logged = self._is_debug_logged
        for item in items:
            if 'categories' not in item:
                item['categories'] = []
            elif isinstance(item['categories'], str):
                item['categories'] = [item['categories']]

            entry = feed.add_entry(order='append')
            entry.title(item['title'])
            entry.link(href=item['link'])
            entry.guid(item['link'], permalink=True)
            # description = '\n\n'.join((item['description'], item['code_link']))
            description = f'{item["description"]} <p>Code: <a href="{item["code_link"]}">{item["code_link"]}</a></p>'
            entry.description(CDATA(description))
            for category in item['categories']:
                if category.startswith('+') and category[1:].isdigit():  # Ex: +1, +2
                    continue
                category = category.capitalize() if category.isupper() else category
                entry.category(term=category)
            if is_debug_logged:
                log.debug('Added: %s', item['title'])

        text_: bytes = feed.rss_str(pretty=True)
        log.info('XML output %s has %s items.', feed_type_desc, text_.count(b'<item>'))
        return text_

    def feed(self) -> bytes:
        feed_type_desc = self._feed_type_desc
        log.debug(f'Reading %s HTML pages %s.', len(self._html_requests), feed_type_desc)
        texts = tuple(cast(bytes, urlopen(html_request).read()) for html_request in self._html_requests)
        log.info('HTML inputs %s have sizes: %s', feed_type_desc, ', '.join(humanize_len(text) for text in texts))
        text = self._output(texts)
        log.info('XML output %s has size %s.', feed_type_desc, humanize_len(text))
        return text


def humanize_len(text: bytes) -> str:
    return naturalsize(len(text), gnu=True, format='%.0f')
