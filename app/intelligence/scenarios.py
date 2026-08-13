"""
What-If Scenario Mathematics Engine.
"""

from datetime import datetime, timedelta
import pandas as pd

from app.intelligence.schemas import ScenarioResult


def run_scenario(
    df: pd.DataFrame,
    category: str,
    change_value: float,
    is_percentage: bool = True,
) -> ScenarioResult:
    """
    Execute What-If scenario simulations.
    Calculates impact of changes relative to the last 30 days of active spending.
    """
    if df.empty:
        raise ValueError("No historical data available to evaluate scenario.")

    data = df.copy()
    data["date"] = pd.to_datetime(data["date"])

    # Baseline: spending in the last 30 days of available data
    max_date = data["date"].max()
    cutoff_date = max_date - timedelta(days=30)
    recent_data = data[data["date"] >= cutoff_date]

    cat_recent = recent_data[recent_data["category"] == category]
    original_spending = float(cat_recent["amount"].sum())

    if is_percentage:
        # change_value is percentage (e.g. -15 for -15%)
        multiplier = change_value / 100.0
        change_amt = original_spending * multiplier
    else:
        # change_value is absolute amount (e.g. -5000)
        change_amt = change_value

    new_spending = max(original_spending + change_amt, 0.0)
    monthly_savings = original_spending - new_spending
    annualized_savings = monthly_savings * 12.0

    # Build descriptive scenario name
    direction = "reduce" if change_value < 0 else "increase"
    amt_str = (
        f"{abs(change_value)}%"
        if is_percentage
        else f"Rs. {abs(change_value):,.2f}"
    )
    scenario_name = f"SCENARIO: {direction.upper()} {category} by {amt_str}"

    return ScenarioResult(
        scenario_name=scenario_name,
        category=category,
        original_spending=round(original_spending, 2),
        change_value=change_value,
        is_percentage=is_percentage,
        new_spending=round(new_spending, 2),
        monthly_savings=round(monthly_savings, 2),
        annualized_savings=round(annualized_savings, 2),
    )
