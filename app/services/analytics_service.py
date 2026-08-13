from collections import defaultdict
from datetime import datetime


class AnalyticsService:
    """Provides analytical and statistical operations over expense data."""

    def __init__(self, repository):
        self.repository = repository

    def get_all_expenses(self):
        """Retrieve all expenses from the repository."""
        return self.repository.get_all()

    def total_spending(self) -> float:
        """Return total amount spent."""
        return sum(
            expense.amount
            for expense in self.get_all_expenses()
        )

    def expense_count(self) -> int:
        """Return total number of expenses."""
        return len(self.get_all_expenses())

    def average_expense(self) -> float:
        """Return average expense amount."""
        expenses = self.get_all_expenses()

        if not expenses:
            return 0.0

        return self.total_spending() / len(expenses)

    def highest_expense(self):
        """Return the largest expense."""
        expenses = self.get_all_expenses()

        if not expenses:
            return None

        return max(
            expenses,
            key=lambda expense: expense.amount
        )

    def lowest_expense(self):
        """Return the smallest expense."""
        expenses = self.get_all_expenses()

        if not expenses:
            return None

        return min(
            expenses,
            key=lambda expense: expense.amount
        )

    def category_totals(self) -> dict[str, float]:
        """Return total spending grouped by category."""

        totals = defaultdict(float)

        for expense in self.get_all_expenses():
            totals[expense.category] += expense.amount

        return dict(totals)

    def category_percentages(self) -> dict[str, float]:
        """Return percentage of total spending per category."""

        total = self.total_spending()

        if total == 0:
            return {}

        return {
            category: (amount / total) * 100
            for category, amount
            in self.category_totals().items()
        }

    def category_count(self) -> dict[str, int]:
        """Return number of transactions per category."""

        counts = defaultdict(int)

        for expense in self.get_all_expenses():
            counts[expense.category] += 1

        return dict(counts)

    def monthly_totals(self) -> dict[str, float]:
        """Return spending grouped by month (YYYY-MM)."""

        totals = defaultdict(float)

        for expense in self.get_all_expenses():

            month = expense.date.strftime("%Y-%m")

            totals[month] += expense.amount

        return dict(totals)

    def daily_totals(self) -> dict[str, float]:
        """Return spending grouped by date (YYYY-MM-DD)."""

        totals = defaultdict(float)

        for expense in self.get_all_expenses():

            day = expense.date.strftime("%Y-%m-%d")

            totals[day] += expense.amount

        return dict(totals)

    def current_month_expenses(self):
        """Return expenses from the current month."""

        now = datetime.now()

        return [
            expense
            for expense in self.get_all_expenses()
            if (
                expense.date.year == now.year
                and expense.date.month == now.month
            )
        ]

    def current_month_total(self) -> float:
        """Return total spending for the current month."""

        return sum(
            expense.amount
            for expense in self.current_month_expenses()
        )

    def previous_month_expenses(self):
        """Return expenses from the previous month."""

        now = datetime.now()

        if now.month == 1:
            year = now.year - 1
            month = 12
        else:
            year = now.year
            month = now.month - 1

        return [
            expense
            for expense in self.get_all_expenses()
            if (
                expense.date.year == year
                and expense.date.month == month
            )
        ]

    def previous_month_total(self) -> float:
        """Return total spending for previous month."""

        return sum(
            expense.amount
            for expense in self.previous_month_expenses()
        )

    def monthly_change(self) -> dict:
        """Compare current month spending with previous month spending."""

        current = self.current_month_total()
        previous = self.previous_month_total()

        difference = current - previous

        if previous == 0:
            percentage = None
        else:
            percentage = (difference / previous) * 100

        return {
            "current": current,
            "previous": previous,
            "difference": difference,
            "percentage": percentage
        }

    def category_total(
        self,
        category: str,
        expenses=None
    ) -> float:
        """Return spending for a specific category."""

        if expenses is None:
            expenses = self.get_all_expenses()

        return sum(
            expense.amount
            for expense in expenses
            if expense.category.lower() == category.lower()
        )

    def monthly_category_totals(self) -> dict[str, dict[str, float]]:
        """Return monthly breakdown matrix grouped by category."""

        results = defaultdict(
            lambda: defaultdict(float)
        )

        for expense in self.get_all_expenses():

            month = expense.date.strftime("%Y-%m")

            results[month][expense.category] += (
                expense.amount
            )

        return {
            month: dict(categories)
            for month, categories
            in results.items()
        }

    def spending_summary(self) -> dict:
        """Return a complete aggregated spending summary."""
        highest = self.highest_expense()
        lowest = self.lowest_expense()

        tot = self.total_spending()
        cnt = self.expense_count()
        avg = self.average_expense()
        cats = self.category_totals()
        cat_pcts = self.category_percentages()

        return {
            "total": tot,
            "count": cnt,
            "average": avg,
            "highest": highest,
            "lowest": lowest,
            "categories": cats,
            "category_percentages": cat_pcts,
            "category_count": self.category_count(),
            "monthly": self.monthly_totals(),
            "daily": self.daily_totals(),
            "monthly_change": self.monthly_change(),
            # Aliases for new tools
            "total_spending": round(tot, 2),
            "total_count": cnt,
            "average_expense": round(avg, 2),
            "category_totals": {k: round(v, 2) for k, v in cats.items()},
        }

    def get_spending_between(
        self, start_date: str | datetime | date, end_date: str | datetime | date
    ) -> dict:
        """
        Return filtered spending statistics between start_date and end_date (inclusive).
        """
        from app.utils.dates import parse_datetime

        s_dt = parse_datetime(start_date)
        e_dt = parse_datetime(end_date)

        # Force end of day for end_date if time is 00:00:00
        if e_dt.hour == 0 and e_dt.minute == 0 and e_dt.second == 0:
            e_dt = e_dt.replace(hour=23, minute=59, second=59)

        all_expenses = self.get_all_expenses()
        filtered = [
            e for e in all_expenses
            if s_dt <= parse_datetime(e.date) <= e_dt
        ]

        total = sum(e.amount for e in filtered)
        count = len(filtered)
        avg = (total / count) if count > 0 else 0.0

        cat_breakdown = defaultdict(float)
        for e in filtered:
            cat_breakdown[e.category] += e.amount

        return {
            "start_date": s_dt.strftime("%Y-%m-%d"),
            "end_date": e_dt.strftime("%Y-%m-%d"),
            "total_spending": round(total, 2),
            "transaction_count": count,
            "average_expense": round(avg, 2),
            "category_breakdown": {
                k: round(v, 2) for k, v in cat_breakdown.items()
            },
        }
