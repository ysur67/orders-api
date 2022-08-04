import os

from django.conf import settings

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
app = Celery('project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.update(
    beat_schedule={
        'parse_orders_every_minute': {
            'task': 'apps.orders.tasks.ParseOrdersTask',
            'schedule': settings.CELERY_PARSE_TASK_SCHEDULE,
        },
    },
)
