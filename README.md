# FastAPI Calculator

My IS 601 Module 8 calculator. It provides a browser interface and four JSON API
endpoints, with unit, integration, and Playwright end-to-end tests.

## Submission

- [Successful GitHub Actions run](https://github.com/tkg1121/fastapi-calculator/actions/runs/40552794843)
- [Application running in the browser](docs/Application%20Running.jpg)
- [Successful workflow screenshot](docs/GitHub%20Actions.jpg)

The suite contains 24 unit tests, 87 integration tests, and 16 Playwright
end-to-end tests. All 127 tests passed locally and in GitHub Actions.

## Source

This project builds on the instructor's
[Module 8 calculator](https://github.com/kaw393939/module8_is601/tree/1c2198fab4c0920797a01c9013358e920433e78b).
It keeps the four arithmetic functions, endpoint paths, and browser calculator
interactions. Changes add operation and request logging, input/result validation,
accessible labels, tests, and a CI workflow. The original license is included.

## Setup and run

Use Python 3.11 or newer. CI uses Python 3.12.

```bash
git clone https://github.com/tkg1121/fastapi-calculator.git
cd fastapi-calculator
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On Linux or macOS:

```bash
source .venv/bin/activate
```

Install dependencies and start the local server:

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open [the calculator](http://127.0.0.1:8000) in your browser. Enter two numbers
and click Add, Subtract, Multiply, or Divide. The result appears on the same
page. Stop the server with Ctrl+C.

Interactive API documentation is available at
[Swagger UI](http://127.0.0.1:8000/docs) and
[ReDoc](http://127.0.0.1:8000/redoc).

## API

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/` | Calculator HTML page |
| POST | `/add` | Add `a` and `b` |
| POST | `/subtract` | Subtract `b` from `a` |
| POST | `/multiply` | Multiply `a` by `b` |
| POST | `/divide` | Divide `a` by `b` |

The POST endpoints accept JSON numbers:

```json
{"a": 10, "b": 5}
```

For `/add`, a successful response has status 200 and the body:

```json
{"result": 15.0}
```

Missing operands, strings, booleans, nulls, nonfinite values, malformed JSON,
division by zero, and overflowing results return status 400 with an `error`
message. Unexpected calculation failures return a generic status 500 message
while details are logged on the server. Invalid paths return 404; incorrect
methods return 405. Calculations use floating-point numbers, so normal decimal
rounding differences can occur.

## Logging

Python logging records each arithmetic operation and result, HTTP method/path
and status, validation failures, and calculation errors. Unexpected calculation
failures include a traceback in the server logs. Logs go to the terminal where
the server runs. The application does not log request bodies or send logs to an
external service.

## Tests

Install the Chromium browser used by Playwright:

```bash
python -m playwright install chromium
```

On Linux, install its system dependencies as well:

```bash
python -m playwright install --with-deps chromium
```

Run the entire suite:

```bash
python -m pytest -v
```

Or run each layer separately:

```bash
python -m pytest tests/unit -v
python -m pytest tests/integration -v
python -m pytest tests/e2e -v --browser chromium
```

- **Unit:** all four arithmetic functions, signs, zero, decimals, and logging.
- **Integration:** the HTML page, all four API endpoints, validation, errors,
  response shapes, logging, and API documentation.
- **End-to-end:** Chromium fills in the form and clicks the real buttons. Tests
  check calculations, divide-by-zero recovery, missing values, overflow, network
  failure recovery, and multiple calculations in one session.

The browser tests start their own Uvicorn process on an available loopback port,
wait for readiness, and shut it down afterward. You do not need to start the
application manually before running tests. Browser contexts are isolated between
tests. The network failure test deliberately interrupts one request, then checks
that a retry works; normal calculation tests use the real API.

## GitHub Actions

The workflow installs Python dependencies and Chromium, then runs the unit,
integration, and end-to-end suites as separate steps on every push and pull
request. Any failed test fails the workflow.

## Project layout

```text
main.py                        FastAPI routes, models, and error handling
app/operations/__init__.py      Arithmetic functions and operation logging
templates/index.html           Browser calculator
tests/conftest.py              API client and live server fixtures
tests/unit/                    Arithmetic tests
tests/integration/             API and logging tests
tests/e2e/                     Playwright browser tests
.github/workflows/tests.yml    Continuous integration
```
