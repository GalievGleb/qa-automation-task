"""Локаторы и ожидаемые тексты защищённой зоны."""


class SecurePageLocators:
    """Селекторы элементов защищённой зоны (XPath).

    Локаторы якорятся на структуру и атрибуты, а не на видимый текст:
    ожидаемые тексты живут в :class:`SecurePageTexts`.
    """

    HEADING_SECURE_AREA = "//*[@id='content']//h2"
    TEXT_SECURE_SUBHEADER = (
        "//*[@id='content']//*[contains(concat(' ', normalize-space(@class), ' '), ' subheader ')]"
    )
    LINK_LOGOUT = "//a[@href='/logout']"


class SecurePageTexts:
    """Ожидаемые тексты защищённой зоны."""

    HEADING = "Secure Area"
    SUBHEADER = "Welcome to the Secure Area"
    LOGIN_SUCCESS = "You logged into a secure area!"
