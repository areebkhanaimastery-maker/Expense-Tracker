"""
Proxy module for backward compatibility.
Re-exports CLI handlers from app.cli.commands.
"""

from app.cli.commands import (
    add_expense,
    delete_expense,
    edit_expense,
    filter_expenses,
    search_expenses,
    show_analytics,
    show_reports,
    start_ai_assistant,
    view_expenses,
)

__all__ = [
    "add_expense",
    "view_expenses",
    "edit_expense",
    "delete_expense",
    "search_expenses",
    "filter_expenses",
    "show_reports",
    "show_analytics",
    "start_ai_assistant",
]
