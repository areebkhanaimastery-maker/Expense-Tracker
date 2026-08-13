"""
Proxy for backward compatibility.
Re-exports ExpenseRepositoryInterface from app.repositories.base.
"""

from app.repositories.base import ExpenseRepositoryInterface

__all__ = ["ExpenseRepositoryInterface"]
