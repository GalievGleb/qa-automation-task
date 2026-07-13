"""Сценарий 3 — Вход на сайт с валидными данными и последующий выход."""

import allure
import pytest
from playwright.sync_api import expect

from config.settings import Settings
from locators.common_locators import CommonTexts
from locators.login_page_locators import LoginPageTexts
from locators.secure_page_locators import SecurePageTexts
from pages.login_page import LoginPage
from pages.secure_page import SecurePage


@pytest.mark.smoke
@pytest.mark.login
class TestLoginLogout:
    """Сценарий 3: полный цикл логин/логаут с валидными данными."""

    def test_user_can_login_and_logout(
        self,
        login_page: LoginPage,
        secure_page: SecurePage,
        settings: Settings,
    ) -> None:
        with allure.step("Входим с валидными учётными данными"):
            login_page.open()
            login_page.login(settings.username, settings.password)

        with allure.step("Проверяем, что попали в защищённую зону"):
            expect(secure_page.page, "После логина не оказались на /secure").to_have_url(
                secure_page.url
            )
            expect(secure_page.page, "Неверный заголовок документа /secure").to_have_title(
                CommonTexts.TITLE
            )
            expect(secure_page.message_flash, "Нет сообщения об успешном входе").to_contain_text(
                SecurePageTexts.LOGIN_SUCCESS
            )
            expect(
                secure_page.heading_secure_area, "Неверный заголовок защищённой зоны"
            ).to_have_text(SecurePageTexts.HEADING)
            expect(
                secure_page.text_secure_subheader, "Нет приветствия в защищённой зоне"
            ).to_contain_text(SecurePageTexts.SUBHEADER)

        with allure.step("Проверяем наличие ссылки Logout"):
            expect(secure_page.link_logout, "Не видно ссылки Logout").to_be_visible()

        with allure.step("Выходим из системы"):
            login_page_after_logout = secure_page.logout()

        with allure.step("Проверяем, что вышли: снова на /login с подтверждением"):
            expect(
                login_page_after_logout.page,
                "После логаута не вернулись на /login",
            ).to_have_url(login_page_after_logout.url)
            expect(
                login_page_after_logout.message_flash, "Нет подтверждения выхода"
            ).to_contain_text(LoginPageTexts.LOGOUT_SUCCESS)

        with allure.step("Убеждаемся, что защищённая зона снова закрыта"):
            secure_page.open()
            expect(
                login_page_after_logout.page,
                "Защищённая зона доступна после выхода",
            ).to_have_url(login_page_after_logout.url)
            expect(
                login_page_after_logout.message_flash,
                "Нет сообщения о необходимости логина",
            ).to_contain_text(LoginPageTexts.LOGIN_REQUIRED)
