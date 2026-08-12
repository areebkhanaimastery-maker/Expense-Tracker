from collections import defaultdict
from datetime import datetime
from models import Expense
from repository import ExpenseRepository

CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Education",
    "Other"
]

class ExpenseService:

    def __init__(self, repository=None):
        self.repository = repository or ExpenseRepository()

    def add_expense(
        self,
        amount: float,
        category: str,
        description: str
    ) -> Expense:

        expense = Expense(
            id=0,
            amount=amount,
            category=category,
            description=description,
            date=datetime.now()
        )

        expense.id = self.repository.add(expense)

        return expense

    def get_all_expenses(self) -> list[Expense]:
        return self.repository.get_all()

    def get_expense(self, expense_id: int) -> Expense | None:
        return self.repository.get_by_id(expense_id)

    def delete_expense(self, expense_id: int) -> bool:
        return self.repository.delete(expense_id)

    def edit_expense(
        self,
        expense_id: int,
        amount: float,
        category: str,
        description: str
    ) -> bool:

        expense = self.repository.get_by_id(expense_id)

        if expense is None:
            return False

        expense.amount = amount
        expense.category = category
        expense.description = description

        return self.repository.update(expense)

    def search_expenses(self, keyword: str) -> list[Expense]:
        keyword = keyword.lower().strip()
        expenses = self.repository.get_all()

        return [
            expense
            for expense in expenses
            if keyword in expense.description.lower()
            or keyword in expense.category.lower()
        ]

    def filter_by_category(self, category: str) -> list[Expense]:
        expenses = self.repository.get_all()
        return [
            expense
            for expense in expenses
            if expense.category.lower() == category.lower()
        ]

    def filter_by_amount(
        self,
        minimum: float,
        maximum: float
    ) -> list[Expense]:
        expenses = self.repository.get_all()

        return [
            expense
            for expense in expenses
            if minimum <= expense.amount <= maximum
        ]

    def get_reports(self) -> dict:
        expenses = self.repository.get_all()
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
