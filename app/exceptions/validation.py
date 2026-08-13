"""Validation Exceptions."""

from app.exceptions.base import ExpenseTrackerError


class ValidationError(ExpenseTrackerError):
    """Raised when input validation fails."""
    pass
