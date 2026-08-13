"""
Subscription Detection System.
"""

import pandas as pd

from app.intelligence.recurring import detect_recurring
from app.intelligence.schemas import Subscription


SUBSCRIPTION_KEYWORDS = [
    "netflix",
    "spotify",
    "youtube premium",
    "gym",
    "internet",
    "mobile plan",
    "hosting",
    "cloud",
    "aws",
    "github",
    "zoom",
    "adobe",
    "microsoft 365",
    "subscription",
    "membership",
    "electricity",
    "sui gas",
    "gas bill",
    "tuition",
    "course",
    "streaming",
]


def detect_subscriptions(df: pd.DataFrame) -> list[Subscription]:
    """
    Filter recurring transactions to identify digital subscriptions, utilities,
    and regular memberships.
    """
    recurring = detect_recurring(df)
    subscriptions = []

    for r in recurring:
        desc_lower = r.description.lower()
        is_sub = False

        # Match subscription keywords
        if any(kw in desc_lower for kw in SUBSCRIPTION_KEYWORDS):
            is_sub = True

        # Match categories generally linked to subscriptions/bills
        if r.category in ("Bills", "Entertainment", "Education"):
            is_sub = True

        if not is_sub:
            continue

        # Annualized cost calculations
        multiplier = 1.0
        if r.frequency == "weekly":
            multiplier = 52.18
        elif r.frequency == "biweekly":
            multiplier = 26.09
        elif r.frequency == "monthly":
            multiplier = 12.0
        elif r.frequency == "quarterly":
            multiplier = 4.0
        elif r.frequency == "yearly":
            multiplier = 1.0

        annualized = r.average_amount * multiplier

        subscriptions.append(
            Subscription(
                service_name=r.description,
                category=r.category,
                frequency=r.frequency,
                average_cost=r.average_amount,
                annualized_cost=round(annualized, 2),
                last_payment=r.last_date,
                next_expected_payment=r.next_expected_date,
            )
        )

    return subscriptions
