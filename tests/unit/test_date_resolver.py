"""
Unit tests for Relative Date Resolver and Date-Aware Tool Routing.
"""

from datetime import date
import pytest

from app.ai.llm import SmartToolFallbackEngine
from app.services.analytics_service import AnalyticsService
from app.utils.dates import resolve_period


# Fixed Anchor Date for Testing: Thursday, August 13, 2026
ANCHOR = date(2026, 8, 13)


def test_resolve_period_last_week():
    # Last week (Calendar week: Mon Aug 3, 2026 to Sun Aug 9, 2026)
    res = resolve_period("How much did I spend last week?", anchor_date=ANCHOR)
    assert res is not None
    assert res["period"] == "last_week"
    assert res["start_date"] == "2026-08-03"
    assert res["end_date"] == "2026-08-09"
    assert res["type"] == "calendar_week"


def test_resolve_period_this_week():
    # This week (Calendar week: Mon Aug 10, 2026 to Sun Aug 16, 2026)
    res = resolve_period("How much did I spend this week?", anchor_date=ANCHOR)
    assert res is not None
    assert res["period"] == "this_week"
    assert res["start_date"] == "2026-08-10"
    assert res["end_date"] == "2026-08-16"
    assert res["type"] == "calendar_week"


def test_resolve_period_last_7_days():
    # Rolling 7 days (Aug 7, 2026 to Aug 13, 2026)
    res = resolve_period("How much did I spend in the last 7 days?", anchor_date=ANCHOR)
    assert res is not None
    assert res["period"] == "last_7_days"
    assert res["start_date"] == "2026-08-07"
    assert res["end_date"] == "2026-08-13"
    assert res["type"] == "rolling_window"


def test_resolve_period_last_30_days():
    # Rolling 30 days (Jul 15, 2026 to Aug 13, 2026)
    res = resolve_period("How much did I spend in the past 30 days?", anchor_date=ANCHOR)
    assert res is not None
    assert res["period"] == "last_30_days"
    assert res["start_date"] == "2026-07-15"
    assert res["end_date"] == "2026-08-13"
    assert res["type"] == "rolling_window"


def test_resolve_period_last_month():
    # Last month (Jul 1, 2026 to Jul 31, 2026)
    res = resolve_period("How much did I spend last month?", anchor_date=ANCHOR)
    assert res is not None
    assert res["period"] == "last_month"
    assert res["start_date"] == "2026-07-01"
    assert res["end_date"] == "2026-07-31"
    assert res["type"] == "calendar_month"


def test_resolve_period_this_month():
    # This month (Aug 1, 2026 to Aug 31, 2026)
    res = resolve_period("How much did I spend this month?", anchor_date=ANCHOR)
    assert res is not None
    assert res["period"] == "this_month"
    assert res["start_date"] == "2026-08-01"
    assert res["end_date"] == "2026-08-31"
    assert res["type"] == "calendar_month"


def test_resolve_period_today_and_yesterday():
    res_today = resolve_period("Show today expenses", anchor_date=ANCHOR)
    assert res_today["start_date"] == "2026-08-13"
    assert res_today["end_date"] == "2026-08-13"

    res_yest = resolve_period("What did I spend yesterday?", anchor_date=ANCHOR)
    assert res_yest["start_date"] == "2026-08-12"
    assert res_yest["end_date"] == "2026-08-12"


def test_intent_matching_priority():
    # "How much did I spend last week?" MUST match get_spending_between with exact calendar week dates
    match_last_week = SmartToolFallbackEngine._match_intent("How much did I spend last week?")
    assert match_last_week is not None
    assert match_last_week["function"]["name"] == "get_spending_between"
    assert "start_date" in match_last_week["function"]["arguments"]
    assert "end_date" in match_last_week["function"]["arguments"]

    # "What is my total lifetime spending?" MUST match get_spending_summary
    match_lifetime = SmartToolFallbackEngine._match_intent("What is my total lifetime spending?")
    assert match_lifetime is not None
    assert match_lifetime["function"]["name"] == "get_spending_summary"


def test_analytics_service_get_spending_between(repository):
    analytics = AnalyticsService(repository)

    # Empty result check
    summary = analytics.get_spending_between("2026-08-01", "2026-08-10")
    assert summary["total_spending"] == 0.0
    assert summary["transaction_count"] == 0
    assert summary["start_date"] == "2026-08-01"
    assert summary["end_date"] == "2026-08-10"
