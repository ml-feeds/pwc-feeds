from functools import lru_cache
import logging
from urllib.request import urlopen

from cachetools.func import ttl_cache
from feedgen.feed import FeedGenerator
from hext import Html, Rule
from humanize import naturalsize

from pwc import config

config.configure_logging()

log = logging.getLogger(__name__)


class Feed:

    def __init__(self, feed_type: str):
        self._feed_type = feed_type
        self._feed_desc = f'for "{self._feed_type}"'
        html_url_suffix = feed_type if feed_type != "trending" else ''
        self._html_url = f'{config.HTML_URL_BASE}{html_url_suffix}'
        self._feed = FeedGenerator()
        self._hext_rule_extract = Rule(config.HTML_HEXT).extract
        self._is_debug_logged = log.isEnabledFor(logging.DEBUG)
        self._init_feed()

    @lru_cache(maxsize=1)
    def _output(self, text: bytes) -> bytes:
        feed_desc = self._feed_desc
        items = self._hext_rule_extract(Html(text.decode()))
        log.info('HTML input %s has %s items.', feed_desc, len(items))

        feed = self._feed
        is_debug_logged = self._is_debug_logged
        for item in items:
            if isinstance(item['categories'], str):
                item['categories'] = [item['categories']]

            entry = feed.add_entry(order='append')
            entry.title(item['title'])
            entry.link(href=item['link'])
            entry.guid(item['link'], permalink=True)
            entry.description(item['description'])
            for category in item['categories']:
                entry.category(term=category)
            if is_debug_logged:
                log.debug('Added: %s', item['title'])

        text_: bytes = feed.rss_str(pretty=True)
        log.info('XML output %s has %s items.', feed_desc, text_.count(b'<item>'))
        return text_

    def _init_feed(self) -> None:
        feed = self._feed
        title = config.FEED_TITLE_TEMPLATE.format(feed_type=self._feed_type)
        feed.title(title)
        feed.link(href=config.REPO_URL, rel='self')
        feed.description(config.FEED_DESCRIPTION)

    @ttl_cache(maxsize=1, ttl=config.CACHE_TTL)
    def feed(self) -> bytes:
        feed_desc = self._feed_desc
        log.debug(f'Reading HTML %s.', feed_desc)
        text = urlopen(self._html_url).read()
        log.info('HTML input %s has size %s.', feed_desc, humanize_len(text))
        text = self._output(text)
        log.info('XML output %s has size %s.', feed_desc, humanize_len(text))
        return text


def humanize_len(text: bytes) -> str:
    return naturalsize(len(text), gnu=True, format='%.0f')
