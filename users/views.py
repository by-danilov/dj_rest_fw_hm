import django_filters
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Payment, User, Subscription
from .serializers import PaymentSerializer, UserSerializer, UserRegisterSerializer, SubscriptionSerializer
from .filters import PaymentFilter
from rest_framework.filters import OrderingFilter


# Контроллер для списка платежей с фильтрацией и сортировкой
class PaymentListAPIView(generics.ListAPIView):
    """
    Вывод списка платежей с возможностью фильтрации по курсу/уроку,
    способу оплаты и сортировки по дате.
    """
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    # 1. Подключение класса фильтрации
    filterset_class = PaymentFilter

    # 2. Подключение OrderingFilter для сортировки
    filter_backends = [OrderingFilter, django_filters.rest_framework.DjangoFilterBackend]

    # 3. Указываем, по каким полям разрешена сортировка
    # 'date' для даты оплаты
    ordering_fields = ['date']

    # Можно добавить сортировку по умолчанию
    ordering = ['-date']  # Сортировка по убыванию даты (самые новые — первыми)


# View для регистрации (доступен всем!)
class UserRegisterAPIView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    # 💡 AllowAny: разрешает доступ неавторизованным пользователям
    permission_classes = [AllowAny]
    queryset = User.objects.all()

# ViewSet для CRUD пользователей (закрыт авторизацией по умолчанию)
class UserViewSet(viewsets.ModelViewSet):
    """
    Полный CRUD для модели User. Доступен только авторизованным пользователям.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()


# View для установки/удаления подписки
class SubscriptionManageAPIView(generics.CreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    # Мы используем POST-запрос для подписки/отписки
    def post(self, request, *args, **kwargs):
        course_id = request.data.get('course')
        user = request.user

        if not course_id:
            return Response({"error": "Необходимо указать ID курса."}, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем, существует ли подписка
        try:
            subscription = Subscription.objects.get(user=user, course_id=course_id)

            # Если подписка существует — удаляем (отписываемся)
            subscription.delete()
            return Response({"message": "Подписка успешно удалена (отписка)."}, status=status.HTTP_204_NO_CONTENT)

        except Subscription.DoesNotExist:
            # Если подписка не существует — создаем (подписываемся)
            Subscription.objects.create(user=user, course_id=course_id)
            return Response({"message": "Подписка успешно оформлена."}, status=status.HTTP_201_CREATED)
