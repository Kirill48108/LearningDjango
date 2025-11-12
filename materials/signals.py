from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from materials.models import Well, Lesson
from materials.tasks import send_course_update_notifications


@receiver(post_save, sender=Well)
def on_course_saved(sender, instance: Well, created, **kwargs):
    """
    При сохранении курса — запланировать рассылку подписчикам.
    """
    send_course_update_notifications.delay(instance.id)


@receiver(post_save, sender=Lesson)
def on_lesson_saved(sender, instance: Lesson, created, **kwargs):
    """
    При сохранении урока — запланировать рассылку по курсу, если нет рассылок/обновлений за 4 часа.
    (логика проверки выполняется в самой задаче)
    """
    send_course_update_notifications.delay(instance.course_id)
