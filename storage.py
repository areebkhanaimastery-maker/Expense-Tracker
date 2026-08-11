import json
from datetime import datetime
from pathlib import Path

from models import Expense


DATA_FILE = Path("data/expenses.json")


def save_expenses(expenses: list[Expense]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = []

    for expense in expenses:
        data.append({
            "id": expense.id,
            "amount": expense.amount,
            "category": expense.category,
            "description": expense.description,
            "date": expense.date.isoformat()
        })

    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_expenses() -> list[Expense]:
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except (json.JSONDecodeError, OSError):
        return []

    expenses = []

    for item in data:
        expenses.append(
            Expense(
                id=item["id"],
                amount=item["amount"],
                category=item["category"],
                description=item["description"],
                date=datetime.fromisoformat(item["date"])
            )
        )

    return expenses
