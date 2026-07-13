"""Базовый класс с поведением, общим для всех page object'ов."""

import logging
from typing import Self

from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class BasePage:
    """Общая инфраструктура страниц: page, base URL и открытие страницы по её URL.

    Каждая конкретная страница задаёт свой ``path``; абсолютный URL собирается
    относительно зависящего от окружения ``base_url``, который прокидывают
    фикстуры, — поэтому одни и те же page object'ы работают против любого
    деплоя приложения.

    Attributes:
        page: Playwright-страница, управляющая вкладкой браузера.
        base_url: Корневой URL тестируемого приложения (без завершающего слэша).
    """

    # Относительный путь страницы; переопределяется в каждом наследнике.
    path = "/"

    def __init__(self, page: Page, base_url: str) -> None:
        """Привязывает page object к вкладке браузера и целевому окружению.

        Args:
            page: Playwright-страница, с которой работают все локаторы и действия.
            base_url: Корневой URL тестируемого приложения без завершающего
                слэша (нормализацией владеет ``config.settings.Settings``).
        """
        self.page = page
        self.base_url = base_url

    @property
    def url(self) -> str:
        """Абсолютный URL страницы — для навигации и проверок адреса.

        Returns:
            ``base_url``, склеенный с относительным ``path`` страницы.
        """
        return f"{self.base_url}{self.path}"

    def open(self) -> Self:
        """Переходит на страницу по её URL.

        ``wait_until="commit"`` сознательно не ждёт события ``load``: демо-сайт
        периодически «зависает» на отдаче тяжёлого статического ресурса, из-за
        чего навигация повисла бы. Все проверки в наборе полагаются на
        авто-ожидающие assert'ы Playwright, а не на событие ``load``.

        Returns:
            Тот же page object — чтобы можно было чейнить вызовы.

        Raises:
            RuntimeError: Если сервер ответил ошибкой (не-2xx/3xx статусом).
        """
        logger.info("Открываю страницу: %s", self.url)
        response = self.page.goto(self.url, wait_until="commit")
        # goto не падает на HTTP 5xx: без этой проверки ошибка сервера (например,
        # 502 от "холодного" Heroku) проявилась бы невнятным таймаутом первого
        # expect в тесте вместо мгновенной и ясной инфраструктурной ошибки.
        if response is not None and not response.ok:
            raise RuntimeError(
                f"Сайт ответил {response.status} {response.status_text} на {self.url}"
            )
        return self
