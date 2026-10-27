import logging

import pytest

from app.operations import add, divide, multiply, subtract


pytestmark = pytest.mark.unit


@pytest.mark.parametrize("operation,a,b,expected", [
    (add, 2, 3, 5), (add, -2, -3, -5), (add, 2.5, 3, 5.5),
    (add, 0, 3, 3), (add, .1, .2, .3),
    (subtract, 5, 3, 2), (subtract, -5, -3, -2), (subtract, 2, 5, -3),
    (subtract, 2.5, .5, 2), (subtract, 0, 0, 0),
    (multiply, 2, 3, 6), (multiply, -2, 3, -6), (multiply, -2, -3, 6),
    (multiply, .5, .5, .25), (multiply, 0, 3, 0),
    (divide, 6, 3, 2), (divide, -6, 3, -2), (divide, -6, -3, 2),
    (divide, 5.5, 2, 2.75), (divide, 0, 5, 0), (divide, 1, 3, 1/3),
])
def test_operations_and_success_logs(operation, a, b, expected, caplog):
    with caplog.at_level(logging.INFO):
        assert operation(a, b) == pytest.approx(expected)
    assert f"operation={operation.__name__}" in caplog.text
    assert "result=" in caplog.text


@pytest.mark.parametrize("divisor", [0, 0.0, -0.0])
def test_divide_by_zero(divisor, caplog):
    with pytest.raises(ValueError, match="Cannot divide by zero!"):
        divide(5, divisor)
    assert "rejected zero divisor" in caplog.text
