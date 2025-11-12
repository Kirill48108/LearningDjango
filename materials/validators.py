from urllib.parse import urlparse
from rest_framework import serializers


def validate_youtube_url(value: str):
    """
    Разрешаем только ссылки на youtube (включая youtu.be).
    Пустые значения допускаем (поле lesson.video_url необязательное).
    """
    if value in (None, "",):
        return value
    try:
        parsed = urlparse(value)
    except Exception:
        raise serializers.ValidationError("Некорректный URL.")

    host = (parsed.netloc or "").lower()
    # Разрешённые домены YouTube
    allowed = ("youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtu.be")
    if not any(host.endswith(d) for d in allowed):
        raise serializers.ValidationError("Допускаются только ссылки на YouTube.")
    return value
