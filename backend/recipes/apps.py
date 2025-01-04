"""Приложение 'Рецепты'."""
from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """RecipesConfig."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    verbose_name = 'Рецепты'
