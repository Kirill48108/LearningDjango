from django.conf import settings
from django.db import models


class Well(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название курса",
        help_text="Укажите название курса",
    )
    preview = models.ImageField(
        upload_to="course_previews/",
        blank=True,
        null=True,
        verbose_name="Превью Курса",
        help_text="Загрузите изображение курса",
    )
    description = models.TextField(
        max_length=500,
        verbose_name="Описание курса",
        help_text="Введите описание курса (до 500 символов)",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Владелец курса",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    course = models.ForeignKey(
        Well,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс",
        help_text="Выберите курс, к которому относится данный урок.",
    )
    title = models.CharField(
        max_length=160,
        verbose_name="Название урока",
        help_text="Введите название урока (до 160 символов).",
    )
    description = models.TextField(
        verbose_name="Описание урока", help_text="Введите подробное описание урока."
    )
    preview_img = models.ImageField(
        upload_to="lesson_previews/",
        blank=True,
        null=True,
        verbose_name="Превью урока",
        help_text="Загрузите изображение для превью урока (необязательно).",
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на видео",
        help_text="Введите URL-адрес видео для урока (необязательно).",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Владелец урока",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_subscriptions",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        Well,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "Подписка на курс"
        verbose_name_plural = "Подписки на курсы"
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user} -> {self.course}"
