import logging

from app.exceptions import (
    ValidationError,
    ExpenseNotFoundError,
    ExpenseTrackerError
)

from app.validators.expense_validator import (
    validate_amount,
    validate_description,
    validate_id,
    CATEGORIES
)

from app.cli.display import display_expenses


logger = logging.getLogger(__name__)


def add_expense(service):

    print("\n--- Add Expense ---")

    try:

        amount = validate_amount(
            input("Amount: Rs. ")
        )

        print("\nCategories:")

        for index, category in enumerate(
            CATEGORIES,
            start=1
        ):
            print(f"{index}. {category}")

        choice = int(input("Category: "))

        if not 1 <= choice <= len(CATEGORIES):
            raise ValidationError(
                "Invalid category."
            )

        category = CATEGORIES[choice - 1]

        description = validate_description(
            input("Description: ")
        )

        expense = service.add_expense(
            amount,
            category,
            description
        )

        logger.info("Expense created: id=%s", expense.id)
        print(
            f"\nExpense #{expense.id} added successfully."
        )

    except (ValidationError, ValueError) as error:

        logger.error("Error adding expense: %s", error)
        print(f"\nError: {error}")


def view_expenses(service):

    print("\n--- Expenses ---")

    expenses = service.get_all_expenses()

    display_expenses(expenses)


def edit_expense(service):

    print("\n--- Edit Expense ---")

    try:

        expense_id = validate_id(
            input("Expense ID: ")
        )

        expense = service.get_expense(expense_id)

        print("\nLeave a field empty to keep its current value.")

        amount_input = input(
            f"Amount [{expense.amount}]: Rs. "
        )

        print("\nCategories:")
        for index, category in enumerate(
            CATEGORIES,
            start=1
        ):
            print(f"{index}. {category}")

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

        if category_input.strip():
            try:
                choice = int(category_input)
                if 1 <= choice <= len(CATEGORIES):
                    category = CATEGORIES[choice - 1]
                else:
                    raise ValidationError(
                        "Invalid category."
                    )
            except ValueError:
                raise ValidationError(
                    "Please enter a category number."
                )
        else:
            category = expense.category

        description = (
            expense.description
            if not description_input.strip()
            else validate_description(description_input)
        )

        service.edit_expense(
            expense_id,
            amount,
            category,
            description
        )

        logger.info("Expense updated: id=%s", expense_id)
        print("\nExpense updated successfully!")

    except (
        ValidationError,
        ExpenseNotFoundError
    ) as error:
        logger.error("Error editing expense: %s", error)
        print(f"\nError: {error}")


def delete_expense(service):

    print("\n--- Delete Expense ---")

    try:

        expense_id = validate_id(
            input("Expense ID: ")
        )

        expense = service.get_expense(expense_id)

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
            logger.info(
                "Expense deleted: id=%s", expense_id
            )
            print("Expense deleted successfully!")

        else:
            print("Deletion cancelled.")

    except (
        ValidationError,
        ExpenseNotFoundError
    ) as error:
        logger.error("Error deleting expense: %s", error)
        print(f"\nError: {error}")


def search_expenses(service):

    print("\n--- Search Expenses ---")

    keyword = input("Search: ").strip()

    if not keyword:
        print("Search cannot be empty.")
        return

    results = service.search(keyword)

    display_expenses(results)


def filter_expenses(service):

    print("\n--- Filter Expenses ---")
    print("1. By Category")
    print("2. By Amount")

    choice = input("Choose: ").strip()

    if choice == "1":

        print("\nCategories:")
        for index, category in enumerate(
            CATEGORIES,
            start=1
        ):
            print(f"{index}. {category}")

        try:
            cat_choice = int(input("Category: "))
            if 1 <= cat_choice <= len(CATEGORIES):
                category = CATEGORIES[cat_choice - 1]
            else:
                print("Invalid category.")
                return
        except ValueError:
            print("Please enter a number.")
            return

        results = service.filter_category(category)
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

            results = service.filter_amount(
                minimum,
                maximum
            )

            display_expenses(results)

        except ExpenseTrackerError as error:
            logger.error(
                "Error filtering expenses: %s", error
            )
            print(f"Error: {error}")

    else:
        print("Invalid option.")


def show_reports(service):

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


def show_analytics(analytics):

    print("\n" + "=" * 50)
    print("              ANALYTICS & REPORTS")
    print("=" * 50)

    total = analytics.total_spending()
    count = analytics.expense_count()
    average = analytics.average_expense()

    if count == 0:
        print("\nNo expenses available.")
        return

    print(f"\nTotal Spending : Rs. {total:,.2f}")
    print(f"Transactions   : {count}")
    print(f"Average        : Rs. {average:,.2f}")

    highest = analytics.highest_expense()

    if highest:
        print(
            f"Largest Expense: "
            f"Rs. {highest.amount:,.2f} "
            f"({highest.category} — {highest.description})"
        )

    print("\nCategory Breakdown:")

    categories = analytics.category_totals()
    percentages = analytics.category_percentages()

    for category, amount in categories.items():
        percentage = percentages.get(category, 0)
        print(
            f"{category:<18}"
            f"Rs. {amount:>10,.2f}"
            f"  ({percentage:>5.1f}%)"
        )

    print("\nMonthly Spending:")

    for month, amount in analytics.monthly_totals().items():
        print(
            f"{month}: Rs. {amount:,.2f}"
        )

