from rest_framework import serializers
from .validators import validate_youtube_link
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'preview', 'video_link', 'course', 'owner']
        read_only_fields = ['owner']

    def validate_video_link(self, value):
        """
        Используем метод validate_<field_name> для валидации ссылки.
        Это предпочтительный способ для валидации конкретного поля в сериализаторе.
        """
        validate_youtube_link(value)
        return value


class CourseSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'preview', 'lesson_count', 'lessons', 'is_subscribed', 'owner']
        read_only_fields = ['owner']

    def get_lesson_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        # Проверяем наличие контекста и пользователя
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Проверяем наличие подписки для данного курса (obj) и текущего пользователя
            return obj.subscriptions.filter(user=request.user).exists()

        return False  # Если пользователь не аутентифицирован
