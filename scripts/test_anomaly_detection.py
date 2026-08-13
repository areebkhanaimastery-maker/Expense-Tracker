import sys
from pathlib import Path

# Add project root directory to PYTHONPATH if run directly
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from ml.dataset import load_expenses
from ml.anomaly_detection import (
    ExpenseAnomalyDetector
)


def main():

    print("\n")
    print("=" * 60)
    print("        EXPENSE ANOMALY DETECTION")
    print("=" * 60)

    data = load_expenses()

    print(
        f"\nAnalyzing {len(data)} expenses..."
    )

    detector = ExpenseAnomalyDetector(
        contamination=0.02
    )

    detector.fit(data)

    anomalies = detector.get_anomalies(
        data
    )

    print(
        f"\nAnomalies detected: "
        f"{len(anomalies)}"
    )

    print("\nUnusual Expenses:")
    print("-" * 60)

    anomalies.sort(
        key=lambda x: x.anomaly_score
    )

    for anomaly in anomalies:

        print(
            f"\nID: {anomaly.expense_id}"
        )

        print(
            f"Amount: "
            f"Rs. {anomaly.amount:,.2f}"
        )

        print(
            f"Category: "
            f"{anomaly.category}"
        )

        print(
            f"Description: "
            f"{anomaly.description}"
        )

        print(
            f"Date: "
            f"{anomaly.date}"
        )

        print(
            f"Anomaly Score: "
            f"{anomaly.anomaly_score:.4f}"
        )


if __name__ == "__main__":
    main()
