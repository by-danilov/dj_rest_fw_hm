import stripe
from django.conf import settings
from materials.models import Course
from users.models import Payment


stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_product(course: Course):
    """
    Создает продукт (Product) в Stripe.
    """
    try:
        stripe_product = stripe.Product.create(
            name=f"Курс: {course.title}",
            description=course.description,
            metadata={'course_id': course.pk}
        )
        return stripe_product.id
    except stripe.error.StripeError as e:
        print(f"Ошибка Stripe при создании продукта: {e}")
        return None


def create_stripe_price(course: Course, product_id: str):
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
            product=product_id,
            type="one_time",
        )

        # Сохраняем ID цены в курсе для дальнейшего использования
        course.stripe_price_id = stripe_price.id
        course.save()

        return stripe_price.id

    except stripe.error.StripeError as e:
        print(f"Ошибка Stripe при создании цены: {e}")
        return None


def create_stripe_session(price_id: str, user_email: str, client_ref_id: str):
    """
    Создает сессию оплаты Checkout в Stripe для данного ID цены.
    Не создает объекты в БД.
    """
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://127.0.0.1:8000/api/v1/users/payments/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://127.0.0.1:8000/api/v1/users/payments/cancel',

            client_reference_id=client_ref_id,
            customer_email=user_email,
        )

        return None, checkout_session

    except stripe.error.StripeError as e:
        print(f"Ошибка Stripe при создании сессии: {e}")
        return {"error": str(e)}, None
