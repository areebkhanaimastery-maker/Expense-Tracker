from app.cli.app import ExpenseTrackerCLI
from app.repositories.sqlite_repository import (
    SQLiteExpenseRepository
)
from app.services.expense_service import ExpenseService
from app.logging_config import configure_logging
from app.config import settings


def main():

    configure_logging(settings.log_level)

    repository = SQLiteExpenseRepository()

    service = ExpenseService(repository)

    application = ExpenseTrackerCLI(service)

    application.run()


if __name__ == "__main__":
    main()