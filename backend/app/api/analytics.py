"""
Analytics API Router.
"""

from fastapi import APIRouter, Depends
from backend.app.deps import get_analytics_service
from backend.app.schemas.common import APIResponse
from backend.app.schemas.analytics import AnalyticsSummaryResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=APIResponse[AnalyticsSummaryResponse])
def get_analytics_summary(analytics=Depends(get_analytics_service)):
    """Retrieve aggregated spending summary statistics."""
    summary = analytics.spending_summary()
    highest = analytics.highest_expense()
    lowest = analytics.lowest_expense()

    highest_dict = (
        {
            "id": highest.id,
            "amount": highest.amount,
            "category": highest.category,
            "description": highest.description,
            "date": str(highest.date),
        }
        if highest
        else None
    )

    lowest_dict = (
        {
            "id": lowest.id,
            "amount": lowest.amount,
            "category": lowest.category,
            "description": lowest.description,
            "date": str(lowest.date),
        }
        if lowest
        else None
    )

    data = AnalyticsSummaryResponse(
        total_spending=summary.get("total_spending", 0.0),
        transaction_count=summary.get("total_count", 0),
        average_expense=summary.get("average_expense", 0.0),
        highest_expense=highest_dict,
        lowest_expense=lowest_dict,
        category_totals=summary.get("category_totals", {}),
        category_percentages=summary.get("category_percentages", {}),
        monthly_totals=summary.get("monthly_totals", {}),
        monthly_change=summary.get("monthly_change", {}),
    )
    return APIResponse(success=True, data=data)


@router.get("/daily", response_model=APIResponse[dict[str, float]])
def get_daily_totals(analytics=Depends(get_analytics_service)):
    """Retrieve daily spending totals grouped by YYYY-MM-DD."""
    return APIResponse(success=True, data=analytics.daily_totals())


@router.get("/monthly", response_model=APIResponse[dict[str, float]])
def get_monthly_totals(analytics=Depends(get_analytics_service)):
    """Retrieve monthly spending totals grouped by YYYY-MM."""
    return APIResponse(success=True, data=analytics.monthly_totals())


@router.get("/categories", response_model=APIResponse[dict[str, float]])
def get_category_totals(analytics=Depends(get_analytics_service)):
    """Retrieve spending totals grouped by category."""
    return APIResponse(success=True, data=analytics.category_totals())
