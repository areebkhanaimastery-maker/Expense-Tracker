def validate_amount(amount: str) -> float:
    try:
        value = float(amount)

        if value <= 0:
            raise ValueError

        return value

    except ValueError:
        raise ValueError("Amount must be a positive number.")


def validate_text(value: str, field_name: str) -> str:
    value = value.strip()

    if not value:
        raise ValueError(f"{field_name} cannot be empty.")

    return value


def validate_id(value: str) -> int:
    try:
        expense_id = int(value)

        if expense_id <= 0:
            raise ValueError

        return expense_id

    except ValueError:
        raise ValueError("ID must be a positive integer.")