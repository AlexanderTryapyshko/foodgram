"""Пагинаторы проекта foodgram."""
from rest_framework.pagination import PageNumberPagination

from api.constants import PAGE_SIZE


class PageLimitPaginator(PageNumberPagination):
    """Определяет количество отображаемых на странице рецептов."""

    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
