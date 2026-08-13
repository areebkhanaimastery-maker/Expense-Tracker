"""
Shared Pytest Fixtures for Unit and Integration Testing.
"""

from datetime import datetime
import pytest

from app.database.initialization import init_db
from app.models.expense import Expense
from app.repositories.expense_repository import SQLiteExpenseRepository
from app.services.expense_service import ExpenseService
from app.services.analytics_service import AnalyticsService


@pytest.fixture
def temp_db(tmp_path):
    """Fixture providing a temporary SQLite database path."""
    db_file = tmp_path / "test_expenses.db"
    init_db(db_file)
    return db_file


@pytest.fixture
def sample_expenses():
    """Fixture providing sample Expense objects."""
    return [
        Expense(
            id=1,
            amount=500.0,
            category="Food",
            description="Lunch",
            date=datetime(2026, 8, 1, 12, 0),
        ),
        Expense(
            id=2,
            amount=1500.0,
            category="Transport",
            description="Fuel",
            date=datetime(2026, 8, 2, 9, 30),
        ),
        Expense(
            id=3,
            amount=12000.0,
            category="Bills",
            description="Electricity bill",
            date=datetime(2026, 8, 5, 14, 0),
        ),
    ]


@pytest.fixture
def repository(temp_db):
    """Fixture providing a clean SQLiteExpenseRepository with temporary database."""
    return SQLiteExpenseRepository(database=temp_db)


@pytest.fixture
def expense_service(repository):
    """Fixture providing an ExpenseService instance."""
    return ExpenseService(repository)


@pytest.fixture
def analytics_service(repository):
    """Fixture providing an AnalyticsService instance."""
    return AnalyticsService(repository)
