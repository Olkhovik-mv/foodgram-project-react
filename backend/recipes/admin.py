from django.contrib import admin
from django.db.models import Count

from .models import (Basket, Favorite, Foodstuff, Ingredient, Recipe,
                     RecipeTag, Subscription, Tag)


class RecipeAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели Recipe в админке.

    - trim_text - обрезка поля text.
    - favorite_count - подсчет количества добавлений рецепта в избранное
    - get_tags - возвращает список связанных с рецептом тегов
    """
    list_display = (
        'id', 'author', 'name', 'trim_text', 'cooking_time',
        'pub_date', 'image', 'get_tags',
    )
    readonly_fields = ('favorite_count',)
    search_fields = ('author__username', 'name',)
    list_filter = ('author__username', 'name', 'tags', 'pub_date',)

    def trim_text(self, obj):
        return f'{obj.text[:50]}'

    def favorite_count(self, obj):
        return obj.favorite.aggregate(Count('user'))['user__count']

    def get_tags(self, obj):
        return ', '.join([str(tag) for tag in obj.tags.all()])

    trim_text.short_description = 'Описание'
    favorite_count.short_description = 'Добавлено в избранное'
    get_tags.short_description = 'Теги'


class TagAdmin(admin.ModelAdmin):
    """Настройки отображения модели Tag в админке."""
    list_display = ('id', 'name', 'color', 'slug')


class FoodstuffAdmin(admin.ModelAdmin):
    """Настройки отображения модели Foodstuff в админке."""
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)


class BasketAdmin(admin.ModelAdmin):
    """Настройки отображения модели Basket в админке."""
    list_display = ('id', 'user', 'recipe')


class FavoriteAdmin(admin.ModelAdmin):
    """Настройки отображения модели Favorite в админке."""
    list_display = ('id', 'user', 'recipe')


class SubscriptionAdmin(admin.ModelAdmin):
    """Настройки отображения модели Subscription в админке."""
    list_display = ('id', 'user', 'author')


class IngredientAdmin(admin.ModelAdmin):
    """Настройки отображения модели Ingredient в админке."""
    list_display = ('id', 'foodstuff', 'recipe', 'amount')


class RecipeTagAdmin(admin.ModelAdmin):
    """Настройки отображения модели RecipeTag в админке."""
    list_display = ('id', 'recipe', 'tag')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Foodstuff, FoodstuffAdmin)
admin.site.register(Basket, BasketAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
