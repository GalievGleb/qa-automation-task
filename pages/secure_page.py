"""Page object защищённой зоны, доступной только после успешного логина."""

import logging

from playwright.sync_api import Page

from locators.common_locators import CommonLocators
from locators.secure_page_locators import SecurePageLocators
from pages.base_page import BasePage
from pages.login_page import LoginPage

logger = logging.getLogger(__name__)


class SecurePage(BasePage):
    """Защищённая зона: заголовок, приветствие, flash-сообщение и ссылка выхода."""

    path = "/secure"

    def __init__(self, page: Page, base_url: str) -> None:
        """Создаёт page object и его локаторы.

        Args:
            page: Playwright-страница, с которой работают все локаторы и действия.
            base_url: Корневой URL тестируемого приложения.
        """
        super().__init__(page, base_url)
        loc = SecurePageLocators
        self.heading_secure_area = page.locator(loc.HEADING_SECURE_AREA)
        self.text_secure_subheader = page.locator(loc.TEXT_SECURE_SUBHEADER)
        self.message_flash = page.locator(CommonLocators.MESSAGE_FLASH)
        self.link_logout = page.locator(loc.LINK_LOGOUT)

    def logout(self) -> LoginPage:
        """Кликает по ссылке Logout.

        Returns:
            Page object страницы логина, на которую редиректит приложение.
        """
        logger.info("Кликаю по ссылке 'Logout'")
        self.link_logout.click()
        return LoginPage(self.page, self.base_url)
