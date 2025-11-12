from rest_framework import serializers

from materials.models import Lesson, Well
from materials.validators import validate_youtube_url
from materials.models import Subscription



class LessonShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "title")


class WellSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = serializers.SerializerMethodField
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Well
        fields = "__all__"

    def get_lessons_count(self, obj: Well) -> int:
        return obj.lessons.count()

    def get_lessons(self, obj: Well):
        lessons_qs = obj.lessons.all()
        return LessonSerializer(lessons_qs, many=True, context=self.context).data

    def get_is_subscribed(self,obj: Well) -> bool:
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(user=request.user, course=obj).exists()


class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(
        required=False,allow_null=True,allow_blank=True,validators=[validate_youtube_url])
    class Meta:
        model = Lesson
        fields = "__all__"
