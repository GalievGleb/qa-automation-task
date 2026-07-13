# QA Automation Test Task

[![Tests](https://github.com/GalievGleb/qa-automation-task/actions/workflows/tests.yml/badge.svg)](https://github.com/GalievGleb/qa-automation-task/actions/workflows/tests.yml)

UI tests for [the-internet.herokuapp.com](https://the-internet.herokuapp.com)
built with Python 3.13, Playwright, and Pytest.

Russian documentation: [README.ru.md](README.ru.md).

## Covered behavior

The suite collects 12 tests covering the three task scenarios:

- 3 main-page checks;
- 1 navigation check (Main Page -> "Form Authentication" link -> Login Page);
- 6 invalid-login cases and 1 direct-access check;
- 1 complete valid login/logout scenario.

Scenario 3 verifies the complete flow required by the task:

1. open the login page;
2. log in with valid credentials;
3. verify the actual `/secure` URL, page title, heading, content, and Logout link;
4. log out and verify the login-page confirmation;
5. open `/secure` again and verify that access is denied.

## Project structure

```text
config/                         environment-dependent settings
locators/                       per-page XPath selectors + expected texts
pages/                          Page Objects: bound locators and page actions
data/                           test data (login cases, credential resolving)
tests/                          the three scenario tests
conftest.py                     shared pytest fixtures and hooks
pytest.ini                      pytest defaults, logging, markers
pyproject.toml                  mypy and ruff configuration
requirements.txt                pinned runtime dependencies
requirements-dev.txt            + dev tooling (ruff, mypy)
.github/workflows/tests.yml     CI workflow (lint -> types -> tests)
```

Tests do not contain selectors or navigation implementation. Locator classes
contain no actions, while Page Objects contain no test assertions. Each
`locators/<page>_locators.py` holds that page's `*Locators` (XPath selectors)
and `*Texts` (expected titles, headings, flash messages), so page objects carry
neither. Cross-page elements (the flash message, the shared document title)
live in `locators/common_locators.py`. Selectors are anchored to structure and
attributes rather than visible text, so `to_have_text` checks produce a
meaningful diff and each expected text has a single source of truth.

## Local setup

Python 3.13 is recommended because it is the version used by CI.

```bash
cd qa-automation-task
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt   # includes runtime deps + ruff and mypy
playwright install chromium
```

To install only what the tests need at runtime, use `requirements.txt` instead.

Windows PowerShell activation:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Running tests

```bash
# Full suite, headless Chromium
pytest

# Visible browser
pytest --headed

# Scenario 3 only; remains headless unless --headed is supplied
pytest -k test_user_can_login_and_logout

# Markers
pytest -m smoke
pytest -m "login and negative"

# Parallel run (the suite is xdist-ready: isolated function-scoped pages)
pytest -n auto

# Lint, formatting and type checks (same gates as CI)
ruff check .
ruff format --check .
mypy

# Self-contained HTML report
pytest --html=reports/report.html --self-contained-html
```

Failed tests are not rerun automatically; pytest continues running the
remaining selected tests. For a failed test Playwright saves a screenshot and
a trace (`--tracing retain-on-failure` is on by default) under `test-results/`,
and pytest writes the full run log to `logs/pytest.log` — the directory is
deliberately separate from `test-results/`, which pytest-playwright wipes at
session start.

## Allure report

Every run writes Allure results to `allure-results/` (configured in
`pytest.ini`; the directory is cleaned on every run). Tests are split into
readable blocks with `allure.step(...)`, and a failure screenshot is attached
to the Allure report automatically (see the hook in `conftest.py`).
To open the report locally you need the
[Allure command-line tool](https://allurereport.org/docs/install/):

```bash
pytest                          # produces allure-results/
allure serve allure-results     # builds and opens the HTML report
```

CI uploads `allure-results/` as an artifact, so the report can be generated
from any run.

## Environment configuration

Base URL precedence:

1. `--base-url` CLI option;
2. `BASE_URL` environment variable or local `.env` file;
3. `https://the-internet.herokuapp.com`.

| Variable | Default | Purpose |
|---|---|---|
| `BASE_URL` | `https://the-internet.herokuapp.com` | Application deployment |
| `LOGIN_USERNAME` | `tomsmith` | Valid secure-area username |
| `LOGIN_PASSWORD` | `SuperSecretPassword!` | Valid secure-area password |

Examples:

```bash
pytest --base-url https://staging.example.com
BASE_URL=https://staging.example.com pytest
```

```powershell
$env:BASE_URL = "https://staging.example.com"
$env:LOGIN_USERNAME = "staging-user"
$env:LOGIN_PASSWORD = "staging-password"
pytest
```

Alternatively, copy `.env.example` to `.env`. The local `.env` file is ignored
by Git.

## Test design

- Playwright web-first `expect()` assertions (with Russian failure messages)
  wait for the required state.
- Function-scoped browser pages isolate tests from one another — this is what
  makes the suite xdist-ready.
- `pytest -k` only filters tests; headed mode is always explicit.
- Failures are not rerun automatically, so regressions remain visible. To keep
  infrastructure errors distinguishable, `BasePage.open()` checks the HTTP
  response and fails fast with the status code instead of a vague timeout.
- Login actions never log username or password values, and an autouse guard
  fixture asserts after every test that neither credential leaked into logs.
- Invalid non-empty credentials are derived at runtime and guaranteed to differ
  from the configured valid value; parametrized cases reference credentials via
  a typed `Credential` enum, so a typo is a mypy error.
- Selectors live in page-specific classes under `locators/`, use raw XPath
  without `xpath=`, follow uppercase `ELEMENT_PURPOSE` names, and are anchored
  to structure/attributes — expected texts stay in `*Texts` classes only.
- Bound Page Object attributes follow lowercase `element_purpose` names. Logout
  is `LINK_LOGOUT`/`link_logout` because the DOM element is an `<a>`.

## CI workflow

`.github/workflows/tests.yml` runs the cheapest gates first (ruff lint/format,
then mypy), installs Chromium (cached between runs, keyed on the pinned
Playwright version), runs the complete test suite and publishes an HTML report
plus Allure results. Failure traces, screenshots and the full run log are
stored as diagnostic artifacts. The job has a 15-minute timeout, and a newer
push cancels an in-progress run of the same branch.

Manual runs accept a custom base URL. Deployments with different credentials
can define `LOGIN_USERNAME` and `LOGIN_PASSWORD` as repository secrets;
otherwise the public demo credentials are used.

## Notes on the task itself

Ambiguities found in the task statement and how they were resolved (the full
walkthrough is in [README.ru.md](README.ru.md)):

- **`/security` vs `/secure`** — the task says `/security`, but the real
  application redirects a successful login to `/secure`; `/security` does not
  exist. The tests verify the actual route.
- **"44 links"** — the task does not define which links count; the suite checks
  links inside `#content` (exactly 44). A hard-coded count also inherently
  contradicts the "any base URL" requirement — it only holds for this app.
- **"Sufficient amount of test cases"** — interpreted as 6 equivalence classes
  of invalid credentials plus a direct unauthenticated access check.
- **"Logout button"** — in the DOM it is a styled `<a>` link, not a `<button>`,
  which is reflected in the locator naming.
