"""Утилиты проекта foodgram."""
import csv

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


def favorite_shopping_cart_recipe(model_name, serializer_name, request, pk):
    """Добавление/удаление рецепта в избранное/список покупок."""
    recipe = get_object_or_404(Recipe, id=pk)
    user = request.user
    serializer = serializer_name(
        data={'user': user.id, 'recipe': recipe.id},
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    if request.method == 'POST':
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)
    model_recipe = model_name.objects.filter(
        user=request.user, recipe=recipe)
    if model_recipe:
        model_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)


def shoppings_in_file(cart):
    """Формирование списка покупок пользователя."""
    shopping_cart = {}
    for item in cart:
        shopping_cart[item['ingredient__name']] = (
            f'{item["amount"]} '
            f'{item["ingredient__measurement_unit"]}'
        )
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_cart.txt"'
    )
    writer = csv.writer(response)
    writer.writerow(['ингредиент', 'единица измерения', 'количество'])
    for item, value in shopping_cart.items():
        writer.writerow(
            [f'{item} - {value}']
        )
    return response
