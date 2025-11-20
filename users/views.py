import django_filters
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Payment, User, Subscription
from .serializers import PaymentSerializer, UserSerializer, UserRegisterSerializer, SubscriptionSerializer
from .filters import PaymentFilter
from rest_framework.filters import OrderingFilter
from drf_spectacular.utils import extend_schema
from users.serializers import PaymentRequestSerializer
from materials.services import create_stripe_product, create_stripe_price, create_stripe_session
from materials.models import Course
from users.models import Payment
from django.shortcuts import get_object_or_404


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

@extend_schema(
    summary="Управление подпиской на курс",
    description="POST-запрос для подписки/отписки. Если подписка существует, она удаляется (отписка). Если нет, она создается (подписка).",
    # В теле запроса ожидаем только course_id
    request=SubscriptionSerializer,
    # Возможные ответы
    responses={
        201: {'description': 'Подписка успешно оформлена.'},
        204: {'description': 'Подписка успешно удалена (отписка).'},
        400: {'description': 'Ошибка: Не указан ID курса.'},
    }
)

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


# View для создания платежной сессии Stripe
class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data['course_id']
        user = request.user

        # Получаем курс
        course = get_object_or_404(Course, pk=course_id)

        # Проверяем наличие Stripe Price ID и создаем Product/Price при необходимости
        price_id = course.stripe_price_id

        if not price_id:
            # Cоздаем Product
            product_id = create_stripe_product(course)
            if not product_id:
                return Response({"error": "Не удалось создать продукт Stripe."}, status=status.HTTP_400_BAD_REQUEST)

            # Cоздаем Price, используя Product ID
            price_id = create_stripe_price(course, product_id)
            if not price_id:
                return Response({"error": "Не удалось создать цену Stripe."}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем запись о платеже в нашей базе данных (Статус is_paid=False)
        payment = Payment.objects.create(
            user=user,
            paid_course=course,  # Используем твое имя поля 'paid_course'
            amount=course.price,
            payment_method=Payment.PaymentMethod.STRIPE,
        )

        # Создаем сессию Stripe, используя ID цены
        client_ref_id = str(payment.pk)  # Используем ID нашего Payment для обратной связи
        error, checkout_session = create_stripe_session(price_id, user.email, client_ref_id)

        if error:
            # Если Stripe вернул ошибку, удаляем созданный объект Payment
            payment.delete()
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        # Сохраняем ID сессии и ссылку в нашем объекте Payment
        payment.stripe_session_id = checkout_session.id
        payment.payment_link = checkout_session.url
        payment.save()

        # Возвращаем ссылку на оплату
        return Response(
            {"payment_url": checkout_session.url},
            status=status.HTTP_201_CREATED
        )
