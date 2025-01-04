"""Утилиты проекта foodgram."""
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from api.serializers import ShortRecipeSerializer
from recipes.models import Recipe, RecipeIngredient, ShoppingCart


def favorite_shopping_cart_recipe(model_name, request, pk):
    """Добавление/удаление рецепта в избранное/список покупок."""
    recipe = get_object_or_404(Recipe, id=pk)
    if request.method == 'POST':
        serializer = ShortRecipeSerializer(
            recipe,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        if model_name.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        model_name.objects.create(user=request.user, recipe=recipe)
        modified_data = {
            **serializer.data,
            'image': request.build_absolute_uri(
                recipe.image.url)}
        return Response(
            modified_data,
            status=status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        model_recipe = model_name.objects.filter(
            user=request.user, recipe=recipe)
        if model_recipe:
            model_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


def shopping_cart(cart_user):
    """Формирование списка покупок пользователя."""
    shopping_cart = {}
    recipes_ids = [
        item.recipe.id for item in ShoppingCart.objects.filter(user=cart_user)
    ]
    for id in recipes_ids:
        for item in RecipeIngredient.objects.filter(recipe_id=id):
            if item.ingredient.name not in shopping_cart:
                shopping_cart[item.ingredient.name] = {
                    'measurement_unit': item.ingredient.measurement_unit,
                    'amount': item.amount
                }
            else:
                shopping_cart[item.ingredient.name]['amount'] += item.amount
    return shopping_cart
