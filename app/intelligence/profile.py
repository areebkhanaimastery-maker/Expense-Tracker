"""
Personal Spending Profile Analyzer.
"""

from collections import defaultdict
import numpy as np
import pandas as pd

from app.intelligence.schemas import SpendingProfile


def analyze_profile(df: pd.DataFrame) -> SpendingProfile:
    """
    Analyze historical expense records and construct a SpendingProfile.
    Assumes df has columns: ['id', 'amount', 'category', 'description', 'date']
    and date is datetime-like.
    """
    if df.empty or len(df) < 10:
        raise ValueError(
            f"Insufficient data to construct a spending profile. Minimum required: 10 transactions. Found: {len(df)}"
        )

    data = df.copy()
    data["date"] = pd.to_datetime(data["date"])

    total_spending = float(data["amount"].sum())
    transaction_count = len(data)
    avg_transaction_size = float(data["amount"].mean())

    # Date range metrics
    min_date = data["date"].min()
    max_date = data["date"].max()
    span_days = max((max_date - min_date).days, 1)
    span_months = max(span_days / 30.44, 1.0)

    avg_monthly_spending = total_spending / span_months

    # Daily spending series (with 0-fill for days with no expenses)
    daily_spend = (
        data.groupby(data["date"].dt.date)["amount"]
        .sum()
        .reindex(
            pd.date_range(start=min_date.date(), end=max_date.date(), freq="D"),
            fill_value=0.0,
        )
    )

    avg_daily_spending = float(daily_spend.mean())
    median_daily_spending = float(daily_spend.median())

    # Largest expense
    largest_row = data.loc[data["amount"].idxmax()]
    largest_expense_id = int(largest_row["id"])
    largest_expense_amount = float(largest_row["amount"])
    largest_expense_desc = str(largest_row["description"])

    # Categories breakdown
    cat_totals = data.groupby("category")["amount"].sum()
    category_percentages = (cat_totals / total_spending * 100).to_dict()

    most_expensive_category = str(cat_totals.idxmax())
    lowest_spending_category = str(cat_totals.idxmin())

    # Weekend vs Weekday spending (Weekend: Saturday=5, Sunday=6)
    data["is_weekend"] = data["date"].dt.dayofweek >= 5
    weekend_totals = data.groupby("is_weekend")["amount"].sum()

    total_weekends = max(span_days / 7.0, 1.0) * 2  # Approx weekend days
    total_weekdays = max(span_days - total_weekends, 1.0)

    # Convert to monthly average weekend/weekday metrics
    avg_monthly_weekend = float(
        weekend_totals.get(True, 0.0) / (total_weekends / 2) * 8.7
    )
    avg_monthly_weekday = float(
        weekend_totals.get(False, 0.0) / (total_weekdays / 5) * 21.7
    )

    # Spending Volatility calculation (CV of monthly spending)
    monthly_spend = data.groupby(data["date"].dt.to_period("M"))["amount"].sum()
    if len(monthly_spend) >= 3:
        cv = float(monthly_spend.std() / monthly_spend.mean())
        if cv < 0.15:
            volatility = "Low"
        elif cv <= 0.35:
            volatility = "Moderate"
        else:
            volatility = "High"
    else:
        volatility = "Moderate"

    # Spending Frequency
    freq_ratio = transaction_count / span_days
    if freq_ratio >= 1.0:
        spending_frequency = "Daily"
    elif freq_ratio >= 0.3:
        spending_frequency = "Frequent"
    elif freq_ratio >= 0.1:
        spending_frequency = "Occasional"
    else:
        spending_frequency = "Rare"

    return SpendingProfile(
        total_spending=round(total_spending, 2),
        avg_monthly_spending=round(avg_monthly_spending, 2),
        avg_daily_spending=round(avg_daily_spending, 2),
        median_daily_spending=round(median_daily_spending, 2),
        avg_transaction_size=round(avg_transaction_size, 2),
        largest_expense_id=largest_expense_id,
        largest_expense_amount=round(largest_expense_amount, 2),
        largest_expense_desc=largest_expense_desc,
        most_expensive_category=most_expensive_category,
        lowest_spending_category=lowest_spending_category,
        category_percentages={k: round(v, 2) for k, v in category_percentages.items()},
        weekend_spending_monthly=round(avg_monthly_weekend, 2),
        weekday_spending_monthly=round(avg_monthly_weekday, 2),
        spending_volatility=volatility,
        transaction_count=transaction_count,
        spending_frequency=spending_frequency,
    )
