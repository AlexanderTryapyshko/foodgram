"""Сериализаторы приложения 'Api'."""
from rest_framework import serializers

from api.constants import MIN_NUM
from api.fields import Base64ImageField
from recipes.models import (
    Ingredient,
    Favorite,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import Subscribe, User
from users.serializers import UsersGETSerializer


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
        source='recipeingredients'
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
        return (
            request.user.is_authenticated
            and obj.favorites.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Отображение нахождения рецепта в избранном списке покупок."""
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and obj.shoppingcarts.filter(user=request.user).exists()
        )


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

    def validate(self, data):
        """Валидация присутствия полей ингредиента и тега."""
        request = self.context.get('request')
        if request and (
            request.method == 'PATCH' or request.method == 'POST'
        ):
            if 'ingredients' not in data:
                raise serializers.ValidationError(
                    'В запросе отсутствует поле ingredients'
                )
            if 'tags' not in data:
                raise serializers.ValidationError(
                    'В запросе отсутствует поле tags'
                )
            all_ingredients = data['ingredients']
            unique_ingredients = set(
                element['id'] for element in all_ingredients
            )
            if not all_ingredients:
                raise serializers.ValidationError(
                    'Необходимо добавить хотя бы один ингредиент'
                )
            if len(all_ingredients) != len(unique_ingredients):
                raise serializers.ValidationError(
                    'Ингредиенты повторяются'
                )
        return data

    def validate_tags(self, value):
        """Валидация наличия тегов в рецепте."""
        unique_tags = set(value)
        if not value:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один тег'
            )
        if len(value) != len(unique_tags):
            raise serializers.ValidationError(
                'Теги повторяются'
            )
        return value

    def validate_cooking_time(self, value):
        """Валидация времени приготовления."""
        if value < MIN_NUM:
            raise serializers.ValidationError(
                f'Время приготовления должно быть не менее {MIN_NUM} минуты'
            )
        return value

    def create_recipe_ingredient(self, ingredients, recipe):
        """Метод создания связки 'Рецепт-Ингредиент'."""
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                ingredient=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients
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
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.create_recipe_ingredient(ingredients, recipe)
        updated_instance = super().update(instance, validated_data)
        updated_instance.tags.set(tags)
        return updated_instance

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

        fields = UsersGETSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = ['email', 'username', 'first_name', 'last_name']

    def validate(self, data):
        """Валидация подписки."""
        author = self.context.get('author')
        request = self.context.get('request')
        is_subscribed = request.user.subscribe_user.filter(
            author=author
        ).exists()
        if request.method == 'POST':
            if request.user == author:
                raise serializers.ValidationError(
                    'Нельзя подписаться на себя'
                )
            if is_subscribed:
                raise serializers.ValidationError(
                    'Вы уже подписаны на пользователя'
                )
        if request.method == 'DELETE':
            if not is_subscribed:
                raise serializers.ValidationError(
                    'Вы уже отписаны от пользователя'
                )
        return data

    def create(self, validated_data):
        """Создание подписки."""
        return Subscribe.objects.create(**validated_data)

    def get_recipes(self, author):
        """Отображение рецептов автора."""
        request = self.context.get('request')
        recipes = author.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, author):
        """Получение количества рецептов у автора."""
        return author.recipes.count()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара."""

    avatar = Base64ImageField()

    class Meta:
        """Meta."""

        model = User
        fields = ['avatar']

    def update(self, instance, validated_data):
        """Update."""
        instance.avatar = validated_data.get('avatar',)
        instance.save()
        return instance


class ShoppingCartSerializer(ShortRecipeSerializer):
    """Добавление в список покупок."""

    class Meta(ShortRecipeSerializer.Meta):
        """Meta."""

        fields = ShortRecipeSerializer.Meta.fields

    def validate(self, data):
        """Наличие в списке покупок."""
        recipe = self.context.get('recipe')
        request = self.context.get('request')
        is_in_shopping_cart = request.user.shoppingcarts.filter(
            recipe=recipe
        ).exists()
        if is_in_shopping_cart and request.method == 'POST':
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок'
            )
        if not is_in_shopping_cart and request.method == 'DELETE':
            raise serializers.ValidationError(
                'Рецепт и так отсутствует в списке покупок'
            )
        return data

    def create(self, validated_data):
        """Добавление в список покупок."""
        return ShoppingCart.objects.create(**validated_data)

    def to_representation(self, instance):
        """Изменение ответа api."""
        request = self.context.get('request')
        recipe = self.context.get('recipe')
        image = request.build_absolute_uri(recipe.image.url)
        serializer_data = ShortRecipeSerializer(
            instance,
            context={'request': request},
        ).data
        modified_data = {
            **serializer_data,
            'image': image
        }
        return modified_data


class FavoriteSerializer(ShortRecipeSerializer):
    """Добавление в избранное."""

    class Meta(ShortRecipeSerializer.Meta):
        """Meta."""

        fields = ShortRecipeSerializer.Meta.fields

    def validate(self, data):
        """Наличие в избранном."""
        recipe = self.context.get('recipe')
        request = self.context.get('request')
        is_favorited = request.user.favorites.filter(recipe=recipe).exists()
        if is_favorited and request.method == 'POST':
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное'
            )
        if not is_favorited and request.method == 'DELETE':
            raise serializers.ValidationError(
                'Рецепт и так отсутствует в избранном'
            )
        return data

    def create(self, validated_data):
        """Добавление в избранное."""
        return Favorite.objects.create(**validated_data)

    def to_representation(self, instance):
        """Изменение ответа api."""
        request = self.context.get('request')
        recipe = self.context.get('recipe')
        image = request.build_absolute_uri(recipe.image.url)
        serializer_data = ShortRecipeSerializer(
            instance,
            context={'request': request},
        ).data
        modified_data = {
            **serializer_data,
            'image': image
        }
        return modified_data
