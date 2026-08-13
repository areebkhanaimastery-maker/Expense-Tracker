"""
CLI Menu Definitions.
"""

from app.cli.formatting import print_header


def display_menu() -> None:
    """Display the main application menu."""
    print_header("EXPENSE TRACKER", width=45)
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Edit Expense")
    print("4. Delete Expense")
    print("5. Search Expenses")
    print("6. Filter Expenses")
    print("7. Reports")
    print("8. Analytics")
    print("9. AI Expense Assistant")
    print("10. Exit")
    print("=" * 45)
