from celery import shared_task
from django.core.mail import send_mail
from materials.models import Course
from users.models import Subscription
from django.conf import settings


@shared_task
def send_course_update_notification(course_id):
    """
    Отправляет уведомление по email всем подписчикам курса об его обновлении.
    """
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return f"Курс с ID {course_id} не найден."

    # Находим всех подписчиков этого курса
    subscriptions = Subscription.objects.filter(course=course)

    if not subscriptions.exists():
        return f"У курса {course.title} нет подписчиков."

    # Собираем список адресов для рассылки
    recipient_list = [sub.user.email for sub in subscriptions]

    subject = f'Обновление курса "{course.title}"'
    message = (
        f'Привет!\n\n'
        f'Материалы курса "{course.title}" были обновлены. '
        f'Заходи скорее, чтобы посмотреть новые уроки или изменения.\n\n'
        f'С уважением, Администрация.'
    )

    # Вызываем встроенную функцию Django для отправки писем
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipient_list,
        fail_silently=False,
    )

    return f"Уведомления отправлены {len(recipient_list)} пользователям."
