from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    CourseViewSet,
    LessonListAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
    LessonDestroyAPIView,
    # LessonCreateAPIView
)

# Маршрутизатор для ViewSet Course
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

# Маршруты для Generic-классов Lesson
urlpatterns = [
    # CRUD для Урока (Lesson)
    path('lessons/', LessonListAPIView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonRetrieveAPIView.as_view(), name='lesson-detail'),
    path('lessons/update/<int:pk>/', LessonUpdateAPIView.as_view(), name='lesson-update'),
    path('lessons/delete/<int:pk>/', LessonDestroyAPIView.as_view(), name='lesson-delete'),
    # path('lessons/create/', LessonCreateAPIView.as_view(), name='lesson-create'), # Отдельное создание

    # Подключаем маршруты ViewSet
    path('', include(router.urls)),
]
