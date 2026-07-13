"""Сценарий 2 — Страница логина.

Переход на страницу логина с главной по ссылке 'Form Authentication'
проверяется отдельным тестом; вход с любыми невалидными учётными данными
должен быть невозможен.
"""

import allure
import pytest
from playwright.sync_api import expect

from config.settings import Settings
from data.login import Credential, resolve_credentials
from locators.login_page_locators import LoginPageTexts
from pages.login_page import LoginPage
from pages.main_page import MainPage
from pages.secure_page import SecurePage


@pytest.mark.smoke
@pytest.mark.login
class TestLoginPageNavigation:
    """Сценарий 2 (точка входа): переход на страницу логина с главной."""

    def test_login_page_opens_from_main_page(self, main_page: MainPage) -> None:
        with allure.step("Открываем главную страницу"):
            main_page.open()

        with allure.step("Кликаем по ссылке 'Form Authentication'"):
            login_page = main_page.go_to_login_page()

        with allure.step("Проверяем, что открылась страница логина"):
            expect(login_page.page, "Переход не привёл на страницу /login").to_have_url(
                login_page.url
            )
            expect(
                login_page.heading_login, "На странице логина нет ожидаемого заголовка"
            ).to_have_text(LoginPageTexts.HEADING)


@pytest.mark.login
@pytest.mark.negative
class TestLoginWithInvalidCredentials:
    """Сценарий 2: вход с невалидными данными невозможен."""

    @pytest.mark.parametrize(
        ("username", "password", "expected_error"),
        [
            pytest.param(
                Credential.VALID_USERNAME,
                Credential.INVALID_PASSWORD,
                LoginPageTexts.PASSWORD_INVALID,
                id="valid-username-invalid-password",
            ),
            pytest.param(
                Credential.INVALID_USERNAME,
                Credential.VALID_PASSWORD,
                LoginPageTexts.USERNAME_INVALID,
                id="invalid-username-valid-password",
            ),
            pytest.param(
                Credential.INVALID_USERNAME,
                Credential.INVALID_PASSWORD,
                LoginPageTexts.USERNAME_INVALID,
                id="invalid-username-and-password",
            ),
            pytest.param(
                "",
                Credential.VALID_PASSWORD,
                LoginPageTexts.USERNAME_INVALID,
                id="empty-username",
            ),
            pytest.param(
                Credential.VALID_USERNAME,
                "",
                LoginPageTexts.PASSWORD_INVALID,
                id="empty-password",
            ),
            pytest.param(
                "",
                "",
                LoginPageTexts.USERNAME_INVALID,
                id="empty-credentials",
            ),
        ],
    )
    def test_cannot_login_with_invalid_credentials(
        self,
        login_page: LoginPage,
        settings: Settings,
        username: str | Credential,
        password: str | Credential,
        expected_error: str,
    ) -> None:
        with allure.step("Открываем страницу логина"):
            login_page.open()

        with allure.step("Отправляем форму с невалидными учётными данными"):
            login_page.login(
                resolve_credentials(username, settings),
                resolve_credentials(password, settings),
            )

        with allure.step("Проверяем сообщение об ошибке и что остались на /login"):
            expect(
                login_page.message_flash, "Не показано flash-сообщение об ошибке"
            ).to_be_visible()
            expect(
                login_page.message_flash,
                f"Во flash нет ожидаемого текста: {expected_error!r}",
            ).to_contain_text(expected_error)
            expect(
                login_page.message_flash, "У flash-сообщения нет класса 'error'"
            ).to_contain_class("error")
            expect(
                login_page.page,
                "После неудачного логина пользователь ушёл со страницы /login",
            ).to_have_url(login_page.url)

    def test_secure_area_is_not_accessible_without_login(
        self, secure_page: SecurePage, login_page: LoginPage
    ) -> None:
        """Прямой обход формы тоже не должен давать доступ."""
        with allure.step("Пробуем открыть /secure напрямую, без логина"):
            secure_page.open()

        with allure.step("Проверяем редирект на /login и сообщение о входе"):
            expect(login_page.page, "Прямой заход на /secure не привёл на /login").to_have_url(
                login_page.url
            )
            expect(
                login_page.message_flash, "Нет сообщения о необходимости логина"
            ).to_contain_text(LoginPageTexts.LOGIN_REQUIRED)
