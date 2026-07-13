"""Page object страницы аутентификации (Form Authentication / login)."""

import logging

from playwright.sync_api import Page

from locators.common_locators import CommonLocators
from locators.login_page_locators import LoginPageLocators
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """Страница логина: поля ввода, кнопка отправки и flash-сообщения приложения."""

    path = "/login"

    def __init__(self, page: Page, base_url: str) -> None:
        """Создаёт page object и его локаторы.

        Args:
            page: Playwright-страница, с которой работают все локаторы и действия.
            base_url: Корневой URL тестируемого приложения.
        """
        super().__init__(page, base_url)
        loc = LoginPageLocators
        self.heading_login = page.locator(loc.HEADING_LOGIN)
        self.input_username = page.locator(loc.INPUT_USERNAME)
        self.input_password = page.locator(loc.INPUT_PASSWORD)
        self.button_login = page.locator(loc.BUTTON_LOGIN)
        self.message_flash = page.locator(CommonLocators.MESSAGE_FLASH)

    def login(self, username: str, password: str) -> None:
        """Заполняет форму учётными данными и отправляет её.

        Метод намеренно не проверяет результат: он используется и с валидными,
        и с невалидными данными, поэтому проверка исхода — ответственность
        вызывающего теста.

        Args:
            username: Значение для поля username; может быть пустым или неверным.
            password: Значение для поля password; может быть пустым или неверным.
        """
        # Значения полей не логируем: в негативных сценариях любое из них может
        # содержать реальные учётные данные.
        logger.info("Отправляю форму логина")
        self.input_username.fill(username)
        self.input_password.fill(password)
        self.button_login.click()
