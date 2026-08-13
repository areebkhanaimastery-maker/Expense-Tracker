import pandas as pd

from ml.anomaly_detection import (
    ExpenseAnomalyDetector
)


def create_test_data():

    records = []

    for index in range(100):

        records.append({
            "id": index + 1,
            "amount": 500 + (index % 5) * 50,
            "category": "Food",
            "description": "Normal expense",
            "date": "2026-08-01"
        })

    records.append({
        "id": 101,
        "amount": 50000,
        "category": "Shopping",
        "description": "Large purchase",
        "date": "2026-08-01"
    })

    return pd.DataFrame(records)


def test_detector_finds_anomaly():

    data = create_test_data()

    detector = ExpenseAnomalyDetector(
        contamination=0.02
    )

    detector.fit(data)

    anomalies = detector.get_anomalies(
        data
    )

    assert len(anomalies) >= 1

    assert any(
        anomaly.amount == 50000
        for anomaly in anomalies
    )
