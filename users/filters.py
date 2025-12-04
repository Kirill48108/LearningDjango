import django_filters
from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name="course__id", lookup_expr="exact")
    lesson = django_filters.NumberFilter(field_name="lesson__id", lookup_expr="exact")
    payment_method = django_filters.ChoiceFilter(field_name="payment_method", choices=Payment.PaymentMethod.choices)
    paid_at = django_filters.DateFromToRangeFilter(field_name="paid_at")

    class Meta:
        model = Payment
        fields = (
            "course",
            "lesson",
            "payment_method",
            "paid_at",
        )
