import pandas as pd

from ml.preprocessing import (
    temporal_train_test_split,
)


def test_temporal_split():

    data = pd.DataFrame({
        "amount": [
            100,
            200,
            300,
            400,
            500
        ],
        "date": pd.to_datetime([
            "2026-01-01",
            "2026-02-01",
            "2026-03-01",
            "2026-04-01",
            "2026-05-01"
        ])
    })

    train, test = temporal_train_test_split(
        data,
        test_size=0.2
    )

    assert len(train) == 4
    assert len(test) == 1

    assert train["date"].max() < test["date"].min()
