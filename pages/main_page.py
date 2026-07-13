"""Page object главной страницы со списком доступных примеров."""

import logging

from playwright.sync_api import Page

from locators.main_page_locators import MainPageLocators
from pages.base_page import BasePage
from pages.login_page import LoginPage

logger = logging.getLogger(__name__)


class MainPage(BasePage):
    """Главная страница: лента 'Fork me on GitHub', ссылки контента и переход к логину."""

    path = "/"

    def __init__(self, page: Page, base_url: str) -> None:
        """Создаёт page object и его локаторы.

        Args:
            page: Playwright-страница, с которой работают все локаторы и действия.
            base_url: Корневой URL тестируемого приложения.
        """
        super().__init__(page, base_url)
        loc = MainPageLocators
        self.image_github_ribbon = page.locator(loc.IMAGE_GITHUB_RIBBON)
        self.link_content_items = page.locator(loc.LINK_CONTENT_ITEMS)
        self.link_form_authentication = page.locator(loc.LINK_FORM_AUTHENTICATION)

    def go_to_login_page(self) -> LoginPage:
        """Кликает по ссылке 'Form Authentication'.

        Returns:
            Page object страницы логина, привязанный к той же вкладке браузера.
        """
        logger.info("Кликаю по ссылке 'Form Authentication'")
        self.link_form_authentication.click()
        return LoginPage(self.page, self.base_url)
