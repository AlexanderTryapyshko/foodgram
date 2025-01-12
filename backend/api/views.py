"""Views проекта foodgram."""

from django.contrib.auth.hashers import check_password
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404, redirect
from djoser.views import UserViewSet
from rest_framework import filters, permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.paginations import PageLimitPaginator
from api.permissions import AllowAnyExceptEndpointMe, ReadOrAuthorOnly
from api.serializers import (
    AvatarSerializer,
    CreateRecipeSerializer,
    FavoriteSerializer,
    IngredientsSerializer,
    RecipesGETSerializer,
    ShoppingCartSerializer,
    SubscribeUserSerializer,
    TagsSerializer
)
from api.utils import favorite_shopping_cart_recipe, shoppings_in_file
from recipes.models import (
    Ingredient,
    Favorite,
    Recipe,
    ShoppingCart,
    ShortLink,
    Tag
)
from users.models import Subscribe, User
from users.serializers import (
    CreateUserSerializer,
    SetPasswordSerializer,
    UsersGETSerializer
)


class UserViewSet(UserViewSet):
    """Вьюсет для модели юзера."""

    queryset = User.objects.all()
    pagination_class = PageLimitPaginator
    permission_classes = (AllowAnyExceptEndpointMe,)

    def get_serializer_class(self):
        """Определение класса сериализатора в зависимости от запроса."""
        if self.request.method in permissions.SAFE_METHODS:
            return UsersGETSerializer
        return CreateUserSerializer

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        """Метод изменения пароля."""
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']
        username = request.user.username
        user = get_object_or_404(
            self.get_queryset(),
            username=username
        )
        if check_password(password, user.password):
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def avatar(self, request):
        """Метод смены/удаления аватара."""
        if request.method == 'PUT':
            serializer = AvatarSerializer(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {'avatar': request.build_absolute_uri(
                    request.user.avatar.url)})
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def subscriptions(self, request):
        """Метод получения подписок пользователя."""
        queryset = User.objects.filter(
            subscribe_author__user=self.request.user
        )
        authors = self.paginate_queryset(queryset)
        serializer = SubscribeUserSerializer(
            authors,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
        """Подписка/отписка на определенного пользователя."""
        author = get_object_or_404(User, id=id)
        user = request.user
        serializer = SubscribeUserSerializer(
            author,
            data={'user': user},
            context={'request': request, 'author': author}
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            serializer.create(validated_data={'author': author, 'user': user})
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        user_author = Subscribe.objects.filter(
            user=request.user, author=author)
        if user_author:
            user_author.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (
        ReadOrAuthorOnly,
        permissions.IsAuthenticatedOrReadOnly,
    )
    pagination_class = PageLimitPaginator
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    )
    filterset_class = RecipeFilter
    ordering_fields = ('created_at')
    ordering = ('-created_at',)
    search_fields = ('^ingredients__name',)

    def get_serializer_class(self):
        """Определение класса сериализатора в зависимости от запроса."""
        if self.request.method == 'GET':
            return RecipesGETSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        """Определение автора рецепта."""
        serializer.save(author=self.request.user)

    @action(detail=True, url_path='get-link')
    def get_link(self, request, pk):
        """Полечение короткой ссылки по эндпоинту '/get-link/."""
        data = get_object_or_404(ShortLink, recipe_id=pk).short_link
        short_link = f'{request.get_host()}/s/{data}/'
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        """Добавление рецепта в список покупок."""
        return favorite_shopping_cart_recipe(
            ShoppingCart,
            ShoppingCartSerializer,
            request,
            pk
        )

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        """Добавление рецепта в избранное."""
        return favorite_shopping_cart_recipe(
            Favorite,
            FavoriteSerializer,
            request,
            pk
        )

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Метод для скачивания списпа ингредиентов."""
        return shoppings_in_file(request)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_fields = ['name']
    search_fields = ('^name',)


class RedirectShortLinkView(views.View):
    """Редиррект с короткой ссылки."""

    def get(self, request, short_link):
        """Получение необходимого рецепта по короткой ссылке."""
        short_link_recipe = get_object_or_404(
            ShortLink,
            short_link=short_link
        )
        recipe_id = short_link_recipe.recipe_id
        return redirect(
            request.build_absolute_uri(f'/recipes/{recipe_id}/')
        )
