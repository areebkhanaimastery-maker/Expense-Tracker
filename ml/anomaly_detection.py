"""
Anomaly Detection.

Identifies unusual spending patterns
by comparing expenses to historical norms.

Implementation planned for Phase 4.
"""


class AnomalyDetector:
    """Detects anomalous spending patterns."""

    def __init__(self):
        self.threshold = None

    def train(self, features):
        """Train the anomaly detection model."""
        raise NotImplementedError(
            "Anomaly detection will be implemented"
            " in Phase 4."
        )

    def detect(self, features):
        """Detect anomalies in the given features."""
        raise NotImplementedError(
            "Anomaly detection will be implemented"
            " in Phase 4."
        )
