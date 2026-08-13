"""
Intelligence Engine Orchestrator.

Manages data validation thresholds, schedules specialized sub-analyzers,
and caches calculated results for low-overhead re-entry.
"""

from typing import Any
import pandas as pd

from app.exceptions.ml import MLModelError
from app.intelligence.budgeting import analyze_budgets
from app.intelligence.forecasting import forecast_category
from app.intelligence.habits import analyze_habits
from app.intelligence.insights import generate_insights
from app.intelligence.profile import analyze_profile
from app.intelligence.recurring import detect_recurring
from app.intelligence.scenarios import run_scenario
from app.intelligence.schemas import (
    BudgetAnalysis,
    HabitAnalysis,
    IntelligenceInsights,
    RecurringExpense,
    ScenarioResult,
    SpendingProfile,
    Subscription,
    TrendAnalysis,
)
from app.intelligence.subscriptions import detect_subscriptions
from app.intelligence.trends import detect_trends


class IntelligenceEngine:
    """Central orchestration hub coordinating all sub-analyzers."""

    def __init__(self, repository):
        self.repository = repository
        self._cache: dict[str, Any] = {}
        self._cache_timestamp_count: int = -1

    def _load_data(self) -> pd.DataFrame:
        """Load database records into pandas DataFrame and validate."""
        expenses = self.repository.get_all()
        records = [
            {
                "id": e.id,
                "amount": e.amount,
                "category": e.category,
                "description": e.description,
                "date": e.date,
            }
            for e in expenses
        ]
        if not records:
            return pd.DataFrame()
        return pd.DataFrame(records)

    def _get_working_data(self) -> pd.DataFrame:
        """Fetch working dataset, validating against cache counters."""
        current_len = len(self.repository.get_all())

        # If transaction count changed, invalidate cached calculations
        if current_len != self._cache_timestamp_count:
            self._cache.clear()
            self._cache_timestamp_count = current_len

        if "df" not in self._cache:
            df = self._load_data()
            self._cache["df"] = df
        return self._cache["df"]

    def get_profile(self) -> SpendingProfile:
        """Retrieve SpendingProfile (cached)."""
        df = self._get_working_data()
        if "profile" not in self._cache:
            self._cache["profile"] = analyze_profile(df)
        return self._cache["profile"]

    def get_budget_analysis(self) -> list[BudgetAnalysis]:
        """Retrieve list of BudgetAnalysis reports (cached)."""
        df = self._get_working_data()
        if "budgets" not in self._cache:
            self._cache["budgets"] = analyze_budgets(df)
        return self._cache["budgets"]

    def get_recurring_expenses(self) -> list[RecurringExpense]:
        """Retrieve list of detected RecurringExpense patterns (cached)."""
        df = self._get_working_data()
        if "recurring" not in self._cache:
            self._cache["recurring"] = detect_recurring(df)
        return self._cache["recurring"]

    def get_subscriptions(self) -> list[Subscription]:
        """Retrieve list of detected Subscriptions (cached)."""
        df = self._get_working_data()
        if "subscriptions" not in self._cache:
            self._cache["subscriptions"] = detect_subscriptions(df)
        return self._cache["subscriptions"]

    def get_habits(self) -> HabitAnalysis:
        """Retrieve HabitAnalysis (cached)."""
        df = self._get_working_data()
        if "habits" not in self._cache:
            self._cache["habits"] = analyze_habits(df)
        return self._cache["habits"]

    def get_category_forecasts(self) -> dict[str, float]:
        """Retrieve next-month spending forecasts per category (cached)."""
        df = self._get_working_data()
        if "forecasts" not in self._cache:
            forecasts = {}
            for cat in df["category"].unique():
                try:
                    forecasts[cat] = forecast_category(df, cat)
                except ValueError:
                    # Skip categories with insufficient records
                    pass
            self._cache["forecasts"] = forecasts
        return self._cache["forecasts"]

    def get_trends(self) -> list[TrendAnalysis]:
        """Retrieve list of TrendAnalysis reports (cached)."""
        df = self._get_working_data()
        if "trends" not in self._cache:
            self._cache["trends"] = detect_trends(df)
        return self._cache["trends"]

    def run_scenario(
        self, category: str, change_value: float, is_percentage: bool = True
    ) -> ScenarioResult:
        """Simulate a What-If scenario (live calculation, not cached)."""
        df = self._get_working_data()
        return run_scenario(df, category, change_value, is_percentage)

    def generate_insights(
        self, anomalies: list[dict] | None = None
    ) -> IntelligenceInsights:
        """Synthesize and generate financial insights (cached)."""
        if "insights" not in self._cache:
            profile = self.get_profile()
            budgets = self.get_budget_analysis()
            recurring = self.get_recurring_expenses()
            subscriptions = self.get_subscriptions()
            habits = self.get_habits()
            trends = self.get_trends()

            self._cache["insights"] = generate_insights(
                profile=profile,
                budgets=budgets,
                recurring=recurring,
                subscriptions=subscriptions,
                habits=habits,
                trends=trends,
                anomalies=anomalies,
            )
        return self._cache["insights"]
