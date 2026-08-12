import logging
from app.config import settings
from app.logging_config import configure_logging
from app.exceptions import ExpenseTrackerError
from services import CATEGORIES
from services import ExpenseService
from validators import (
    validate_amount,
    validate_text,
    validate_id
)

configure_logging(settings.log_level)
logger = logging.getLogger(__name__)

service = ExpenseService()


def display_menu():
    print("\n" + "=" * 40)
    print("          EXPENSE TRACKER")
    print("=" * 40)
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Edit Expense")
    print("4. Delete Expense")
    print("5. Search Expenses")
    print("6. Filter Expenses")
    print("7. Reports")
    print("8. Exit")
    print("=" * 40)



def add_expense():
    print("\n--- Add Expense ---")

    try:
        amount = validate_amount(
            input("Amount: Rs. ")
        )

        category = select_category()

        description = validate_text(
            input("Description: "),
            "Description"
        )

        expense = service.add_expense(
            amount,
            category,
            description
        )

        logger.info("Expense created: id=%s", expense.id)
        print("\nExpense added successfully!")
        print(f"Expense ID: {expense.id}")

    except ExpenseTrackerError as error:
        logger.error("Error adding expense: %s", error)
        print(f"\nError: {error}")

def select_category():
    print("\nSelect Category:")

    for index, category in enumerate(CATEGORIES, start=1):
        print(f"{index}. {category}")

    while True:
        choice = input("Category: ").strip()

        try:
            choice = int(choice)

            if 1 <= choice <= len(CATEGORIES):
                return CATEGORIES[choice - 1]

            print("Please select a valid category.")

        except ValueError:
            print("Please enter a number.")


def display_expenses(expenses):
    if not expenses:
        print("\nNo expenses found.")
        return

    print(
        f"\n{'ID':<5}"
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


def view_expenses():
    print("\n--- Expenses ---")
    display_expenses(service.get_all_expenses())


def search_expenses():
    print("\n--- Search Expenses ---")

    keyword = input("Search: ").strip()

    if not keyword:
        print("Search cannot be empty.")
        return

    results = service.search_expenses(keyword)

    display_expenses(results)


def filter_expenses():
    print("\n--- Filter Expenses ---")
    print("1. By Category")
    print("2. By Amount")

    choice = input("Choose: ").strip()

    if choice == "1":
        category = select_category()
        results = service.filter_by_category(category)
        display_expenses(results)

    elif choice == "2":
        try:
            minimum = validate_amount(
                input("Minimum amount: Rs. ")
            )

            maximum = validate_amount(
                input("Maximum amount: Rs. ")
            )

            if minimum > maximum:
                print("Minimum cannot exceed maximum.")
                return

            results = service.filter_by_amount(
                minimum,
                maximum
            )

            display_expenses(results)

        except ExpenseTrackerError as error:
            logger.error("Error filtering expenses: %s", error)
            print(f"Error: {error}")

    else:
        print("Invalid option.")


def show_reports():
    print("\n--- Expense Reports ---")

    report = service.get_reports()

    if report["count"] == 0:
        print("No expenses available.")
        return

    print(f"\nTotal Expenses:   Rs. {report['total']:,.2f}")
    print(f"Number of Expenses: {report['count']}")
    print(f"Average Expense:  Rs. {report['average']:,.2f}")

    highest = report["highest"]
    lowest = report["lowest"]

    print(
        f"\nHighest Expense:  Rs. {highest.amount:,.2f}"
        f" ({highest.description})"
    )

    print(
        f"Lowest Expense:   Rs. {lowest.amount:,.2f}"
        f" ({lowest.description})"
    )

    print("\n--- Category Breakdown ---")

    for category, amount in report["categories"].items():
        print(f"{category:<20} Rs. {amount:,.2f}")


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

        logger.info("Expense updated: id=%s", expense_id)
        print("\nExpense updated successfully!")

    except ExpenseTrackerError as error:
        logger.error("Error editing expense: %s", error)
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
            logger.info("Expense deleted: id=%s", expense_id)
            print("Expense deleted successfully!")

        else:
            print("Deletion cancelled.")

    except ExpenseTrackerError as error:
        logger.error("Error deleting expense: %s", error)
        print(f"\nError: {error}")


def main():
    logger.info("Expense application started")
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
            search_expenses()

        elif choice == "6":
            filter_expenses()

        elif choice == "7":
            show_reports()

        elif choice == "8":
            print("\nThank you for using Expense Tracker.")
            logger.info("Expense application stopped")
            break

        else:
            print("\nInvalid option.")


if __name__ == "__main__":
    main()