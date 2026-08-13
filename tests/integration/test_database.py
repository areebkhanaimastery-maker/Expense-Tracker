"""
Integration tests for Database initialization, connections, and transactions.
"""

from datetime import datetime

from app.database.connection import get_db_connection
from app.database.initialization import init_db, verify_schema
from app.models.expense import Expense
from app.repositories.expense_repository import SQLiteExpenseRepository


def test_db_init_and_verify_schema(temp_db):
    assert verify_schema(temp_db)


def test_db_transaction_commit(temp_db):
    repo = SQLiteExpenseRepository(database=temp_db)
    exp = Expense(
        id=None,
        amount=100.0,
        category="Food",
        description="Coffee",
        date=datetime.now(),
    )
    exp_id = repo.add(exp)
    assert exp_id > 0

    fetched = repo.get_by_id(exp_id)
    assert fetched is not None
    assert fetched.amount == 100.0
