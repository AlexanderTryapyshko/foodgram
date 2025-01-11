"""Модели приложения пользователя."""
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from api.constants import REGULAR, STR_CONST
from api.validators import validate_username


class User(AbstractUser):
    """Модель Пользователя."""

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True,
        validators=[
            validate_username,
            RegexValidator(
            regex=REGULAR,
            message='Имя пользователя содержит недопустимый символ'
        )]
    )

    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True
    )
    email = models.EmailField(unique=True)

    class Meta:
        """Meta для модели пользователя."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        """Переопределение метода __str__."""
        return self.username[:STR_CONST]


class Subscribe(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='subscribe_user'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='subscribe_author'
    )

    class Meta:
        """Meta для модели подписки."""

        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ('author__username',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribing'
            ),
        ]

    def __str__(self):
        """Переопределение метода __str__."""
        return f'{self.user} подписан на {self.author}'
