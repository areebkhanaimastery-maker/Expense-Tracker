"""Machine Learning Exceptions."""

from app.exceptions.base import ExpenseTrackerError


class MLModelError(ExpenseTrackerError):
    """Base exception for machine learning model errors."""
    pass


class PredictionError(MLModelError):
    """Raised when a prediction fails or insufficient data exists."""
    pass


class AnomalyDetectionError(MLModelError):
    """Raised when anomaly detection fails."""
    pass
