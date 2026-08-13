def display_menu():

    print("\n" + "=" * 45)
    print("              EXPENSE TRACKER")
    print("=" * 45)

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


def display_expenses(expenses):

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

        print(
            f"{expense.id:<5}"
            f"Rs. {expense.amount:<10.2f}"
            f"{expense.category:<18}"
            f"{expense.description:<25}"
            f"{expense.date.strftime('%Y-%m-%d %H:%M'):<20}"
        )
