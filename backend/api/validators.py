"""Валидаторы проекта foodgram."""
from django.core.exceptions import ValidationError

from api.constants import BAD_USERNAME, MIN_NUM


def validate_cooking_time(value):
    """
    Валидатор времени приготовления.

    Проверяет, чтобы указанное время приготовления было не менее 1 минуты.
    """
    if value < MIN_NUM:
        raise ValidationError(
            f'{value} не может быть меньше {MIN_NUM} минуты'
        )


def validate_username(value):
    """Валидация имени."""
    if value == BAD_USERNAME:
        raise ValidationError(
            f'Поле "username" не может быть равно {BAD_USERNAME}'
        )
