"""
Spending Trend Detection Engine.
"""

import numpy as np
import pandas as pd

from app.intelligence.schemas import TrendAnalysis


def detect_trends(df: pd.DataFrame) -> list[TrendAnalysis]:
    """
    Detect category spending trends over historical monthly periods.
    Requires at least 3 monthly periods.
    """
    if df.empty:
        return []

    data = df.copy()
    data["date"] = pd.to_datetime(data["date"])

    # Group by category and month
    grouped = (
        data.groupby(["category", data["date"].dt.to_period("M")])["amount"]
        .sum()
        .unstack(fill_value=0.0)
    )

    # We need at least 3 months to calculate valid trend directions
    if grouped.shape[1] < 3:
        return []

    trends = []

    for cat in grouped.index:
        series = grouped.loc[cat].values
        recent_values = [float(v) for v in series[-3:]]

        # Calculate average monthly growth rate using consecutive percentage changes
        pct_changes = []
        for i in range(len(series) - 1):
            val1 = series[i]
            val2 = series[i + 1]
            if val1 > 0:
                pct_changes.append((val2 - val1) / val1)

        avg_growth = float(np.mean(pct_changes)) if pct_changes else 0.0

        # Classify direction
        if avg_growth >= 0.03:
            direction = "Increasing"
        elif avg_growth <= -0.03:
            direction = "Decreasing"
        else:
            direction = "Stable"

        # Check acceleration: is last month's growth higher than historical average growth?
        is_accelerating = False
        if len(pct_changes) >= 2:
            last_change = pct_changes[-1]
            prior_changes = pct_changes[:-1]
            is_accelerating = last_change > np.mean(prior_changes)

        trends.append(
            TrendAnalysis(
                category=cat,
                direction=direction,
                growth_rate=round(avg_growth * 100, 2),
                recent_values=recent_values,
                is_accelerating=is_accelerating,
            )
        )

    return trends
