import os

from celery import Celery

# Указываем Django‑настройки по умолчанию
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Берём настройки Celery из Django settings с префиксом CELERY_
# Например, CELERY_BROKER_URL, CELERY_RESULT_BACKEND и т.п.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически находим tasks.py во всех приложениях
app.autodiscover_tasks()
