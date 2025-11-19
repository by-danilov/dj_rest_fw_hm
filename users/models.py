from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from materials.models import Course, Lesson
from django.conf import settings


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
    # Список методов оплаты
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', _('Наличные')
        TRANSFER = 'transfer', _('Перевод на счет')
        STRIPE = 'stripe', _('Stripe')

    # Пользователь
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь')
    )

    # Дата оплаты
    date = models.DateTimeField(
        verbose_name=_('Дата оплаты'),
        auto_now_add=True
    )

    # Оплаченный курс
    paid_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        verbose_name=_('Оплаченный курс'),
        null=True, blank=True
    )

    # Оплаченный урок
    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        verbose_name=_('Оплаченный урок'),
        null=True, blank=True
    )

    # Сумма оплаты
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Сумма оплаты')
    )

    # Способ оплаты
    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        default=PaymentMethod.STRIPE,
        verbose_name=_('Способ оплаты')
    )

    # Поля для интеграции Stripe
    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='ID сессии Stripe'
    )
    payment_link = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Ссылка на оплату Stripe'
    )
    is_paid = models.BooleanField(
        default=False,
        verbose_name='Статус оплаты'
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
