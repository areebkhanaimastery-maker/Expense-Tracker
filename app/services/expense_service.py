from collections import defaultdict
from datetime import datetime

from app.exceptions import ExpenseNotFoundError
from app.models.expense import Expense
from app.repositories.interface import ExpenseRepositoryInterface


class ExpenseService:

    def __init__(
        self,
        repository: ExpenseRepositoryInterface
    ):
        self.repository = repository

    def add_expense(
        self,
        amount: float,
        category: str,
        description: str,
        date_str: str | datetime | None = None,
        date: str | datetime | None = None,
    ) -> Expense:
        from app.utils.dates import parse_datetime
        dt_val = date_str or date
        parsed_dt = parse_datetime(dt_val) if dt_val else datetime.now()

        expense = Expense(
            id=0,
            amount=amount,
            category=category,
            description=description,
            date=parsed_dt
        )

        expense.id = self.repository.add(expense)

        return expense

    def get_all_expenses(self):
        return self.repository.get_all()

    def get_expense(self, expense_id):

        expense = self.repository.get_by_id(expense_id)

        if expense is None:
            raise ExpenseNotFoundError(
                f"Expense {expense_id} was not found."
            )

        return expense

    def delete_expense(self, expense_id):

        if not self.repository.delete(expense_id):
            raise ExpenseNotFoundError(
                f"Expense {expense_id} was not found."
            )

    def edit_expense(
        self,
        expense_id: int,
        amount: float | None = None,
        category: str | None = None,
        description: str | None = None,
        date_str: str | datetime | None = None,
        date: str | datetime | None = None,
    ):

        expense = self.get_expense(expense_id)

        if amount is not None:
            expense.amount = amount
        if category is not None:
            expense.category = category
        if description is not None:
            expense.description = description
        dt_val = date_str or date
        if dt_val is not None:
            from app.utils.dates import parse_datetime
            expense.date = parse_datetime(dt_val)

        self.repository.update(expense)

        return expense

    def search(self, keyword):

        keyword = keyword.lower().strip()

        expenses = self.get_all_expenses()

        return [
            expense
            for expense in expenses
            if keyword in expense.description.lower()
            or keyword in expense.category.lower()
        ]

    def filter_category(self, category):

        return [
            expense
            for expense in self.get_all_expenses()
            if expense.category.lower() == category.lower()
        ]

    def filter_amount(self, minimum, maximum):

        return [
            expense
            for expense in self.get_all_expenses()
            if minimum <= expense.amount <= maximum
        ]

    def get_reports(self):

        expenses = self.get_all_expenses()

        if not expenses:
            return {
                "total": 0,
                "count": 0,
                "average": 0,
                "highest": None,
                "lowest": None,
                "categories": {}
            }

        total = sum(expense.amount for expense in expenses)

        category_totals = defaultdict(float)

        for expense in expenses:
            category_totals[expense.category] += expense.amount

        return {
            "total": total,
            "count": len(expenses),
            "average": total / len(expenses),
            "highest": max(
                expenses,
                key=lambda expense: expense.amount
            ),
            "lowest": min(
                expenses,
                key=lambda expense: expense.amount
            ),
            "categories": dict(category_totals)
        }
