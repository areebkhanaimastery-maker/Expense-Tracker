"""Configuration Exceptions."""

from app.exceptions.base import ExpenseTrackerError


class ConfigurationError(ExpenseTrackerError):
    """Raised when application configuration is invalid."""
    pass
