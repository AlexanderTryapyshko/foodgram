"""Приложение 'Пользователи'."""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """UserConfig."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Пользователи'
