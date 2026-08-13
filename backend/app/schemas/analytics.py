"""
Analytics Pydantic Schemas.
"""

from typing import Optional, Dict
from pydantic import BaseModel


class CategoryTotal(BaseModel):
    category: str
    total: float
    percentage: float
    count: int


class MonthlyTotal(BaseModel):
    month: str
    total: float


class DailyTotal(BaseModel):
    date: str
    total: float


class AnalyticsSummaryResponse(BaseModel):
    total_spending: float
    transaction_count: int
    average_expense: float
    highest_expense: Optional[Dict[str, float | str | int]] = None
    lowest_expense: Optional[Dict[str, float | str | int]] = None
    category_totals: Dict[str, float]
    category_percentages: Dict[str, float]
    monthly_totals: Dict[str, float]
    monthly_change: Dict[str, float]
