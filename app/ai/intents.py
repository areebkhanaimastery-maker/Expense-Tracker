"""
AI Intents — defines the types of user intents
that the AI assistant can recognize and handle.
"""

from enum import Enum


class Intent(Enum):
    """User intents the AI can detect."""

    ADD_EXPENSE = "add_expense"
    VIEW_EXPENSES = "view_expenses"
    SPENDING_SUMMARY = "spending_summary"
    CATEGORY_BREAKDOWN = "category_breakdown"
    SEARCH = "search"
    UNKNOWN = "unknown"
