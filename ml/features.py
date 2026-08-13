import sys
from pathlib import Path

# Add project root directory to PYTHONPATH if run directly
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import pandas as pd


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()

    data["date"] = pd.to_datetime(data["date"])

    data["year"] = data["date"].dt.year

    data["month"] = data["date"].dt.month

    data["day"] = data["date"].dt.day

    data["day_of_week"] = data["date"].dt.dayofweek

    data["week_of_year"] = (
        data["date"].dt.isocalendar().week
        .astype(int)
    )

    data["is_weekend"] = (
        data["day_of_week"] >= 5
    ).astype(int)

    data["quarter"] = (
        data["date"].dt.quarter
    )

    data["days_since_start"] = (
        data["date"] -
        data["date"].min()
    ).dt.days

    return data


def encode_categories(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()

    data = pd.get_dummies(
        data,
        columns=["category"],
        prefix="category",
        dtype=int
    )

    return data


def build_ml_dataset(
    df: pd.DataFrame
) -> pd.DataFrame:
    data = create_features(df)

    data = encode_categories(data)

    data = data.sort_values("date")

    return data.reset_index(drop=True)


if __name__ == "__main__":
    from ml.dataset import load_expenses
    df = load_expenses()
    ml_df = build_ml_dataset(df)
    print(ml_df.head())
    print("Dataset shape:", ml_df.shape)
