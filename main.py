from service import ExpenseService
from validators import (
    validate_amount,
    validate_text,
    validate_id
)


service = ExpenseService()


def display_menu():
    print("\n" + "=" * 40)
    print("          EXPENSE TRACKER")
    print("=" * 40)
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Edit Expense")
    print("4. Delete Expense")
    print("5. Exit")
    print("=" * 40)


def add_expense():
    print("\n--- Add Expense ---")

    try:
        amount = validate_amount(
            input("Amount: Rs. ")
        )

        category = validate_text(
            input("Category: "),
            "Category"
        )

        description = validate_text(
            input("Description: "),
            "Description"
        )

        expense = service.add_expense(
            amount,
            category,
            description
        )

        print("\nExpense added successfully!")
        print(f"Expense ID: {expense.id}")

    except ValueError as error:
        print(f"\nError: {error}")


def view_expenses():
    print("\n--- Expenses ---")

    expenses = service.get_all_expenses()

    if not expenses:
        print("No expenses found.")
        return

    print(
        f"{'ID':<5}"
        f"{'Amount':<15}"
        f"{'Category':<15}"
        f"{'Description':<20}"
        f"{'Date':<20}"
    )

    print("-" * 75)

    for expense in expenses:
        print(
            f"{expense.id:<5}"
            f"Rs. {expense.amount:<10.2f}"
            f"{expense.category:<15}"
            f"{expense.description:<20}"
            f"{expense.date.strftime('%Y-%m-%d %H:%M'):<20}"
        )


def edit_expense():
    print("\n--- Edit Expense ---")

    try:
        expense_id = validate_id(
            input("Expense ID: ")
        )

        expense = service.get_expense(expense_id)

        if expense is None:
            print("Expense not found.")
            return

        print("\nLeave a field empty to keep its current value.")

        amount_input = input(
            f"Amount [{expense.amount}]: Rs. "
        )

        category_input = input(
            f"Category [{expense.category}]: "
        )

        description_input = input(
            f"Description [{expense.description}]: "
        )

        amount = (
            expense.amount
            if not amount_input.strip()
            else validate_amount(amount_input)
        )

        category = (
            expense.category
            if not category_input.strip()
            else validate_text(category_input, "Category")
        )

        description = (
            expense.description
            if not description_input.strip()
            else validate_text(description_input, "Description")
        )

        service.edit_expense(
            expense_id,
            amount,
            category,
            description
        )

        print("\nExpense updated successfully!")

    except ValueError as error:
        print(f"\nError: {error}")


def delete_expense():
    print("\n--- Delete Expense ---")

    try:
        expense_id = validate_id(
            input("Expense ID: ")
        )

        expense = service.get_expense(expense_id)

        if expense is None:
            print("Expense not found.")
            return

        print(
            f"\nYou are deleting:"
            f"\nRs. {expense.amount:.2f}"
            f" | {expense.category}"
            f" | {expense.description}"
        )

        confirmation = input(
            "\nAre you sure? (y/n): "
        ).strip().lower()

        if confirmation == "y":
            service.delete_expense(expense_id)
            print("Expense deleted successfully!")

        else:
            print("Deletion cancelled.")

    except ValueError as error:
        print(f"\nError: {error}")


def main():
    while True:
        display_menu()

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_expense()

        elif choice == "2":
            view_expenses()

        elif choice == "3":
            edit_expense()

        elif choice == "4":
            delete_expense()

        elif choice == "5":
            print("\nThank you for using Expense Tracker.")
            break

        else:
            print("\nInvalid option. Please choose 1-5.")


if __name__ == "__main__":
    main()