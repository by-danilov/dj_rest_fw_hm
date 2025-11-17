from rest_framework.serializers import ValidationError
from urllib.parse import urlparse


def validate_youtube_link(value):
    """
    Проверяет, что предоставленная ссылка относится только к домену youtube.com.
    """
    if not value:
        return

    # Разбираем URL на составляющие части
    parsed_url = urlparse(value)

    # Получаем домен
    domain = parsed_url.netloc.lower()

    # Проверяем, что в домене есть 'youtube.com'
    if 'youtube.com' not in domain:
        raise ValidationError(
            "Ссылки на видео разрешены только с домена youtube.com."
        )
