# pyrefly: ignore [missing-import]
import pytest
from datetime import datetime

from app.models.expense import Expense
from app.repositories.sqlite_repository import SQLiteExpenseRepository
from app.exceptions import DatabaseError


@pytest.fixture
def repository(tmp_path):
    db_path = tmp_path / "test.db"
    return SQLiteExpenseRepository(db_path)


def _make_expense(amount=1000, category="Food", description="Lunch"):
    return Expense(
        id=0,
        amount=amount,
        category=category,
        description=description,
        date=datetime.now()
    )


def test_add_and_get_expense(repository):
    expense = _make_expense(1500, "Food", "Dinner")

    expense_id = repository.add(expense)

    result = repository.get_by_id(expense_id)

    assert result is not None
    assert result.amount == 1500
    assert result.category == "Food"
    assert result.description == "Dinner"


def test_get_all_expenses(repository):
    repository.add(_make_expense(100, "Food", "Breakfast"))
    repository.add(_make_expense(200, "Transport", "Taxi"))
    repository.add(_make_expense(300, "Bills", "Electric"))

    expenses = repository.get_all()

    assert len(expenses) == 3


def test_get_by_id_missing(repository):
    result = repository.get_by_id(999)

    assert result is None


def test_delete_expense(repository):
    expense = _make_expense(500, "Transport", "Taxi")

    expense_id = repository.add(expense)

    assert repository.delete(expense_id) is True
    assert repository.get_by_id(expense_id) is None


def test_delete_missing_expense(repository):
    assert repository.delete(999) is False


def test_update_expense(repository):
    expense = _make_expense(1000, "Food", "Lunch")

    expense.id = repository.add(expense)

    expense.amount = 1500
    expense.description = "Dinner"

    assert repository.update(expense) is True

    updated = repository.get_by_id(expense.id)

    assert updated.amount == 1500
    assert updated.description == "Dinner"


def test_update_missing_expense(repository):
    expense = _make_expense()
    expense.id = 999

    assert repository.update(expense) is False


def test_empty_database(repository):
    expenses = repository.get_all()

    assert expenses == []
