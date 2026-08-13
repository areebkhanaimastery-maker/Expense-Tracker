"""
Structured Insight Generation Engine.
"""

from datetime import datetime

from app.intelligence.schemas import (
    BudgetAnalysis,
    HabitAnalysis,
    IntelligenceInsights,
    RecurringExpense,
    SpendingProfile,
    Subscription,
    TrendAnalysis,
)


def generate_insights(
    profile: SpendingProfile,
    budgets: list[BudgetAnalysis],
    recurring: list[RecurringExpense],
    subscriptions: list[Subscription],
    habits: HabitAnalysis,
    trends: list[TrendAnalysis],
    anomalies: list[dict] | None = None,
) -> IntelligenceInsights:
    """
    Synthesize computed analytical parameters and output actionable insights.
    All insights originate strictly from computed metrics.
    """
    insights_list = []

    # 1. Budget Insights
    exceeded = [b.category for b in budgets if b.status == "EXCEEDED"]
    at_risk = [b.category for b in budgets if b.status == "AT RISK"]

    if exceeded:
        cats_str = ", ".join(exceeded)
        insights_list.append(
            f"[BUDGET EXCEEDED] Current month spending exceeds recommended limits in: {cats_str}."
        )
    if at_risk:
        cats_str = ", ".join(at_risk)
        insights_list.append(
            f"[BUDGET AT RISK] High spending velocity indicates risk of exceeding recommended budgets in: {cats_str}."
        )

    # 2. Trend & Growth Insights
    rising = [
        t
        for t in trends
        if t.direction == "Increasing" and t.growth_rate >= 10.0
    ]
    if rising:
        for t in rising:
            insights_list.append(
                f"[TREND WARNING] Spending in {t.category} is accelerating at a rate of "
                f"+{t.growth_rate:.1f}% Month-over-Month."
            )

    # 3. Subscription & Recurring Insights
    sub_count = len(subscriptions)
    sub_total = sum(s.average_cost for s in subscriptions)
    sub_annual = sum(s.annualized_cost for s in subscriptions)

    if sub_count > 0:
        insights_list.append(
            f"[SUBSCRIPTIONS] Detected {sub_count} active subscription/utility patterns, "
            f"costing Rs. {sub_total:,.2f}/month (annualized to Rs. {sub_annual:,.2f})."
        )

    # 4. Behavioral Habit Insights
    if habits.small_transaction_count >= 15:
        insights_list.append(
            f"[HABIT WARNING] High frequency of small purchases (count: {habits.small_transaction_count}) "
            f"accumulates to Rs. {habits.small_transaction_total:,.2f}."
        )
    if habits.weekend_vs_weekday_ratio >= 0.6:
        insights_list.append(
            f"[HABIT INSIGHT] Spending is weekend-skewed, representing elevated leisure/discretionary spending."
        )

    # 5. Anomaly Detection Insights
    if anomalies and len(anomalies) > 0:
        insights_list.append(
            f"[ANOMALIES] Unsupervised Isolation Forest flagged {len(anomalies)} transaction(s) "
            f"as statistically unusual based on historical baselines."
        )

    # 6. Default general insight if list is empty
    if not insights_list:
        insights_list.append(
            "[HEALTHY STATUS] Spending profiles, category budgets, and trends remain stable and within normal baselines."
        )

    return IntelligenceInsights(
        insights=insights_list,
        generated_at=datetime.now().isoformat(),
    )
