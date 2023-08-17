from rest_framework.pagination import PageNumberPagination

PAGE_SIZE = 6


class PageLimitPagination(PageNumberPagination):
    """
    Паджинатор.

    limit - параметр запроса, устанавливает количество объектов
    для отображения на одной странице, по умолчанию page_size
    """
    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
