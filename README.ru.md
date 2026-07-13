# QA Automation Test Task — краткое описание

[![Tests](https://github.com/GalievGleb/qa-automation-task/actions/workflows/tests.yml/badge.svg)](https://github.com/GalievGleb/qa-automation-task/actions/workflows/tests.yml)

UI-автотесты для [the-internet.herokuapp.com](https://the-internet.herokuapp.com)
на Python 3.13, Playwright и Pytest.

## Что проверяется

Набор содержит 12 тестов — ровно три сценария из задания:

- 3 проверки главной страницы;
- 1 проверка перехода: Главная -> ссылка «Form Authentication» -> Логин;
- 6 случаев невалидного входа и 1 проверка прямого доступа;
- 1 полный сценарий валидного входа и выхода.

Scenario 3 покрыт полностью: открытие Login page, валидный вход, проверка
`/secure`, title, content и Logout, выход, подтверждение выхода и повторный
запрет доступа к защищённой странице.

## Локальный запуск

```powershell
cd qa-automation-task
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
playwright install chromium

pytest
pytest --headed
pytest -m smoke
pytest -n auto                  # параллельный прогон (pytest-xdist)

ruff check .                    # линт (те же гейты, что и в CI)
ruff format --check .           # формат
mypy                            # типы (цели заданы в pyproject.toml)

allure serve allure-results     # отчёт Allure (нужен установленный allure CLI)
```

Для установки только рантайм-зависимостей используйте `requirements.txt`;
`requirements-dev.txt` добавляет dev-инструменты (ruff, mypy).

Для Linux и macOS виртуальное окружение активируется командой:

```bash
source .venv/bin/activate
```

## Структура

```text
config/                         настройки окружения
locators/                       XPath-селекторы + ожидаемые тексты (по странице)
pages/                          Page Objects: связанные локаторы и действия
data/                           тестовые данные (кейсы логина, разрешение кредов)
tests/                          три тестовых сценария
conftest.py                     общие fixtures и хуки Pytest
pytest.ini                      настройки запуска, логирование, маркеры
pyproject.toml                  конфигурация mypy и ruff
requirements.txt                рантайм-зависимости (пины)
requirements-dev.txt            + dev-инструменты (ruff, mypy)
.github/workflows/tests.yml     CI: линт -> типы -> тесты
```

Тесты не содержат селекторы и реализацию навигации. Locator-классы не содержат
действия, а Page Objects не содержат тестовые проверки. В каждом файле
`locators/<страница>_locators.py` лежат `*Locators` (XPath-селекторы) и
`*Texts` (ожидаемые title, заголовки, flash-сообщения) этой страницы — в самих
page object'ах нет ни того, ни другого. Общие для всего приложения элементы
(flash-сообщение, единый title) — в `locators/common_locators.py`. Локаторы
якорятся на структуру и атрибуты, а не на видимый текст, поэтому проверки
`to_have_text` показывают осмысленный diff, а у каждого текста один источник
правды.

## Настройки окружения

Base URL выбирается в следующем порядке:

1. `pytest --base-url URL`;
2. переменная `BASE_URL` или локальный `.env`;
3. публичный demo URL.

Валидные данные можно изменить через `LOGIN_USERNAME` и `LOGIN_PASSWORD`.
Пример для PowerShell:

```powershell
$env:BASE_URL = "https://staging.example.com"
$env:LOGIN_USERNAME = "staging-user"
$env:LOGIN_PASSWORD = "staging-password"
pytest
```

Можно скопировать `.env.example` в `.env`. Файл `.env` игнорируется Git.

## Основные решения

- Playwright `expect()` автоматически ожидает нужное состояние страницы.
- Function-scoped browser page изолирует состояние каждого теста — благодаря
  этому набор готов к параллельному прогону (`pytest -n auto`).
- `pytest -k` только фильтрует тесты; видимый браузер включается `--headed`.
- Падения не перезапускаются автоматически и остаются видимыми. Чтобы
  инфраструктурные ошибки не маскировались под таймауты, `BasePage.open()`
  проверяет HTTP-ответ и падает сразу с кодом статуса.
- Значения username и password не записываются в логи, а autouse-фикстура-страж
  проверяет это после каждого теста (включая позитивный сценарий).
- Невалидные данные детерминированно выводятся из валидных во время теста;
  в параметризации креды указываются типизированным enum `Credential` —
  опечатку ловит mypy.
- После Logout тест повторно проверяет запрет доступа к `/secure`.
- Селекторы вынесены в отдельные классы `locators/`, названы в формате `ELEMENT_PURPOSE` и якорятся на
  структуру/атрибуты; ожидаемые тексты — только в классах `*Texts`.
- Атрибуты Page Object используют `element_purpose`. Logout называется
  `LINK_LOGOUT`/`link_logout`, потому что в DOM это ссылка `<a>`.

## Отчёты и логи

- **Allure** — каждый прогон пишет результаты в `allure-results/` (задано в
  `pytest.ini`; каталог очищается на старте), тесты разбиты на блоки через
  `with allure.step(...)`, а скриншот падения прикладывается к Allure-отчёту
  автоматически (хук в `conftest.py`). Локально отчёт открывается командой
  `allure serve allure-results` (нужен установленный Allure CLI). CI заливает
  `allure-results/` артефактом.
- **Проверки** — используются web-first `expect(...)` с русским текстом ошибки
  (`message=`): они и ждут нужное состояние, и валят тест с понятным сообщением.
- **Логи** — шаги пишутся в консоль и в `logs/pytest.log`; каталог намеренно
  отделён от `test-results/`, который pytest-playwright очищает на старте
  сессии (иначе лог терялся бы из CI-артефактов). Скриншот и trace падения
  (`--tracing retain-on-failure` включён по умолчанию) — в `test-results/`.

## Замечания к заданию

Что в постановке стоило бы уточнить (чтобы вы тоже видели):

1. **`/security` vs `/secure`** — в задании `/security`, реального маршрута нет
   (см. раздел ниже).
2. **«44 links»** — не сказано, что считать; берём ссылки внутри `#content`
   (их ровно 44). Точное число к тому же противоречит требованию «менять base
   URL на любой»: на другом сайте столько ссылок не будет.
3. **«sufficient amount of test cases»** — размыто; взято 6 негативных кейсов
   + проверка прямого доступа к `/secure`.
4. **«title and content»** — не уточнено, что за «content»; проверяю заголовок,
   подзаголовок и flash-сообщение.
5. **«Logout button»** — на самом деле это ссылка `<a>`, а не `<button>`.
6. **Нестабильность демо-сайта** — скорее всего это свойство окружения; поэтому
   навигация с `wait_until="commit"` и опора на авто-ожидание `expect()`.

## CI

Workflow запускает сначала самые дешёвые проверки (ruff линт/формат, затем
mypy), кеширует браузер Playwright между прогонами (ключ — версия из
requirements.txt), прогоняет весь набор в Chromium, ограничивает job 15
минутами и отменяет устаревший прогон при новом пуше в ту же ветку.
Артефакты: HTML-отчёт и Allure-результаты — всегда; trace'ы, скриншоты и полный
лог — при падении. Для другого окружения credentials передаются через
repository secrets `LOGIN_USERNAME` и `LOGIN_PASSWORD`, а не через открытые
inputs.

## `/security` и `/secure`

В тексте задания указан `/security`, но реальное приложение после успешного
входа открывает `/secure`; маршрута `/security` нет. Тест проверяет фактическое
поведение приложения.
