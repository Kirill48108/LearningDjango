from urllib.parse import urlparse
from rest_framework import serializers



def validate_youtube_url(value: str):
    """
    Старый функциональный валидатор (оставляем на случай переиспользования).
    """
    if value in (None, ""):
        return value
    try:
        parsed = urlparse(value)
    except Exception:
        raise serializers.ValidationError("Некорректный URL.")
    host = (parsed.netloc or "").lower()
    allowed = ("youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtu.be")
    if not any(host.endswith(d) for d in allowed):
        raise serializers.ValidationError("Допускаются только ссылки на YouTube.")
    return value


class YouTubeOnlyValidator:
    """
    Класс-валидатор для использования на уровне сериализатора (Meta.validators).
    Проверяет, что поле self.field содержит ссылку только на домены YouTube.
    """

    def __init__(self, field: str):
        self.field = field

    def __call__(self, attrs):
        value = attrs.get(self.field)
        if value in (None, ""):
            return
        try:
            parsed = urlparse(value)
        except Exception:
            raise serializers.ValidationError({self.field: "Некорректный URL."})
        host = (parsed.netloc or "").lower()
        allowed = ("youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtu.be")
        if not any(host.endswith(d) for d in allowed):
            raise serializers.ValidationError({self.field: "Допускаются только ссылки на YouTube."})

    @property
    def __fields__(self):
        # Для инструментов/валидаторов, которые ожидают список полей валидатора
        return [self.field]
