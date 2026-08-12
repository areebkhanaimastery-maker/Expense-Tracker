import logging

from app.cli.display import display_menu
from app.cli.handlers import (
    add_expense,
    view_expenses,
    edit_expense,
    delete_expense,
    search_expenses,
    filter_expenses,
    show_reports,
    show_analytics
)


logger = logging.getLogger(__name__)


class ExpenseTrackerCLI:

    def __init__(self, service, analytics=None):
        self.service = service
        self.analytics = analytics

    def run(self):

        logger.info("Expense application started")

        while True:

            display_menu()

            choice = input(
                "Choose an option: "
            ).strip()

            try:

                if choice == "1":
                    add_expense(self.service)

                elif choice == "2":
                    view_expenses(self.service)

                elif choice == "3":
                    edit_expense(self.service)

                elif choice == "4":
                    delete_expense(self.service)

                elif choice == "5":
                    search_expenses(self.service)

                elif choice == "6":
                    filter_expenses(self.service)

                elif choice == "7":
                    if self.analytics:
                        show_analytics(self.analytics)
                    else:
                        show_reports(self.service)

                elif choice == "8":
                    print(
                        "\nAI Assistant is not yet available."
                        "\nThis feature will be implemented"
                        " in Phase 4."
                    )

                elif choice == "9":
                    print(
                        "\nThank you for using"
                        " Expense Tracker."
                    )
                    logger.info(
                        "Expense application stopped"
                    )
                    break

                else:
                    print("\nInvalid option.")

            except Exception as error:

                logger.exception(
                    "Unexpected application error"
                )
                print(
                    f"\nUnexpected application error:"
                    f" {error}"
                )
