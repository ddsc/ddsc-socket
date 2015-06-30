# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from ddsc_socket.celery import celery

SETTINGS_DIR = os.path.dirname(os.path.realpath(__file__))
BUILDOUT_DIR = os.path.abspath(os.path.join(SETTINGS_DIR, '..'))
BROKER_URL = celery.conf['BROKER_URL']

HOST = ''  # An empty string means: listen on all available network interfaces.
PORT = 0  # Port 0 means: let the server choose an arbitrary unused port.
DIR = os.path.join(BUILDOUT_DIR, 'var', 'csv')

# See: http://initd.org/psycopg/docs/module.html.
# Override these values in localsettings.py:
DATABASE = {
    'host': '',
    'database': 'lizard_nxt',
    'user': 'vagrant',
    'password': 'vagrant',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BUILDOUT_DIR, 'var', 'log', 'socks.log'),
            'formatter': 'verbose',
            'level': 'INFO',
        },
        'logstash': {
            'level': 'INFO',
            'class': 'logstash.LogstashHandler',
            'host': 'localhost',
            'port': 5959,  # Default value: 5959.
            'version': 1,  # Default value: 0.
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    }
}

try:
    # Allow each environment to override these settings.
    from .localsettings import *  # NOQA
except ImportError:
    pass
