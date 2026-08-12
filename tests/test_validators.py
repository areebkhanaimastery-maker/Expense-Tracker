import pytest
from app.exceptions import ValidationError
from validators import validate_amount, validate_text, validate_id


def test_validate_amount():
    assert validate_amount("100") == 100.0
    assert validate_amount("10.50") == 10.50
    
    with pytest.raises(ValidationError) as excinfo:
        validate_amount("-10")
    assert "greater than zero" in str(excinfo.value)
    
    with pytest.raises(ValidationError) as excinfo:
        validate_amount("abc")
    assert "valid number" in str(excinfo.value)


def test_validate_text():
    assert validate_text("Hello", "Field") == "Hello"
    assert validate_text("  trimmed  ", "Field") == "trimmed"
    
    with pytest.raises(ValidationError) as excinfo:
        validate_text("", "Field")
    assert "Field cannot be empty" in str(excinfo.value)


def test_validate_id():
    assert validate_id("123") == 123
    
    with pytest.raises(ValidationError) as excinfo:
        validate_id("-5")
    assert "positive integer" in str(excinfo.value)
    
    with pytest.raises(ValidationError) as excinfo:
        validate_id("abc")
    assert "positive integer" in str(excinfo.value)
