from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from django.contrib.auth import get_user_model


@shared_task(name="users.deactivate_inactive_users")
def deactivate_inactive_users():
    """
    Ежедневная задача: блокирует пользователей, не заходивших более 30 дней (is_active=False).
    """
    User = get_user_model()
    threshold = timezone.now() - timedelta(days=30)
    qs = User.objects.filter(is_active=True, last_login__lt=threshold)
    updated = qs.update(is_active=False)
    return {"updated": updated}
