"""
Spending Habit Analyzer.
"""

from collections import Counter
import pandas as pd

from app.intelligence.schemas import HabitAnalysis


def analyze_habits(df: pd.DataFrame) -> HabitAnalysis:
    """
    Perform statistical behavioral habit analysis on the historical dataset.
    """
    if df.empty or len(df) < 10:
        raise ValueError(
            f"Insufficient transactions for habit analysis. Minimum: 10. Found: {len(df)}"
        )

    data = df.copy()
    data["date"] = pd.to_datetime(data["date"])
    data["day_of_month"] = data["date"].dt.day
    data["day_of_week"] = data["date"].dt.dayofweek

    # 1. Weekend vs Weekday ratios
    weekend_mask = data["day_of_week"] >= 5
    weekend_sum = data[weekend_mask]["amount"].sum()
    weekday_sum = data[~weekend_mask]["amount"].sum()
    ratio_weekend = float(weekend_sum / weekday_sum) if weekday_sum > 0 else 0.0

    # 2. Late Month vs Early Month ratios
    early_month_sum = data[data["day_of_month"] <= 10]["amount"].sum()
    late_month_sum = data[data["day_of_month"] >= 21]["amount"].sum()
    ratio_late_early = (
        float(late_month_sum / early_month_sum) if early_month_sum > 0 else 0.0
    )

    # 3. Small vs Large transactions
    small_tx = data[data["amount"] < 1000.0]
    large_tx = data[data["amount"] >= 10000.0]

    small_count = len(small_tx)
    small_total = float(small_tx["amount"].sum())

    large_count = len(large_tx)
    large_total = float(large_tx["amount"].sum())

    # 4. Most frequent category
    cat_counts = Counter(data["category"].tolist())
    freq_cat, freq_count = (
        cat_counts.most_common(1)[0] if cat_counts else ("None", 0)
    )

    # 5. Formulate non-judgmental, statistical bullet points
    summaries = []

    # Small accumulators
    if small_count >= 15:
        summaries.append(
            f"Accumulation Pattern: You recorded {small_count} transactions under Rs. 1,000, "
            f"accumulating to Rs. {small_total:,.2f}."
        )

    # Large concentrations
    if large_count >= 3:
        summaries.append(
            f"Concentration Pattern: {large_count} large transactions (>= Rs. 10,000) "
            f"represent Rs. {large_total:,.2f} ({large_total/data['amount'].sum()*100:.1f}% of total)."
        )

    # Weekend spending habits
    if ratio_weekend > 0.6:
        summaries.append(
            f"Weekend Biased: Weekend spending (Rs. {weekend_sum:,.2f}) is elevated compared "
            f"with weekdays (ratio of {ratio_weekend:.2f})."
        )
    elif ratio_weekend < 0.15:
        summaries.append(
            f"Weekday Biased: Weekend spending is low (Rs. {weekend_sum:,.2f}) compared "
            f"with weekdays (ratio of {ratio_weekend:.2f})."
        )

    # Late month spending spikes
    if ratio_late_early > 1.3:
        summaries.append(
            f"Month-End Acceleration: Spending in the last 10 days of the month (Rs. {late_month_sum:,.2f}) "
            f"is higher than the first 10 days (Rs. {early_month_sum:,.2f}), representing a MoM late-month surge."
        )

    # Frequency summary
    summaries.append(
        f"Frequency Bias: Your most frequent category is {freq_cat} with {freq_count} transactions."
    )

    return HabitAnalysis(
        weekend_vs_weekday_ratio=round(ratio_weekend, 2),
        late_month_vs_early_month_ratio=round(ratio_late_early, 2),
        small_transaction_count=small_count,
        small_transaction_total=round(small_total, 2),
        large_transaction_count=large_count,
        large_transaction_total=round(large_total, 2),
        most_frequent_category=freq_cat,
        most_frequent_category_count=freq_count,
        habits_summary=summaries,
    )
