"""Сериализаторы приложения 'Api'."""
import base64

from rest_framework import serializers
from django.core.files.base import ContentFile

from recipes.models import (
    Ingredient,
    Favorite,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import User
from users.serializers import UsersGETSerializer


class Base64ImageField(serializers.ImageField):
    """Сериализатор преобразования изображения."""

    def to_internal_value(self, data):
        """Метод преобразования изображения."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipesIngredientGETSerializer(serializers.ModelSerializer):
    """Сериализатор отображения ингредиентов в рецепте."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        """Meta."""

        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор создания связи 'Рецепт-Ингредиент'."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        """Meta."""

        model = RecipeIngredient
        fields = ('id', 'amount')


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингредиента."""

    class Meta:
        """Meta."""

        model = Ingredient
        fields = '__all__'


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор модели тега."""

    class Meta:
        """Meta."""

        model = Tag
        fields = '__all__'


class RecipesGETSerializer(serializers.ModelSerializer):
    """Сериализатор получения рецепта."""

    tags = TagsSerializer(many=True, read_only=True)
    author = UsersGETSerializer()
    ingredients = RecipesIngredientGETSerializer(
        many=True,
        source='recipeingredient_recipe'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)

    class Meta:
        """Meta."""

        model = Recipe
        read_only_fields = ('author',)
        exclude = ['created_at']

    def get_image_url(self, obj):
        """Получение ссылки на изображение."""
        if obj.image:
            return obj.image.url
        return None

    def get_is_favorited(self, obj):
        """Отображение нахождения рецепта в избранном."""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj, user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        """Отображение нахождения рецепта в избранном списке покупок."""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            recipe=obj,
            user=request.user
        ).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""

    ingredients = CreateRecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(required=True)
    image_url = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )

    class Meta:
        """Meta."""

        model = Recipe
        read_only_fields = ('author',)
        exclude = ['created_at']
        required_fields = (
            'ingredients',
            'tags',
            'cooking_time',
            'name',
            'text'
        )

    def get_image_url(self, obj):
        """Получение ссылки на изображение."""
        if obj.image:
            return obj.image.url
        return None

    def validate(self, data):
        """Валидация присутствия полей ингредиента и тега."""
        request = self.context.get('request')
        if request and request.method == 'PATCH':
            if 'ingredients' not in data:
                raise serializers.ValidationError(
                    'В запросе отсутствует поле ingredients'
                )
            if 'tags' not in data:
                raise serializers.ValidationError(
                    'В запросе отсутствует поле tags'
                )
        return data

    def validate_ingredients(self, value):
        """Валидация наличия ингредиентов в рецепте."""
        unique_ingredients = set(element['id'] for element in value)
        if len(value) == 0:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один ингредиент'
            )
        elif len(value) != len(unique_ingredients):
            raise serializers.ValidationError(
                'Ингредиенты повторяются'
            )
        return value

    def validate_tags(self, value):
        """Валидация наличия тегов в рецепте."""
        unique_tags = set(value)
        if len(value) == 0:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один тег'
            )
        elif len(value) != len(unique_tags):
            raise serializers.ValidationError(
                'Теги повторяются'
            )
        return value

    def validate_cooking_time(self, value):
        """Валидация времени приготовления."""
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть не менее 1 минуты'
            )
        return value

    def create_recipe_ingredient(self, ingredients, recipe):
        """Метод создания связки 'Рецепт-Ингредиент'."""
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    ingredient=ingredient.get('id'),
                    recipe=recipe,
                    amount=ingredient.get('amount')
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        """Создание рецепта."""
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.create_recipe_ingredient(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        recipe = instance
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.tags.clear()
        tags = validated_data.get('tags')
        instance.tags.set(tags)
        instance.ingredients.clear()
        ingredients = validated_data.get('ingredients')
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.create_recipe_ingredient(ingredients, recipe)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Изменение ответа api."""
        return RecipesGETSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения короткой информации о рецепте."""

    name = serializers.ReadOnlyField()
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        """Meta."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscribeUserSerializer(UsersGETSerializer):
    """Сериализатор для модели подписки."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UsersGETSerializer.Meta):
        """Meta."""

        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )
        read_only_fields = ['email', 'username', 'first_name', 'last_name', ]

    def get_author_recipes(self, author):
        """Получение рецептов автора."""
        return Recipe.objects.filter(author=author)

    def get_recipes(self, author):
        """Отображение рецептов автора."""
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes_limit = int(recipes_limit)
        recipes = self.get_author_recipes(author)[:recipes_limit]
        return ShortRecipeSerializer(recipes, many=True,).data

    def get_recipes_count(self, author):
        """Получение количества рецептов у автора."""
        return self.get_author_recipes(author).count()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара."""

    avatar = Base64ImageField()

    class Meta:
        """Meta."""

        model = User
        fields = ['avatar', ]

    def update(self, instance, validated_data):
        """Update."""
        instance.avatar = validated_data.get('avatar',)
        instance.save()
        return instance
