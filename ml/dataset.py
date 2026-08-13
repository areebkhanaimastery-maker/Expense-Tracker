import sys
from pathlib import Path

# Add project root directory to PYTHONPATH if run directly
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import pandas as pd
from app.repositories.sqlite_repository import (
    SQLiteExpenseRepository
)


def load_expenses() -> pd.DataFrame:
    repository = SQLiteExpenseRepository()

    expenses = repository.get_all()

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

    dataframe = pd.DataFrame(records)

    if dataframe.empty:
        raise ValueError(
            "No expense data available for ML."
        )

    return dataframe


if __name__ == "__main__":
    df = load_expenses()
    print(df.head())
