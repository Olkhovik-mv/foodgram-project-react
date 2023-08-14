from rest_framework import exceptions, viewsets


class ExcludePutViewSet(viewsets.ModelViewSet):
    """Вьюсет без метода PUT."""

    def update(self, request, *args, **kwargs):
        if self.request.method == 'PUT':
            raise exceptions.MethodNotAllowed(method='PUT')
        return super().update(request, *args, **kwargs)
