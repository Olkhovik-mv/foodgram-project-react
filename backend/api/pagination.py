from rest_framework.pagination import PageNumberPagination

from api import constants as c


class PageLimitPagination(PageNumberPagination):
    """
    Паджинатор.

    limit - параметр запроса, устанавливает количество объектов
    для отображения на одной странице, по умолчанию page_size
    """
    page_size = c.PAGE_SIZE
    page_size_query_param = 'limit'
