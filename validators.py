from app.exceptions import ValidationError


def validate_amount(amount: str) -> float:
    try:
        value = float(amount)

    except ValueError:
        raise ValidationError(
            "Amount must be a valid number."
        )

    if value <= 0:
        raise ValidationError(
            "Amount must be greater than zero."
        )

    return value


def validate_text(value: str, field_name: str) -> str:
    value = value.strip()

    if not value:
        raise ValidationError(
            f"{field_name} cannot be empty."
        )

    return value


def validate_id(value: str) -> int:
    try:
        expense_id = int(value)

    except ValueError:
        raise ValidationError(
            "ID must be a positive integer."
        )

    if expense_id <= 0:
        raise ValidationError(
            "ID must be a positive integer."
        )

    return expense_id