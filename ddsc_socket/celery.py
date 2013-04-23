# (c) Fugro GeoServices. MIT licensed, see LICENSE.rst.
from __future__ import absolute_import

from celery import Celery

from ddsc_socket import celeryconfig

celery = Celery()  # AKA the "app"
celery.config_from_object(celeryconfig)
