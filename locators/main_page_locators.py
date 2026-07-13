"""Локаторы главной страницы."""


class MainPageLocators:
    """Селекторы элементов главной страницы (XPath)."""

    IMAGE_GITHUB_RIBBON = "//img[@alt='Fork me on GitHub']"
    LINK_CONTENT_ITEMS = "//*[@id='content']//a"
    LINK_FORM_AUTHENTICATION = "//*[@id='content']//a[@href='/login']"
