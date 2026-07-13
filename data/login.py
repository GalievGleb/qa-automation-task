"""Плейсхолдеры и хелперы для сценариев логина.

Плейсхолдеры позволяют разрешать environment-dependent credentials уже во
время выполнения теста, когда доступна фикстура настроек.
"""

from enum import Enum

from config.settings import Settings


class Credential(Enum):
    """Типизированные плейсхолдеры учётных данных для параметризации.

    Параметризация вычисляется на этапе сбора тестов, когда фикстуры (а значит
    и учётные данные из окружения) ещё недоступны. Поэтому кейсы ссылаются на
    значения через плейсхолдеры, а :func:`resolve_credentials` разрешает их уже
    во время выполнения теста. Enum вместо строковых шаблонов — чтобы опечатку
    ловил mypy, а тестовые строки могли содержать любые символы.
    """

    VALID_USERNAME = "valid username"
    VALID_PASSWORD = "valid password"
    INVALID_USERNAME = "invalid username"
    INVALID_PASSWORD = "invalid password"


def make_invalid_credential(value: str) -> str:
    """Создаёт детерминированное значение, гарантированно отличное от исходного."""
    return f"{value}__invalid"


def resolve_credentials(value: str | Credential, settings: Settings) -> str:
    """Разрешает значение кейса в конкретную строку для формы логина.

    Args:
        value: Либо готовая строка (вводится как есть, например пустая), либо
            плейсхолдер :class:`Credential`, разрешаемый из настроек окружения.
        settings: Разрешённая конфигурация прогона с валидными учётными данными.

    Returns:
        Строка, готовая для ввода в форму логина; «невалидные» значения
        детерминированно выводятся из валидных и гарантированно отличаются
        от них.
    """
    if isinstance(value, str):
        return value
    resolved: dict[Credential, str] = {
        Credential.VALID_USERNAME: settings.username,
        Credential.VALID_PASSWORD: settings.password,
        Credential.INVALID_USERNAME: make_invalid_credential(settings.username),
        Credential.INVALID_PASSWORD: make_invalid_credential(settings.password),
    }
    return resolved[value]
