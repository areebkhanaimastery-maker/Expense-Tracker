"""
Advanced Expense Intelligence CLI Submenu.
"""

from app.cli.formatting import print_header, print_subheader
from app.utils.numbers import format_currency


def show_intelligence_menu(intelligence_service) -> None:
    """Run the interactive Expense Intelligence CLI menu loop."""
    while True:
        print_header("EXPENSE INTELLIGENCE", width=45)
        print("1. Spending Profile")
        print("2. Budget Analysis")
        print("3. Recurring Expenses")
        print("4. Subscriptions")
        print("5. Spending Habits")
        print("6. Category Forecasts")
        print("7. Spending Trends")
        print("8. What-If Scenario")
        print("9. AI Insights")
        print("10. Back")
        print("=" * 45)

        choice = input("Choose an option: ").strip()

        if choice == "10":
            break

        try:
            if choice == "1":
                _show_profile(intelligence_service)
            elif choice == "2":
                _show_budgets(intelligence_service)
            elif choice == "3":
                _show_recurring(intelligence_service)
            elif choice == "4":
                _show_subscriptions(intelligence_service)
            elif choice == "5":
                _show_habits(intelligence_service)
            elif choice == "6":
                _show_forecasts(intelligence_service)
            elif choice == "7":
                _show_trends(intelligence_service)
            elif choice == "8":
                _run_scenario(intelligence_service)
            elif choice == "9":
                _show_insights(intelligence_service)
            else:
                print("\nInvalid option.")
        except Exception as e:
            print(f"\nError running analysis: {e}")


def _show_profile(service) -> None:
    print_subheader("Spending Profile")
    p = service.get_spending_profile()
    print(f"Total Spending       : {format_currency(p.total_spending)}")
    print(f"Avg Monthly Spending : {format_currency(p.avg_monthly_spending)}")
    print(f"Avg Daily Spending   : {format_currency(p.avg_daily_spending)}")
    print(f"Median Daily Spending: {format_currency(p.median_daily_spending)}")
    print(f"Avg Transaction Size : {format_currency(p.avg_transaction_size)}")
    print(
        f"Largest Expense      : {format_currency(p.largest_expense_amount)} ({p.largest_expense_desc})"
    )
    print(f"Most Expensive Cat   : {p.most_expensive_category}")
    print(f"Lowest Spending Cat  : {p.lowest_spending_category}")
    print(f"Weekend Spend / month: {format_currency(p.weekend_spending_monthly)}")
    print(f"Weekday Spend / month: {format_currency(p.weekday_spending_monthly)}")
    print(f"Spending Volatility  : {p.spending_volatility}")
    print(f"Transaction Count    : {p.transaction_count:,}")
    print(f"Spending Frequency   : {p.spending_frequency}")


def _show_budgets(service) -> None:
    print_subheader("Budget Analysis")
    budgets = service.get_budget_status()
    print(
        f"{'Category':<15}{'Limit':<15}{'Current':<15}{'Remaining':<15}{'Proj':<15}{'Status':<10}"
    )
    print("-" * 85)
    for b in budgets:
        print(
            f"{b.category:<15}"
            f"{format_currency(b.recommended_budget):<15}"
            f"{format_currency(b.current_spending):<15}"
            f"{format_currency(b.remaining):<15}"
            f"{format_currency(b.projected_spending):<15}"
            f"{b.status:<10}"
        )


def _show_recurring(service) -> None:
    print_subheader("Recurring Expenses")
    recurring = service.get_recurring_expenses()
    if not recurring:
        print("\nNo recurring transactions detected.")
        return

    print(f"{'Description':<22}{'Category':<15}{'Frequency':<12}{'Avg Amount':<15}{'Confidence':<10}")
    print("-" * 74)
    for r in recurring:
        print(
            f"{r.description[:20]:<22}"
            f"{r.category:<15}"
            f"{r.frequency:<12}"
            f"{format_currency(r.average_amount):<15}"
            f"{r.confidence * 100:>8.0f}%"
        )


def _show_subscriptions(service) -> None:
    print_subheader("Subscriptions")
    subs = service.get_subscriptions()
    if not subs:
        print("\nNo subscriptions detected.")
        return

    print(f"{'Service':<22}{'Category':<15}{'Frequency':<12}{'Cost':<15}{'Annualized':<15}")
    print("-" * 79)
    for s in subs:
        print(
            f"{s.service_name[:20]:<22}"
            f"{s.category:<15}"
            f"{s.frequency:<12}"
            f"{format_currency(s.average_cost):<15}"
            f"{format_currency(s.annualized_cost):<15}"
        )


def _show_habits(service) -> None:
    print_subheader("Spending Habits")
    h = service.get_spending_habits()
    print(f"Weekend/Weekday Ratio: {h.weekend_vs_weekday_ratio:.2f}")
    print(f"Late/Early Month Ratio: {h.late_month_vs_early_month_ratio:.2f}")
    print(
        f"Small Purchases (< Rs 1000): {h.small_transaction_count} times (Total {format_currency(h.small_transaction_total)})"
    )
    print(
        f"Large Purchases (>= Rs 10000): {h.large_transaction_count} times (Total {format_currency(h.large_transaction_total)})"
    )
    print("\nBehavioral Habits:")
    for s in h.habits_summary:
        print(f"  * {s}")


def _show_forecasts(service) -> None:
    print_subheader("Category Forecasts")
    forecasts = service.get_category_forecasts()
    if not forecasts:
        print("\nInsufficient historical observations to forecast categories.")
        return
    for cat, amt in forecasts.items():
        print(f"  - {cat:<15}: Estimated Spending {format_currency(amt)}")


def _show_trends(service) -> None:
    print_subheader("Spending Trends")
    trends = service.get_spending_trends()
    if not trends:
        print("\nInsufficient historical periods to analyze trends.")
        return

    print(f"{'Category':<15}{'Trend Direction':<18}{'MoM Growth Rate':<18}{'Acceleration':<15}")
    print("-" * 66)
    for t in trends:
        acc = "Accelerating" if t.is_accelerating else "Stable"
        print(
            f"{t.category:<15}"
            f"{t.direction:<18}"
            f"{t.growth_rate:>+14.1f}%"
            f"{acc:>19}"
        )


def _run_scenario(service) -> None:
    print_subheader("What-If Scenario Simulation")
    cat = input("Enter category (e.g. Food): ").strip()
    change = input("Enter change value (e.g. -15 for reduction, 5000 for increase): ").strip()

    is_pct = input("Is this a percentage change? (y/n): ").strip().lower() == "y"

    try:
        val = float(change)
        res = service.run_scenario(cat, val, is_pct)
        print("\n" + "=" * 50)
        print(res.scenario_name)
        print("=" * 50)
        print(f"Category          : {res.category}")
        print(f"Original Spending : {format_currency(res.original_spending)}")
        print(f"Simulated Spending: {format_currency(res.new_spending)}")
        print(f"Monthly savings   : {format_currency(res.monthly_savings)}")
        print(f"Annualized savings: {format_currency(res.annualized_savings)}")
        print("=" * 50)
    except ValueError:
        print("\nError: Please enter a valid change number.")


def _show_insights(service) -> None:
    print_subheader("AI Financial Insights")
    insights = service.get_insights()
    for idx, insight in enumerate(insights.insights, start=1):
        print(f" {idx}. {insight}")
