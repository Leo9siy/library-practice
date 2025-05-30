import os
from celery import Celery

# Устанавливаем переменную окружения по умолчанию для настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Library.settings")

# Создаём экземпляр Celery
app = Celery("Library")

# Загружаем конфигурацию из Django settings.py (по префиксу CELERY_)
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически находит задачи во всех приложениях (если есть tasks.py)
app.autodiscover_tasks()