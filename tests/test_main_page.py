"""Сценарий 1 — Главная страница.

Открыть главную страницу и проверить её заголовок, ленту 'Fork me on GitHub'
и что контент страницы содержит ровно 44 ссылки.
"""

from typing import Final

import allure
import pytest
from playwright.sync_api import expect

from locators.common_locators import CommonTexts
from pages.main_page import MainPage

EXPECTED_CONTENT_LINK_COUNT: Final[int] = 44


@pytest.mark.smoke
class TestMainPage:
    """Сценарий 1: проверки главной страницы."""

    def test_page_has_title(self, main_page: MainPage) -> None:
        with allure.step("Открываем главную страницу"):
            main_page.open()

        with allure.step("Проверяем заголовок вкладки"):
            expect(main_page.page, "У главной страницы неверный заголовок документа").to_have_title(
                CommonTexts.TITLE
            )

    def test_page_has_fork_me_on_github_ribbon(self, main_page: MainPage) -> None:
        with allure.step("Открываем главную страницу"):
            main_page.open()

        with allure.step("Проверяем ленту 'Fork me on GitHub'"):
            expect(
                main_page.image_github_ribbon,
                "Лента 'Fork me on GitHub' не отображается",
            ).to_be_visible()

    def test_page_content_contains_44_links(self, main_page: MainPage) -> None:
        with allure.step("Открываем главную страницу"):
            main_page.open()

        with allure.step(f"Проверяем, что в контенте ровно {EXPECTED_CONTENT_LINK_COUNT} ссылок"):
            expect(
                main_page.link_content_items,
                f"Ожидали {EXPECTED_CONTENT_LINK_COUNT} ссылок в контенте страницы",
            ).to_have_count(EXPECTED_CONTENT_LINK_COUNT)
