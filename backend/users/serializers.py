"""Сериализаторы приложения пользователей."""
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from api.constants import USER_MAX_LENGHT
from users.models import Subscribe, User


class CreateUserSerializer(UserCreateSerializer):
    """
    Сериализатор на создание пользователя.

    Поля, необходимые для заполнения:
    - email;
    - username;
    - first_name;
    - last_name;
    - password.
    """

    class Meta:
        """Класс Meta для сериализатора создания пользователя."""

        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        required_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class UsersGETSerializer(serializers.ModelSerializer):
    """Сериализатор получения объекта пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        """Класс Meta для сериализатора создания пользователя."""

        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        """Метод определения подписки пользователя на автора рецепта."""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            author=obj,
            user=request.user).exists()


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля."""

    new_password = serializers.CharField(max_length=USER_MAX_LENGHT)
    current_password = serializers.CharField(max_length=USER_MAX_LENGHT)
