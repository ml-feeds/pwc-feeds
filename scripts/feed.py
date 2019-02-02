import logging

from pwc import config
from pwc.feed import Feed

log = logging.getLogger(__name__)

if __name__ == '__main__':
    feeds = [Feed(feed_type) for feed_type in config.FEED_TYPES]
    outputs1 = {feed: feed.feed().decode() for feed in feeds}
    outputs2 = {feed: feed.feed().decode() for feed in feeds}
    for o1, o2 in zip(outputs1.values(), outputs2.values()):
        assert o1 == o2
        print(o1)
