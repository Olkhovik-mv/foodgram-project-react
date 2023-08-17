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
