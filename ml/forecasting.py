"""
Spending Forecasting Module.

Converts transaction-level data into daily spending time series,
engineers lag/rolling/temporal features, and trains multiple
regression models to forecast future daily spending.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import (
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


def build_daily_spending(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate transaction-level data into daily totals.

    Fills missing days with zero spending so the time series
    is continuous.
    """
    data = df.copy()
    data["date"] = pd.to_datetime(data["date"])
    data["day"] = data["date"].dt.date

    daily = (
        data.groupby("day")["amount"]
        .sum()
        .reset_index()
    )
    daily.columns = ["date", "total_spending"]
    daily["date"] = pd.to_datetime(daily["date"])

    # Fill gaps with zero-spending days
    full_range = pd.date_range(
        start=daily["date"].min(),
        end=daily["date"].max(),
        freq="D",
    )
    daily = (
        daily.set_index("date")
        .reindex(full_range, fill_value=0.0)
        .rename_axis("date")
        .reset_index()
    )

    return daily


def build_forecasting_features(
    daily: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build temporal, lag, and rolling features for forecasting.

    All features use only past information to prevent leakage.
    """
    data = daily.copy()

    # --- Temporal features ---
    data["day_of_week"] = data["date"].dt.dayofweek
    data["day_of_month"] = data["date"].dt.day
    data["month"] = data["date"].dt.month
    data["quarter"] = data["date"].dt.quarter
    data["week_of_year"] = (
        data["date"].dt.isocalendar().week.astype(int)
    )
    data["is_weekend"] = (
        data["day_of_week"] >= 5
    ).astype(int)
    data["days_since_start"] = (
        data["date"] - data["date"].min()
    ).dt.days

    # --- Lag features ---
    for lag in [1, 2, 3, 7, 14, 30]:
        data[f"spending_lag_{lag}"] = (
            data["total_spending"].shift(lag)
        )

    # --- Rolling features ---
    for window in [7, 14, 30]:
        data[f"rolling_mean_{window}"] = (
            data["total_spending"]
            .shift(1)
            .rolling(window, min_periods=1)
            .mean()
        )
    for window in [7, 30]:
        data[f"rolling_std_{window}"] = (
            data["total_spending"]
            .shift(1)
            .rolling(window, min_periods=1)
            .std()
            .fillna(0)
        )

    # Drop rows where lag features are NaN
    data = data.dropna().reset_index(drop=True)

    return data


def temporal_split(
    data: pd.DataFrame, test_size: float = 0.2
) -> tuple:
    """
    Split time series data chronologically.
    """
    data = data.sort_values("date").reset_index(drop=True)
    split_idx = int(len(data) * (1 - test_size))
    train = data.iloc[:split_idx].copy()
    test = data.iloc[split_idx:].copy()
    return train, test


FEATURE_COLUMNS = [
    "day_of_week",
    "day_of_month",
    "month",
    "quarter",
    "week_of_year",
    "is_weekend",
    "days_since_start",
    "spending_lag_1",
    "spending_lag_2",
    "spending_lag_3",
    "spending_lag_7",
    "spending_lag_14",
    "spending_lag_30",
    "rolling_mean_7",
    "rolling_mean_14",
    "rolling_mean_30",
    "rolling_std_7",
    "rolling_std_30",
]

TARGET_COLUMN = "total_spending"


def train_and_evaluate_models(
    train: pd.DataFrame,
    test: pd.DataFrame,
) -> dict:
    """
    Train multiple models and evaluate them.

    Returns dict with model comparison results and the
    best model selected by MAE.
    """
    X_train = train[FEATURE_COLUMNS]
    y_train = train[TARGET_COLUMN]
    X_test = test[FEATURE_COLUMNS]
    y_test = test[TARGET_COLUMN]

    results = {}

    # --- Baseline: predict mean of training set ---
    baseline_pred = np.full(len(y_test), y_train.mean())
    results["Baseline"] = {
        "model": None,
        "mae": mean_absolute_error(y_test, baseline_pred),
        "rmse": float(
            np.sqrt(mean_squared_error(y_test, baseline_pred))
        ),
        "r2": r2_score(y_test, baseline_pred),
        "predictions": baseline_pred,
    }

    # --- Random Forest ---
    rf = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    results["RandomForest"] = {
        "model": rf,
        "mae": mean_absolute_error(y_test, rf_pred),
        "rmse": float(np.sqrt(mean_squared_error(y_test, rf_pred))),
        "r2": r2_score(y_test, rf_pred),
        "predictions": rf_pred,
    }

    # --- HistGradientBoosting ---
    hgb = HistGradientBoostingRegressor(
        max_iter=300,
        max_depth=8,
        learning_rate=0.05,
        random_state=42,
    )
    hgb.fit(X_train, y_train)
    hgb_pred = hgb.predict(X_test)
    results["HistGradientBoosting"] = {
        "model": hgb,
        "mae": mean_absolute_error(y_test, hgb_pred),
        "rmse": float(
            np.sqrt(mean_squared_error(y_test, hgb_pred))
        ),
        "r2": r2_score(y_test, hgb_pred),
        "predictions": hgb_pred,
    }

    # Select best model by MAE
    best_name = min(
        [k for k in results if k != "Baseline"],
        key=lambda k: results[k]["mae"],
    )

    return {
        "results": results,
        "best_model_name": best_name,
        "best_model": results[best_name]["model"],
        "feature_columns": FEATURE_COLUMNS,
        "train_size": len(train),
        "test_size": len(test),
        "train_period": (
            str(train["date"].min()),
            str(train["date"].max()),
        ),
        "test_period": (
            str(test["date"].min()),
            str(test["date"].max()),
        ),
    }
