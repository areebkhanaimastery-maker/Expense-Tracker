from dataclasses import dataclass

import pandas as pd
from sklearn.ensemble import IsolationForest


@dataclass
class AnomalyResult:
    expense_id: int
    amount: float
    category: str
    description: str
    date: str
    anomaly_score: float
    is_anomaly: bool


class ExpenseAnomalyDetector:
    """
    Detects unusual expense transactions using
    Isolation Forest.
    """

    def __init__(
        self,
        contamination: float = 0.02,
        random_state: int = 42
    ):
        if not 0 < contamination < 0.5:
            raise ValueError(
                "contamination must be between 0 and 0.5."
            )

        self.contamination = contamination

        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=200
        )

        self.is_fitted = False

    def _build_features(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Build numerical features used by the model.
        """

        data = df.copy()

        data["date"] = pd.to_datetime(
            data["date"]
        )

        features = pd.DataFrame(index=data.index)

        features["amount"] = data["amount"]

        features["month"] = (
            data["date"].dt.month
        )

        features["day_of_week"] = (
            data["date"].dt.dayofweek
        )

        features["day_of_month"] = (
            data["date"].dt.day
        )

        features["is_weekend"] = (
            data["date"].dt.dayofweek >= 5
        ).astype(int)

        return features

    def fit(
        self,
        df: pd.DataFrame
    ):
        """
        Train the anomaly detection model.
        """

        if df.empty:
            raise ValueError(
                "Cannot train anomaly detector "
                "with an empty dataset."
            )

        features = self._build_features(df)

        self.model.fit(features)

        self.is_fitted = True

        return self

    def detect(
        self,
        df: pd.DataFrame
    ) -> list[AnomalyResult]:
        """
        Detect anomalies in expense data.
        """

        if not self.is_fitted:
            raise RuntimeError(
                "Model must be fitted before detection."
            )

        if df.empty:
            return []

        features = self._build_features(df)

        predictions = self.model.predict(
            features
        )

        scores = self.model.decision_function(
            features
        )

        results = []

        for index, prediction in enumerate(
            predictions
        ):

            row = df.iloc[index]

            results.append(
                AnomalyResult(
                    expense_id=int(row["id"]),
                    amount=float(row["amount"]),
                    category=str(row["category"]),
                    description=str(
                        row["description"]
                    ),
                    date=str(row["date"]),
                    anomaly_score=float(
                        scores[index]
                    ),
                    is_anomaly=prediction == -1
                )
            )

        return results

    def get_anomalies(
        self,
        df: pd.DataFrame
    ) -> list[AnomalyResult]:
        """
        Return only detected anomalies.
        """

        results = self.detect(df)

        return [
            result
            for result in results
            if result.is_anomaly
        ]
