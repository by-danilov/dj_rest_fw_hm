from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Название'))
    preview = models.ImageField(upload_to='materials/previews/', verbose_name=_('Превью'),
                                **{'blank': True, 'null': True})
    description = models.TextField(verbose_name=_('Описание'), **{'blank': True, 'null': True})

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_('Владелец'),
        null=True, blank=True
    )

    class Meta:
        verbose_name = _('Курс')
        verbose_name_plural = _('Курсы')

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Название'))
    description = models.TextField(verbose_name=_('Описание'), **{'blank': True, 'null': True})
    preview = models.ImageField(upload_to='materials/previews/', verbose_name=_('Превью'),
                                **{'blank': True, 'null': True})
    video_link = models.URLField(verbose_name=_('Ссылка на видео'), **{'blank': True, 'null': True})

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_('Владелец'),
        null=True, blank=True
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name=_('Курс'),
        related_name='lessons'
    )

    class Meta:
        verbose_name = _('Урок')
        verbose_name_plural = _('Уроки')

    def __str__(self):
        return f'{self.title} ({self.course.title})'
