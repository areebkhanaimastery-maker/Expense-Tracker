from datetime import datetime
from models import Expense

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
        self.expenses: list[Expense] = []
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

        return True