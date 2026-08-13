"""Database and Repository Exceptions."""

from app.exceptions.base import ExpenseTrackerError


class DatabaseError(ExpenseTrackerError):
    """Raised when a database operation fails."""
    pass


class RepositoryError(DatabaseError):
    """Raised when a repository operation fails."""
    pass
