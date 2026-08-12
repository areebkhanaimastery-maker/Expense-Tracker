import pytest
from datetime import datetime

from models import Expense
from repository import ExpenseRepository
from app.exceptions import DatabaseError


def test_add_and_get_expense(tmp_path):

    database = tmp_path / "test.db"

    repository = ExpenseRepository(str(database))

    expense = Expense(
        id=0,
        amount=1500,
        category="Food",
        description="Dinner",
        date=datetime.now()
    )

    expense_id = repository.add(expense)

    result = repository.get_by_id(expense_id)

    assert result is not None
    assert result.amount == 1500
    assert result.category == "Food"
    assert result.description == "Dinner"


def test_delete_expense(tmp_path):

    database = tmp_path / "test.db"

    repository = ExpenseRepository(str(database))

    expense = Expense(
        id=0,
        amount=500,
        category="Transport",
        description="Taxi",
        date=datetime.now()
    )

    expense_id = repository.add(expense)

    assert repository.delete(expense_id) is True
    assert repository.get_by_id(expense_id) is None


def test_update_expense(tmp_path):

    database = tmp_path / "test.db"

    repository = ExpenseRepository(str(database))

    expense = Expense(
        id=0,
        amount=1000,
        category="Food",
        description="Lunch",
        date=datetime.now()
    )

    expense.id = repository.add(expense)

    expense.amount = 1500
    expense.description = "Dinner"

    assert repository.update(expense) is True

    updated = repository.get_by_id(expense.id)

    assert updated.amount == 1500
    assert updated.description == "Dinner"


def test_database_error_handling(tmp_path):
    # Attempting to open a directory as a database triggers an sqlite3 OperationalError
    invalid_db_path = tmp_path
    
    with pytest.raises(DatabaseError):
        ExpenseRepository(str(invalid_db_path))
