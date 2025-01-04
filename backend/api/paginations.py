"""Пагинаторы проекта foodgram."""
from rest_framework.pagination import PageNumberPagination


class PageLimitPaginator(PageNumberPagination):
    """Определяет количество отображаемых на странице рецептов."""

    page_size = 6
    page_size_query_param = 'limit'
