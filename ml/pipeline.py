from ml.dataset import load_expenses
from ml.features import build_ml_dataset
from ml.preprocessing import (
    prepare_features,
    prepare_target,
    temporal_train_test_split,
)


def build_pipeline():

    # 1. Load raw data
    raw_data = load_expenses()

    # 2. Feature engineering
    data = build_ml_dataset(raw_data)

    # 3. Temporal split
    train, test = temporal_train_test_split(
        data,
        test_size=0.2
    )

    # 4. Prepare features
    X_train = prepare_features(train)
    X_test = prepare_features(test)

    # 5. Prepare target
    y_train = prepare_target(train)
    y_test = prepare_target(test)

    return (
        X_train,
        X_test,
        y_train,
        y_test
    )
