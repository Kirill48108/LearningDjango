from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lesson, Subscription, Well
from .paginators import CoursePagination, LessonPagination
from .permissions import DenyCreateDeleteForModer, IsModer, IsOwnerOrReadWriteOwn
from .serializers import LessonSerializer, WellSerializer


# Список/создание курсов
class WellListCreateAPIView(ListAPIView, CreateAPIView):
    serializer_class = WellSerializer
    permission_classes = [DenyCreateDeleteForModer]
    pagination_class = CoursePagination

    def get_queryset(self):
        # Модераторы видят все, остальные — только свои
        user = self.request.user
        if IsModer.is_user_moder(user):
            return Well.objects.order_by("id")
        return Well.objects.filter(owner=user).order_by("id")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# Детально курс
class WellRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = WellSerializer
    permission_classes = [DenyCreateDeleteForModer & (IsModer | IsOwnerOrReadWriteOwn)]
    queryset = Well.objects.all()


# Аналогично для уроков
class LessonListCreateAPIView(ListAPIView, CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [DenyCreateDeleteForModer]
    pagination_class = LessonPagination

    def get_queryset(self):
        user = self.request.user
        if IsModer.is_user_moder(user):
            return Lesson.objects.select_related("course").order_by("id")
        return Lesson.objects.select_related("course").filter(owner=user).order_by("id")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer
    permission_classes = [DenyCreateDeleteForModer & (IsModer | IsOwnerOrReadWriteOwn)]
    queryset = Lesson.objects.select_related("course").all()


# Управление подпиской (toggle)
class SubscriptionToggleAPIView(APIView):
    permission_classes = [DenyCreateDeleteForModer | IsOwnerOrReadWriteOwn]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")
        course = get_object_or_404(Well, pk=course_id)

        subs_qs = Subscription.objects.filter(user=user, course=course)
        if subs_qs.exists():
            subs_qs.delete()
            message = "подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course)
            message = "подписка добавлена"

        return Response({"message": message})
