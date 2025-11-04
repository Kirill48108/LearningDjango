from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from .models import Well, Lesson
from .serializers import WellSerializer, LessonSerializer
from .permissions import IsModer, IsOwnerOrReadWriteOwn, DenyCreateDeleteForModer

# Список/создание курсов
class WellListCreateAPIView(ListAPIView, CreateAPIView):
    serializer_class = WellSerializer
    permission_classes = [DenyCreateDeleteForModer]

    def get_queryset(self):
        # Модераторы видят все, остальные — только свои
        user = self.request.user
        if IsModer.is_user_moder(user):
            return Well.objects.all()
        return Well.objects.filter(owner=user)

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

    def get_queryset(self):
        user = self.request.user
        if IsModer.is_user_moder(user):
            return Lesson.objects.select_related("course").all()
        return Lesson.objects.select_related("course").filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class LessonRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer
    permission_classes = [DenyCreateDeleteForModer & (IsModer | IsOwnerOrReadWriteOwn)]
    queryset = Lesson.objects.select_related("course").all()
