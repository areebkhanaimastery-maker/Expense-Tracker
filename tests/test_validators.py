# pyrefly: ignore [missing-import]
import pytest

from app.exceptions import ValidationError
from app.validators.expense_validator import (
    validate_amount,
    validate_category,
    validate_description,
    validate_id,
    CATEGORIES
)


# --- Amount ---

def test_valid_amount():
    assert validate_amount("100") == 100.0
    assert validate_amount("10.50") == 10.50
    assert validate_amount(50) == 50.0


def test_zero_amount():
    with pytest.raises(ValidationError, match="greater than zero"):
        validate_amount("0")


def test_negative_amount():
    with pytest.raises(ValidationError, match="greater than zero"):
        validate_amount("-10")


def test_invalid_amount():
    with pytest.raises(ValidationError, match="valid number"):
        validate_amount("abc")


def test_none_amount():
    with pytest.raises(ValidationError, match="valid number"):
        validate_amount(None)


def test_huge_amount():
    with pytest.raises(ValidationError, match="too large"):
        validate_amount("99999999")


# --- Category ---

def test_valid_category():
    assert validate_category("Food") == "Food"
    assert validate_category("  Transport  ") == "Transport"


def test_invalid_category():
    with pytest.raises(ValidationError, match="Invalid"):
        validate_category("InvalidCategory")


def test_empty_category():
    with pytest.raises(ValidationError, match="Invalid"):
        validate_category("")


# --- Description ---

def test_valid_description():
    assert validate_description("Lunch at cafe") == "Lunch at cafe"
    assert validate_description("  trimmed  ") == "trimmed"


def test_empty_description():
    with pytest.raises(ValidationError, match="cannot be empty"):
        validate_description("")


def test_whitespace_description():
    with pytest.raises(ValidationError, match="cannot be empty"):
        validate_description("   ")


def test_long_description():
    with pytest.raises(ValidationError, match="200 characters"):
        validate_description("A" * 201)


def test_max_length_description():
    result = validate_description("A" * 200)
    assert len(result) == 200


# --- ID ---

def test_valid_id():
    assert validate_id("123") == 123
    assert validate_id(5) == 5


def test_invalid_id():
    with pytest.raises(ValidationError, match="integer"):
        validate_id("abc")


def test_negative_id():
    with pytest.raises(ValidationError, match="positive"):
        validate_id("-5")


def test_zero_id():
    with pytest.raises(ValidationError, match="positive"):
        validate_id("0")


def test_none_id():
    with pytest.raises(ValidationError, match="integer"):
        validate_id(None)
