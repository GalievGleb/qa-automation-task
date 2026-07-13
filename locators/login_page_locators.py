"""Локаторы и ожидаемые тексты страницы авторизации (Form Authentication)."""


class LoginPageLocators:
    """Селекторы элементов страницы авторизации (XPath).

    Локаторы якорятся на структуру и атрибуты, а не на видимый текст:
    ожидаемые тексты живут в :class:`LoginPageTexts`, поэтому проверка
    ``to_have_text`` показывает осмысленный diff при регрессии, а источник
    правды для каждого текста один.
    """

    HEADING_LOGIN = "//*[@id='content']//h2"
    INPUT_USERNAME = "//*[@id='username']"
    INPUT_PASSWORD = "//*[@id='password']"
    BUTTON_LOGIN = "//form[@id='login']//button[@type='submit']"


class LoginPageTexts:
    """Ожидаемые тексты страницы авторизации."""

    HEADING = "Login Page"
    USERNAME_INVALID = "Your username is invalid!"
    PASSWORD_INVALID = "Your password is invalid!"
    LOGOUT_SUCCESS = "You logged out of the secure area!"
    LOGIN_REQUIRED = "You must login to view the secure area!"
