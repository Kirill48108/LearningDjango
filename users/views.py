from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import viewsets, permissions
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
# Исправляем импорт StripeService на корректный путь файла
from users.stripe_service import StripeService

from .paginators import PaymentsPagination

from .serializers import (
    RegistrationSerializer,
    UserPublicSerializer,
    UserPrivateSerializer,
    PaymentSerializer,
    PaymentCreateSerializer,  # используем реальный сериализатор из serializers.py
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
    pagination_class = PaymentsPagination



class PaymentCheckoutCreateAPIView(CreateAPIView):
    """
    Создание локального платежа + создание product/price/session в Stripe.
    Возвращает checkout_url для оплаты.
    """
    serializer_class = PaymentCreateSerializer

    @extend_schema(
        request=PaymentCreateSerializer,
        responses={
            201: OpenApiResponse(response=PaymentSerializer, description="Платёж создан, ссылка на оплату сохранена"),
            400: OpenApiResponse(description="Ошибка валидации"),
        },
        description="Создаёт платёж в системе и checkout-сессию в Stripe. Возвращает платёж с checkout_url.",
    )
    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        payment: Payment = ser.save(user=request.user)

        target_name = payment.course.name if payment.course else payment.lesson.title
        service = StripeService()
        try:
            product = service.create_product(name=target_name)
            price = service.create_price(product_id=product["id"], amount=payment.amount)
            session = service.create_checkout_session(price_id=price["id"])
        except Exception as e:
            return Response({"detail": f"Stripe error: {e}"}, status=400)

        payment.stripe_product_id = product["id"]
        payment.stripe_price_id = price["id"]
        payment.stripe_session_id = session["id"]
        payment.checkout_url = session.get("url")
        payment.save(update_fields=["stripe_product_id", "stripe_price_id", "stripe_session_id", "checkout_url"])

        return Response(PaymentSerializer(payment).data, status=201)


class PaymentCheckoutStatusAPIView(APIView):
    """
    Доп. задание: получение статуса чекаута по session_id.
    """
    @extend_schema(
        responses={200: OpenApiResponse(description="Данные Stripe Checkout Session")},
        description="Возвращает состояние платежной сессии Stripe по session_id платежа.",
    )
    def get(self, request, pk: int):
        try:
            payment = Payment.objects.get(pk=pk, user=request.user)
        except Payment.DoesNotExist:
            return Response({"detail": "Платёж не найден"}, status=404)
        if not payment.stripe_session_id:
            return Response({"detail": "У платежа нет Stripe session_id"}, status=400)

        service = StripeService()
        try:
            data = service.retrieve_session(payment.stripe_session_id)
        except Exception as e:
            return Response({"detail": f"Stripe error: {e}"}, status=400)

        payment.status = data.get("status")
        payment.save(update_fields=["status"])

        return Response({"session": data, "status": data.get("status")}, status=200)

