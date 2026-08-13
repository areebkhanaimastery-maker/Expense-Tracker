"""
Prediction Service.

Provides spending forecasts by loading the trained model and
generating predictions for future dates.
"""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from ml import model_manager
from ml.forecasting import (
    FEATURE_COLUMNS,
    build_daily_spending,
    build_forecasting_features,
)


class PredictionService:
    """Generates spending predictions using a trained ML model."""

    def __init__(self, repository):
        self.repository = repository
        self._model = None
        self._model_info = None

    def _load_model(self):
        """Load the trained model if not already cached."""
        if self._model is None:
            self._model = model_manager.load_model()
        if self._model_info is None:
            self._model_info = model_manager.get_model_info()

    def _get_historical_daily(self) -> pd.DataFrame:
        """Build daily spending DataFrame from repository."""
        expenses = self.repository.get_all()
        records = [
            {
                "id": e.id,
                "amount": e.amount,
                "category": e.category,
                "description": e.description,
                "date": e.date,
            }
            for e in expenses
        ]
        if not records:
            return pd.DataFrame()
        df = pd.DataFrame(records)
        return build_daily_spending(df)

    def _predict_days(self, num_days: int) -> dict:
        """
        Predict spending for the next `num_days` days.

        Iterates day-by-day, appending each prediction as a
        new row so lag features stay up to date.
        """
        self._load_model()

        if self._model is None:
            return {
                "error": (
                    "No trained model found. "
                    "Run: python scripts/train_models.py"
                ),
            }

        daily = self._get_historical_daily()
        if daily.empty or len(daily) < 31:
            return {
                "error": "Insufficient historical data for prediction.",
            }

        featured = build_forecasting_features(daily)
        last_date = featured["date"].max()
        working = featured.copy()

        predictions = []

        for i in range(1, num_days + 1):
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

            # Build lag features from working data
            for lag in [1, 2, 3, 7, 14, 30]:
                idx = len(working) - lag
                if idx >= 0:
                    new_row[f"spending_lag_{lag}"] = (
                        working.iloc[idx]["total_spending"]
                    )
                else:
                    new_row[f"spending_lag_{lag}"] = 0.0

            # Build rolling features from working data
            recent = working["total_spending"].values
            for window in [7, 14, 30]:
                vals = recent[-window:] if len(recent) >= window else recent
                new_row[f"rolling_mean_{window}"] = (
                    float(np.mean(vals)) if len(vals) > 0 else 0.0
                )
            for window in [7, 30]:
                vals = recent[-window:] if len(recent) >= window else recent
                new_row[f"rolling_std_{window}"] = (
                    float(np.std(vals)) if len(vals) > 1 else 0.0
                )

            row_df = pd.DataFrame([new_row])
            X = row_df[FEATURE_COLUMNS]
            pred_value = float(self._model.predict(X)[0])
            pred_value = max(pred_value, 0.0)

            predictions.append({
                "date": future_date.strftime("%Y-%m-%d"),
                "predicted_spending": round(pred_value, 2),
            })

            # Append prediction as actual for next iteration
            new_row["total_spending"] = pred_value
            working = pd.concat(
                [working, pd.DataFrame([new_row])],
                ignore_index=True,
            )

        total = sum(p["predicted_spending"] for p in predictions)
        model_name = (
            self._model_info.get("model_name", "Unknown")
            if self._model_info
            else "Unknown"
        )

        return {
            "predictions": predictions,
            "total": round(total, 2),
            "days": num_days,
            "model": model_name,
            "note": (
                "These are statistical estimates based on "
                "historical patterns, not guaranteed outcomes."
            ),
        }

    def predict_next_day(self) -> dict:
        """Predict spending for tomorrow."""
        result = self._predict_days(1)
        if "error" in result:
            return result
        result["period"] = "next_day"
        return result

    def predict_next_7_days(self) -> dict:
        """Predict spending for the next 7 days."""
        result = self._predict_days(7)
        if "error" in result:
            return result
        result["period"] = "next_7_days"
        return result

    def predict_next_30_days(self) -> dict:
        """Predict spending for the next 30 days."""
        result = self._predict_days(30)
        if "error" in result:
            return result
        result["period"] = "next_30_days"
        return result

    def predict_next_month(self) -> dict:
        """Predict spending for the next 30 days (monthly estimate)."""
        result = self._predict_days(30)
        if "error" in result:
            return result
        result["period"] = "next_month"
        return result
