"""Настройки админ-зоны пользователей."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import Subscribe, User


@admin.register(User)
class UserAdmin(UserAdmin):
    """Админ-зона пользователя."""

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'get_authors'
    )
    search_fields = ('username', 'email',)

    @admin.display(description='Подписан на')
    def get_authors(self, instance):
        """Метод для отображения подписок."""
        authors = Subscribe.objects.filter(user_id=instance.id)
        return ', '.join(str(element.author) for element in authors)
