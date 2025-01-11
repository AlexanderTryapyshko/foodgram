"""Валидаторы проекта foodgram."""
from django.core.exceptions import ValidationError

from api.constants import MIN_NUM


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
    if value.lower() == 'me':
        raise ValidationError('Поле "username" не может быть равно "me"')
