import os
from celery import Celery
from django.conf import settings

# Настройки Django для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Создаем экземпляр Celery
app = Celery('dj_rest_fw_hm')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматический поиск задач в файлах tasks.py внутри приложений
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Пример тестовой задачи (для проверки работоспособности)
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')