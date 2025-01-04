"""Модели проекта Foodgram."""
import shortuuid

from django.core.validators import MinValueValidator
from django.db import models
from django.dispatch import receiver

from api.constants import (
    IMAGE_UPLOAD_DIRECTORY,
    ING_TAG_NAME_MAX_LENGTH,
    MAX_UNIT,
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
                1, message='Время приготовления не менее 1 минуты'
            ),
        ),
        default=1,
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
    is_favorited = models.BooleanField(
        verbose_name='В избранном',
        default=False
    )
    is_in_shopping_cart = models.BooleanField(
        verbose_name='В списке покупок',
        default=False
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
        related_name='recipeingredient_recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipeingredient_ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(
                1, message='Кол-во ингредиентов не менее 1'
            ),
        ),
        default=1,
    )

    class Meta:
        """Класс Meta промежуточной модели."""

        verbose_name = 'Наличие ингредиента в рецепте'
        verbose_name_plural = 'Наличие ингредиентов в рецепте'
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
        related_name='recipetag_recipe'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег',
        related_name='recipetag_tag'
    )

    class Meta:
        """Класс Meta промежуточной модели."""

        verbose_name = 'Соответствие тега и рецепта'
        verbose_name_plural = 'Соответствие тегов и рецептов'
        ordering = ('recipe',)

    def __str__(self):
        """Переопределение метода __str__."""
        return f'{self.recipe} принадлежит к тегу {self.tag}'


class Favorite(models.Model):
    """Модель 'Избранное'."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites_recipe'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites_user'
    )

    class Meta:
        """Класс Meta для модели избранного."""

        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

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
        related_name='shoppings_recipe'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppings_user'
    )

    class Meta:
        """Класс Meta для модели списка покупок."""

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

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
