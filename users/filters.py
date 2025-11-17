import django_filters
from .models import Payment


class PaymentFilter(django_filters.FilterSet):

    class Meta:
        model = Payment
        fields = {
            # Фильтрация по способу оплаты (payment_method)
            'payment_method': ['exact'],
            # Фильтрация по курсу (ID)
            'paid_course': ['exact'],
            # Фильтрация по уроку (ID)
            'paid_lesson': ['exact'],
        }
