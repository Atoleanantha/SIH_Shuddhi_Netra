from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab


# Set the default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')
app.conf.update(timezone="Asia/Kolkata")

# Load task modules from all registered Django app configs
app.config_from_object(settings, namespace='CELERY')
# app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery Beat Settings
app.conf.beat_schedule = {
    'update-notification-status': {
        'task': 'notifications.tasks.escalate_unresolved_notifications',
        'schedule': crontab(minute=1),#every 1 minute
        #'args': (2,)
    }
    
}

# Discover tasks
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
