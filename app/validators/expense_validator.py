from app.exceptions import ValidationError


CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Education",
    "Other"
]


def validate_amount(value) -> float:

    try:
        amount = float(value)
    except (TypeError, ValueError):
        raise ValidationError(
            "Amount must be a valid number."
        )

    if amount <= 0:
        raise ValidationError(
            "Amount must be greater than zero."
        )

    if amount > 10_000_000:
        raise ValidationError(
            "Amount is too large."
        )

    return round(amount, 2)


def validate_category(category: str) -> str:

    category = category.strip()

    if category not in CATEGORIES:
        raise ValidationError(
            "Invalid expense category."
        )

    return category


def validate_description(description: str) -> str:

    description = description.strip()

    if not description:
        raise ValidationError(
            "Description cannot be empty."
        )

    if len(description) > 200:
        raise ValidationError(
            "Description cannot exceed 200 characters."
        )

    return description


def validate_id(value) -> int:

    try:
        expense_id = int(value)
    except (TypeError, ValueError):
        raise ValidationError(
            "ID must be an integer."
        )

    if expense_id <= 0:
        raise ValidationError(
            "ID must be positive."
        )

    return expense_id
