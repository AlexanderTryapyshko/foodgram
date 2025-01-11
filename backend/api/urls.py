"""Urls.py."""
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (
    IngredientsViewSet,
    RecipesViewSet,
    TagsViewSet,
    UserViewSet
)

app_name = 'api'

router = SimpleRouter()
router.register('recipes', RecipesViewSet, basename='api-recipes')
router.register('tags', TagsViewSet, basename='api-tags')
router.register('ingredients', IngredientsViewSet, basename='api-ingredients')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
