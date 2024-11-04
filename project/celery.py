from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

from .settings import CELERY_BROKER_URL

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

app = Celery("project", broker=os.environ.get(CELERY_BROKER_URL))
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
