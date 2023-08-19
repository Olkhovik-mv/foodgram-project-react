from django import forms
from django.contrib import admin
from django.db.models import Count

from recipes import constants as c
from recipes.models import (Basket, Favorite, Foodstuff, Ingredient, Recipe,
                            RecipeTag, Subscription, Tag)


class IngredientFormSet(forms.models.BaseInlineFormSet):
    """Набор встроенных форм ингредиент."""
    def clean(self):
        for form in self.forms:
            data = form.cleaned_data
            if 'foodstuff' in data and not data['DELETE']:
                return super().clean()
        raise forms.ValidationError('Добавьте в рецепт ингредиенты!')


class TagFormSet(forms.models.BaseInlineFormSet):
    """Набор встроенных форм тег."""
    def clean(self):
        for form in self.forms:
            data = form.cleaned_data
            if 'tag' in data and not data['DELETE']:
                return super().clean()
        raise forms.ValidationError('Добавьте в рецепт теги!')


class IngredientInline(admin.TabularInline):
    """Встроенная табличная форма ингредиент."""
    model = Ingredient
    formset = IngredientFormSet
    extra = 1


class TagInline(admin.TabularInline):
    """Встроенная табличная форма тег."""
    model = RecipeTag
    formset = TagFormSet
    extra = 1


@admin.register(Recipe)
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
    inlines = (IngredientInline, TagInline)

    def trim_text(self, obj):
        return f'{obj.text[:c.TRIM_TEXT_FIELD]}'

    def favorite_count(self, obj):
        return obj.favorite_set.aggregate(Count('user'))['user__count']

    def get_tags(self, obj):
        return ', '.join([str(tag) for tag in obj.tags.all()])

    trim_text.short_description = 'Описание'
    favorite_count.short_description = 'Добавлено в избранное'
    get_tags.short_description = 'Теги'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки отображения модели Tag в админке."""
    list_display = ('id', 'name', 'color', 'slug')


@admin.register(Foodstuff)
class FoodstuffAdmin(admin.ModelAdmin):
    """Настройки отображения модели Foodstuff в админке."""
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    """Настройки отображения модели Basket в админке."""
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настройки отображения модели Favorite в админке."""
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настройки отображения модели Subscription в админке."""
    list_display = ('id', 'user', 'author')
    search_fields = ('user__username',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки отображения модели Ingredient в админке."""
    list_display = ('id', 'recipe', 'foodstuff', 'amount')
    search_fields = ('recipe__name',)


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    """Настройки отображения модели RecipeTag в админке."""
    list_display = ('id', 'recipe', 'tag')
