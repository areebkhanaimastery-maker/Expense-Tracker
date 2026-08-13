import sys
from pathlib import Path

# Add project root directory to PYTHONPATH if run directly
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from ml.dataset import load_expenses
from ml.features import build_ml_dataset
from ml.preprocessing import temporal_train_test_split


def main():

    raw = load_expenses()

    print("\nRAW DATA")
    print("=" * 50)

    print(f"Records: {len(raw)}")
    print(f"Columns: {list(raw.columns)}")

    ml_data = build_ml_dataset(raw)

    print("\nML DATASET")
    print("=" * 50)

    print(f"Rows: {len(ml_data)}")
    print(f"Columns: {len(ml_data.columns)}")

    train, test = temporal_train_test_split(
        ml_data
    )

    print("\nTRAIN / TEST")
    print("=" * 50)

    print(f"Training records: {len(train)}")
    print(f"Testing records:  {len(test)}")

    print(
        f"\nTraining period:"
        f" {train['date'].min()}"
        f" -> {train['date'].max()}"
    )

    print(
        f"Testing period:"
        f" {test['date'].min()}"
        f" -> {test['date'].max()}"
    )


if __name__ == "__main__":
    main()
