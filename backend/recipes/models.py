"""Модели проекта Foodgram."""
import shortuuid

from django.core.validators import MinValueValidator
from django.db import models
from django.dispatch import receiver

from api.constants import (
    IMAGE_UPLOAD_DIRECTORY,
    ING_TAG_NAME_MAX_LENGTH,
    MAX_UNIT,
    MIN_NUM,
    REC_NAME_MAX_LENGTH,
    SHORT_LINK_LENGTH,
    STR_CONST
)
from users.models import User


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField('Название', max_length=ING_TAG_NAME_MAX_LENGTH)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_UNIT
    )

    class Meta:
        """Класс Meta для модели ингредиента."""

        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredients'
            ),
        )

    def __str__(self):
        """Переопределение метода __str__."""
        return self.name[:STR_CONST]


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        'Название',
        max_length=ING_TAG_NAME_MAX_LENGTH,
        unique=True
    )
    slug = models.SlugField('Идентификатор', unique=True)

    class Meta:
        """Класс Meta для модели тега."""

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        """Переопределение метода __str__."""
        return self.name[:STR_CONST]


class Recipe(models.Model):
    """Модель рецепта."""

    name = models.CharField('Название', max_length=REC_NAME_MAX_LENGTH)
    text = models.TextField('Текстовое описание')
    image = models.ImageField(upload_to=IMAGE_UPLOAD_DIRECTORY)
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=(
            MinValueValidator(
                MIN_NUM,
                message=f'Время приготовления не менее {MIN_NUM} минуты'
            ),
        ),
        default=MIN_NUM,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиент'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Тег'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создан'
    )

    class Meta:
        """Класс Meta для модели рецепта."""

        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['created_at']

    def __str__(self):
        """Переопределение метода __str__."""
        return self.name[:STR_CONST]


class RecipeIngredient(models.Model):
    """Промежуточная модель связи рецепта и ингредиента."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(
                MIN_NUM,
                message=f'Количество ингредиентов не менее {MIN_NUM}'
            ),
        ),
        default=MIN_NUM,
    )

    class Meta:
        """Класс Meta промежуточной модели."""

        verbose_name = 'Наличие ингредиента в рецепте'
        verbose_name_plural = 'Наличие ингредиентов в рецепте'
        default_related_name = 'recipeingredients'
        ordering = ('recipe',)

    def __str__(self):
        """Переопределение метода __str__."""
        return f'{self.ingredient} присутствует в рецепте {self.recipe}'


class RecipeTag(models.Model):
    """Промежуточная модель связи рецепта и тега."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег',
    )

    class Meta:
        """Класс Meta промежуточной модели."""

        verbose_name = 'Соответствие тега и рецепта'
        verbose_name_plural = 'Соответствие тегов и рецептов'
        default_related_name = 'recipetags'
        ordering = ('recipe',)

    def __str__(self):
        """Переопределение метода __str__."""
        return f'{self.recipe} принадлежит к тегу {self.tag}'


class Favorite(models.Model):
    """Модель 'Избранное'."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        """Класс Meta для модели избранного."""

        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        default_related_name = 'favorites'
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorites'
            ),
        )

    def __str__(self):
        """Переопределение метода __str__."""
        return (
            f'Рецепт {self.recipe} присутствует в избранном у пользователей:'
        )


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        """Класс Meta для модели списка покупок."""

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shoppingcarts'
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shoppings'
            ),
        )

    def __str__(self):
        """Переопределение метода __str__."""
        return (
            f'Рецепт {self.recipe} присутствует в '
            'списке покупок у пользователей:'
        )


class ShortLink(models.Model):
    """Модель короткой ссылки."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    short_link = models.CharField(max_length=SHORT_LINK_LENGTH, unique=True)

    @receiver(models.signals.post_save, sender=Recipe)
    def generate_short_link(sender, instance, created, **kwargs):
        """Создание короткой ссылки."""
        if created:
            ShortLink.objects.create(
                short_link=shortuuid.ShortUUID().random(
                    length=SHORT_LINK_LENGTH
                ),
                recipe_id=instance.id
            )
