"""
Intelligence Service Layer.

Interfaces with the IntelligenceEngine and exposes clean methods to the CLI,
AI tools, and tests.
"""

from app.intelligence.engine import IntelligenceEngine
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


class IntelligenceService:
    """Service layer abstraction wrapping the IntelligenceEngine."""

    def __init__(self, repository, anomaly_service=None):
        self.repository = repository
        self.anomaly_service = anomaly_service
        self.engine = IntelligenceEngine(repository)

    def get_spending_profile(self) -> SpendingProfile:
        """Construct the user's historical SpendingProfile."""
        return self.engine.get_profile()

    def get_budget_status(self) -> list[BudgetAnalysis]:
        """Retrieve current budget utilization analysis per category."""
        return self.engine.get_budget_analysis()

    def get_recurring_expenses(self) -> list[RecurringExpense]:
        """Detect and list recurring expense obligations."""
        return self.engine.get_recurring_expenses()

    def get_subscriptions(self) -> list[Subscription]:
        """Identify subscription services and annualized costs."""
        return self.engine.get_subscriptions()

    def get_spending_habits(self) -> HabitAnalysis:
        """Extract statistical behavioral habits and trends."""
        return self.engine.get_habits()

    def get_category_forecasts(self) -> dict[str, float]:
        """Generate category-level forecasts for next month."""
        return self.engine.get_category_forecasts()

    def get_spending_trends(self) -> list[TrendAnalysis]:
        """Identify spending growth and acceleration directions."""
        return self.engine.get_trends()

    def run_scenario(
        self, category: str, change_value: float, is_percentage: bool = True
    ) -> ScenarioResult:
        """Simulate hypothetical scenario mathematics."""
        return self.engine.run_scenario(
            category=category,
            change_value=change_value,
            is_percentage=is_percentage,
        )

    def get_insights(self) -> IntelligenceInsights:
        """Compile and generate actionable intelligence insights."""
        anomalies_list = None
        if self.anomaly_service:
            try:
                raw_anom = self.anomaly_service.detect()
                anomalies_list = [
                    {
                        "amount": a.amount,
                        "category": a.category,
                        "description": a.description,
                        "date": str(a.date),
                    }
                    for a in raw_anom
                ]
            except Exception:
                anomalies_list = None

        return self.engine.generate_insights(anomalies=anomalies_list)
