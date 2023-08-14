from rest_framework import routers

from api.views import FoodstuffViewSet, RecipeViewSet, TagViewSet, UserViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', FoodstuffViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')

urlpatterns = router.urls
