class ExpenseTrackerError(Exception):
    """Base exception for the application."""


class ValidationError(ExpenseTrackerError):
    """Raised when user input is invalid."""


class ExpenseNotFoundError(ExpenseTrackerError):
    """Raised when an expense does not exist."""


class DatabaseError(ExpenseTrackerError):
    """Raised when a database operation fails."""


class ConfigurationError(ExpenseTrackerError):
    """Raised when application configuration is invalid."""
