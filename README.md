# Expense Tracker

A command-line interface (CLI) Expense Tracker built in Python. This project utilizes a clean layered architecture with an SQLite database backend, parameterized SQL queries for security, robust input validators, and automated testing with Pytest.

## Features

- **Add Expense**: Record expenses with a positive amount, category, and non-empty description.
- **View Expenses**: List all recorded expenses, ordered by date descending.
- **Edit Expense**: Update the amount, category, or description of any expense using its ID.
- **Delete Expense**: Delete recorded expenses by ID with a confirmation prompt.
- **Search Expenses**: Look up expenses by a case-insensitive keyword match in descriptions or categories.
- **Filter Expenses**: Filter expenses either by category or within a minimum/maximum amount range.
- **Reports**: View summary statistics including total spending, average transaction, highest/lowest transactions, and category breakdowns.
- **SQLite Persistence**: Data is persisted in a local SQLite database (`data/expenses.db`).
- **Input Validation**: Prevents invalid values (e.g. empty descriptions, negative amounts) using custom validators.

---

## Project Architecture

```
expense_tracker/
│
├── main.py             # User interaction (CLI Menu & Prompts)
├── models.py           # Data representations (Expense dataclass)
├── services.py         # Business logic (Filtering, search, reports)
├── repository.py       # SQLite database operations (CRUD, queries)
├── validators.py       # Input validation logic
│
├── tests/              # Pytest automated test suite
│   ├── __init__.py
│   ├── test_repository.py
│   └── test_services.py
│
└── data/               # Persistent storage directory
    └── expenses.db     # SQLite database file (ignored in Git)
```

---

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Expense_Tracker
   ```

2. **Install testing dependencies**:
   ```bash
   pip install pytest
   ```

---

## Running the Application

Start the CLI Expense Tracker by running the main entry point:
```bash
python main.py
```

Follow the interactive menu options:
```
========================================
          EXPENSE TRACKER
========================================
1. Add Expense
2. View Expenses
3. Edit Expense
4. Delete Expense
5. Search Expenses
6. Filter Expenses
7. Reports
8. Exit
========================================
```

---

## Running Tests

Execute the automated test suite using `pytest`:
```bash
pytest
```
All database operations in the test suite run in temporary test databases, preserving your local `data/expenses.db` records intact.
