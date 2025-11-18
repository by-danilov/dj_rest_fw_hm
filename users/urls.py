from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentListAPIView, UserRegisterAPIView, UserViewSet, SubscriptionManageAPIView, PaymentCreateAPIView


user_router = DefaultRouter()
user_router.register(r'users', UserViewSet, basename='user')


urlpatterns = [
    # Регистрация (доступна всем)
    path('register/', UserRegisterAPIView.as_view(), name='user-register'),
    # CRUD для пользователей (закрыт авторизацией)
    path('', include(user_router.urls)),
    # Список платежей с фильтрацией и сортировкой (закрыт авторизацией)
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
    # Эндпоинт для управления подпиской
    path('subscriptions/manage/', SubscriptionManageAPIView.as_view(), name='subscription-manage'),
    # Эндпоинт для создания оплаты Stripe
    path('payments/create/', PaymentCreateAPIView.as_view(), name='payment-create'),
]
