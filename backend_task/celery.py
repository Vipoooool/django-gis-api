from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# setting the Django settings module.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_task.settings')
app = Celery('backend_task')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Looks up for task modules in Django applications and loads them
app.autodiscover_tasks()
