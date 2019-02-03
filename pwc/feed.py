from functools import lru_cache
import logging
from urllib.request import Request, urlopen

from cachetools.func import ttl_cache
from feedgen.feed import FeedGenerator
from hext import Html, Rule
from humanize import naturalsize

from pwc import config

config.configure_logging()

log = logging.getLogger(__name__)


class Feed:

    def __init__(self, feed_type: str):
        html_url_suffix = feed_type if feed_type != "trending" else ''
        html_url = f'{config.HTML_URL_BASE}{html_url_suffix}'
        self._html_request = Request(html_url, headers={'User-Agent': config.USER_AGENT})

        self._feed_type = feed_type
        self._feed_type_desc = f'for "{self._feed_type}"'
        self._feed_title = config.FEED_TITLE_TEMPLATE.format(feed_type=self._feed_type.title())

        self._hext_rule_extract = Rule(config.HTML_HEXT).extract
        self._is_debug_logged = log.isEnabledFor(logging.DEBUG)

        self._output = lru_cache(maxsize=1)(self._output)  # type: ignore  # Instance level cache
        self.feed = ttl_cache(maxsize=1, ttl=config.CACHE_TTL)(self.feed)  # type: ignore  # Instance level cache

    def _output(self, text: bytes) -> bytes:  # type: ignore
        feed_type_desc = self._feed_type_desc
        items = self._hext_rule_extract(Html(text.decode()))
        log.info('HTML input %s has %s items.', feed_type_desc, len(items))

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
            entry.description(item['description'])
            for category in item['categories']:
                category = category.capitalize() if category.isupper() else category
                entry.category(term=category)
            if is_debug_logged:
                log.debug('Added: %s', item['title'])

        text_: bytes = feed.rss_str(pretty=True)
        log.info('XML output %s has %s items.', feed_type_desc, text_.count(b'<item>'))
        return text_

    def _init_feed(self) -> FeedGenerator:
        feed = FeedGenerator()
        feed.title(self._feed_title)
        feed.link(href=config.REPO_URL, rel='self')
        feed.description(config.FEED_DESCRIPTION)
        return feed

    def feed(self) -> bytes:  # type: ignore
        feed_type_desc = self._feed_type_desc
        log.debug(f'Reading HTML %s.', feed_type_desc)
        text = urlopen(self._html_request).read()
        log.info('HTML input %s has size %s.', feed_type_desc, humanize_len(text))
        text = self._output(text)
        log.info('XML output %s has size %s.', feed_type_desc, humanize_len(text))
        return text


def humanize_len(text: bytes) -> str:
    return naturalsize(len(text), gnu=True, format='%.0f')
