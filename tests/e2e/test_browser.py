import pytest
from playwright.sync_api import expect


pytestmark = pytest.mark.e2e


@pytest.fixture
def calculator(page, fastapi_server):
    page.goto(fastapi_server)
    return page


def test_home_page(calculator):
    expect(calculator.get_by_role("heading", name="Hello World", exact=True)).to_be_visible()
    expect(calculator.get_by_role("heading", name="Calculator", exact=True)).to_be_visible()
    expect(calculator.get_by_label("First number")).to_be_visible()
    expect(calculator.get_by_label("Second number")).to_be_visible()


@pytest.mark.parametrize("button,a,b,result", [
    ("Add", "10", "5", "15"), ("Add", "-2.5", "1", "-1.5"),
    ("Subtract", "10", "5", "5"), ("Subtract", "-2", "-5", "3"),
    ("Multiply", "10", "5", "50"), ("Multiply", "0.5", "0.5", "0.25"),
    ("Divide", "10", "2", "5"), ("Divide", "-9", "2", "-4.5"),
])
def test_operations_through_real_api(calculator, button, a, b, result):
    calculator.get_by_label("First number").fill(a)
    calculator.get_by_label("Second number").fill(b)
    with calculator.expect_response(lambda response: response.url.endswith(f"/{button.lower()}")) as response:
        calculator.get_by_role("button", name=button, exact=True).click()
    assert response.value.status == 200
    expect(calculator.get_by_role("status")).to_have_text(f"Calculation Result: {result}")


def test_divide_by_zero_and_recovery(calculator):
    calculator.get_by_label("First number").fill("10")
    calculator.get_by_label("Second number").fill("0")
    calculator.get_by_role("button", name="Divide", exact=True).click()
    expect(calculator.get_by_role("status")).to_have_text("Error: Cannot divide by zero!")
    calculator.get_by_label("Second number").fill("2")
    calculator.get_by_role("button", name="Divide", exact=True).click()
    expect(calculator.get_by_role("status")).to_have_text("Calculation Result: 5")


@pytest.mark.parametrize("a,b", [("", ""), ("1", ""), ("", "2")])
def test_missing_numbers(calculator, a, b):
    calculator.get_by_label("First number").fill(a)
    calculator.get_by_label("Second number").fill(b)
    calculator.get_by_role("button", name="Add", exact=True).click()
    expect(calculator.get_by_role("status")).to_have_text("Error: Enter a valid number in both fields.")


def test_server_rejects_overflow(calculator):
    calculator.get_by_label("First number").fill("1e308")
    calculator.get_by_label("Second number").fill("1e308")
    calculator.get_by_role("button", name="Multiply", exact=True).click()
    expect(calculator.get_by_role("status")).to_have_text("Error: Result is too large for a finite number.")


def test_network_failure_and_retry(calculator):
    calculator.get_by_label("First number").fill("1")
    calculator.get_by_label("Second number").fill("2")
    calculator.route("**/add", lambda route: route.abort())
    calculator.get_by_role("button", name="Add", exact=True).click()
    expect(calculator.get_by_role("status")).to_have_text("Error: Could not reach the calculator. Please try again.")
    calculator.unroute("**/add")
    calculator.get_by_role("button", name="Add", exact=True).click()
    expect(calculator.get_by_role("status")).to_have_text("Calculation Result: 3")


def test_multiple_operations_in_one_session(calculator):
    calculator.get_by_label("First number").fill("8")
    calculator.get_by_label("Second number").fill("2")
    for button, result in [("Add", "10"), ("Subtract", "6"), ("Multiply", "16"), ("Divide", "4")]:
        calculator.get_by_role("button", name=button, exact=True).click()
        expect(calculator.get_by_role("status")).to_have_text(f"Calculation Result: {result}")
