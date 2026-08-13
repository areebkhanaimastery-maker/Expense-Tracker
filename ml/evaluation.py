"""
Evaluation metrics for machine learning models.
"""
from typing import List


def mean_absolute_error(y_true: List[float], y_pred: List[float]) -> float:
    """Calculate the Mean Absolute Error (MAE) between true and predicted values."""
    if not y_true or len(y_true) != len(y_pred):
        raise ValueError("Inputs must be non-empty and of equal length.")
    return sum(abs(t - p) for t, p in zip(y_true, y_pred)) / len(y_true)


def mean_squared_error(y_true: List[float], y_pred: List[float]) -> float:
    """Calculate the Mean Squared Error (MSE) between true and predicted values."""
    if not y_true or len(y_true) != len(y_pred):
        raise ValueError("Inputs must be non-empty and of equal length.")
    return sum((t - p) ** 2 for t, p in zip(y_true, y_pred)) / len(y_true)


def classification_accuracy(y_true: List[int], y_pred: List[int]) -> float:
    """Calculate accuracy for classification tasks (e.g., category prediction)."""
    if not y_true or len(y_true) != len(y_pred):
        raise ValueError("Inputs must be non-empty and of equal length.")
    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    return correct / len(y_true)
