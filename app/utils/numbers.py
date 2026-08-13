"""
Number and Currency Formatting Utility Functions.
"""

from app.config import settings


def format_currency(
    amount: float, symbol: str | None = None
) -> str:
    """Format a float as currency (e.g. Rs. 1,234.56)."""
    curr = symbol or settings.currency
    prefix = "Rs. " if curr in ("PKR", "Rs") else f"{curr} "
    return f"{prefix}{amount:,.2f}"


def safe_float(val: object, default: float = 0.0) -> float:
    """Convert value to float safely."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return default
