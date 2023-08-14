from rest_framework import permissions


class AuthorAdminOrReadOnly(permissions.BasePermission):
    """
    Определяет права доступа.

    Использование класса предполагает наличие в модели поля 'author'
    (экземпляр класса User)
    При подключении класса в представлении доступ предоставляется:
    Безопасные методы - всем пользователям
    POST метод - аутентифицированным пользователям
    Остальные методы - пользователю, создавшему объект или администратору
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        print(obj.author)
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author or request.user.is_staff
        )
