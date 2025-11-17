from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from materials.models import Course, Lesson
from users.models import Subscription

User = get_user_model()


class LessonCRUDTestCase(APITestCase):
    """Тестирование CRUD операций для уроков с учетом прав доступа."""

    def setUp(self):
        # 🌟 1. Создание тестовых пользователей
        self.user_owner = User.objects.create_user(email='owner@test.ru', password='testpassword', username='owner')
        self.user_other = User.objects.create_user(email='other@test.ru', password='testpassword', username='other')
        self.user_moderator = User.objects.create_user(email='mod@test.ru', password='testpassword', username='mod')

        # 🌟 2. Создание группы модераторов
        moderators_group, _ = Group.objects.get_or_create(name='Модераторы')
        self.user_moderator.groups.add(moderators_group)

        # 🌟 3. Создание курса и уроков
        self.course = Course.objects.create(title='Test Course', owner=self.user_owner)
        self.lesson_owner = Lesson.objects.create(
            title='Owner Lesson',
            course=self.course,
            owner=self.user_owner,
            video_link='https://www.youtube.com/watch?v=example1'  # Валидная ссылка
        )
        self.lesson_other = Lesson.objects.create(
            title='Other Lesson',
            course=self.course,
            owner=self.user_other,
            video_link='https://www.youtube.com/watch?v=example2'
        )

        # URLs для тестирования
        self.list_url = reverse('lesson-list')
        self.create_url = reverse('lesson-list')
        self.detail_url_owner = reverse('lesson-detail', kwargs={'pk': self.lesson_owner.pk})
        self.update_url_owner = reverse('lesson-update', kwargs={'pk': self.lesson_owner.pk})
        self.delete_url_owner = reverse('lesson-delete', kwargs={'pk': self.lesson_owner.pk})

        self.valid_data = {'title': 'New Lesson', 'course': self.course.pk,
                           'video_link': 'https://www.youtube.com/watch?v=new'}
        self.invalid_data_link = {'title': 'Invalid Lesson', 'course': self.course.pk,
                                  'video_link': 'https://www.google.com'}

    # --- ТЕСТЫ ДОСТУПА ---

    def test_lesson_create_by_owner(self):
        """Владелец (не модератор) может создавать уроки."""
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.post(self.create_url, data=self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], self.user_owner.pk)

    def test_lesson_create_by_moderator_forbidden(self):
        """Модератор не может создавать уроки (Задание 9)."""
        self.client.force_authenticate(user=self.user_moderator)
        response = self.client.post(self.create_url, data=self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_update_by_owner(self):
        """Владелец может обновлять свой урок."""
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.patch(self.update_url_owner, data={'title': 'Updated Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson_owner.refresh_from_db()
        self.assertEqual(self.lesson_owner.title, 'Updated Title')

    def test_lesson_update_by_moderator(self):
        """Модератор может обновлять любой урок (Задание 9)."""
        self.client.force_authenticate(user=self.user_moderator)
        response = self.client.patch(self.update_url_owner, data={'title': 'Mod Update'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson_owner.refresh_from_db()
        self.assertEqual(self.lesson_owner.title, 'Mod Update')

    def test_lesson_update_by_other_user_forbidden(self):
        """Другой пользователь не может обновлять чужой урок (Задание 10)."""
        self.client.force_authenticate(user=self.user_other)
        response = self.client.patch(self.update_url_owner, data={'title': 'Forbidden Update'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- ТЕСТЫ ВАЛИДАЦИИ ---

    def test_lesson_create_with_invalid_link(self):
        """Проверка валидатора на стороннюю ссылку."""
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.post(self.create_url, data=self.invalid_data_link, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_link', response.data)
        self.assertIn('youtube.com', response.data['video_link'][0])


class SubscriptionTestCase(APITestCase):
    """Тестирование функционала подписки (Задание 12)."""

    def setUp(self):
        self.user = User.objects.create_user(email='sub@test.ru', password='testpassword', username='sub')
        self.course = Course.objects.create(title='Test Course', owner=self.user)
        self.manage_url = reverse('subscription-manage')
        self.course_detail_url = reverse('course-detail', kwargs={'pk': self.course.pk})

    def test_subscription_create(self):
        """Тест на успешную подписку."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.manage_url, data={'course': self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscription_delete(self):
        """Тест на успешную отписку."""
        # Создаем подписку
        Subscription.objects.create(user=self.user, course=self.course)

        # Отправляем запрос на управление (он должен удалить)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.manage_url, data={'course': self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_is_subscribed_field_true(self):
        """Проверка поля is_subscribed, когда пользователь подписан."""
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.course_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('is_subscribed'))

    def test_is_subscribed_field_false(self):
        """Проверка поля is_subscribed, когда пользователь не подписан."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.course_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data.get('is_subscribed'))
