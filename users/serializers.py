from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Payment

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name", "last_name")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "city", "avatar")


class UserPrivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "city",
            "avatar",
            "is_active",
            "date_joined",
        )
        read_only_fields = ("is_active", "date_joined")



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

    def validate(self, attrs):
        course = attrs.get("course")
        lesson = attrs.get("lesson")
        if not course and not lesson:
            raise serializers.ValidationError("Нужно указать либо course, либо lesson.")
        if course and lesson:
            raise serializers.ValidationError("Укажите только один объект оплаты: course или lesson.")
        return attrs


class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания локальной записи платежа,
    после чего создаётся product/price/session в Stripe.
    Требует указать РОВНО одно из полей: course ИЛИ lesson.
    """
    class Meta:
        model = Payment
        fields = ("id", "user", "paid_at", "course", "lesson", "amount", "payment_method")
        read_only_fields = ("user",)

    def validate(self, attrs):
        course = attrs.get("course")
        lesson = attrs.get("lesson")
        if not course and not lesson:
            raise serializers.ValidationError("Укажите либо course, либо lesson.")
        if course and lesson:
            raise serializers.ValidationError("Укажите только один объект оплаты: course ИЛИ lesson.")
        return attrs

