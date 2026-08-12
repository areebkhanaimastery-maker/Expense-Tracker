"""
Feature Engineering for ML models.

Transforms raw Expense objects into numerical feature
vectors suitable for machine learning.
"""


def build_features(expenses):
    """
    Build feature vectors from a list of expenses.

    Each feature vector contains:
    - amount
    - day of week (0=Monday, 6=Sunday)
    - day of month (1-31)
    - month (1-12)
    """

    return [
        [
            expense.amount,
            expense.date.weekday(),
            expense.date.day,
            expense.date.month
        ]
        for expense in expenses
    ]
