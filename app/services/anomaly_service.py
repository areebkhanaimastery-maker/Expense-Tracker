from ml.anomaly_detection import (
    ExpenseAnomalyDetector
)


class AnomalyService:

    def __init__(self, repository):

        self.repository = repository

        self.detector = ExpenseAnomalyDetector(
            contamination=0.02
        )

    def _load_dataframe(self):

        import pandas as pd

        expenses = self.repository.get_all()

        records = [
            {
                "id": expense.id,
                "amount": expense.amount,
                "category": expense.category,
                "description": expense.description,
                "date": expense.date,
            }
            for expense in expenses
        ]

        return pd.DataFrame(records)

    def train(self):

        dataframe = self._load_dataframe()

        if dataframe.empty:
            raise ValueError(
                "No expenses available for "
                "anomaly detection."
            )

        self.detector.fit(dataframe)

    def detect(self):

        dataframe = self._load_dataframe()

        if dataframe.empty:
            return []

        if not self.detector.is_fitted:
            self.train()

        return self.detector.get_anomalies(
            dataframe
        )
