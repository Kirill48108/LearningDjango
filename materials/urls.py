from django.urls import path

from .views import (LessonListCreateAPIView,
                    LessonRetrieveUpdateDestroyAPIView,
                    SubscriptionToggleAPIView, WellListCreateAPIView,
                    WellRetrieveUpdateDestroyAPIView)

app_name = "materials"

urlpatterns = [
    # Курсы
    path("wells/", WellListCreateAPIView.as_view(), name="well-list-create"),
    path(
        "wells/<int:pk>/",
        WellRetrieveUpdateDestroyAPIView.as_view(),
        name="well-detail",
    ),
    # Уроки
    path("lessons/", LessonListCreateAPIView.as_view(), name="lesson-list-create"),
    path(
        "lessons/<int:pk>/",
        LessonRetrieveUpdateDestroyAPIView.as_view(),
        name="lesson-detail",
    ),
    # Подписка toggle
    path(
        "wells/subscribe/",
        SubscriptionToggleAPIView.as_view(),
        name="subscription-toggle",
    ),
]
