# Expense Tracker

A professional CLI Expense Tracker built in Python with a layered architecture, SQLite persistence, dependency injection, custom exception handling, logging, statistical analytics, machine learning (anomaly detection & spending prediction), and a local LLM conversational AI assistant.

## Architecture

```text
Expense-Tracker/
│
├── app/
│   ├── config.py                  # Centralized configuration (Settings, LLM, ML)
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
│   │   ├── expense_service.py     # Core CRUD business logic
│   │   ├── analytics_service.py   # Analytics & statistical aggregation
│   │   ├── anomaly_service.py     # Isolation Forest anomaly detection bridge
│   │   └── prediction_service.py  # Iterative time-series spending forecast bridge
│   │
│   ├── validators/
│   │   └── expense_validator.py   # Input validation
│   │
│   ├── cli/
│   │   ├── app.py                 # CLI application runner
│   │   ├── display.py             # Display helpers & interactive menus
│   │   └── handlers.py            # CLI action handlers & AI chat loop
│   │
│   └── ai/                        # AI Assistant Module
│       ├── llm.py                 # Abstract LLMProvider & OllamaProvider
│       ├── prompts.py             # Grounded system prompts
│       ├── registry.py            # ToolRegistry & ToolDefinition (read-only tools)
│       ├── tools.py               # 20+ service-backed AI tools
│       ├── memory.py              # Session-based ConversationMemory
│       └── conversation.py        # Multi-turn tool-calling ConversationManager
│
├── ml/                            # Machine Learning Engine
│   ├── dataset.py                 # SQLite extraction to pandas DataFrame
│   ├── features.py                # Temporal & categorical feature engineering
│   ├── preprocessing.py           # Temporal train/test splitting & column preparation
│   ├── evaluation.py              # MAE, RMSE, R², accuracy evaluation metrics
│   ├── forecasting.py             # Daily aggregation, lag/rolling features, multi-model training
│   ├── model_manager.py           # Model serialization & metadata persistence (joblib)
│   ├── anomaly_detection.py       # Isolation Forest anomaly detector
│   ├── pipeline.py                # End-to-end ML data pipeline
│   └── models/                    # Saved ML model artifacts (.joblib, .json)
│
├── tests/                         # Comprehensive Unit Test Suite (90 tests)
│   ├── test_models.py
│   ├── test_validators.py
│   ├── test_repository.py
│   ├── test_services.py
│   ├── test_reports.py
│   ├── test_analytics.py
│   ├── test_anomaly_detection.py
│   ├── test_forecasting.py
│   ├── test_ai_tools.py
│   ├── test_memory.py
│   └── test_conversation.py
│
├── scripts/                       # Executable Utilities
│   ├── generate_expenses.py       # Realistic synthetic dataset generator
│   ├── check_ml_dataset.py        # Dataset validation & stats summary
│   ├── test_anomaly_detection.py  # Anomaly detection experiment runner
│   └── train_models.py            # End-to-end ML model training & evaluation
│
├── data/
│   └── expenses.db                # SQLite database
│
├── main.py                        # Thin Dependency Injection entry point
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Core Features

1. **Add Expense** — Record expenses with amount, category, and description.
2. **View Expenses** — List expenses formatted neatly in tabular view.
3. **Edit Expense** — Interactively update any expense by ID.
4. **Delete Expense** — Remove expenses with user confirmation.
5. **Search Expenses** — Case-insensitive keyword search on description and category.
6. **Filter Expenses** — Filter transactions by category or amount range.
7. **Reports** — Total, average, highest, lowest, and category breakdown.
8. **Analytics** — Comprehensive statistical insights (category percentages, monthly trends, month-over-month comparison).
9. **AI Expense Assistant** — Natural-language chat powered by local LLM (Ollama) with tool-calling capabilities.
10. **ML Anomaly Detection** — Isolation Forest model detecting unusual spending patterns.
11. **ML Spending Prediction** — Time-series model predicting future daily/monthly spending.

## Dependency Injection Architecture

```text
main.py
   │
   ├── SQLiteExpenseRepository()
   │         │
   ├── ExpenseService(repository)
   ├── AnalyticsService(repository)
   ├── AnomalyService(repository)
   ├── PredictionService(repository)
   │         │
   └── ExpenseTrackerCLI(service, analytics, anomaly, prediction)
```

## Installation & Setup

```bash
git clone <repository-url>
cd Expense_Tracker
pip install -r requirements.txt
```

### Local LLM Setup (Optional for AI Assistant)

To use option `9. AI Expense Assistant`, ensure [Ollama](https://ollama.com/) is installed and running:

```bash
ollama serve
ollama pull qwen3
```

## Running the Application

```bash
python main.py
```

## Machine Learning Workflows

### 1. Generate Synthetic Dataset

Populate your SQLite database with 2,000–5,000 realistic historical transactions over 24 months:

```bash
python scripts/generate_expenses.py --records 3500 --months 24
```

### 2. Train Spending Forecasting Models

Train multiple regression algorithms (Baseline, Random Forest, HistGradientBoosting) on daily spending, evaluate via chronological temporal split, select the top performer by MAE, and save it to `ml/models/`:

```bash
python scripts/train_models.py
```

### 3. Run Anomaly Detection

Run Isolation Forest anomaly detection to identify statistical outliers:

```bash
python scripts/test_anomaly_detection.py
```

## Running Tests

Run the complete test suite (90 unit tests covering core CRUD, repositories, services, analytics, ML pipeline, forecasting, tool registry, memory, and conversation manager):

```bash
pytest -v
```
