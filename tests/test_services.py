# pyrefly: ignore [missing-import]
import pytest
from datetime import datetime

from app.models.expense import Expense
from app.repositories.sqlite_repository import SQLiteExpenseRepository
from app.services.expense_service import ExpenseService
from app.exceptions import ExpenseNotFoundError


@pytest.fixture
def service(tmp_path):
    db_path = tmp_path / "test_services.db"
    repo = SQLiteExpenseRepository(db_path)
    return ExpenseService(repository=repo)


def test_add_expense(service):
    expense = service.add_expense(
        amount=100.50,
        category="Shopping",
        description="New shoes"
    )

    assert expense.id > 0
    assert expense.amount == 100.50
    assert expense.category == "Shopping"
    assert expense.description == "New shoes"
    assert isinstance(expense.date, datetime)


def test_get_all_expenses(service):
    service.add_expense(200, "Food", "Groceries")
    service.add_expense(50, "Transport", "Bus fare")

    expenses = service.get_all_expenses()
    assert len(expenses) == 2


def test_get_expense(service):
    expense = service.add_expense(300, "Bills", "Electric bill")

    retrieved = service.get_expense(expense.id)

    assert retrieved.id == expense.id
    assert retrieved.description == "Electric bill"


def test_get_expense_not_found(service):
    with pytest.raises(ExpenseNotFoundError, match="not found"):
        service.get_expense(999)


def test_delete_expense(service):
    expense = service.add_expense(150, "Entertainment", "Movie")

    service.delete_expense(expense.id)

    with pytest.raises(ExpenseNotFoundError):
        service.get_expense(expense.id)


def test_delete_expense_not_found(service):
    with pytest.raises(ExpenseNotFoundError, match="not found"):
        service.delete_expense(999)


def test_edit_expense(service):
    expense = service.add_expense(400, "Health", "Medicine")

    updated = service.edit_expense(
        expense.id,
        amount=450,
        category="Health",
        description="Vitamins"
    )

    assert updated.amount == 450
    assert updated.description == "Vitamins"

    retrieved = service.get_expense(expense.id)
    assert retrieved.amount == 450


def test_edit_expense_not_found(service):
    with pytest.raises(ExpenseNotFoundError, match="not found"):
        service.edit_expense(999, 10, "Other", "Test")


def test_search(service):
    service.add_expense(10, "Food", "Burgers")
    service.add_expense(20, "Shopping", "T-shirt")
    service.add_expense(30, "Other", "Random burger gift")

    results = service.search("burger")
    assert len(results) == 2
    assert all("burger" in r.description.lower() for r in results)


def test_search_by_category(service):
    service.add_expense(10, "Food", "Burgers")
    service.add_expense(20, "Shopping", "T-shirt")

    results = service.search("shopping")
    assert len(results) == 1
    assert results[0].category == "Shopping"


def test_filter_category(service):
    service.add_expense(10, "Food", "Burgers")
    service.add_expense(20, "Shopping", "T-shirt")
    service.add_expense(30, "Food", "Fries")

    results = service.filter_category("Food")
    assert len(results) == 2
    assert all(r.category == "Food" for r in results)


def test_filter_amount(service):
    service.add_expense(10, "Food", "Burgers")
    service.add_expense(50, "Shopping", "T-shirt")
    service.add_expense(100, "Bills", "Electricity")

    results = service.filter_amount(15, 80)
    assert len(results) == 1
    assert results[0].amount == 50
