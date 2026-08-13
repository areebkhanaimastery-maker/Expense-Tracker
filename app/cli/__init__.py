"""
CLI Package.
"""

from app.cli.app import ExpenseTrackerCLI
from app.cli.commands import start_ai_assistant
from app.cli.formatting import display_expenses
from app.cli.menus import display_menu

__all__ = [
    "ExpenseTrackerCLI",
    "display_menu",
    "display_expenses",
    "start_ai_assistant",
]
