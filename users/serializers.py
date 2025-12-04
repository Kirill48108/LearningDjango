from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    course_name = serializers.CharField(source="course.name", read_only=True)
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "user_email",
            "paid_at",
            "course",
            "course_name",
            "lesson",
            "lesson_title",
            "amount",
            "payment_method",
        )
        read_only_fields = (
            "user_email",
            "course_name",
            "lesson_title",
        )
