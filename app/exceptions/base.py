"""Base Exception for the Expense Tracker Application."""


class ExpenseTrackerError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str = "An application error occurred."):
        super().__init__(message)
        self.message = message
