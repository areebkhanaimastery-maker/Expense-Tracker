"""
AI Tools — functions that the AI assistant can invoke.

These tools act as the boundary between the AI layer
and the ExpenseService. The AI never touches SQLite directly.
"""

from collections import defaultdict


def get_spending_summary(service):
    """Get a summary of total spending."""

    expenses = service.get_all_expenses()

    total = sum(
        expense.amount
        for expense in expenses
    )

    return {
        "total": total,
        "count": len(expenses)
    }


def get_category_breakdown(service):
    """Get spending broken down by category."""

    expenses = service.get_all_expenses()

    category_totals = defaultdict(float)

    for expense in expenses:
        category_totals[expense.category] += expense.amount

    return dict(category_totals)
