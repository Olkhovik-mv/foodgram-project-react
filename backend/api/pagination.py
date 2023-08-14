from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """
    Паджинатор.

    limit - параметр запроса, устанавливает количество объектов
    для отображения на одной странице, по умолчанию page_size
    """
    page_size = 6
    page_size_query_param = 'limit'
