import logging
from typing import Dict, Tuple

import flask

from pwc.feed import Feed

log = logging.getLogger(__name__)
feed = Feed()


def serve(request: flask.Request) -> Tuple[bytes, int, Dict[str, str]]:
    hget = request.headers.get
    log.info('Received request for path %s from %s from %s, %s, %s.', request.path, hget('X-Appengine-User-Ip'),
             hget('X-Appengine-City'), hget('X-Appengine-Region'), hget('X-Appengine-Country'))
    if request.path is None:
        raise flask.abort(404)
    path = request.path[1:]  # Strip /
    return feed.feed(path), 200, {'Content-Type': 'text/xml; charset=utf-8'}
