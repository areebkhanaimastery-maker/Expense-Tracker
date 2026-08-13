"""
Data schemas and typed dataclasses for the Intelligence Engine.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class SpendingProfile:
    """Historical spending behavior and stats."""

    total_spending: float
    avg_monthly_spending: float
    avg_daily_spending: float
    median_daily_spending: float
    avg_transaction_size: float
    largest_expense_id: int
    largest_expense_amount: float
    largest_expense_desc: str
    most_expensive_category: str
    lowest_spending_category: str
    category_percentages: dict[str, float]
    weekend_spending_monthly: float
    weekday_spending_monthly: float
    spending_volatility: str  # "Low", "Moderate", "High"
    transaction_count: int
    spending_frequency: str  # "Daily", "Frequent", "Occasional", "Rare"


@dataclass(frozen=True)
class BudgetAnalysis:
    """Historical budget status and recommendation details for a single category."""

    category: str
    historical_average: float
    median: float
    std_dev: float
    minimum: float
    maximum: float
    recent_trend: float  # Percentage change in recent period
    recommended_budget: float
    current_spending: float
    remaining: float
    utilization_percentage: float
    projected_spending: float
    status: str  # "UNDER BUDGET", "AT RISK", "EXCEEDED"


@dataclass(frozen=True)
class RecurringExpense:
    """Details of a detected recurring payment pattern."""

    description: str
    category: str
    frequency: str  # "weekly", "biweekly", "monthly", "quarterly", "yearly"
    average_amount: float
    occurrences: int
    last_date: datetime
    next_expected_date: datetime
    confidence: float  # Value between 0.0 and 1.0


@dataclass(frozen=True)
class Subscription:
    """Specialized subscription details."""

    service_name: str
    category: str
    frequency: str
    average_cost: float
    annualized_cost: float
    last_payment: datetime
    next_expected_payment: datetime


@dataclass(frozen=True)
class HabitAnalysis:
    """Behavioral spending habits analysis result."""

    weekend_vs_weekday_ratio: float
    late_month_vs_early_month_ratio: float
    small_transaction_count: int
    small_transaction_total: float
    large_transaction_count: int
    large_transaction_total: float
    most_frequent_category: str
    most_frequent_category_count: int
    habits_summary: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TrendAnalysis:
    """MoM category spending trend information."""

    category: str
    direction: str  # "Increasing", "Decreasing", "Stable"
    growth_rate: float  # MoM percentage change
    recent_values: list[float]
    is_accelerating: bool


@dataclass(frozen=True)
class ScenarioResult:
    """Result of a What-If behavioral spending simulation."""

    scenario_name: str
    category: str
    original_spending: float
    change_value: float  # positive or negative percentage/amount
    is_percentage: bool
    new_spending: float
    monthly_savings: float
    annualized_savings: float


@dataclass(frozen=True)
class IntelligenceInsights:
    """Structured actionable financial insights output."""

    insights: list[str] = field(default_factory=list)
    generated_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
