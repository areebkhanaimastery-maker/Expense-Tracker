"""
AI Tools — read-only functions the AI assistant can invoke.

These tools act as the boundary between the AI layer and the service layers.
The AI never touches SQLite directly.
"""

from typing import Any
from app.ai.registry import ToolDefinition, ToolParameter, ToolRegistry


def build_tool_registry(
    expense_service,
    analytics_service,
    anomaly_service=None,
    prediction_service=None,
    intelligence_service=None,
) -> ToolRegistry:
    """
    Build and return a fully populated ToolRegistry.

    All tools are read-only and delegate to the service layer.
    """
    registry = ToolRegistry()

    # --- Analytics tools ---

    def get_total_spending():
        return {"total": analytics_service.total_spending()}

    registry.register(ToolDefinition(
        name="get_total_spending",
        description="Get the total amount spent across all expenses.",
        handler=get_total_spending,
    ))

    def get_expense_count():
        return {"count": analytics_service.expense_count()}

    registry.register(ToolDefinition(
        name="get_expense_count",
        description="Get the total number of expense transactions.",
        handler=get_expense_count,
    ))

    def get_average_expense():
        return {"average": round(analytics_service.average_expense(), 2)}

    registry.register(ToolDefinition(
        name="get_average_expense",
        description="Get the average expense amount.",
        handler=get_average_expense,
    ))

    def get_highest_expense():
        e = analytics_service.highest_expense()
        if e is None:
            return {"error": "No expenses found."}
        return {
            "id": e.id,
            "amount": e.amount,
            "category": e.category,
            "description": e.description,
            "date": str(e.date),
        }

    registry.register(ToolDefinition(
        name="get_highest_expense",
        description="Get the single largest expense transaction.",
        handler=get_highest_expense,
    ))

    def get_lowest_expense():
        e = analytics_service.lowest_expense()
        if e is None:
            return {"error": "No expenses found."}
        return {
            "id": e.id,
            "amount": e.amount,
            "category": e.category,
            "description": e.description,
            "date": str(e.date),
        }

    registry.register(ToolDefinition(
        name="get_lowest_expense",
        description="Get the single smallest expense transaction.",
        handler=get_lowest_expense,
    ))

    def get_category_totals():
        return analytics_service.category_totals()

    registry.register(ToolDefinition(
        name="get_category_totals",
        description="Get total spending for each category.",
        handler=get_category_totals,
    ))

    def get_category_spending(category: str):
        total = analytics_service.category_total(category)
        return {"category": category, "total": total}

    registry.register(ToolDefinition(
        name="get_category_spending",
        description="Get total spending for a specific category.",
        handler=get_category_spending,
        parameters=[ToolParameter(
            name="category",
            type="string",
            description="The expense category (e.g. Food, Transport, Shopping, Bills, Entertainment, Health, Education, Other).",
        )],
    ))

    def get_monthly_spending():
        return analytics_service.monthly_totals()

    registry.register(ToolDefinition(
        name="get_monthly_spending",
        description="Get total spending grouped by month (YYYY-MM).",
        handler=get_monthly_spending,
    ))

    def get_daily_spending():
        return analytics_service.daily_totals()

    registry.register(ToolDefinition(
        name="get_daily_spending",
        description="Get total spending grouped by day (YYYY-MM-DD).",
        handler=get_daily_spending,
    ))

    def get_current_month_summary():
        expenses = analytics_service.current_month_expenses()
        total = sum(e.amount for e in expenses)
        count = len(expenses)
        return {
            "total": round(total, 2),
            "count": count,
            "average": round(total / count, 2) if count > 0 else 0,
        }

    registry.register(ToolDefinition(
        name="get_current_month_summary",
        description="Get spending summary for the current month (total, count, average).",
        handler=get_current_month_summary,
    ))

    def get_spending_between(start_date: str, end_date: str):
        return analytics_service.get_spending_between(start_date, end_date)

    registry.register(ToolDefinition(
        name="get_spending_between",
        description="Get spending summary and category breakdown between specific start_date and end_date (YYYY-MM-DD).",
        handler=get_spending_between,
        parameters=[
            ToolParameter(
                name="start_date",
                type="string",
                description="Start date in YYYY-MM-DD format.",
            ),
            ToolParameter(
                name="end_date",
                type="string",
                description="End date in YYYY-MM-DD format.",
            ),
        ],
    ))

    def get_previous_month_summary():
        expenses = analytics_service.previous_month_expenses()
        total = sum(e.amount for e in expenses)
        count = len(expenses)
        return {
            "total": round(total, 2),
            "count": count,
            "average": round(total / count, 2) if count > 0 else 0,
        }

    registry.register(ToolDefinition(
        name="get_previous_month_summary",
        description="Get spending summary for the previous month.",
        handler=get_previous_month_summary,
    ))

    def compare_months():
        return analytics_service.monthly_change()

    registry.register(ToolDefinition(
        name="compare_months",
        description="Compare current month spending with previous month. Returns current total, previous total, difference, and percentage change.",
        handler=compare_months,
    ))

    def get_category_percentages():
        return analytics_service.category_percentages()

    registry.register(ToolDefinition(
        name="get_category_percentages",
        description="Get percentage of total spending per category.",
        handler=get_category_percentages,
    ))

    def search_expenses(keyword: str):
        results = expense_service.search(keyword)
        return [
            {
                "id": e.id,
                "amount": e.amount,
                "category": e.category,
                "description": e.description,
                "date": str(e.date),
            }
            for e in results[:20]
        ]

    registry.register(ToolDefinition(
        name="search_expenses",
        description="Search expenses by keyword in description or category. Returns up to 20 results.",
        handler=search_expenses,
        parameters=[ToolParameter(
            name="keyword",
            type="string",
            description="Search keyword.",
        )],
    ))

    def filter_by_category(category: str):
        results = expense_service.filter_category(category)
        return {
            "category": category,
            "count": len(results),
            "total": round(sum(e.amount for e in results), 2),
            "recent": [
                {
                    "id": e.id,
                    "amount": e.amount,
                    "description": e.description,
                    "date": str(e.date),
                }
                for e in results[:10]
            ],
        }

    registry.register(ToolDefinition(
        name="filter_by_category",
        description="Filter expenses by category and show count, total, and recent transactions.",
        handler=filter_by_category,
        parameters=[ToolParameter(
            name="category",
            type="string",
            description="The expense category.",
        )],
    ))

    def get_spending_summary():
        return analytics_service.spending_summary()

    registry.register(ToolDefinition(
        name="get_spending_summary",
        description="Get a comprehensive spending summary including totals, averages, categories, monthly breakdown, and month-over-month change.",
        handler=get_spending_summary,
    ))

    # --- Anomaly tools ---
    if anomaly_service is not None:
        def detect_anomalies():
            try:
                anomalies = anomaly_service.detect()
                return [
                    {
                        "id": a.expense_id,
                        "amount": a.amount,
                        "category": a.category,
                        "description": a.description,
                        "date": a.date,
                        "anomaly_score": round(a.anomaly_score, 4),
                    }
                    for a in anomalies
                ]
            except Exception as e:
                return {"error": str(e)}

        registry.register(ToolDefinition(
            name="detect_anomalies",
            description="Detect unusual/anomalous expenses using the ML anomaly detection model. Returns a list of statistically unusual transactions.",
            handler=detect_anomalies,
        ))

    # --- Prediction tools ---
    if prediction_service is not None:
        def predict_next_day():
            return prediction_service.predict_next_day()

        registry.register(ToolDefinition(
            name="predict_next_day",
            description="Predict estimated spending for tomorrow based on the trained ML model.",
            handler=predict_next_day,
        ))

        def predict_next_7_days():
            return prediction_service.predict_next_7_days()

        registry.register(ToolDefinition(
            name="predict_next_7_days",
            description="Predict estimated spending for the next 7 days.",
            handler=predict_next_7_days,
        ))

        def predict_next_30_days():
            return prediction_service.predict_next_30_days()

        registry.register(ToolDefinition(
            name="predict_next_30_days",
            description="Predict estimated spending for the next 30 days.",
            handler=predict_next_30_days,
        ))

        def predict_next_month():
            return prediction_service.predict_next_month()

        registry.register(ToolDefinition(
            name="predict_next_month",
            description="Predict estimated total spending for next month based on historical patterns.",
            handler=predict_next_month,
        ))

    # --- Advanced Intelligence tools ---
    if intelligence_service is not None:
        def get_spending_profile():
            p = intelligence_service.get_spending_profile()
            return {
                "total_spending": p.total_spending,
                "avg_monthly_spending": p.avg_monthly_spending,
                "avg_daily_spending": p.avg_daily_spending,
                "median_daily_spending": p.median_daily_spending,
                "avg_transaction_size": p.avg_transaction_size,
                "largest_expense_amount": p.largest_expense_amount,
                "largest_expense_desc": p.largest_expense_desc,
                "most_expensive_category": p.most_expensive_category,
                "lowest_spending_category": p.lowest_spending_category,
                "weekend_spending_monthly": p.weekend_spending_monthly,
                "weekday_spending_monthly": p.weekday_spending_monthly,
                "spending_volatility": p.spending_volatility,
                "transaction_count": p.transaction_count,
                "spending_frequency": p.spending_frequency,
            }

        registry.register(ToolDefinition(
            name="get_spending_profile",
            description="Retrieve detailed personal spending profile statistics and volatility.",
            handler=get_spending_profile,
        ))

        def get_budget_status():
            budgets = intelligence_service.get_budget_status()
            return [
                {
                    "category": b.category,
                    "historical_average": b.historical_average,
                    "recommended_budget": b.recommended_budget,
                    "current_spending": b.current_spending,
                    "remaining": b.remaining,
                    "utilization_percentage": b.utilization_percentage,
                    "projected_spending": b.projected_spending,
                    "status": b.status,
                }
                for b in budgets
            ]

        registry.register(ToolDefinition(
            name="get_budget_status",
            description="Get current month budget utilization analysis and recommended budget limits for all categories.",
            handler=get_budget_status,
        ))

        def get_recurring_expenses():
            recurring = intelligence_service.get_recurring_expenses()
            return [
                {
                    "description": r.description,
                    "category": r.category,
                    "frequency": r.frequency,
                    "average_amount": r.average_amount,
                    "occurrences": r.occurrences,
                    "confidence": r.confidence,
                }
                for r in recurring
            ]

        registry.register(ToolDefinition(
            name="get_recurring_expenses",
            description="Detect recurring payment pattern obligations (weekly, monthly, quarterly).",
            handler=get_recurring_expenses,
        ))

        def get_subscriptions():
            subs = intelligence_service.get_subscriptions()
            return [
                {
                    "service_name": s.service_name,
                    "category": s.category,
                    "frequency": s.frequency,
                    "average_cost": s.average_cost,
                    "annualized_cost": s.annualized_cost,
                }
                for s in subs
            ]

        registry.register(ToolDefinition(
            name="get_subscriptions",
            description="Identify active software, entertainment, or utility subscriptions and annualized costs.",
            handler=get_subscriptions,
        ))

        def get_spending_habits():
            h = intelligence_service.get_spending_habits()
            return {
                "weekend_vs_weekday_ratio": h.weekend_vs_weekday_ratio,
                "late_month_vs_early_month_ratio": h.late_month_vs_early_month_ratio,
                "small_transaction_count": h.small_transaction_count,
                "small_transaction_total": h.small_transaction_total,
                "large_transaction_count": h.large_transaction_count,
                "large_transaction_total": h.large_transaction_total,
                "habits_summary": h.habits_summary,
            }

        registry.register(ToolDefinition(
            name="get_spending_habits",
            description="Retrieve behavioral spending habits (weekend bias, late-month surge, small impulses).",
            handler=get_spending_habits,
        ))

        def get_category_forecasts():
            return intelligence_service.get_category_forecasts()

        registry.register(ToolDefinition(
            name="get_category_forecasts",
            description="Generate category-level forecasts for next month using machine learning.",
            handler=get_category_forecasts,
        ))

        def get_spending_trends():
            trends = intelligence_service.get_spending_trends()
            return [
                {
                    "category": t.category,
                    "direction": t.direction,
                    "growth_rate": t.growth_rate,
                    "is_accelerating": t.is_accelerating,
                }
                for t in trends
            ]

        registry.register(ToolDefinition(
            name="get_spending_trends",
            description="Identify category spending growth MoM and acceleration trends.",
            handler=get_spending_trends,
        ))

        def run_spending_scenario(category: str, change_value: float, is_percentage: bool = True):
            s = intelligence_service.run_scenario(category, change_value, is_percentage)
            return {
                "scenario_name": s.scenario_name,
                "category": s.category,
                "original_spending": s.original_spending,
                "new_spending": s.new_spending,
                "monthly_savings": s.monthly_savings,
                "annualized_savings": s.annualized_savings,
            }

        registry.register(ToolDefinition(
            name="run_spending_scenario",
            description="Run a What-If math scenario simulating changes in spending.",
            handler=run_spending_scenario,
            parameters=[
                ToolParameter(
                    name="category",
                    type="string",
                    description="Category to modify.",
                ),
                ToolParameter(
                    name="change_value",
                    type="number",
                    description="Change value (e.g. -15.0 for reduction, 5000.0 for increase).",
                ),
                ToolParameter(
                    name="is_percentage",
                    type="boolean",
                    description="True if change_value is a percentage, False if absolute PKR amount.",
                    required=False,
                )
            ]
        ))

        def get_advanced_insights():
            insights = intelligence_service.get_insights()
            return {"insights": insights.insights}

        registry.register(ToolDefinition(
            name="get_advanced_insights",
            description="Get structured actionable financial insights and alarms derived from active calculations.",
            handler=get_advanced_insights,
        ))

    return registry
