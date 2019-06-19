import datetime
import logging.config
import os
from pathlib import Path


def configure_logging() -> None:
    logging.config.dictConfig(LOGGING)
    log = logging.getLogger(__name__)
    log.debug('Logging is configured.')


CACHE_TTL = datetime.timedelta(minutes=20).total_seconds()
FEED_DESCRIPTION = 'As a disclaimer, this is an unofficial feed and has no affiliation with Papers with Code.'
FEED_TITLE_TEMPLATE = 'Papers with Code: {feed_type} (unofficial)'
FEED_TYPES = {'trending', 'latest', 'greatest'}
HTML_HEXT = """
<h1><a href^="/paper/" href:prepend("https://paperswithcode.com"):link @text:title/></h1>
<p class="item-strip-abstract" @text:description/>
<p><?a><span class="badge badge-primary" @text:categories/></a></p>
"""
HTML_URL_BASE = 'https://paperswithcode.com/'
ON_SERVERLESS = bool(os.getenv('GCLOUD_PROJECT'))
PACKAGE_NAME = Path(__file__).parent.stem
REPO_URL = 'https://github.com/ml-feeds/pwc-feeds'
USER_AGENT = 'Mozilla/5.0'

LOGGING = {  # Ref: https://docs.python.org/3/howto/logging.html#configuring-logging
    'version': 1,
    'formatters': {
        'detailed': {
            'format': '[%(relativeCreated)i] %(name)s:%(lineno)d:%(funcName)s:%(levelname)s: %(message)s',
        },
        'serverless': {
            'format': '%(thread)x:%(name)s:%(lineno)d:%(funcName)s:%(levelname)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'serverless' if ON_SERVERLESS else 'detailed',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        PACKAGE_NAME: {
            'level': 'INFO' if ON_SERVERLESS else 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        '': {
            'level': 'DEBUG',
            'handlers': ['console'],
         },
    },
}
