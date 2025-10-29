from rest_framework import serializers

from materials.models import Lesson, Well


class WellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Well
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    model = Lesson
    fields = "__all__"
