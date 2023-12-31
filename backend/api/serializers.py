import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers, validators

from recipes.models import (Basket, Favorite, Foodstuff, Ingredient, Recipe,
                            Subscription, Tag)

User = get_user_model()


class RecipesMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe с ограниченным набором полей."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(BaseUserSerializer):
    """Сериализатор модели User.

    Наследует djoser класс UserSerializer, добавляя метод is_subscribed.
    Метод проверяет, подписан ли текущий пользователь на объект, переданный
    в сериализатор.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return self.context.get('request').user.id in (
            subscriber.user_id for subscriber in obj.subscribers.all()
        )


class UserSubscriptionSerializer(UserSerializer):
    """
    Сериализатор модели User.

    Наследует пользовательский UserSerializer, добавляя связанные с объектом
    рецепты и их общее количество. Ограничивает количество рецептов на каждый
    объект в случае передачи в запрос фильтра 'recipes_limit'
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get('recipes_limit')
        if limit is not None:
            try:
                limit = int(limit)
                limit = limit if limit >= 0 else None
            except ValueError:
                limit = None
        return RecipesMinifiedSerializer(
            obj.recipes.all()[:limit], context=self.context, many=True
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Сериализатор модели User.

    Наследует djoser сериализатор UserCreateSerializer,
    переопределяя обязательные поля при регистрации пользователя.
    """
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')
        read_only_fields = ('id',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tags."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class FoodstuffSerializer(serializers.ModelSerializer):
    """Сериализатор модели Foodstuff."""

    class Meta:
        model = Foodstuff
        fields = ('id', 'name', 'measurement_unit')


class IngregientSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Ingredient.

    Выводит данные об ингредиентах из связанных таблиц
    Ingredient - Foodstuff
    """
    id = serializers.ReadOnlyField(source='foodstuff.id')
    name = serializers.ReadOnlyField(source='foodstuff.name')
    measurement_unit = serializers.ReadOnlyField(
        source='foodstuff.measurement_unit'
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class IngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient."""
    id = serializers.PrimaryKeyRelatedField(
        source='foodstuff', queryset=Foodstuff.objects.all()
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Recipe.

    Выводит данные о рецептах, а также данные из связанных с рецептом таблиц.
    """
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngregientSerializer(read_only=True, many=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time',)


class Base64ImageField(serializers.ImageField):
    """Преобразует текстовые данные в файл изображения."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            _, ext = format.split('/')
            data = ContentFile(
                base64.b64decode(imgstr), name='temp.' + ext
            )
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Recipe.

    Сохраняет и обновляет данные рецепта и связанных с рецептом тегов и
    ингредиентов.
    Возвращает данные используя сериализатор RecipeReadOnlySerializer.
    """
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True, allow_empty=False
    )
    ingredients = IngredientCreateSerializer(many=True, allow_empty=False)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name',
                  'text', 'cooking_time', 'author')

    def validate_tags(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'В рецепте есть одинаковые теги!'
            )
        return value

    def validate_ingredients(self, value):
        if len(value) != len({obj['foodstuff'] for obj in value}):
            raise serializers.ValidationError(
                'В рецепте есть одинаковые ингредиенты!'
            )
        try:
            [(obj['foodstuff'], obj['amount']) for obj in value]
        except KeyError as e:
            raise (f'{e} - обязательное поле')
        return value

    def save_ingredients(self, data, recipe, is_update=False):
        ingredients = []
        if is_update:
            ingredients = recipe.ingredients.all()
        objs_mapping = {obj.foodstuff: obj for obj in ingredients}
        data_mapping = {item['foodstuff']: item for item in data}
        objs_create, objs_update = [], []
        for obj_id, item in data_mapping.items():
            obj = objs_mapping.pop(obj_id, None)
            if obj is None:
                objs_create.append(Ingredient(recipe=recipe, **item))
            else:
                if obj.amount != item['amount']:
                    obj.amount = item['amount']
                    objs_update.append(obj)
        if objs_create:
            Ingredient.objects.bulk_create(objs_create)
        if objs_update:
            Ingredient.objects.bulk_update(objs_update, ['amount'])
        if objs_mapping:
            Ingredient.objects.filter(
                recipe=recipe, foodstuff__in=objs_mapping.keys()
            ).delete()

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.save_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.get('ingredients')
        if ingredients is not None:
            self.save_ingredients(ingredients, instance, is_update=True)
        tags = validated_data.get('tags')
        if tags is not None:
            instance.tags.set(tags)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        return (RecipeReadOnlySerializer(context=self.context).
                to_representation(instance))


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Subscription.

    Добавляет или удаляет подписки текущего пользователя на автора рецепта.
    При добавлении подписки возвращает данные об авторе через сериализатор
    UserSubscriptionSerializer.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Subscription
        fields = ('user', 'author',)

        validators = [
            validators.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого автора!'
            )
        ]

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя!'
            )
        return data

    def to_representation(self, instance):
        instance = self.validated_data['author']
        return (UserSubscriptionSerializer(context=self.context).
                to_representation(instance))


class BasketSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Basket.

    Добавляет или удаляет рецепт в корзину текущего пользователя.
    При добавлении возвращает данные о рецепте через сериализатор
    RecipesMinifiedSerializer.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Basket
        fields = ('recipe', 'user',)

        validators = [
            validators.UniqueTogetherValidator(
                queryset=Basket.objects.all(),
                fields=('recipe', 'user'),
                message='Этот рецепт уже есть в корзине!'
            )
        ]

    def to_representation(self, instance):
        instance = self.validated_data['recipe']
        return RecipesMinifiedSerializer().to_representation(instance)


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Favorite.

    Добавляет или удаляет рецепт в избранное текущего пользователя.
    При добавлении возвращает данные о рецепте через сериализатор
    RecipesMinifiedSerializer.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже добавлен в избранное!'
            )
        ]

    def to_representation(self, instance):
        instance = self.validated_data['recipe']
        return RecipesMinifiedSerializer().to_representation(instance)
