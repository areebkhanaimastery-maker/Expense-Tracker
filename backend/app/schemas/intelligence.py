"""
Intelligence Pydantic Schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SpendingProfileResponse(BaseModel):
    total_spending: float
    avg_monthly_spending: float
    avg_daily_spending: float
    median_daily_spending: float
    avg_transaction_size: float
    largest_expense_amount: float
    largest_expense_description: str
    volatility_classification: str
    transaction_count: int
    spending_frequency: str


class CategoryBudgetResponse(BaseModel):
    category: str
    recommended_budget: float
    current_spending: float
    remaining: float
    percentage_used: float
    status: str


class BudgetAnalysisResponse(BaseModel):
    total_budget: float
    total_spending: float
    total_remaining: float
    at_risk_count: int
    over_budget_count: int
    category_budgets: List[CategoryBudgetResponse]


class RecurringExpenseResponse(BaseModel):
    description: str
    category: str
    average_amount: float
    frequency: str
    last_date: str
    confidence: float


class SubscriptionResponse(BaseModel):
    service_name: str
    category: str
    average_cost: float
    frequency: str
    annualized_cost: float
    next_expected_date: str


class HabitAnalysisResponse(BaseModel):
    weekend_vs_weekday_ratio: float
    late_month_vs_early_month_ratio: float
    small_transaction_count: int
    small_transaction_total: float
    large_transaction_count: int
    large_transaction_total: float
    habits_summary: List[str]


class TrendResponse(BaseModel):
    category: str
    direction: str
    growth_rate: float
    is_accelerating: bool


class CategoryForecastResponse(BaseModel):
    forecasts: Dict[str, float]


class ScenarioRequest(BaseModel):
    category: str = Field(..., description="Target category name")
    change_value: float = Field(..., description="Percentage or absolute change value (e.g. -20 for -20%)")
    is_percentage: bool = Field(True, description="True if percentage, False if absolute amount")


class ScenarioResponse(BaseModel):
    category: str
    change_description: str
    original_spending: float
    new_spending: float
    monthly_savings: float
    annualized_savings: float


class InsightsResponse(BaseModel):
    insights: List[str]
    generated_at: str
