"""Утилиты для определения хостов и состояния дебага."""
import os


def get_debug():
    """Получение состояния дебага."""
    return os.getenv('DEBUG', 'True').lower() == 'true'


def get_allowed_hosts():
    """Получение доступных хостов."""
    allowed_hosts = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1')
    return [host.strip() for host in allowed_hosts.split(',')]
