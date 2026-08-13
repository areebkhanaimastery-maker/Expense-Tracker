"""AI & LLM Exceptions."""

from app.exceptions.base import ExpenseTrackerError


class AIError(ExpenseTrackerError):
    """Base exception for AI module errors."""
    pass


class LLMUnavailableError(AIError):
    """Raised when the LLM service/daemon is unreachable."""
    pass


class ToolExecutionError(AIError):
    """Raised when an AI tool execution fails."""
    pass
