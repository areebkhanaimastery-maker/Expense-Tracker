"""
Date Utility Functions.
"""

from datetime import datetime, date


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
