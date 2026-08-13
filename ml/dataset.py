"""
Dataset loading and splitting for the ML pipeline.
"""
from typing import List, Tuple
from app.models.expense import Expense


def load_dataset(repository) -> List[Expense]:
    """Retrieve all expenses from the repository."""
    return repository.get_all()


def train_test_split_dataset(
    expenses: List[Expense], 
    test_size: float = 0.2
) -> Tuple[List[Expense], List[Expense]]:
    """
    Split a list of expenses into training and testing sets.
    
    Preserves chronological order (time-based split) for time-series forecasting
    and spending prediction.
    """
    if not expenses:
        return [], []
        
    split_index = int(len(expenses) * (1 - test_size))
    # Ensure they are sorted chronologically
    sorted_expenses = sorted(expenses, key=lambda e: e.date)
    return sorted_expenses[:split_index], sorted_expenses[split_index:]
