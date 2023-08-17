from django.db.models import Sum

from recipes.models import Ingredient


def create_shopping_cart(request):
    """Создает результирующий список ингредиентов."""
    query = (
        Ingredient.objects.filter(recipe__basket__user=request.user).
        values('foodstuff__name', 'foodstuff__measurement_unit').
        annotate(amount=Sum('amount')).order_by()
    )
    file = 'Список продуктов: \r\n' + '-' * 40 + '\r\n'
    for obj in query:
        line = '- {0} ({1}) - {2}'.format(*obj.values())
        file += line + '\r\n'
    return file
