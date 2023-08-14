from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользовательская модель пользователя."""
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(
        max_length=254,
        unique=True,
        error_messages={
            'unique': 'Пользователь с такой почтой уже существует.',
        },
    )
