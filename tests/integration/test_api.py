import logging

import pytest

import main


pytestmark = pytest.mark.integration
ENDPOINTS = ["add", "subtract", "multiply", "divide"]


def test_home_page(client, monkeypatch, tmp_path):
    # Template resolution must not depend on the caller's working directory.
    monkeypatch.chdir(tmp_path)
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Hello World" in response.text
    for label in ["Add", "Subtract", "Multiply", "Divide"]:
        assert f">{label}</button>" in response.text


@pytest.mark.parametrize("endpoint,a,b,expected", [
    ("add", 10, 5, 15), ("add", -10, 5, -5), ("add", .1, .2, .3),
    ("subtract", 10, 5, 5), ("subtract", -10, -5, -5), ("subtract", 2.5, .5, 2),
    ("multiply", 10, 5, 50), ("multiply", -10, 5, -50), ("multiply", .5, .5, .25),
    ("divide", 10, 2, 5), ("divide", -9, 2, -4.5), ("divide", 0, 5, 0),
])
def test_api_results_and_logging(client, endpoint, a, b, expected, caplog):
    with caplog.at_level(logging.INFO):
        response = client.post(f"/{endpoint}", json={"a": a, "b": b})
    assert response.status_code == 200
    assert set(response.json()) == {"result"}
    assert response.json()["result"] == pytest.approx(expected)
    assert f"operation={endpoint}" in caplog.text
    assert f"path=/{endpoint} status=200" in caplog.text


@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize("payload", [{}, {"a": 1}, {"b": 2}, {"a": "hello", "b": 2},
    {"a": 1, "b": "2"}, {"a": None, "b": 2}, {"a": True, "b": 2},
    {"a": [], "b": 2}, {"a": 1, "b": {}}])
def test_invalid_request(client, endpoint, payload, caplog):
    response = client.post(f"/{endpoint}", json=payload)
    assert response.status_code == 400
    assert isinstance(response.json()["error"], str)
    assert "result" not in response.json()
    assert "Validation error" in caplog.text


@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize("payload", [
    '{"a": NaN, "b": 2}', '{"a": 1, "b": Infinity}',
    '{"a": -Infinity, "b": 2}', '{"a": 1e999, "b": 2}',
])
def test_nonfinite_input(client, endpoint, payload):
    response = client.post(f"/{endpoint}", content=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    assert "finite" in response.json()["error"]


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_malformed_json(client, endpoint):
    response = client.post(f"/{endpoint}", content="{bad json", headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    assert "error" in response.json()


@pytest.mark.parametrize("divisor", [0, -0.0])
def test_divide_by_zero(client, divisor, caplog):
    response = client.post("/divide", json={"a": 10, "b": divisor})
    assert response.status_code == 400
    assert response.json() == {"error": "Cannot divide by zero!"}
    assert "operation=divide" in caplog.text


@pytest.mark.parametrize("endpoint,a,b", [("add", 1e308, 1e308), ("subtract", 1e308, -1e308), ("multiply", 1e308, 2), ("divide", 1e308, 1e-308)])
def test_overflow_returns_readable_error(client, endpoint, a, b):
    response = client.post(f"/{endpoint}", json={"a": a, "b": b})
    assert response.status_code == 400
    assert "too large" in response.json()["error"]


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_unexpected_failure_is_logged_without_exposing_details(client, monkeypatch, endpoint, caplog):
    def broken(a, b):
        raise RuntimeError("private diagnostic details")

    monkeypatch.setitem(main.OPERATIONS, endpoint, broken)
    response = client.post(f"/{endpoint}", json={"a": 1, "b": 2})
    assert response.status_code == 500
    assert response.json() == {"error": "Internal Server Error"}
    assert "private diagnostic details" not in response.text
    assert "Unexpected calculation failure" in caplog.text
    assert "private diagnostic details" in caplog.text


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_wrong_method(client, endpoint):
    response = client.get(f"/{endpoint}")
    assert response.status_code == 405
    assert response.json() == {"error": "Method Not Allowed"}
    assert response.headers["allow"] == "POST"


def test_unknown_endpoint(client):
    response = client.post("/unknown", json={"a": 1, "b": 2})
    assert response.status_code == 404
    assert response.json() == {"error": "Not Found"}


def test_openapi_documents_all_operations(client):
    schema = client.get("/openapi.json").json()
    for endpoint in ENDPOINTS:
        assert "post" in schema["paths"][f"/{endpoint}"]
        assert "400" in schema["paths"][f"/{endpoint}"]["post"]["responses"]


@pytest.mark.parametrize("path", ["/docs", "/redoc"])
def test_documentation_pages(client, path):
    assert client.get(path).status_code == 200
