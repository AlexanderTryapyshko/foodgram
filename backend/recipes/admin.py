"""Настройки админки."""
from django.contrib import admin

from api.constants import MIN_NUM
from recipes.models import (
    Ingredient,
    Favorite,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShoppingCart,
    ShortLink,
    Tag
)


class IngredientInLine(admin.TabularInline):
    """Вспомогательный класс для ингредиентов."""

    model = RecipeIngredient
    extra = 0
    min_num = MIN_NUM


class TagInLine(admin.TabularInline):
    """Вспомогательный класс для тегов."""

    model = RecipeTag
    extra = 0
    min_num = MIN_NUM


class FavoriteInLine(admin.TabularInline):
    """Вспомогательный класс для списка избранного."""

    model = Favorite
    extra = 0


class ShoppingCartInline(admin.TabularInline):
    """Вспомогательный класс для списка избранного."""

    model = ShoppingCart
    extra = 0


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Класс настройки ингредиентов."""

    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Класс настройки тегов."""

    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Класс настройки рецептов."""

    list_display = (
        'pk',
        'name',
        'text',
        'cooking_time',
        'author',
        'get_ingredient',
        'get_tag',
        'created_at',
        'get_is_favorited_count',
        'get_short_link'
    )
    search_fields = ('name', 'author__username',)
    list_filter = ('tags',)
    inlines = (
        IngredientInLine,
        FavoriteInLine,
        ShoppingCartInline,
        TagInLine,
    )

    @admin.display(description='Ингредиенты')
    def get_ingredient(self, instance):
        """Метод для отображения ингредиентов."""
        return ', '.join(value.name for value in instance.ingredients.all())

    @admin.display(description='Теги')
    def get_tag(self, instance):
        """Метод для отображения тегов."""
        return ', '.join(value.name for value in instance.tags.all())

    @admin.display(description='В избранном')
    def get_is_favorited_count(self, instance):
        """Метод для отображения количества добавлений рецепта в избранное."""
        count = Favorite.objects.filter(recipe_id=instance.pk).count()
        if count == 1:
            return f'У {count} пользователя.'
        elif count == 0:
            return 'Не встречается.'
        else:
            return f'У {count} пользователей.'

    @admin.display(description='Короткая ссылка на рецепт')
    def get_short_link(self, instance):
        """Метод для отображения короткой ссылки на рецепт."""
        link = ShortLink.objects.get(recipe=instance).short_link
        return f'/s/{link}/'
