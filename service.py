from collections import defaultdict
from datetime import datetime
from models import Expense
from storage import load_expenses, save_expenses

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

    def __init__(self):
        self.expenses = load_expenses()

        if self.expenses:
            self.next_id = max(
                expense.id for expense in self.expenses
            ) + 1
        else:
            self.next_id = 1

    def add_expense(
        self,
        amount: float,
        category: str,
        description: str
    ) -> Expense:

        expense = Expense(
            id=self.next_id,
            amount=amount,
            category=category,
            description=description,
            date=datetime.now()
        )

        self.expenses.append(expense)
        self.next_id += 1
        save_expenses(self.expenses)

        return expense

    def get_all_expenses(self) -> list[Expense]:
        return self.expenses

    def get_expense(self, expense_id: int) -> Expense | None:
        for expense in self.expenses:
            if expense.id == expense_id:
                return expense

        return None

    def delete_expense(self, expense_id: int) -> bool:
        expense = self.get_expense(expense_id)

        if expense is None:
            return False

        self.expenses.remove(expense)
        save_expenses(self.expenses)
        return True

    def edit_expense(
        self,
        expense_id: int,
        amount: float,
        category: str,
        description: str
    ) -> bool:

        expense = self.get_expense(expense_id)

        if expense is None:
            return False

        expense.amount = amount
        expense.category = category
        expense.description = description

        save_expenses(self.expenses)
        return True

    def search_expenses(self, keyword: str) -> list[Expense]:
        keyword = keyword.lower().strip()

        return [
            expense
            for expense in self.expenses
            if keyword in expense.description.lower()
            or keyword in expense.category.lower()
        ]

    def filter_by_category(self, category: str) -> list[Expense]:
        return [
            expense
            for expense in self.expenses
            if expense.category.lower() == category.lower()
        ]

    def filter_by_amount(
        self,
        minimum: float,
        maximum: float
    ) -> list[Expense]:

        return [
            expense
            for expense in self.expenses
            if minimum <= expense.amount <= maximum
        ]

    def get_reports(self) -> dict:
        if not self.expenses:
            return {
                "total": 0,
                "count": 0,
                "average": 0,
                "highest": None,
                "lowest": None,
                "categories": {}
            }

        total = sum(expense.amount for expense in self.expenses)

        category_totals = defaultdict(float)

        for expense in self.expenses:
            category_totals[expense.category] += expense.amount

        return {
            "total": total,
            "count": len(self.expenses),
            "average": total / len(self.expenses),
            "highest": max(
                self.expenses,
                key=lambda expense: expense.amount
            ),
            "lowest": min(
                self.expenses,
                key=lambda expense: expense.amount
            ),
            "categories": dict(category_totals)
        }