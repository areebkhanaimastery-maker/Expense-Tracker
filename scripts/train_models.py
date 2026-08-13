#!/usr/bin/env python3
"""
Train ML spending prediction models.

Loads expense data, aggregates to daily spending, engineers
features, trains multiple models, evaluates them, selects the
best, and saves it for later use by the prediction service.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from ml.dataset import load_expenses
from ml.forecasting import (
    build_daily_spending,
    build_forecasting_features,
    temporal_split,
    train_and_evaluate_models,
)
from ml.model_manager import save_model


def main():
    print("\n" + "=" * 60)
    print("          EXPENSE ML TRAINING")
    print("=" * 60)

    # 1. Load data
    raw = load_expenses()
    print(f"\nDataset:")
    print(f"  Total transactions: {len(raw):,}")

    # 2. Daily aggregation
    daily = build_daily_spending(raw)
    print(f"  Daily records: {len(daily):,}")
    print(
        f"  Period: {daily['date'].min().date()}"
        f" -> {daily['date'].max().date()}"
    )

    # 3. Feature engineering
    featured = build_forecasting_features(daily)
    print(f"  Featured records: {len(featured):,}")
    print(f"  Features: {featured.shape[1]}")

    # 4. Temporal split
    train, test = temporal_split(featured, test_size=0.2)
    print(f"\nTraining:")
    print(f"  Records: {len(train):,}")
    print(
        f"  Period: {train['date'].min().date()}"
        f" -> {train['date'].max().date()}"
    )
    print(f"\nTesting:")
    print(f"  Records: {len(test):,}")
    print(
        f"  Period: {test['date'].min().date()}"
        f" -> {test['date'].max().date()}"
    )

    # 5. Train and evaluate
    print("\nTraining models...")
    comparison = train_and_evaluate_models(train, test)

    print("\n" + "-" * 60)
    print("MODEL COMPARISON")
    print("-" * 60)

    for name, res in comparison["results"].items():
        print(f"\n{name}:")
        print(f"  MAE:  Rs. {res['mae']:,.2f}")
        print(f"  RMSE: Rs. {res['rmse']:,.2f}")
        print(f"  R2:   {res['r2']:.4f}")

    best_name = comparison["best_model_name"]
    best_metrics = comparison["results"][best_name]

    print("\n" + "-" * 60)
    print(f"SELECTED MODEL: {best_name}")
    print("-" * 60)
    print(f"  MAE:  Rs. {best_metrics['mae']:,.2f}")
    print(f"  RMSE: Rs. {best_metrics['rmse']:,.2f}")
    print(f"  R2:   {best_metrics['r2']:.4f}")

    # 6. Save model
    model_path = save_model(
        model=comparison["best_model"],
        model_name=best_name,
        metrics={
            "mae": best_metrics["mae"],
            "rmse": best_metrics["rmse"],
            "r2": best_metrics["r2"],
        },
        feature_columns=comparison["feature_columns"],
        train_period=comparison["train_period"],
        test_period=comparison["test_period"],
        train_size=comparison["train_size"],
        test_size=comparison["test_size"],
    )

    print(f"\nModel saved: {model_path}")
    print("\nTraining complete.")


if __name__ == "__main__":
    main()
