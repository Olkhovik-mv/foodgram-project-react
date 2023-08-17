from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.mixins import ExcludePutViewSet
from api.pagination import PageLimitPagination
from api.permissions import AuthorAdminOrReadOnly
from api.scripts import create_shopping_cart
from api.serializers import (BasketSerializer, FavoriteSerializer,
                             FoodstuffSerializer, RecipeSerializer,
                             SubscriptionSerializer, TagSerializer,
                             UserSubscriptionSerializer)
from recipes.models import (Basket, Favorite, Foodstuff, Recipe, Subscription,
                            Tag)

User = get_user_model()


class UserViewSet(views.UserViewSet):
    """
    Представление обрабатывает ендпоинт 'users'.

    Наследует djoser UserViewSet. Добавлены actions:
    - subscriptions - возвращает подписки текущего пользователя
    - subscribe - добавление и удаление подписок
    """
    queryset = User.objects.prefetch_related('subscribers').all()
    pagination_class = PageLimitPagination

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'subscriptions':
            return UserSubscriptionSerializer
        if self.action == 'subscribe':
            return SubscriptionSerializer
        return super().get_serializer_class(*args, **kwargs)

    @action(detail=False)
    def subscriptions(self, request):
        queryset = (
            User.objects.all().prefetch_related('subscribers', 'recipes').
            filter(subscribers__user=request.user.id)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, id):
        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscription, author=id, user=self.request.user.id
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(data={'author': id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление обрабатывает ендпоинт 'tags'."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class FoodstuffViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление обрабатывает эндпоинт 'ingredients'."""
    queryset = Foodstuff.objects.all()
    serializer_class = FoodstuffSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class RecipeViewSet(ExcludePutViewSet):
    """
    Представление обрабатывает ендпоинт 'recipes'.

    actions:
    - shopping_cart - добавляет или удаляет рецепт из списка покупок.
    - favorite - добавляет или удаляет рецепт из избранного.
    - download_shopping_cart - отправляет пользователю файл Ingredients.txt
        со списком ингредиентов.
    """
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageLimitPagination
    permission_classes = (AuthorAdminOrReadOnly,)

    def get_queryset(self):
        current_user = self.request.user
        if not isinstance(current_user, User):
            current_user = None
        favorites = Favorite.objects.filter(
            user=current_user, recipe=OuterRef('pk')
        )
        shoppings = Basket.objects.filter(
            user=current_user, recipe=OuterRef('pk')
        )
        return (
            Recipe.objects.select_related('author').prefetch_related(
                'tags', 'ingredients__foodstuff', 'author__subscribers'
            ).annotate(is_favorited=Exists(favorites),
                       is_in_shopping_cart=Exists(shoppings))
        )

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'shopping_cart':
            return BasketSerializer
        if self.action == 'favorite':
            return FavoriteSerializer
        return super().get_serializer_class(*args, **kwargs)

    def actions(self, model, request, pk):
        if request.method == 'DELETE':
            record = get_object_or_404(model, recipe=pk, user=request.user.id)
            record.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(data={'recipe': pk})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        return self.actions(Basket, request, pk)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        return self.actions(Favorite, request, pk)

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        file = create_shopping_cart(request)
        response = HttpResponse(file, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="Ingredients.txt"'
        )
        return response
