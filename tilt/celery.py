import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tilt.settings')

app = Celery('tilt',
             broker='amqp://',
             backend='amqp://',)

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()