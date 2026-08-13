# Expense Tracker

A professional CLI Expense Tracker built in Python with a layered architecture, SQLite persistence, dependency injection, custom exception handling, logging, and an AI/ML-ready foundation.

## Architecture

```text
Expense-Tracker/
│
├── app/
│   ├── config.py                  # Centralized configuration
│   ├── exceptions.py              # Custom exception hierarchy
│   ├── logging_config.py          # Logging configuration
│   │
│   ├── models/
│   │   └── expense.py             # Expense dataclass
│   │
│   ├── repositories/
│   │   ├── interface.py           # Abstract repository interface
│   │   └── sqlite_repository.py   # SQLite implementation
│   │
│   ├── services/
│   │   └── expense_service.py     # Business logic
│   │
│   ├── validators/
│   │   └── expense_validator.py   # Input validation
│   │
│   ├── cli/
│   │   ├── app.py                 # CLI application class
│   │   ├── display.py             # Display helpers
│   │   └── handlers.py            # CLI action handlers
│   │
│   └── ai/                        # AI module (Phase 4)
│       ├── assistant.py
│       ├── tools.py
│       ├── context.py
│       └── intents.py
│
├── ml/                            # ML module (Phase 4)
│   ├── features.py
│   ├── prediction.py
│   └── anomaly_detection.py
│
├── tests/
│   ├── test_models.py
│   ├── test_validators.py
│   ├── test_repository.py
│   ├── test_services.py
│   └── test_reports.py
│
├── data/
│   └── expenses.db
│
├── main.py                        # Thin DI entry point
├── requirements.txt
├── .gitignore
└── README.md
```

## Features

- **Add Expense** — Record expenses with amount, category, and description.
- **View Expenses** — List all expenses ordered by date.
- **Edit Expense** — Update any expense by ID.
- **Delete Expense** — Remove expenses with confirmation.
- **Search Expenses** — Case-insensitive keyword search.
- **Filter Expenses** — Filter by category or amount range.
- **Reports** — Total, average, highest, lowest, and category breakdown.
- **SQLite Persistence** — Data persists across sessions.
- **Custom Exceptions** — `ValidationError`, `ExpenseNotFoundError`, `DatabaseError`.
- **Logging** — Application events logged to `expense_tracker.log`.
- **AI/ML Ready** — Architecture prepared for intelligence features.

## Dependency Injection

```text
main.py
   │
   ├── SQLiteExpenseRepository()
   │         │
   ├── ExpenseService(repository)
   │         │
   └── ExpenseTrackerCLI(service)
```

The service layer depends on the repository **interface**, not on SQLite directly. This enables swapping databases or injecting test repositories without changing business logic.

## Installation & Setup

```bash
git clone <repository-url>
cd Expense_Tracker
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

## Generating Synthetic ML Dataset

The repository includes a synthetic expense generator to populate the SQLite database with realistic historical transactions for machine learning training and anomaly detection testing.

The generator simulates:
- Realistic PKR amount distributions skewed towards smaller transactions.
- Weekday vs. weekend spending distributions (higher transport on weekdays, higher dining/entertainment on weekends).
- Inflation/growth patterns (e.g. food spending gradually increasing over time).
- Seasonal spikes (e.g. higher shopping frequency and amounts in November and December).
- Regular monthly bills (Electricity, Internet, Sui Gas) occurring in the first week of every calendar month.
- Occasional large education tuition fees occurring once every 6 months.
- Legitimate rare outliers (e.g. flagship smartphone purchases, surgery fees).

To run the generator with default settings (3,500 records over 24 months):

```bash
python scripts/generate_expenses.py
```

### Configurable Options

You can customize the number of generated records, historical date range, seed, or database path using CLI arguments:

- `--records`: Total target records to generate (default: `3500`).
- `--months`: Span of historical data in months (default: `24`).
- `--seed`: Seed for reproducibility (default: `42`).
- `--db-path`: Custom SQLite database path (defaults to settings).

For example, to generate 2,000 records over 12 months with a custom seed:

```bash
python scripts/generate_expenses.py --records 2000 --months 12 --seed 101
```

The script is **idempotent**. If you run it multiple times with the same parameters and seed, it will check the database and skip records that have already been generated, preventing duplicates.

## Running Tests

```bash
pytest -v
```

All tests use temporary databases via `pytest`'s `tmp_path` fixture, preserving your local data.
