"""Валидаторы проекта foodgram."""
from django.core.exceptions import ValidationError


def validate_cooking_time(value):
    """
    Валидатор времени приготовления.

    Проверяет, чтобы указанное время приготовления было не менее 1 минуты.
    """
    if value < 1:
        raise ValidationError(f'{value} не может быть меньше 1 минуты')
