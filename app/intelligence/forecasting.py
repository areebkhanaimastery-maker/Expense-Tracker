"""
Category-Level ML Forecasting Engine.
"""

from datetime import timedelta
import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from app.exceptions.ml import PredictionError
from ml.forecasting import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    build_daily_spending,
    build_forecasting_features,
)


logger = logging.getLogger(__name__)


def forecast_category(df: pd.DataFrame, category: str) -> float:
    """
    Generate category spending prediction for the next 30 days using ML.
    Requires at least 30 observations for the specified category.
    """
    cat_df = df[df["category"] == category].copy()

    if len(cat_df) < 30:
        raise ValueError(
            f"Insufficient historical data for category '{category}' forecasting (minimum 30, found {len(cat_df)})."
        )

    try:
        # 1. Aggregate to daily spending for category
        daily = build_daily_spending(cat_df)

        if len(daily) < 31:
            raise ValueError(
                f"Insufficient historical days for category '{category}' (minimum 31 days span required)."
            )

        # 2. Build time-series features
        featured = build_forecasting_features(daily)
        if len(featured) < 10:
            raise ValueError(
                f"Insufficient feature records after lag creation for category '{category}'."
            )

        # 3. Train category-specific ML model on the fly
        X = featured[FEATURE_COLUMNS]
        y = featured[TARGET_COLUMN]

        # Use HistGradientBoostingRegressor
        model = HistGradientBoostingRegressor(
            max_iter=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
        )
        model.fit(X, y)

        # 4. Predict next 30 days day-by-day (auto-regressive forecasting)
        last_date = featured["date"].max()
        working = featured.copy()
        predictions = []

        for i in range(1, 31):
            future_date = last_date + timedelta(days=i)

            new_row = {
                "date": future_date,
                "total_spending": np.nan,
                "day_of_week": future_date.weekday(),
                "day_of_month": future_date.day,
                "month": future_date.month,
                "quarter": (future_date.month - 1) // 3 + 1,
                "week_of_year": future_date.isocalendar()[1],
                "is_weekend": 1 if future_date.weekday() >= 5 else 0,
                "days_since_start": (
                    future_date - daily["date"].min()
                ).days,
            }

            # Build lag features from working dataset
            for lag in [1, 2, 3, 7, 14, 30]:
                idx = len(working) - lag
                if idx >= 0:
                    new_row[f"spending_lag_{lag}"] = working.iloc[idx][
                        "total_spending"
                    ]
                else:
                    new_row[f"spending_lag_{lag}"] = 0.0

            # Build rolling features from working dataset
            recent = working["total_spending"].values
            for window in [7, 14, 30]:
                vals = (
                    recent[-window:] if len(recent) >= window else recent
                )
                new_row[f"rolling_mean_{window}"] = (
                    float(np.mean(vals)) if len(vals) > 0 else 0.0
                )
            for window in [7, 30]:
                vals = (
                    recent[-window:] if len(recent) >= window else recent
                )
                new_row[f"rolling_std_{window}"] = (
                    float(np.std(vals)) if len(vals) > 1 else 0.0
                )

            row_df = pd.DataFrame([new_row])
            X_pred = row_df[FEATURE_COLUMNS]

            pred_value = float(model.predict(X_pred)[0])
            pred_value = max(pred_value, 0.0)

            predictions.append(pred_value)

            # Append prediction as actual for next iterations
            new_row["total_spending"] = pred_value
            working = pd.concat(
                [working, pd.DataFrame([new_row])], ignore_index=True
            )

        total_forecast = sum(predictions)
        return round(total_forecast, 2)

    except Exception as error:
        logger.exception("Category forecasting failed: %s", error)
        raise PredictionError(f"Forecasting model error: {error}") from error
