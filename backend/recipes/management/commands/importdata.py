import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Foodstuff


class Command(BaseCommand):
    """Импортирует записи ингредиентов в базу данных."""

    def handle(self, *args, **kwargs):
        FILE_NAME = 'ingredients.csv'
        with open(
            Path(Path.cwd().resolve(), 'data', FILE_NAME),
            newline='\r\n',
            encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            self.stdout.write(f'Импорт данных из файла {FILE_NAME}:')
            self.stdout.write('-' * 60)
            # счетчики
            success = 0
            errors = 0
            for row in reader:
                try:
                    success += Foodstuff.objects.get_or_create(**row)[1]
                except Exception as e:
                    self.stdout.write(f'Ошибка импорта: {e}')
                    errors += 1
            self.stdout.write(
                f'Из файла {FILE_NAME} импортировано записей: {success}, '
                f'ошибок импорта: {errors} \n\n'
            )
