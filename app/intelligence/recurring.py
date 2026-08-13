"""
Recurring Transaction Detector.
"""

from datetime import datetime, timedelta
import re
import numpy as np
import pandas as pd

from app.intelligence.schemas import RecurringExpense


def _clean_description(desc: str) -> str:
    """Helper to clean description strings for matching."""
    # Convert to lower case, remove digits, special characters, and extra spaces
    d = desc.lower().strip()
    d = re.sub(r"\b\d+\b", "", d)  # remove numbers
    d = re.sub(r"[^\w\s]", "", d)  # remove special chars
    return " ".join(d.split())


def detect_recurring(df: pd.DataFrame) -> list[RecurringExpense]:
    """
    Detect recurring expense transactions from historical dataset.
    Minimum data: requires at least 3 occurrences spanning multiple months.
    """
    if df.empty or len(df) < 10:
        return []

    data = df.copy()
    data["date"] = pd.to_datetime(data["date"])
    data["clean_desc"] = data["description"].apply(_clean_description)

    # Group by clean description and category
    groups = data.groupby(["clean_desc", "category"])
    recurring_patterns = []

    for (clean_desc, category), group in groups:
        if len(group) < 3:
            continue

        sorted_group = group.sort_values("date")
        dates = sorted_group["date"].tolist()
        amounts = sorted_group["amount"].tolist()

        # Calculate time differences in days
        diffs = [
            (dates[i + 1] - dates[i]).days
            for i in range(len(dates) - 1)
        ]
        mean_diff = float(np.mean(diffs))
        std_diff = float(np.std(diffs)) if len(diffs) > 1 else 0.0

        # Classify interval
        if 5 <= mean_diff <= 9:
            freq = "weekly"
        elif 11 <= mean_diff <= 17:
            freq = "biweekly"
        elif 25 <= mean_diff <= 35:
            freq = "monthly"
        elif 80 <= mean_diff <= 100:
            freq = "quarterly"
        elif 340 <= mean_diff <= 380:
            freq = "yearly"
        else:
            # Not a standard frequency
            continue

        # Check amount consistency (standard deviation relative to mean < 20%)
        mean_amount = float(np.mean(amounts))
        std_amount = float(np.std(amounts))
        amount_coef_var = (
            (std_amount / mean_amount) if mean_amount > 0 else 1.0
        )

        if amount_coef_var > 0.20:
            continue  # amount fluctuates too much for reliable auto-recurrence

        # Date consistency score (lower variance in intervals -> higher score)
        date_score = max(0.0, 1.0 - (std_diff / mean_diff)) if mean_diff > 0 else 0.0

        # Amount consistency score
        amount_score = max(0.0, 1.0 - amount_coef_var)

        # Count score
        count_score = min(len(dates) / 5.0, 1.0)

        # Combined confidence metric
        confidence = (date_score * 0.4) + (amount_score * 0.4) + (count_score * 0.2)
        confidence = min(max(confidence, 0.0), 1.0)

        if confidence < 0.6:
            continue

        # Estimate next payment date
        last_date = dates[-1]
        next_date = last_date + timedelta(days=round(mean_diff))

        # Re-fetch original name representative (longest name matching)
        original_desc = sorted_group["description"].value_counts().idxmax()

        recurring_patterns.append(
            RecurringExpense(
                description=original_desc,
                category=category,
                frequency=freq,
                average_amount=round(mean_amount, 2),
                occurrences=len(dates),
                last_date=last_date,
                next_expected_date=next_date,
                confidence=round(confidence, 2),
            )
        )

    return recurring_patterns
