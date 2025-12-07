from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    PaymentCheckoutCreateAPIView,
    PaymentCheckoutStatusAPIView,
    PaymentListAPIView,
    RegistrationAPIView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"profiles", UserViewSet, basename="profiles")

urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("payments/", PaymentListAPIView.as_view(), name="payments-list"),
    path(
        "payments/checkout/",
        PaymentCheckoutCreateAPIView.as_view(),
        name="payments-checkout-create",
    ),
    path(
        "payments/<int:pk>/status/",
        PaymentCheckoutStatusAPIView.as_view(),
        name="payments-checkout-status",
    ),
    path("", include(router.urls)),
]
