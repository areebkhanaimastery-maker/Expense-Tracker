"""Service Layer Exceptions."""

from app.exceptions.base import ExpenseTrackerError


class ServiceError(ExpenseTrackerError):
    """Raised when a service operation fails."""
    pass


class ExpenseNotFoundError(ServiceError):
    """Raised when an expense does not exist."""
    pass
