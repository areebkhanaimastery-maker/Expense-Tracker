"""
Intelligence Engine API Router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.deps import get_intelligence_service
from backend.app.schemas.common import APIResponse
from backend.app.schemas.intelligence import (
    SpendingProfileResponse,
    BudgetAnalysisResponse,
    CategoryBudgetResponse,
    RecurringExpenseResponse,
    SubscriptionResponse,
    HabitAnalysisResponse,
    TrendResponse,
    CategoryForecastResponse,
    ScenarioRequest,
    ScenarioResponse,
    InsightsResponse,
)

router = APIRouter(prefix="/intelligence", tags=["Intelligence"])


@router.get("/profile", response_model=APIResponse[SpendingProfileResponse])
def get_spending_profile(service=Depends(get_intelligence_service)):
    """Retrieve comprehensive Personal Spending Profile."""
    profile = service.get_spending_profile()
    return APIResponse(
        success=True,
        data=SpendingProfileResponse(
            total_spending=profile.total_spending,
            avg_monthly_spending=profile.avg_monthly_spending,
            avg_daily_spending=profile.avg_daily_spending,
            median_daily_spending=profile.median_daily_spending,
            avg_transaction_size=profile.avg_transaction_size,
            largest_expense_amount=profile.largest_expense_amount,
            largest_expense_description=profile.largest_expense_desc,
            volatility_classification=profile.spending_volatility,
            transaction_count=profile.transaction_count,
            spending_frequency=profile.spending_frequency,
        ),
    )


@router.get("/budget", response_model=APIResponse[BudgetAnalysisResponse])
def get_budget_analysis(service=Depends(get_intelligence_service)):
    """Retrieve Budget Analysis and Recommendations."""
    budgets = service.get_budget_status()
    category_budgets = [
        CategoryBudgetResponse(
            category=b.category,
            recommended_budget=round(b.recommended_budget, 2),
            current_spending=round(b.current_spending, 2),
            remaining=round(b.remaining, 2),
            percentage_used=round(b.utilization_percentage, 1),
            status=b.status,
        )
        for b in budgets
    ]
    tot_budget = sum(b.recommended_budget for b in budgets)
    tot_spending = sum(b.current_spending for b in budgets)
    tot_remaining = tot_budget - tot_spending
    at_risk = sum(1 for b in budgets if b.status == "AT RISK")
    over_budget = sum(1 for b in budgets if b.status == "EXCEEDED")

    return APIResponse(
        success=True,
        data=BudgetAnalysisResponse(
            total_budget=round(tot_budget, 2),
            total_spending=round(tot_spending, 2),
            total_remaining=round(tot_remaining, 2),
            at_risk_count=at_risk,
            over_budget_count=over_budget,
            category_budgets=category_budgets,
        ),
    )


@router.get("/recurring", response_model=APIResponse[list[RecurringExpenseResponse]])
def get_recurring_expenses(service=Depends(get_intelligence_service)):
    """Retrieve identified recurring transactions."""
    items = service.get_recurring_expenses()
    data = [
        RecurringExpenseResponse(
            description=r.description,
            category=r.category,
            average_amount=r.average_amount,
            frequency=r.frequency,
            last_date=r.last_date.strftime("%Y-%m-%d") if hasattr(r.last_date, "strftime") else str(r.last_date),
            confidence=r.confidence,
        )
        for r in items
    ]
    return APIResponse(success=True, data=data)


@router.get("/subscriptions", response_model=APIResponse[list[SubscriptionResponse]])
def get_subscriptions(service=Depends(get_intelligence_service)):
    """Retrieve active subscriptions and utility services."""
    items = service.get_subscriptions()
    data = [
        SubscriptionResponse(
            service_name=s.service_name,
            category=s.category,
            average_cost=s.average_cost,
            frequency=s.frequency,
            annualized_cost=s.annualized_cost,
            next_expected_date=s.next_expected_date.strftime("%Y-%m-%d") if hasattr(s.next_expected_date, "strftime") else str(s.next_expected_date),
        )
        for s in items
    ]
    return APIResponse(success=True, data=data)


@router.get("/habits", response_model=APIResponse[HabitAnalysisResponse])
def get_spending_habits(service=Depends(get_intelligence_service)):
    """Retrieve spending habit analysis and ratios."""
    habits = service.analyze_habits()
    return APIResponse(
        success=True,
        data=HabitAnalysisResponse(
            weekend_vs_weekday_ratio=habits.weekend_vs_weekday_ratio,
            late_month_vs_early_month_ratio=habits.late_month_vs_early_month_ratio,
            small_transaction_count=habits.small_transaction_count,
            small_transaction_total=habits.small_transaction_total,
            large_transaction_count=habits.large_transaction_count,
            large_transaction_total=habits.large_transaction_total,
            habits_summary=habits.habits_summary,
        ),
    )


@router.get("/trends", response_model=APIResponse[list[TrendResponse]])
def get_spending_trends(service=Depends(get_intelligence_service)):
    """Retrieve historical category trend directions."""
    trends = service.detect_trends()
    data = [
        TrendResponse(
            category=t.category,
            direction=t.direction,
            growth_rate=t.growth_rate,
            is_accelerating=t.is_accelerating,
        )
        for t in trends
    ]
    return APIResponse(success=True, data=data)


@router.get("/forecasts", response_model=APIResponse[CategoryForecastResponse])
def get_category_forecasts(service=Depends(get_intelligence_service)):
    """Retrieve next month ML category forecasts."""
    forecasts = service.forecast_categories()
    return APIResponse(success=True, data=CategoryForecastResponse(forecasts=forecasts))


@router.post("/scenario", response_model=APIResponse[ScenarioResponse])
def run_scenario(req: ScenarioRequest, service=Depends(get_intelligence_service)):
    """Simulate a what-if spending reduction/increase scenario."""
    try:
        res = service.run_scenario(
            category=req.category,
            change_value=req.change_value,
            is_percentage=req.is_percentage,
        )
        return APIResponse(
            success=True,
            data=ScenarioResponse(
                category=res.category,
                change_description=res.scenario_name,
                original_spending=res.original_spending,
                new_spending=res.new_spending,
                monthly_savings=res.monthly_savings,
                annualized_savings=res.annualized_savings,
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "SCENARIO_ERROR", "message": str(e)},
        )


@router.get("/insights", response_model=APIResponse[InsightsResponse])
def get_insights(service=Depends(get_intelligence_service)):
    """Retrieve generated actionable financial insights."""
    res = service.generate_insights()
    return APIResponse(
        success=True,
        data=InsightsResponse(
            insights=res.insights,
            generated_at=res.generated_at,
        ),
    )
