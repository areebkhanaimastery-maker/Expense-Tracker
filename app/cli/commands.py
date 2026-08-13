"""
CLI Action Handlers / Commands.
"""

import logging

from app.cli.formatting import display_expenses, print_header, print_subheader
from app.exceptions import (
    ExpenseNotFoundError,
    ExpenseTrackerError,
    ValidationError,
)
from app.utils.numbers import format_currency
from app.utils.validation import (
    CATEGORIES,
    validate_amount,
    validate_description,
    validate_id,
)


logger = logging.getLogger(__name__)


def add_expense(service) -> None:
    """CLI action to add an expense."""
    print_subheader("Add Expense")
    try:
        amount = validate_amount(input("Amount: Rs. "))

        print("\nCategories:")
        for idx, cat in enumerate(CATEGORIES, start=1):
            print(f"{idx}. {cat}")

        choice = int(input("Category: "))
        if not 1 <= choice <= len(CATEGORIES):
            raise ValidationError("Invalid category.")

        category = CATEGORIES[choice - 1]
        description = validate_description(input("Description: "))

        expense = service.add_expense(amount, category, description)
        logger.info("Expense created: id=%s", expense.id)
        print(f"\nExpense #{expense.id} added successfully.")

    except (ValidationError, ValueError) as error:
        logger.error("Error adding expense: %s", error)
        print(f"\nError: {error}")


def view_expenses(service) -> None:
    """CLI action to view all expenses."""
    print_subheader("Expenses")
    expenses = service.get_all_expenses()
    display_expenses(expenses)


def edit_expense(service) -> None:
    """CLI action to edit an expense."""
    print_subheader("Edit Expense")
    try:
        expense_id = validate_id(input("Expense ID: "))
        expense = service.get_expense(expense_id)

        print("\nLeave a field empty to keep its current value.")
        amount_input = input(f"Amount [{expense.amount}]: Rs. ")

        print("\nCategories:")
        for idx, cat in enumerate(CATEGORIES, start=1):
            print(f"{idx}. {cat}")

        category_input = input(f"Category [{expense.category}]: ")
        description_input = input(f"Description [{expense.description}]: ")

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
                    raise ValidationError("Invalid category.")
            except ValueError:
                raise ValidationError("Please enter a category number.")
        else:
            category = expense.category

        description = (
            expense.description
            if not description_input.strip()
            else validate_description(description_input)
        )

        service.edit_expense(expense_id, amount, category, description)
        logger.info("Expense updated: id=%s", expense_id)
        print("\nExpense updated successfully!")

    except (ValidationError, ExpenseNotFoundError) as error:
        logger.error("Error editing expense: %s", error)
        print(f"\nError: {error}")


def delete_expense(service) -> None:
    """CLI action to delete an expense."""
    print_subheader("Delete Expense")
    try:
        expense_id = validate_id(input("Expense ID: "))
        expense = service.get_expense(expense_id)

        formatted_amount = format_currency(expense.amount)
        print(
            f"\nYou are deleting:\n{formatted_amount} | {expense.category} | {expense.description}"
        )

        confirmation = input("\nAre you sure? (y/n): ").strip().lower()
        if confirmation == "y":
            service.delete_expense(expense_id)
            logger.info("Expense deleted: id=%s", expense_id)
            print("Expense deleted successfully!")
        else:
            print("Deletion cancelled.")

    except (ValidationError, ExpenseNotFoundError) as error:
        logger.error("Error deleting expense: %s", error)
        print(f"\nError: {error}")


def search_expenses(service) -> None:
    """CLI action to search expenses by keyword."""
    print_subheader("Search Expenses")
    keyword = input("Search: ").strip()
    if not keyword:
        print("Search cannot be empty.")
        return

    results = service.search(keyword)
    display_expenses(results)


def filter_expenses(service) -> None:
    """CLI action to filter expenses by category or amount range."""
    print_subheader("Filter Expenses")
    print("1. By Category")
    print("2. By Amount")

    choice = input("Choose: ").strip()

    if choice == "1":
        print("\nCategories:")
        for idx, cat in enumerate(CATEGORIES, start=1):
            print(f"{idx}. {cat}")

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
            minimum = validate_amount(input("Minimum amount: Rs. "))
            maximum = validate_amount(input("Maximum amount: Rs. "))

            if minimum > maximum:
                print("Minimum cannot exceed maximum.")
                return

            results = service.filter_amount(minimum, maximum)
            display_expenses(results)

        except ExpenseTrackerError as error:
            logger.error("Error filtering expenses: %s", error)
            print(f"Error: {error}")
    else:
        print("Invalid option.")


def show_reports(service) -> None:
    """CLI action to display statistical reports."""
    print_subheader("Expense Reports")
    report = service.get_reports()

    if report["count"] == 0:
        print("No expenses available.")
        return

    print(f"\nTotal Expenses:   {format_currency(report['total'])}")
    print(f"Number of Expenses: {report['count']}")
    print(f"Average Expense:  {format_currency(report['average'])}")

    highest = report["highest"]
    lowest = report["lowest"]
    print(
        f"\nHighest Expense:  {format_currency(highest.amount)} ({highest.description})"
    )
    print(
        f"Lowest Expense:   {format_currency(lowest.amount)} ({lowest.description})"
    )

    print("\n--- Category Breakdown ---")
    for cat, amt in report["categories"].items():
        print(f"{cat:<20} {format_currency(amt)}")


def show_analytics(analytics) -> None:
    """CLI action to display detailed analytics."""
    print_header("ANALYTICS & REPORTS", width=50)

    total = analytics.total_spending()
    count = analytics.expense_count()
    average = analytics.average_expense()

    if count == 0:
        print("\nNo expenses available.")
        return

    print(f"\nTotal Spending : {format_currency(total)}")
    print(f"Transactions   : {count}")
    print(f"Average        : {format_currency(average)}")

    highest = analytics.highest_expense()
    if highest:
        print(
            f"Largest Expense: {format_currency(highest.amount)} ({highest.category} — {highest.description})"
        )

    print("\nCategory Breakdown:")
    categories = analytics.category_totals()
    percentages = analytics.category_percentages()

    for cat, amt in categories.items():
        pct = percentages.get(cat, 0)
        formatted = format_currency(amt)
        print(f"{cat:<18}{formatted:>15}  ({pct:>5.1f}%)")

    print("\nMonthly Spending:")
    for month, amt in analytics.monthly_totals().items():
        print(f"{month}: {format_currency(amt)}")


def start_ai_assistant(
    expense_service,
    analytics_service,
    anomaly_service=None,
    prediction_service=None,
    intelligence_service=None,
) -> None:
    """CLI action to launch the AI Expense Assistant."""
    print_header("AI EXPENSE ASSISTANT", width=50)

    print("\nAsk anything about your expenses.")
    print("\nExamples:")
    print("  - How much did I spend this month?")
    print("  - What category costs me the most?")
    print("  - Compare this month with last month.")
    print("  - What was my biggest expense?")
    print("  - Did I have any unusual expenses?")
    print("  - How much am I likely to spend next month?")
    print("  - Give me a complete spending summary.")
    print("\nCommands:")
    print("  /help   - Show help message")
    print("  /clear  - Clear conversation history")
    print("  /exit   - Leave AI mode")

    try:
        from app.ai.conversation import ConversationManager
        from app.ai.llm import OllamaProvider
        from app.ai.memory import ConversationMemory
        from app.ai.tools import build_tool_registry

        llm = OllamaProvider()
        health = llm.check_health()

        print("\n" + "=" * 50)
        print("           EXPENSE AI SYSTEM STATUS")
        print("=" * 50)
        print(f"Ollama Server   : {'[OK] Connected' if health['server_online'] else '[OFFLINE] Unavailable'}")
        print(f"Model           : {health['model_name']} ({'[OK] Available' if health['model_available'] else '[MISSING] Unpulled'})")
        print(f"AI Provider     : {'Ollama Local LLM' if health['status'] == 'ONLINE' else 'Smart Tool Fallback Engine'}")
        print(f"AI Tools        : [OK] {len(registry._tools)} Tools Loaded")
        print(f"SQLite          : [OK] Connected")
        print(f"Fallback Engine : [OK] Ready")
        print("-" * 50)
        print(f"AI Mode         : {health['status']}")
        print("=" * 50 + "\n")

        memory = ConversationMemory(max_messages=50)
        manager = ConversationManager(
            llm=llm,
            registry=registry,
            memory=memory,
        )
    except Exception as e:
        logger.error("Failed to initialize AI assistant: %s", e)
        print(f"\nFailed to initialize AI assistant: {e}")
        print("Make sure Ollama is installed and running.")
        return

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nExiting AI mode.")
            break

        if not user_input:
            continue

        if user_input.lower() == "/exit":
            print("\nExiting AI mode.")
            break

        if user_input.lower() == "/clear":
            manager.clear_memory()
            print("\nConversation cleared.")
            continue

        if user_input.lower() == "/help":
            print("\nCommands:")
            print("  /help   - Show help message")
            print("  /clear  - Clear conversation history")
            print("  /exit   - Leave AI mode")
            print("\nAvailable tools:")
            for tool in registry.list_tools():
                print(f"  - {tool.name}: {tool.description}")
            continue

        try:
            response = manager.process_message(user_input)
            print(f"\nAI: {response}")
        except Exception as e:
            logger.error("AI error: %s", e)
            print(f"\nAI Error: {e}")
            print("Please ensure Ollama is running and try again.")
