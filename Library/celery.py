import os
from celery import Celery
from celery.schedules import crontab

# Устанавливаем переменную окружения по умолчанию для настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Library.settings")

# Создаём экземпляр Celery
app = Celery("Library")

# Загружаем конфигурацию из Django settings.py (по префиксу CELERY_)
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически находит задачи во всех приложениях (если есть tasks.py)
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "expire-old-payments-every-hour": {
        "task": "Payment.tasks.expire_old_payments",
        "schedule": crontab(minute=0, hour="*"),  # каждый час
    },
}
