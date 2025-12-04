from django.urls import path

from .views import PaymentListAPIView

urlpatterns = [
    path("payments/", PaymentListAPIView.as_view(), name="payments-list"),
]
