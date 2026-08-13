import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


TARGET_COLUMN = "amount"


def prepare_features(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Prepare the feature matrix for machine learning.

    Removes columns that should not be directly
    provided to the model.
    """

    data = df.copy()

    columns_to_remove = [
        "id",
        "description",
        "date",
        TARGET_COLUMN,
    ]

    existing_columns = [
        column
        for column in columns_to_remove
        if column in data.columns
    ]

    return data.drop(
        columns=existing_columns
    )


def prepare_target(
    df: pd.DataFrame
) -> pd.Series:
    """
    Extract the target variable.
    """

    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Missing target column: {TARGET_COLUMN}"
        )

    return df[TARGET_COLUMN]


def temporal_train_test_split(
    df: pd.DataFrame,
    test_size: float = 0.2
):
    """
    Split expense data chronologically.

    Older records are used for training.
    Newer records are used for testing.

    This prevents temporal data leakage.
    """

    if not 0 < test_size < 1:
        raise ValueError(
            "test_size must be between 0 and 1."
        )

    data = df.sort_values(
        "date"
    ).reset_index(drop=True)

    split_index = int(
        len(data) * (1 - test_size)
    )

    if split_index <= 0:
        raise ValueError(
            "Dataset is too small for splitting."
        )

    train = data.iloc[
        :split_index
    ].copy()

    test = data.iloc[
        split_index:
    ].copy()

    return train, test


def scale_features(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame
):
    """
    Standardize numerical features.

    The scaler is fitted ONLY on training data
    to prevent information leakage.
    """

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(
        X_train
    )

    X_test_scaled = scaler.transform(
        X_test
    )

    return (
        X_train_scaled,
        X_test_scaled,
        scaler
    )
