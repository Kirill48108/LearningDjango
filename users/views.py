from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from .filters import PaymentFilter
from .models import Payment
from .serializers import PaymentSerializer


class PaymentListAPIView(ListAPIView):
    queryset = Payment.objects.select_related("user", "course", "lesson").all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    filterset_fields = ("course", "lesson", "payment_method")
    ordering_fields = ("paid_at",)
    ordering = ("-paid_at",)
