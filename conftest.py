"""Общие pytest-фикстуры и хуки, связывающие конфигурацию и page object'ы."""

import contextlib
import logging
from collections.abc import Generator, Iterator
from dataclasses import replace

import allure
import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, expect

from config.settings import Settings, get_settings
from pages.login_page import LoginPage
from pages.main_page import MainPage
from pages.secure_page import SecurePage

logger = logging.getLogger(__name__)

# Публичный демо-сайт бывает медленным на «холодном» старте; даём web-first
# проверкам чуть больше времени, чем стандартные 5 секунд. Тайм-ауты действий
# и навигации оставлены дефолтными (30 с) сознательно — как запас на редкие
# зависания демо-сайта.
expect.set_options(timeout=10_000)


@pytest.fixture(scope="session")
def settings(pytestconfig: pytest.Config) -> Settings:
    """Разрешает конфигурацию на весь прогон тестов.

    Приоритет base URL: опция ``--base-url`` > переменная ``BASE_URL``
    (или файл ``.env``) > значение по умолчанию.

    Args:
        pytestconfig: Встроенная фикстура pytest с доступом к опциям CLI
            (``--base-url`` регистрирует плагин ``pytest-base-url``).

    Returns:
        Неизменяемые настройки, общие для всех тестов сессии.
    """
    resolved = get_settings()
    cli_base_url: str | None = pytestconfig.getoption("--base-url")
    if cli_base_url:
        resolved = replace(resolved, base_url=cli_base_url)
    logger.info("Base URL под тестом: %s", resolved.base_url)
    return resolved


@pytest.fixture(scope="session")
def base_url(settings: Settings) -> str:
    """Переопределяет одноимённую фикстуру ``pytest-base-url``.

    pytest-playwright передаёт это значение в каждый контекст браузера, поэтому
    относительные переходы и page object'ы всегда согласованы по целевому деплою.

    Returns:
        Полностью разрешённый base URL.
    """
    return settings.base_url


@pytest.fixture
def main_page(page: Page, settings: Settings) -> MainPage:
    """Page object главной страницы, привязанный к странице браузера теста."""
    return MainPage(page, settings.base_url)


@pytest.fixture
def login_page(page: Page, settings: Settings) -> LoginPage:
    """Page object страницы логина, привязанный к странице браузера теста."""
    return LoginPage(page, settings.base_url)


@pytest.fixture
def secure_page(page: Page, settings: Settings) -> SecurePage:
    """Page object защищённой зоны, привязанный к странице браузера теста."""
    return SecurePage(page, settings.base_url)


@pytest.fixture(autouse=True)
def no_credentials_in_logs(settings: Settings, caplog: pytest.LogCaptureFixture) -> Iterator[None]:
    """Страж: валидные учётные данные не должны попадать в логи ни одного теста.

    Проверяется после каждого теста (autouse) — в том числе в позитивном
    сценарии логина, единственном месте, где через форму проходят настоящие
    значения.
    """
    caplog.set_level(logging.INFO)
    yield
    assert settings.username not in caplog.text, (
        f"Имя пользователя {settings.username!r} попало в логи: {caplog.text!r}"
    )
    assert settings.password not in caplog.text, (
        f"Пароль {settings.password!r} попал в логи: {caplog.text!r}"
    )


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    """Прикладывает скриншот страницы к Allure-отчёту при падении теста.

    pytest-playwright сохраняет скриншот падения в test-results/, но в
    Allure-отчёт (основной отчёт проекта) сам он не попадает — прикладываем
    вручную, чтобы падение разбиралось по одному отчёту.
    """
    report = yield
    if report.when == "call" and report.failed:
        page = getattr(item, "funcargs", {}).get("page")
        if isinstance(page, Page):
            # Страница могла уже закрыться — скриншот не важнее исходной ошибки.
            with contextlib.suppress(PlaywrightError):
                allure.attach(
                    page.screenshot(full_page=True),
                    name="screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
    return report
