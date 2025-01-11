"""Management команда импорта csv."""
import csv

from django.core.management.base import BaseCommand

from api.constants import DIRECTORY
from recipes.models import Ingredient

TABLES = {Ingredient: 'ingredients.csv'}


class Command(BaseCommand):
    """Класс импорта данных из csv."""

    def handle(self, *args, **kwargs):
        """handle."""
        for model, file in TABLES.items():
            with open(
                f'{DIRECTORY}{file}',
                'r',
                encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                model.objects.bulk_create(model(**data) for data in reader)
        self.stdout.write(self.style.SUCCESS('Данные успешно загружены'))
