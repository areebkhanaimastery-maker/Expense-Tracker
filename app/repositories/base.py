"""
Abstract Base Expense Repository Interface.
"""

from abc import ABC, abstractmethod

from app.models.expense import Expense


class ExpenseRepositoryInterface(ABC):
    """Abstract interface for expense data access."""

    @abstractmethod
    def add(self, expense: Expense) -> int:
        """Add a new expense and return its generated ID."""
        pass

    @abstractmethod
    def get_all(self) -> list[Expense]:
        """Retrieve all expenses sorted by date descending."""
        pass

    @abstractmethod
    def get_by_id(self, expense_id: int) -> Expense | None:
        """Retrieve an expense by ID or return None."""
        pass

    @abstractmethod
    def update(self, expense: Expense) -> bool:
        """Update an existing expense. Returns True if updated."""
        pass

    @abstractmethod
    def delete(self, expense_id: int) -> bool:
        """Delete an expense by ID. Returns True if deleted."""
        pass
