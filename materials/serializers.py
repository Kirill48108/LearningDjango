from xml.dom.domreg import well_known_implementations

from rest_framework import serializers

from materials.models import Lesson, Well


class LessonShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "title")


class WellSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = serializers.SerializerMethodField

    class Meta:
        model = Well
        fields = "__all__"

    def get_lessons_count(self, obj: Well) -> int:
        return obj.lessons.count()

    def get_lessons(self, obj: Well):
        lessons_qs = obj.lessons.all()
        return LessonSerializer(lessons_qs, many=True, context=self.context).data


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
