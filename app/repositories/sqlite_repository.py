"""
Proxy for backward compatibility.
Re-exports SQLiteExpenseRepository from app.repositories.expense_repository.
"""

from app.repositories.expense_repository import SQLiteExpenseRepository

__all__ = ["SQLiteExpenseRepository"]
