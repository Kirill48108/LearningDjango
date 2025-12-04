from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSelfOrReadOnly(BasePermission):
    """
    - Любой аутентифицированный может просматривать чужие профили (GET/HEAD/OPTIONS).
    - Изменять/удалять — только свой профиль.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and obj == request.user
