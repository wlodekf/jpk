# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from celery import Celery
import os

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jpk.settings')

from django.conf import settings  # noqa

app = Celery('jpk')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
