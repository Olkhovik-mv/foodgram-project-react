from django_filters import rest_framework as filters

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    """
    Фильтр представления RecipeViewSet.

    Возможна фильтрация по нескольким tags по условию ИЛИ.
    is_favorited вернет рецепты, находящиеся в избранном.
    is_in_shopping_cart - рецепты, находящиеся в списке покупок.
    Возможные значения: 1, True. При других значениях фильтр отключен.
    """
    author = filters.NumberFilter(field_name='author')
    tags = filters.CharFilter(method='filter_tags')
    is_favorited = filters.BooleanFilter(method='filter_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_shopping_cart')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs = kwargs

    def filter_tags(self, queryset, field, value):
        list_tags = dict(self.kwargs['data'])['tags']
        return queryset.filter(tags__slug__in=list_tags).distinct()

    def filter_favorited(self, queryset, field, value):
        is_favorited = self.kwargs['data']['is_favorited']
        if is_favorited == '1':
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_shopping_cart(self, queryset, field, value):
        is_in_shopping_cart = self.kwargs['data']['is_in_shopping_cart']
        if is_in_shopping_cart == '1':
            return queryset.filter(basket__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)
