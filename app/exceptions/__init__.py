"""
Central Exception Module.

Re-exports all custom application exceptions for single-point importing.
"""

from app.exceptions.ai import (
    AIError,
    LLMUnavailableError,
    ToolExecutionError,
)
from app.exceptions.base import ExpenseTrackerError
from app.exceptions.config import ConfigurationError
from app.exceptions.database import DatabaseError, RepositoryError
from app.exceptions.ml import (
    AnomalyDetectionError,
    MLModelError,
    PredictionError,
)
from app.exceptions.service import ExpenseNotFoundError, ServiceError
from app.exceptions.validation import ValidationError

__all__ = [
    "ExpenseTrackerError",
    "DatabaseError",
    "RepositoryError",
    "ValidationError",
    "ServiceError",
    "ExpenseNotFoundError",
    "MLModelError",
    "PredictionError",
    "AnomalyDetectionError",
    "AIError",
    "LLMUnavailableError",
    "ToolExecutionError",
    "ConfigurationError",
]
