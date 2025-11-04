from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import RegistrationAPIView, UserViewSet, PaymentListAPIView

router = DefaultRouter()
router.register(r"profiles", UserViewSet, basename="profiles")

urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("payments/", PaymentListAPIView.as_view(), name="payments-list"),
    path("", include(router.urls)),
]
