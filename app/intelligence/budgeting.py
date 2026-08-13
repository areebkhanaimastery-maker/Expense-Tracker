"""
Automatic Budget Detection & Recommendations.
"""

from datetime import datetime
import numpy as np
import pandas as pd

from app.intelligence.schemas import BudgetAnalysis


def analyze_budgets(
    df: pd.DataFrame, target_month: str | None = None
) -> list[BudgetAnalysis]:
    """
    Analyze historical spending and recommend budgets for each category.
    Assumes df has columns: ['amount', 'category', 'date']
    """
    if df.empty:
        return []

    data = df.copy()
    data["date"] = pd.to_datetime(data["date"])

    # Determine target evaluation month
    current_time = datetime.now()
    eval_month = (
        pd.to_datetime(target_month)
        if target_month
        else pd.to_datetime(current_time.strftime("%Y-%m"))
    )

    # Filter data before the evaluation month for historical baseline
    historical = data[data["date"].dt.to_period("M") < eval_month.to_period("M")]
    current_month_data = data[
        data["date"].dt.to_period("M") == eval_month.to_period("M")
    ]

    # Calculate current day elapsed fraction for monthly projections
    total_days = pd.Period(eval_month.to_period("M")).days_in_month
    elapsed_days = (
        current_time.day
        if eval_month.to_period("M") == pd.to_datetime(current_time).to_period("M")
        else total_days
    )
    elapsed_fraction = max(elapsed_days / total_days, 0.05)

    categories = data["category"].unique()
    analyses = []

    for cat in categories:
        cat_hist = historical[historical["category"] == cat]
        cat_curr = current_month_data[current_month_data["category"] == cat]

        current_spending = float(cat_curr["amount"].sum())

        # Group baseline by month to get distribution parameters
        monthly_totals = cat_hist.groupby(cat_hist["date"].dt.to_period("M"))[
            "amount"
        ].sum()

        if len(monthly_totals) >= 1:
            mean_val = float(monthly_totals.mean())
            median_val = float(monthly_totals.median())
            std_val = float(monthly_totals.std()) if len(monthly_totals) > 1 else 0.0
            min_val = float(monthly_totals.min())
            max_val = float(monthly_totals.max())
        else:
            # Fallback if no prior historical months exist for this category
            all_cat_spend = data[data["category"] == cat]
            mean_val = float(all_cat_spend["amount"].sum() / elapsed_fraction)
            median_val = mean_val
            std_val = 0.0
            min_val = mean_val
            max_val = mean_val

        # Recent trend calculation: MoM change between last 2 completed historical months
        recent_trend = 0.0
        if len(monthly_totals) >= 2:
            sorted_months = monthly_totals.sort_index()
            last_two = sorted_months.tail(2)
            v1, v2 = last_two.iloc[0], last_two.iloc[1]
            if v1 > 0:
                recent_trend = float((v2 - v1) / v1)

        # Standardized recommendation logic:
        # Buffer space = 0.5 * standard deviation
        # Trend adjustment = trend percentage capped between -10% and +10%
        trend_adj = min(max(recent_trend, -0.1), 0.1)
        recommended = mean_val + (0.5 * std_val) + (mean_val * trend_adj)

        # Enforce reasonable budget limits: [1.0 * mean, 1.5 * mean]
        recommended = max(recommended, mean_val * 1.0)
        recommended = min(recommended, mean_val * 1.5)
        recommended = round(recommended, 2)

        # Budget details
        remaining = recommended - current_spending
        utilization = (
            (current_spending / recommended * 100) if recommended > 0 else 0.0
        )

        projected = current_spending / elapsed_fraction

        # Status rules
        if current_spending > recommended:
            status = "EXCEEDED"
        elif utilization >= 80.0 or projected > recommended:
            status = "AT RISK"
        else:
            status = "UNDER BUDGET"

        analyses.append(
            BudgetAnalysis(
                category=cat,
                historical_average=round(mean_val, 2),
                median=round(median_val, 2),
                std_dev=round(std_val, 2),
                minimum=round(min_val, 2),
                maximum=round(max_val, 2),
                recent_trend=round(recent_trend * 100, 2),
                recommended_budget=recommended,
                current_spending=round(current_spending, 2),
                remaining=round(remaining, 2),
                utilization_percentage=round(utilization, 2),
                projected_spending=round(projected, 2),
                status=status,
            )
        )

    return analyses
