from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User


class UserAdmin(BaseUserAdmin):
    """Настройки отображения модели User в админке."""
    list_display = ('id', 'username', 'email', 'is_staff')
    list_filter = ('email', 'username', 'is_staff')


admin.site.register(User, UserAdmin)
