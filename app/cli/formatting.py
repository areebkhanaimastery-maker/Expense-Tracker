"""
CLI Display Formatting Utilities.
"""

from app.models.expense import Expense
from app.utils.numbers import format_currency


def print_header(title: str, width: int = 50) -> None:
    """Print a styled section header."""
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width)


def print_subheader(title: str, width: int = 50) -> None:
    """Print a subheader."""
    print(f"\n--- {title} ---")


def display_expenses(expenses: list[Expense]) -> None:
    """Print expenses in a clean tabular view."""
    if not expenses:
        print("\nNo expenses found.")
        return

    print(
        f"\n{'ID':<5}"
        f"{'Amount':<15}"
        f"{'Category':<18}"
        f"{'Description':<25}"
        f"{'Date':<20}"
    )
    print("-" * 83)

    for expense in expenses:
        formatted_amount = format_currency(expense.amount)
        formatted_date = expense.date.strftime("%Y-%m-%d %H:%M")
        print(
            f"{expense.id:<5}"
            f"{formatted_amount:<15}"
            f"{expense.category:<18}"
            f"{expense.description:<25}"
            f"{formatted_date:<20}"
        )
