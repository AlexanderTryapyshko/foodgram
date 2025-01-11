"""Фильтры."""
from django_filters import rest_framework as filters

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    """
    Фильтр для модели рецептов.

    Разрешает фильтрацию по тегам, автору рецепта,
    по нахождению в списке избранного/покупок.
    """

    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        lookup_expr='icontains'
    )
    author = filters.CharFilter(
        field_name='author__id',
        lookup_expr='icontains'
    )
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_my_recipes'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_my_recipes'
    )

    class Meta:
        """Класс Meta для фильтра модели рецептов."""

        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_my_recipes(self, queryset, request, value):
        """Метод для фильтрации по избранному/списку покупок."""
        if self.request.user.is_authenticated:
            is_favorited = self.request.query_params.get('is_favorited')
            is_in_shopping_cart = self.request.query_params.get(
                'is_in_shopping_cart'
            )
            if is_favorited == '1':
                queryset = queryset.filter(
                    favorites__user=self.request.user
                )
            if is_in_shopping_cart == '1':
                queryset = queryset.filter(
                    shoppingcarts__user=self.request.user
                )
        return queryset
