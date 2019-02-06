import logging
from typing import Dict, Tuple, Union

import flask

from pwc import config
from pwc.feed import Feed

log = logging.getLogger(__name__)

FEEDS = {feed_type: Feed(feed_type) for feed_type in config.FEED_TYPES}
VALID_PATHS = {f'/{feed_type}' for feed_type in config.FEED_TYPES}
VALID_PATHS_STR = ', '.join(VALID_PATHS)


def serve(request: flask.Request) -> Tuple[Union[bytes, str], int, Dict[str, str]]:
    hget = request.headers.get
    log.info('Received request for "%s" from %s from %s, %s, %s.', request.path, hget('X-Appengine-User-Ip'),
             hget('X-Appengine-City'), hget('X-Appengine-Region'), hget('X-Appengine-Country'))

    if request.path not in VALID_PATHS:
        request_path = '' if request.path is None else request.path
        msg = f'The requested path "{request_path}" is invalid. Valid paths are: {VALID_PATHS_STR}'
        log.error('Error handling request from %s: %s', hget('X-Appengine-User-Ip'), msg)
        return f'ERROR: {msg}', 400, {'Content-Type': 'text/plain; charset=utf-8'}

    feed_type = request.path[1:]  # Strip leading "/".
    feed = FEEDS[feed_type]
    return feed.feed(), 200, {'Content-Type': 'text/xml; charset=utf-8'}
