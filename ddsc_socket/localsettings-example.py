# (c) Fugro GeoServices, Nelen & Schuurmans. MIT licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .settings import CeleryConfig
from .settings import DATABASE
from .settings import LOGGING

# Socket server
HOST = ''
PORT = 5008
DIR = '/your/result/dir'

# Celery
CeleryConfig.BROKER_URL = (
    'redis://localhost:6379/0'
)

# PostgreSQL
DATABASE['host'] = 'host'
DATABASE['dbname'] = 'dbname'
DATABASE['user'] = 'user'
DATABASE['password'] = 'password'

# Logging
LOGGING['handlers']['logstash']['host'] = 'localhost'
LOGGING['loggers']['']['handlers'].append('logstash')
