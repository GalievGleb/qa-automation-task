"""Централизованная конфигурация тестов, зависящая от окружения.

Все значения, зависящие от окружения, собраны здесь, чтобы набор можно было
направить на любой деплой приложения, просто поменяв переменные окружения
(или локальный файл .env).

Порядок разрешения каждого значения:
    1. Реальная переменная окружения ОС (например, экспортированная в CI).
    2. Значение из локального файла .env (удобство разработчика, в .gitignore).
    3. Разумное значение по умолчанию (публичный демо-сайт).

Опция командной строки ``--base-url`` применяется поверх этого в фикстуре
``settings`` (см. ``conftest.py``) и имеет наивысший приоритет.
"""

import os
from dataclasses import dataclass
from typing import Final

from dotenv import load_dotenv

DEFAULT_BASE_URL: Final[str] = "https://the-internet.herokuapp.com"
DEFAULT_USERNAME: Final[str] = "tomsmith"
DEFAULT_PASSWORD: Final[str] = "SuperSecretPassword!"

# Подхватываем локальный .env, если он есть. Реальные переменные окружения
# всегда важнее (override=False), чтобы секреты CI не перезатирались файлом.
load_dotenv(override=False)


@dataclass(frozen=True)
class Settings:
    """Неизменяемый снимок конфигурации, используемой в прогоне тестов.

    Attributes:
        base_url: Корневой URL тестируемого приложения, без завершающего слэша.
        username: Валидное имя пользователя для защищённой зоны.
        password: Валидный пароль для защищённой зоны.
    """

    base_url: str
    username: str
    password: str

    def __post_init__(self) -> None:
        """Нормализует ``base_url``: инвариантом «без завершающего слэша» владеет Settings.

        Датакласс frozen, поэтому поле переписывается через ``object.__setattr__`` —
        штатный приём из документации dataclasses.
        """
        object.__setattr__(self, "base_url", self.base_url.rstrip("/"))


def get_settings() -> Settings:
    """Собирает снимок :class:`Settings` из текущего окружения.

    Returns:
        Settings, где каждое значение разрешено как: переменная окружения >
        файл ``.env`` > значение по умолчанию. Пустая строка в переменной
        считается «не задано» и тоже падает в значение по умолчанию.
    """
    return Settings(
        base_url=os.getenv("BASE_URL") or DEFAULT_BASE_URL,
        username=os.getenv("LOGIN_USERNAME") or DEFAULT_USERNAME,
        password=os.getenv("LOGIN_PASSWORD") or DEFAULT_PASSWORD,
    )
