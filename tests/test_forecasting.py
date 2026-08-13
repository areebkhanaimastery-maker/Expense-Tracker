"""Tests for forecasting module."""

import pandas as pd

from ml.forecasting import (
    build_daily_spending,
    build_forecasting_features,
    temporal_split,
    FEATURE_COLUMNS,
)


def _make_transactions():
    """Create a minimal transaction dataset for testing."""
    records = []
    for day in range(1, 61):
        date = f"2026-01-{day:02d}" if day <= 31 else f"2026-02-{day - 31:02d}"
        if day > 31 and day - 31 > 28:
            continue
        records.append({
            "id": day,
            "amount": 1000 + day * 10,
            "category": "Food",
            "description": "Test",
            "date": date,
        })
    return pd.DataFrame(records)


def test_build_daily_spending():
    df = _make_transactions()
    daily = build_daily_spending(df)
    assert "date" in daily.columns
    assert "total_spending" in daily.columns
    assert len(daily) > 0
    # Should be continuous (no gaps)
    date_range = (daily["date"].max() - daily["date"].min()).days + 1
    assert len(daily) == date_range


def test_build_forecasting_features():
    df = _make_transactions()
    daily = build_daily_spending(df)
    featured = build_forecasting_features(daily)
    for col in FEATURE_COLUMNS:
        assert col in featured.columns, f"Missing feature: {col}"
    # Should have no NaN values
    assert featured[FEATURE_COLUMNS].isna().sum().sum() == 0


def test_temporal_split():
    df = _make_transactions()
    daily = build_daily_spending(df)
    featured = build_forecasting_features(daily)
    train, test = temporal_split(featured, test_size=0.2)
    assert len(train) > 0
    assert len(test) > 0
    assert train["date"].max() < test["date"].min()
