from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@shared_task
def check_user_activity_and_block():
    """
    Проверяет пользователей, которые не заходили более 1 месяца, и блокирует их (is_active=False).
    """
    # Рассчитываем порог времени (1 месяц назад)
    one_month_ago = timezone.now() - timedelta(days=30)

    # Находим неактивных пользователей, которые:
    inactive_users = User.objects.filter(
        is_active=True,
        is_superuser=False,
        last_login__lt=one_month_ago
    )

    # Блокируем найденных пользователей
    count = inactive_users.update(is_active=False)

    return f"Успешно заблокировано {count} пользователей, неактивных более 30 дней."
