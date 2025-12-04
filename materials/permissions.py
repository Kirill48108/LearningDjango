from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsModer(BasePermission):
    """
    Хелпер для проверки принадлежности к группе 'moderators'.
    Можно использовать и как отдельное правило, и как вспомогательную проверку.
    """

    @staticmethod
    def is_user_moder(user) -> bool:
        return user.is_authenticated and user.groups.filter(name="moderators").exists()

    def has_permission(self, request, view):
        return self.is_user_moder(request.user)

    def has_object_permission(self, request, view, obj):
        return self.is_user_moder(request.user)


class IsOwnerOrReadWriteOwn(BasePermission):
    """
    Не-модераторы: доступ только к своим объектам.
    """

    def has_object_permission(self, request, view, obj):
        # По условию: «видеть, редактировать и удалять только свои»
        return getattr(obj, "owner_id", None) == request.user.id


class DenyCreateDeleteForModer(BasePermission):
    """
    Модераторы: нельзя создавать (POST) и удалять (DELETE) курсы/уроки.
    Просмотр/редактирование — можно.
    """

    def has_permission(self, request, view):
        if IsModer.is_user_moder(request.user):
            if request.method in ("POST", "DELETE"):
                return False
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if IsModer.is_user_moder(request.user) and request.method == "DELETE":
            return False
        return True
