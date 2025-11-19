from rest_framework import serializers
from .models import User, Payment, Subscription
from materials.models import Course, Lesson


class PaymentSerializer(serializers.ModelSerializer):
    # Вывод имени пользователя вместо ID
    user_email = serializers.EmailField(source='user.email', read_only=True)
    # Вывод названий курса/урока вместо ID
    paid_course_title = serializers.CharField(source='paid_course.title', read_only=True)
    paid_lesson_title = serializers.CharField(source='paid_lesson.title', read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id',
            'user',
            'user_email',
            'date',
            'paid_course',
            'paid_course_title',
            'paid_lesson',
            'paid_lesson_title',
            'amount',
            'payment_method'
        )
        read_only_fields = ('user',)


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Включаем email, пароль, телефон, город, аватар
        fields = ('email', 'password', 'phone', 'city', 'avatar')

    # Метод, который Django вызывает при сохранении сериализатора (для POST-запросов)
    def create(self, validated_data):
        # Переопределяем метод, чтобы корректно хешировать пароль
        user = User(
            email=validated_data['email'],
            phone=validated_data.get('phone'),
            city=validated_data.get('city'),
            avatar=validated_data.get('avatar')
        )
        user.set_password(validated_data['password'])  # Хешируем пароль
        user.save()
        return user


# Сериализатор для CRUD (получение и изменение)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', 'is_superuser', 'is_staff', 'is_active', 'groups',
                   'user_permissions')
        read_only_fields = ('email',)


# Сериализатор для Подписки (нужен только для связи ID)
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('course',) # Нам нужно только ID курса для подписки


# Сериализатор для запроса оплаты
class PaymentRequestSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
