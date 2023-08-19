from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Настройки отображения модели User в админке."""
    list_filter = ('email', 'username', 'is_staff')
    add_fieldsets = (
        (None, {
            'fields': (
                'username', 'password1', 'password2',
                'email', 'first_name', 'last_name'
            ),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            disabled_fields = (
                'is_staff', 'is_superuser', 'user_permissions', 'groups',
            )
            for field in disabled_fields:
                if field in form.base_fields:
                    form.base_fields[field].disabled = True
        return form
