from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    RegistrationSerializer,
    UserPublicSerializer,
    UserPrivateSerializer,
    PaymentSerializer,
)
from .permissions import IsSelfOrReadOnly
from .models import Payment
from .filters import PaymentFilter

User = get_user_model()


class RegistrationAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")
    permission_classes = [permissions.IsAuthenticated, IsSelfOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return UserPublicSerializer
        if self.action in ("retrieve", "update", "partial_update", "destroy"):
            obj = None
            try:
                obj = self.get_object()
            except Exception:
                obj = None
            if obj is not None and self.request.user == obj:
                return UserPrivateSerializer
            return UserPublicSerializer
        return UserPublicSerializer

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class PaymentListAPIView(ListAPIView):
    queryset = (
        Payment.objects.select_related('user','course','lesson').all()
    )
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    filterset_fields = ("course", "lesson", "payment_method")
    ordering_fields = ("paid_at",)
    ordering = ("-paid_at",)
