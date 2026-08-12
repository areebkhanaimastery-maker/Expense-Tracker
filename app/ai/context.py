"""
AI Context — provides expense-derived information
to the AI layer without leaking database details.

This is the security boundary: the AI model receives
only sanitized, expense-level data.
"""


class ExpenseAIContext:

    def __init__(self, service):
        self.service = service

    def summary(self):
        """Build a context summary for the AI."""

        expenses = self.service.get_all_expenses()

        return {
            "expense_count": len(expenses),
            "total": sum(
                expense.amount
                for expense in expenses
            )
        }
