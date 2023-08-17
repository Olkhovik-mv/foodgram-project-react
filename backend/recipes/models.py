from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from recipes import constants as c

User = get_user_model()


class Tag(models.Model):
    """Модель таблицы теги."""
    name = models.CharField(max_length=c.TAG_NAME, verbose_name='Наименование')
    color = models.CharField(
        max_length=c.TAG_COLOR, verbose_name='Цвет',
        validators=(
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Значение поля должно содержать цветовой HEX-код!'
            ),
        )
    )
    slug = models.SlugField(
        max_length=c.TAG_SLUG, unique=True, null=True, verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Foodstuff(models.Model):
    """Модель таблицы продукты."""
    name = models.CharField(
        max_length=c.FOODSTUFF_NAME, db_index=True, verbose_name='Наименование'
    )
    measurement_unit = models.CharField(
        max_length=c.FOODSTUFF_UNIT, verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique_foodstuff'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель таблицы рецепты."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(max_length=c.RECIPE_NAME, verbose_name='Рецепт')
    text = models.TextField(verbose_name='Текст')
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(c.RECIPE_COOKING_TIME),),
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name='Дата публикации'
    )
    image = models.ImageField(
        upload_to='recipes/images/', verbose_name='Изображение'
    )
    tags = models.ManyToManyField(
        Tag, through='RecipeTag', related_name='recipes', verbose_name='Теги'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class UserInterface(models.Model):
    """Абстрактный класс для моделей Basket и Favorite."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='%(class)s'
            )
        ]

    def __str__(self):
        return f'пользователь:{self.user}, рецепт:{self.recipe}'


class Basket(UserInterface):
    """Модель таблицы корзина."""

    class Meta(UserInterface.Meta):
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'


class Favorite(UserInterface):
    """Модель таблицы избранное."""

    class Meta(UserInterface.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class Subscription(models.Model):
    """Модель таблицы подписки."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='signed', verbose_name='Пользователь')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscribers', verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            )
        ]

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Нельзя подписаться на себя!')

    def __str__(self):
        return f'пользователь:{self.user}, автор рецепта:{self.author}'


class Ingredient(models.Model):
    """Модель таблицы ингредиенты."""
    foodstuff = models.ForeignKey(
        Foodstuff, on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='ingredients', verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(c.INGREDIENT_AMOUNT),),
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['foodstuff', 'recipe'], name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'рецепт:{self.recipe}, продукт:{self.foodstuff}'


class RecipeTag(models.Model):
    """Модель таблицы рецепты-теги."""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE,
        verbose_name='Тег'
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'], name='unique_tag'
            )
        ]

    def __str__(self):
        return f'рецепт:{self.recipe}, тег:{self.tag}'
