"""Пермишены проекта foodgram."""
from rest_framework import permissions


class ReadOrAuthorOnly(permissions.BasePermission):
    """Определяет доступ либо для безопасных методов, либо для автора."""

    def has_object_permission(self, request, view, obj):
        """has_object_permission."""
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class AllowAnyExceptEndpointMe(permissions.BasePermission):
    """Запрещает доступ анонимного пользователя к эндпоинту /me/."""

    def has_permission(self, request, view):
        """has_permission."""
        if request.path == '/api/users/me/' and request.user.is_anonymous:
            return False
        return super().has_permission(request, view)
