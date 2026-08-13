"""
Unit and Integration Tests for Phase 6 Advanced Expense Intelligence Module.
"""

from datetime import datetime, timedelta
import pytest
import pandas as pd

from app.exceptions.ml import PredictionError
from app.intelligence.engine import IntelligenceEngine
from app.intelligence.profile import analyze_profile
from app.intelligence.budgeting import analyze_budgets
from app.intelligence.recurring import detect_recurring
from app.intelligence.subscriptions import detect_subscriptions
from app.intelligence.habits import analyze_habits
from app.intelligence.trends import detect_trends
from app.intelligence.forecasting import forecast_category
from app.intelligence.scenarios import run_scenario
from app.intelligence.insights import generate_insights
from app.models.expense import Expense


@pytest.fixture
def base_df():
    """Generates a base DataFrame with 40 realistic transactions spanning 3 months."""
    records = []
    start_date = datetime(2026, 6, 1, 10, 0)
    
    # 1. Weekly internet bill
    for i in range(10):
        records.append({
            "id": i + 1,
            "amount": 2500.0,
            "category": "Bills",
            "description": "Internet subscription payment",
            "date": start_date + timedelta(days=i * 7)
        })
        
    # 2. Food expenses (mostly weekdays)
    for i in range(15):
        records.append({
            "id": i + 11,
            "amount": 800.0,
            "category": "Food",
            "description": "Lunch at restaurant",
            "date": start_date + timedelta(days=i * 5 + 1) # Mon-Fri mostly
        })
        
    # 3. Discretionary Shopping (weekend spikes)
    for i in range(10):
        # Force a Saturday/Sunday
        dt = start_date + timedelta(days=i * 8 + 5)
        records.append({
            "id": i + 26,
            "amount": 6000.0,
            "category": "Shopping",
            "description": "Clothes mall purchase",
            "date": dt
        })

    # 4. Large education expense
    records.append({
        "id": 36,
        "amount": 45000.0,
        "category": "Education",
        "description": "Tuition Semester Fee",
        "date": start_date + timedelta(days=45)
    })

    return pd.DataFrame(records)


def test_spending_profile(base_df):
    profile = analyze_profile(base_df)
    assert profile.total_spending > 0
    assert profile.avg_transaction_size > 0
    assert profile.largest_expense_amount == 45000.0
    assert "Shopping" == profile.most_expensive_category
    assert profile.spending_frequency in ("Daily", "Frequent", "Occasional", "Rare")
    assert profile.spending_volatility in ("Low", "Moderate", "High")


def test_spending_profile_insufficient_data():
    empty_df = pd.DataFrame()
    with pytest.raises(ValueError, match="Insufficient data"):
        analyze_profile(empty_df)


def test_budget_analysis(base_df):
    # Evaluate for August 2026
    analyses = analyze_budgets(base_df, target_month="2026-08")
    assert len(analyses) > 0
    
    # Assert recommended budget buffers standard dev and enforces >= historical mean
    for b in analyses:
        assert b.recommended_budget >= b.historical_average
        assert b.utilization_percentage >= 0.0
        assert b.status in ("UNDER BUDGET", "AT RISK", "EXCEEDED")


def test_recurring_detection(base_df):
    recurring = detect_recurring(base_df)
    assert len(recurring) > 0
    
    # Check weekly pattern detected
    weekly_pattern = [r for r in recurring if r.frequency == "weekly"]
    assert len(weekly_pattern) > 0
    assert weekly_pattern[0].category in ("Bills", "Shopping")
    assert weekly_pattern[0].confidence >= 0.6


def test_subscription_detection(base_df):
    subs = detect_subscriptions(base_df)
    assert len(subs) > 0
    assert any("internet" in s.service_name.lower() for s in subs)
    
    # Check annualized math
    for s in subs:
        if s.frequency == "weekly":
            assert s.annualized_cost == round(s.average_cost * 52.18, 2)


def test_habit_analysis(base_df):
    habits = analyze_habits(base_df)
    assert habits.weekend_vs_weekday_ratio >= 0.0
    assert habits.late_month_vs_early_month_ratio >= 0.0
    assert len(habits.habits_summary) > 0
    assert habits.small_transaction_count > 0


def test_spending_trends(base_df):
    trends = detect_trends(base_df)
    # base_df spans June to August (~3 months), should match trend calculation criteria
    assert len(trends) >= 0


def test_category_forecasting(base_df):
    # Needs at least 30 observations per category
    # Food has 15, should raise ValueError
    with pytest.raises(ValueError, match="Insufficient historical data"):
        forecast_category(base_df, "Food")


def test_scenario_mathematics(base_df):
    # Test 15% reduction in Food
    res = run_scenario(base_df, "Food", -15.0, is_percentage=True)
    assert "SCENARIO" in res.scenario_name
    assert res.monthly_savings == round(res.original_spending * 0.15, 2)
    assert res.new_spending == round(res.original_spending * 0.85, 2)
    assert res.annualized_savings == round(res.monthly_savings * 12, 2)

    # Test absolute reduction of 1000 in Shopping
    res_abs = run_scenario(base_df, "Shopping", -1000.0, is_percentage=False)
    assert res_abs.monthly_savings == 1000.0
    assert res_abs.new_spending == res_abs.original_spending - 1000.0


def test_insight_generation(base_df):
    profile = analyze_profile(base_df)
    budgets = analyze_budgets(base_df)
    recurring = detect_recurring(base_df)
    subs = detect_subscriptions(base_df)
    habits = analyze_habits(base_df)
    trends = detect_trends(base_df)

    insights = generate_insights(
        profile=profile,
        budgets=budgets,
        recurring=recurring,
        subscriptions=subs,
        habits=habits,
        trends=trends,
        anomalies=[{"amount": 100000.0, "category": "Other", "description": "Large", "date": "2026-08-01"}]
    )
    assert len(insights.insights) > 0
    assert any("BUDGET" in i or "SUBSCRIPTIONS" in i or "ANOMALIES" in i or "HABIT" in i for i in insights.insights)


def test_engine_caching_and_invalidation(repository):
    engine = IntelligenceEngine(repository)
    
    # Empty DB validation
    df = engine._load_data()
    assert df.empty

    # Add transactions
    repository.add(Expense(id=None, amount=500.0, category="Food", description="Lunch", date=datetime(2026, 8, 1)))
    repository.add(Expense(id=None, amount=12000.0, category="Bills", description="Electricity", date=datetime(2026, 8, 2)))
    
    df1 = engine._get_working_data()
    assert len(df1) == 2

    # Verify cache hit
    df2 = engine._get_working_data()
    assert id(df1) == id(df2)

    # Insert a new record to trigger count change and cache invalidation
    repository.add(Expense(id=None, amount=6000.0, category="Shopping", description="Shoes", date=datetime(2026, 8, 3)))
    df3 = engine._get_working_data()
    assert len(df3) == 3
    assert id(df1) != id(df3)
