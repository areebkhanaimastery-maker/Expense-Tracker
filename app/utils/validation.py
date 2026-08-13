"""
Centralized Input Validation Routines.
"""

from app.exceptions.validation import ValidationError

CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Education",
    "Other",
]


def validate_amount(value: object) -> float:
    """Validate expense amount is positive float under 10,000,000."""
    try:
        amount = float(value)
    except (TypeError, ValueError):
        raise ValidationError("Amount must be a valid number.")

    if amount <= 0:
        raise ValidationError("Amount must be greater than zero.")

    if amount > 10_000_000:
        raise ValidationError("Amount is too large.")

    return round(amount, 2)


def validate_category(category: str) -> str:
    """Validate expense category."""
    if not isinstance(category, str):
        raise ValidationError("Category must be a string.")

    cat = category.strip()
    if cat not in CATEGORIES:
        raise ValidationError("Invalid expense category.")

    return cat


def validate_description(description: str) -> str:
    """Validate expense description."""
    if not isinstance(description, str):
        raise ValidationError("Description must be a string.")

    desc = description.strip()
    if not desc:
        raise ValidationError("Description cannot be empty.")

    if len(desc) > 200:
        raise ValidationError("Description cannot exceed 200 characters.")

    return desc


def validate_id(value: object) -> int:
    """Validate positive integer ID."""
    try:
        expense_id = int(value)
    except (TypeError, ValueError):
        raise ValidationError("ID must be an integer.")

    if expense_id <= 0:
        raise ValidationError("ID must be positive.")

    return expense_id
