from rest_framework import viewsets, generics
from .paginators import CourseLessonPaginator
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsModeratorOrOwner
from materials.tasks import send_course_update_notification
from django.utils import timezone


class CourseViewSet(viewsets.ModelViewSet):
    """
    Реализует полный CRUD для модели Course.
    (GET list, GET detail, POST, PUT/PATCH, DELETE)
    """
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [IsModeratorOrOwner]
    pagination_class = CourseLessonPaginator

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        old_updated_at = serializer.instance.updated_at
        course = serializer.save()
        if old_updated_at != course.updated_at:
            # Асинхронный вызов задачи Celery
            send_course_update_notification.delay(course.pk)

# Получение списка уроков и создание нового
class LessonListAPIView(generics.ListCreateAPIView):
    """Получение списка уроков и создание нового."""
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsModeratorOrOwner]
    pagination_class = CourseLessonPaginator

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# Получение, изменение и удаление одного урока
class LessonCreateAPIView(generics.CreateAPIView):
    """Создание нового урока."""
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsModeratorOrOwner]


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Получение деталей одного урока."""
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsModeratorOrOwner]


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Обновление урока."""
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsModeratorOrOwner]


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Удаление урока."""
    queryset = Lesson.objects.all()
    permission_classes = [IsModeratorOrOwner]
