from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
# from django.contrib.auth import get_user_model
from materials.models import Course, Lesson
from django.conf import settings

# User = get_user_model()


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)

    phone = models.CharField(max_length=35, verbose_name='Телефон', **{'blank': True, 'null': True})
    city = models.CharField(max_length=100, verbose_name='Город', **{'blank': True, 'null': True})

    avatar = models.ImageField(upload_to='users/avatars/', verbose_name='Аватар', **{'blank': True, 'null': True})

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Payment(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
    ]

    # 1. Пользователь
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Пользователь'))

    # 2. Дата оплаты
    date = models.DateTimeField(verbose_name=_('Дата оплаты'), auto_now_add=True)

    # 3. Оплаченный курс
    paid_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        verbose_name=_('Оплаченный курс'),
        null=True, blank=True
    )

    # 4. Оплаченный урок
    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        verbose_name=_('Оплаченный урок'),
        null=True, blank=True
    )

    # 5. Сумма оплаты
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Сумма оплаты'))

    # 6. Способ оплаты
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES,
        verbose_name=_('Способ оплаты')
    )

    class Meta:
        verbose_name = _('Платеж')
        verbose_name_plural = _('Платежи')

    def __str__(self):
        return f'Платеж {self.pk} от {self.user.email} на сумму {self.amount}'


# Подписки
class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name=_('Курс'),
        related_name='subscriptions'
    )

    # Дополнительная проверка на уникальность пары (пользователь, курс)
    class Meta:
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        unique_together = ('user', 'course')  # Пользователь может подписаться на курс только один раз

    def __str__(self):
        return f'Подписка {self.user.email} на курс {self.course.title}'
