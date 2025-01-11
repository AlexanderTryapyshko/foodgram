"""Константы."""
from django.conf import settings

DIRECTORY = f'{settings.BASE_DIR}/data/'

REGULAR = r'^[\w.@+-]+$'

STR_CONST = 25

USER_MAX_LENGHT = 150

EMAIL_MAX_LENGTH = 254

ING_TAG_NAME_MAX_LENGTH = 64

MAX_UNIT = 8

REC_NAME_MAX_LENGTH = 256

IMAGE_UPLOAD_DIRECTORY = 'recipes/images/'

SHORT_LINK_LENGTH = 10

MIN_NUM = 1

PAGE_SIZE = 6
