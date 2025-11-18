import stripe
from django.conf import settings
from materials.models import Course
from users.models import Payment


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_price(course: Course):
    """
    Создает цену (Price) в Stripe на основе данных курса.
    """
    # Цена в центах
    amount_in_cents = int(course.price * 100)

    try:
        # Создание Цены (Price)
        stripe_price = stripe.Price.create(
            currency="usd",  # Используем доллары
            unit_amount=amount_in_cents,
            # Создаем продукт на лету
            product_data={
                "name": f"Курс: {course.title}",
            },
            # Мод оплаты - разовый
            type="one_time",
        )

        # Сохраняем ID цены в курсе для дальнейшего использования
        course.stripe_price_id = stripe_price.id
        course.save()

        return stripe_price.id

    except stripe.error.StripeError as e:
        print(f"Ошибка Stripe при создании цены: {e}")
        return None


def create_stripe_session(course_id: int, user):
    """
    Создает сессию оплаты Checkout в Stripe для данного курса.
    """
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return {"error": "Курс не найден."}, None

    # Если ID цены Stripe еще не создан, создаем его
    if not course.stripe_price_id:
        price_id = create_stripe_price(course)
        if not price_id:
            return {"error": "Не удалось создать цену Stripe."}, None
    else:
        price_id = course.stripe_price_id

    # Создание сессии оплаты
    try:
        checkout_session = stripe.checkout.Session.create(
            # Цена и количество
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            # Режим оплаты
            mode='payment',
            # URL для успешной и отмененной оплаты
            success_url='http://127.0.0.1:8000/api/v1/payments/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://127.0.0.1:8000/api/v1/payments/cancel',

            # Добавляем ID пользователя для отслеживания
            client_reference_id=str(user.pk),
            customer_email=user.email,
        )

        # Создаем запись о платеже в базе данных
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=course.price,
            payment_method=Payment.PaymentMethod.STRIPE,
            stripe_session_id=checkout_session.id,
            payment_link=checkout_session.url
        )

        return None, checkout_session.url

    except stripe.error.StripeError as e:
        print(f"Ошибка Stripe при создании сессии: {e}")
        return {"error": str(e)}, None
