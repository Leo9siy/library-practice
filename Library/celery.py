import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Library.settings")

app = Celery("Library")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "expire-old-payments-every-hour": {
        "task": "Payment.tasks.expire_old_payments",
        "schedule": crontab(minute=0, hour="*"),
    },
}
