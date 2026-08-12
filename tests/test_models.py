from datetime import datetime

from app.models.expense import Expense


def test_expense_creation():
    expense = Expense(
        id=1,
        amount=100.0,
        category="Food",
        description="Lunch",
        date=datetime(2026, 1, 15, 12, 0)
    )

    assert expense.id == 1
    assert expense.amount == 100.0
    assert expense.category == "Food"
    assert expense.description == "Lunch"
    assert expense.date.year == 2026


def test_expense_equality():
    date = datetime.now()

    expense_a = Expense(
        id=1, amount=50, category="Food",
        description="Snack", date=date
    )

    expense_b = Expense(
        id=1, amount=50, category="Food",
        description="Snack", date=date
    )

    assert expense_a == expense_b


def test_expense_mutation():
    expense = Expense(
        id=1, amount=100, category="Food",
        description="Lunch", date=datetime.now()
    )

    expense.amount = 200
    expense.description = "Dinner"

    assert expense.amount == 200
    assert expense.description == "Dinner"
