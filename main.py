import logging
from typing import Dict, Tuple

import flask

from pwc import config
from pwc.feed import Feed

log = logging.getLogger(__name__)
feed = Feed()

VALID_PATHS = {f'/{feed_type}' for feed_type in config.FEED_TYPES}
VALID_PATHS_STR = ', '.join(VALID_PATHS)


def serve(request: flask.Request) -> Tuple[bytes, int, Dict[str, str]]:
    hget = request.headers.get
    log.info('Received request for path %s from %s from %s, %s, %s.', request.path, hget('X-Appengine-User-Ip'),
             hget('X-Appengine-City'), hget('X-Appengine-Region'), hget('X-Appengine-Country'))

    if request.path not in VALID_PATHS:
        request_path = '' if request.path is None else request.path
        return f'Request path "{request_path}" is invalid. Use one of: {VALID_PATHS_STR}', 400

    feed_type = request.path[1:]  # Strip "/"
    return feed.feed(feed_type), 200, {'Content-Type': 'text/xml; charset=utf-8'}
