from django.urls import path
from rest_framework.routers import SimpleRouter

from materials.apps import MaterialsConfig
from materials.views import (LessonCreateAPIView, LessonDestroyAPIView,
                             LessonListAPIView, LessonRetrieveAPIView,
                             LessonUpdateAPIView, WellViewSet)

app_name = MaterialsConfig.name

router = SimpleRouter()
router.register("", WellViewSet)


urlpatterns = [
    path("lessons/", LessonListAPIView.as_view(), name="lessons_list"),
    path("lessons/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lessons_retrieve"),
    path(
        "lessons/<int:pk>/update/", LessonUpdateAPIView.as_view(), name="lessons_update"
    ),
    path(
        "lessons/<int:pk>/destroy/",
        LessonDestroyAPIView.as_view(),
        name="lessons_destroy",
    ),
    path("lessons/create/", LessonCreateAPIView.as_view(), name="lessons_create"),
]

urlpatterns += router.urls
