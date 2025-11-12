from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from celery import shared_task

from materials.models import Well, Subscription


@shared_task(name="materials.send_course_update_notifications")
def send_course_update_notifications(course_id: int):
    """
    Отправляет письма всем подписчикам курса.
    Защита от частых рассылок: если с момента последней рассылки/обновления прошло < 4 часов — не отправлять повторно.
    """
    try:
        course = Well.objects.get(pk=course_id)
    except Well.DoesNotExist:
        return {"status": "not_found", "course_id": course_id}

    now = timezone.now()
    barrier = now - timedelta(hours=4)

    # Если курс обновлялся/уведомлялся в последние 4 часа — выходим
    last_mark = course.notified_at or course.updated_at
    if last_mark and last_mark >= barrier:
        return {"status": "skipped_recent", "course_id": course_id, "last_mark": str(last_mark)}

    emails = list(
        Subscription.objects.filter(course=course).select_related("user").values_list("user__email", flat=True)
    )
    if not emails:
        # всё равно обновим notified_at, чтобы не слать лишний раз
        course.notified_at = now
        course.save(update_fields=["notified_at"])
        return {"status": "no_subscribers", "course_id": course_id}

    subject = f"Обновления по курсу: {course.name}"
    message = f"В курсе «{course.name}» появились обновления материалов."
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com")

    # Отправляем одним письмом каждому пользователю
    for email in emails:
        send_mail(subject, message, from_email, [email], fail_silently=True)

    # Отмечаем время рассылки
    course.notified_at = now
    course.save(update_fields=["notified_at"])

    return {"status": "sent", "count": len(emails), "course_id": course_id}
