"""
AI Tools — read-only functions the AI assistant can invoke.

These tools act as the boundary between the AI layer and
the service/repository layers. The AI never touches SQLite
directly.
"""

from app.ai.registry import ToolDefinition, ToolParameter, ToolRegistry


def build_tool_registry(
    expense_service,
    analytics_service,
    anomaly_service=None,
    prediction_service=None,
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

    return registry
