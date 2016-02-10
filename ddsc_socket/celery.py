# (c) Fugro GeoServices, Nelen & Schuurmans. MIT licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from celery import Celery

from .settings import CeleryConfig

celery = Celery()  # AKA the "app"
celery.config_from_object(CeleryConfig)
