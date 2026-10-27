"""The four arithmetic functions used by the API."""

import logging


logger = logging.getLogger(__name__)
Number = int | float


def add(a: Number, b: Number) -> Number:
    """Return the sum of two numbers."""
    result = a + b
    logger.info("operation=add a=%s b=%s result=%s", a, b, result)
    return result


def subtract(a: Number, b: Number) -> Number:
    """Subtract the second number from the first."""
    result = a - b
    logger.info("operation=subtract a=%s b=%s result=%s", a, b, result)
    return result


def multiply(a: Number, b: Number) -> Number:
    """Return the product of two numbers."""
    result = a * b
    logger.info("operation=multiply a=%s b=%s result=%s", a, b, result)
    return result


def divide(a: Number, b: Number) -> float:
    """Divide the first number by the second, rejecting zero divisors."""
    if b == 0:
        logger.warning("operation=divide rejected zero divisor")
        raise ValueError("Cannot divide by zero!")
    result = a / b
    logger.info("operation=divide a=%s b=%s result=%s", a, b, result)
    return result
