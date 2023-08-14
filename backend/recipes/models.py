from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель таблицы теги."""
    name = models.CharField(max_length=200, verbose_name='Наименование')
    color = models.CharField(max_length=7, null=True, verbose_name='Цвет')
    slug = models.SlugField(
        max_length=200, unique=True, null=True, verbose_name='Слаг'
    )

    def __str__(self):
        return self.name


class Foodstuff(models.Model):
    """Модель таблицы продукты."""
    name = models.CharField(
        max_length=200, db_index=True, verbose_name='Наименование'
    )
    measurement_unit = models.CharField(
        max_length=200, verbose_name='Единица измерения'
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель таблицы рецепты."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(max_length=200, verbose_name='Рецепт')
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),),
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
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class Basket(models.Model):
    """Модель таблицы список покупок."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='basket',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='basket', verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_basket'
            )
        ]


class Favorite(models.Model):
    """Модель таблицы избранное."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorite', verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorite', verbose_name='Рецепт')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]


class Subscription(models.Model):
    """Модель таблицы подписки."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='signed', verbose_name='Пользователь')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscribers', verbose_name='Автор')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            )
        ]


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
        validators=(MinValueValidator(1),), verbose_name='Количество'
    )


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
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'], name='unique_tag'
            )
        ]
