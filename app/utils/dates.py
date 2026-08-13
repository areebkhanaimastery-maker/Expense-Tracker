"""
Date Utility Functions & Relative Date Resolver.
"""

import calendar
from datetime import date, datetime, timedelta
import re
from typing import Any


def parse_datetime(val: str | datetime | date) -> datetime:
    """Parse string or date into datetime object."""
    if isinstance(val, datetime):
        return val
    if isinstance(val, date):
        return datetime.combine(val, datetime.min.time())
    if isinstance(val, str):
        val_str = val.strip()
        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
        ):
            try:
                return datetime.strptime(val_str, fmt)
            except ValueError:
                pass
    raise ValueError(f"Invalid date format: '{val}'. Use YYYY-MM-DD.")


def format_datetime(dt: datetime | date, fmt: str = "%Y-%m-%d %H:%M") -> str:
    """Format datetime or date into readable string."""
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d")
    return dt.strftime(fmt)


def resolve_period(
    text: str, anchor_date: date | None = None
) -> dict[str, Any] | None:
    """
    Parse a user natural language string and resolve relative time expressions
    into structured date boundaries (start_date, end_date).

    Supports:
      - today
      - yesterday
      - this week (Calendar week: Mon to Sun)
      - last week / previous week (Calendar week: Mon to Sun of previous week)
      - this month (Calendar month: 1st to last day)
      - last month / previous month (Calendar month: 1st to last day of previous month)
      - this year (Calendar year: Jan 1 to Dec 31)
      - last year / previous year (Calendar year: Jan 1 to Dec 31 of previous year)
      - previous 7 days / last 7 days / past 7 days (Rolling 7-day window)
      - previous 30 days / last 30 days / past 30 days (Rolling 30-day window)

    Returns:
      Dict with 'period', 'start_date', 'end_date', 'type' or None if no time period detected.
    """
    if not text:
        return None

    norm = text.lower().strip()
    today = anchor_date or date.today()

    # 1. Rolling Windows
    if re.search(r"\b(last|previous|past)\s+7\s+days?\b", norm) or re.search(
        r"\b7\s+days?\b", norm
    ):
        start = today - timedelta(days=6)
        return {
            "period": "last_7_days",
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": today.strftime("%Y-%m-%d"),
            "type": "rolling_window",
        }

    if re.search(r"\b(last|previous|past)\s+30\s+days?\b", norm) or re.search(
        r"\b30\s+days?\b", norm
    ):
        start = today - timedelta(days=29)
        return {
            "period": "last_30_days",
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": today.strftime("%Y-%m-%d"),
            "type": "rolling_window",
        }

    # 2. Calendar Days
    if re.search(r"\btoday\b", norm):
        return {
            "period": "today",
            "start_date": today.strftime("%Y-%m-%d"),
            "end_date": today.strftime("%Y-%m-%d"),
            "type": "calendar_day",
        }

    if re.search(r"\byesterday\b", norm):
        yest = today - timedelta(days=1)
        return {
            "period": "yesterday",
            "start_date": yest.strftime("%Y-%m-%d"),
            "end_date": yest.strftime("%Y-%m-%d"),
            "type": "calendar_day",
        }

    # 3. Calendar Weeks (Monday to Sunday)
    weekday = today.weekday()  # Monday is 0, Sunday is 6
    this_week_start = today - timedelta(days=weekday)
    this_week_end = this_week_start + timedelta(days=6)

    if re.search(r"\b(last|previous|past)\s+week\b", norm):
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = last_week_start + timedelta(days=6)
        return {
            "period": "last_week",
            "start_date": last_week_start.strftime("%Y-%m-%d"),
            "end_date": last_week_end.strftime("%Y-%m-%d"),
            "type": "calendar_week",
        }

    if re.search(r"\bthis\s+week\b", norm):
        return {
            "period": "this_week",
            "start_date": this_week_start.strftime("%Y-%m-%d"),
            "end_date": this_week_end.strftime("%Y-%m-%d"),
            "type": "calendar_week",
        }

    # 4. Calendar Months
    if re.search(r"\b(last|previous|past)\s+month\b", norm):
        first_of_this_month = today.replace(day=1)
        last_of_prev_month = first_of_this_month - timedelta(days=1)
        first_of_prev_month = last_of_prev_month.replace(day=1)
        return {
            "period": "last_month",
            "start_date": first_of_prev_month.strftime("%Y-%m-%d"),
            "end_date": last_of_prev_month.strftime("%Y-%m-%d"),
            "type": "calendar_month",
        }

    if re.search(r"\bthis\s+month\b", norm) or re.search(r"\bcurrent\s+month\b", norm):
        first_of_this_month = today.replace(day=1)
        _, last_day = calendar.monthrange(today.year, today.month)
        last_of_this_month = today.replace(day=last_day)
        return {
            "period": "this_month",
            "start_date": first_of_this_month.strftime("%Y-%m-%d"),
            "end_date": last_of_this_month.strftime("%Y-%m-%d"),
            "type": "calendar_month",
        }

    # 5. Calendar Years
    if re.search(r"\b(last|previous|past)\s+year\b", norm):
        prev_year = today.year - 1
        return {
            "period": "last_year",
            "start_date": f"{prev_year}-01-01",
            "end_date": f"{prev_year}-12-31",
            "type": "calendar_year",
        }

    if re.search(r"\bthis\s+year\b", norm) or re.search(r"\bcurrent\s+year\b", norm):
        return {
            "period": "this_year",
            "start_date": f"{today.year}-01-01",
            "end_date": f"{today.year}-12-31",
            "type": "calendar_year",
        }

    # 6. Explicit date ranges (e.g. YYYY-MM-DD to YYYY-MM-DD)
    dates_found = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", norm)
    if len(dates_found) >= 2:
        return {
            "period": "custom_range",
            "start_date": dates_found[0],
            "end_date": dates_found[1],
            "type": "custom_range",
        }

    return None
