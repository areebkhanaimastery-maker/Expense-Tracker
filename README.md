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

## Running Tests

```bash
pytest -v
```

All tests use temporary databases via `pytest`'s `tmp_path` fixture, preserving your local data.
