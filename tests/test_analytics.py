import pytest
from datetime import datetime

from app.models.expense import Expense
from app.services.analytics_service import AnalyticsService


class FakeRepository:

    def __init__(self, expenses=None):
        self.expenses = expenses if expenses is not None else [
            Expense(
                id=1,
                amount=1000.0,
                category="Food",
                description="Lunch",
                date=datetime(2026, 8, 1, 12, 0)
            ),
            Expense(
                id=2,
                amount=2000.0,
                category="Shopping",
                description="Clothes",
                date=datetime(2026, 8, 2, 14, 30)
            ),
            Expense(
                id=3,
                amount=500.0,
                category="Food",
                description="Coffee",
                date=datetime(2026, 8, 3, 9, 15)
            ),
        ]

    def get_all(self):
        return self.expenses


def test_total_spending():
    analytics = AnalyticsService(FakeRepository())
    assert analytics.total_spending() == 3500.0


def test_expense_count():
    analytics = AnalyticsService(FakeRepository())
    assert analytics.expense_count() == 3


def test_average_expense():
    analytics = AnalyticsService(FakeRepository())
    assert analytics.average_expense() == 3500.0 / 3


def test_average_expense_empty():
    analytics = AnalyticsService(FakeRepository([]))
    assert analytics.average_expense() == 0.0


def test_highest_expense():
    analytics = AnalyticsService(FakeRepository())
    highest = analytics.highest_expense()
    assert highest is not None
    assert highest.amount == 2000.0
    assert highest.category == "Shopping"


def test_highest_expense_empty():
    analytics = AnalyticsService(FakeRepository([]))
    assert analytics.highest_expense() is None


def test_lowest_expense():
    analytics = AnalyticsService(FakeRepository())
    lowest = analytics.lowest_expense()
    assert lowest is not None
    assert lowest.amount == 500.0
    assert lowest.category == "Food"


def test_lowest_expense_empty():
    analytics = AnalyticsService(FakeRepository([]))
    assert analytics.lowest_expense() is None


def test_category_totals():
    analytics = AnalyticsService(FakeRepository())
    totals = analytics.category_totals()
    assert totals["Food"] == 1500.0
    assert totals["Shopping"] == 2000.0


def test_category_percentages():
    analytics = AnalyticsService(FakeRepository())
    percentages = analytics.category_percentages()
    assert pytest.approx(percentages["Food"], 0.1) == (1500.0 / 3500.0) * 100
    assert pytest.approx(percentages["Shopping"], 0.1) == (2000.0 / 3500.0) * 100


def test_category_percentages_empty():
    analytics = AnalyticsService(FakeRepository([]))
    assert analytics.category_percentages() == {}


def test_category_count():
    analytics = AnalyticsService(FakeRepository())
    counts = analytics.category_count()
    assert counts["Food"] == 2
    assert counts["Shopping"] == 1


def test_monthly_totals():
    analytics = AnalyticsService(FakeRepository())
    monthly = analytics.monthly_totals()
    assert monthly["2026-08"] == 3500.0


def test_daily_totals():
    analytics = AnalyticsService(FakeRepository())
    daily = analytics.daily_totals()
    assert daily["2026-08-01"] == 1000.0
    assert daily["2026-08-02"] == 2000.0
    assert daily["2026-08-03"] == 500.0


def test_current_month_expenses():
    now = datetime.now()
    current_expense = Expense(
        id=10,
        amount=150.0,
        category="Bills",
        description="Electricity",
        date=now
    )
    analytics = AnalyticsService(FakeRepository([current_expense]))
    expenses = analytics.current_month_expenses()
    assert len(expenses) == 1
    assert expenses[0].id == 10
    assert analytics.current_month_total() == 150.0


def test_previous_month_expenses():
    now = datetime.now()
    if now.month == 1:
        prev_year = now.year - 1
        prev_month = 12
    else:
        prev_year = now.year
        prev_month = now.month - 1

    prev_expense = Expense(
        id=11,
        amount=250.0,
        category="Bills",
        description="Water",
        date=datetime(prev_year, prev_month, 15, 10, 0)
    )
    analytics = AnalyticsService(FakeRepository([prev_expense]))
    expenses = analytics.previous_month_expenses()
    assert len(expenses) == 1
    assert expenses[0].id == 11
    assert analytics.previous_month_total() == 250.0


def test_monthly_change():
    now = datetime.now()
    if now.month == 1:
        prev_year = now.year - 1
        prev_month = 12
    else:
        prev_year = now.year
        prev_month = now.month - 1

    e_curr = Expense(id=1, amount=200, category="Food", description="Dinner", date=now)
    e_prev = Expense(id=2, amount=100, category="Food", description="Lunch", date=datetime(prev_year, prev_month, 1, 12, 0))

    analytics = AnalyticsService(FakeRepository([e_curr, e_prev]))
    change = analytics.monthly_change()

    assert change["current"] == 200.0
    assert change["previous"] == 100.0
    assert change["difference"] == 100.0
    assert change["percentage"] == 100.0


def test_category_total():
    analytics = AnalyticsService(FakeRepository())
    assert analytics.category_total("Food") == 1500.0
    assert analytics.category_total("Shopping") == 2000.0
    assert analytics.category_total("Health") == 0.0


def test_monthly_category_totals():
    analytics = AnalyticsService(FakeRepository())
    matrix = analytics.monthly_category_totals()
    assert matrix["2026-08"]["Food"] == 1500.0
    assert matrix["2026-08"]["Shopping"] == 2000.0


def test_spending_summary():
    analytics = AnalyticsService(FakeRepository())
    summary = analytics.spending_summary()
    assert summary["total"] == 3500.0
    assert summary["count"] == 3
    assert summary["average"] == 3500.0 / 3
    assert summary["highest"].amount == 2000.0
    assert summary["lowest"].amount == 500.0
    assert summary["categories"]["Food"] == 1500.0
