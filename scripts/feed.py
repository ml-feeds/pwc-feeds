import logging
import time

from pwc import config
from pwc.feed import Feed

log = logging.getLogger(__name__)

if __name__ == '__main__':
    feed = Feed()
    feed_types = list(config.FEED_TYPES)[:1]
    try:
        for feed_type in feed_types:
            output = feed.feed(feed_type)
            print(output.decode())

        for feed_type in feed_types:
            log.info('Testing cachetools cache.')
            assert feed.feed(feed_type) == output
            log.info('Tested cachetools cache.')
    except Exception:
        time.sleep(.01)  # Delay for logs to flush.
        raise
