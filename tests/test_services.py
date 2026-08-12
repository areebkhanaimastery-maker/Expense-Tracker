import pytest
from datetime import datetime

from models import Expense
from repository import ExpenseRepository
from services import ExpenseService


@pytest.fixture
def service(tmp_path):
    db_path = tmp_path / "test_services.db"
    repo = ExpenseRepository(str(db_path))
    return ExpenseService(repository=repo)


def test_add_expense(service):
    expense = service.add_expense(amount=100.50, category="Shopping", description="New shoes")
    
    assert expense.id > 0
    assert expense.amount == 100.50
    assert expense.category == "Shopping"
    assert expense.description == "New shoes"
    assert isinstance(expense.date, datetime)


def test_get_all_expenses(service):
    service.add_expense(amount=200, category="Food", description="Groceries")
    service.add_expense(amount=50, category="Transport", description="Bus fare")
    
    expenses = service.get_all_expenses()
    assert len(expenses) == 2
    # ExpenseRepository orders by date DESC, so the second one added is first in list
    assert expenses[0].description == "Bus fare"
    assert expenses[1].description == "Groceries"


def test_get_expense(service):
    expense = service.add_expense(amount=300, category="Bills", description="Electric bill")
    
    retrieved = service.get_expense(expense.id)
    assert retrieved is not None
    assert retrieved.id == expense.id
    assert retrieved.description == "Electric bill"


def test_delete_expense(service):
    expense = service.add_expense(amount=150, category="Entertainment", description="Movie")
    
    assert service.delete_expense(expense.id) is True
    assert service.get_expense(expense.id) is None
    assert service.delete_expense(999) is False  # Non-existent ID


def test_edit_expense(service):
    expense = service.add_expense(amount=400, category="Health", description="Medicine")
    
    # Edit amount and description
    assert service.edit_expense(expense.id, amount=450, category="Health", description="Vitamins") is True
    
    updated = service.get_expense(expense.id)
    assert updated.amount == 450
    assert updated.description == "Vitamins"
    
    # Edit with non-existent ID
    assert service.edit_expense(999, amount=10, category="Other", description="Test") is False


def test_search_expenses(service):
    service.add_expense(amount=10, category="Food", description="Burgers")
    service.add_expense(amount=20, category="Shopping", description="T-shirt")
    service.add_expense(amount=30, category="Other", description="Random burger gift")
    
    # Search for "burger" case-insensitive
    results = service.search_expenses("burger")
    assert len(results) == 2
    assert all("burger" in r.description.lower() for r in results)
    
    # Search by category
    results = service.search_expenses("shopping")
    assert len(results) == 1
    assert results[0].category == "Shopping"


def test_filter_by_category(service):
    service.add_expense(amount=10, category="Food", description="Burgers")
    service.add_expense(amount=20, category="Shopping", description="T-shirt")
    service.add_expense(amount=30, category="Food", description="Fries")
    
    results = service.filter_by_category("Food")
    assert len(results) == 2
    assert all(r.category == "Food" for r in results)


def test_filter_by_amount(service):
    service.add_expense(amount=10, category="Food", description="Burgers")
    service.add_expense(amount=50, category="Shopping", description="T-shirt")
    service.add_expense(amount=100, category="Bills", description="Electricity")
    
    results = service.filter_by_amount(15, 80)
    assert len(results) == 1
    assert results[0].amount == 50


def test_get_reports(service):
    # Empty reports
    empty_report = service.get_reports()
    assert empty_report["count"] == 0
    assert empty_report["total"] == 0
    
    # Add expenses
    service.add_expense(amount=10, category="Food", description="Burgers")
    service.add_expense(amount=30, category="Food", description="Pizza")
    service.add_expense(amount=60, category="Bills", description="Internet")
    
    report = service.get_reports()
    assert report["count"] == 3
    assert report["total"] == 100
    assert report["average"] == 100 / 3
    assert report["highest"].amount == 60
    assert report["lowest"].amount == 10
    assert report["categories"]["Food"] == 40
    assert report["categories"]["Bills"] == 60
