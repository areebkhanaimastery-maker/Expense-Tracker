"""
Centralized Application Configuration.

Provides a typed Settings class loaded from environment variables
with default values, type validation, and environment switching.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "ml" / "models"


@dataclass(frozen=True)
class Settings:
    """Typed application settings."""

    # General
    app_name: str = "Expense Tracker"
    app_version: str = "1.0.0"
    environment: str = os.environ.get("ENVIRONMENT", "development").lower()
    currency: str = os.environ.get("CURRENCY", "PKR")

    # Paths
    base_dir: Path = BASE_DIR
    data_dir: Path = DATA_DIR
    logs_dir: Path = LOGS_DIR
    models_dir: Path = MODELS_DIR

    # Database
    database_path: Path = field(
        default_factory=lambda: Path(
            os.environ.get("DATABASE_PATH", str(DATA_DIR / "expenses.db"))
        )
    )
    database_timeout: float = float(
        os.environ.get("DATABASE_TIMEOUT", "10.0")
    )

    # Logging
    log_level: str = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_file: Path = field(
        default_factory=lambda: Path(
            os.environ.get("LOG_FILE", str(LOGS_DIR / "expense_tracker.log"))
        )
    )
    log_max_bytes: int = int(
        os.environ.get("LOG_MAX_BYTES", "5242880")
    )  # 5 MB
    log_backup_count: int = int(os.environ.get("LOG_BACKUP_COUNT", "3"))

    # ML Configuration
    ml_model_path: Path = field(
        default_factory=lambda: Path(
            os.environ.get(
                "ML_MODEL_PATH",
                str(MODELS_DIR / "spending_model.joblib"),
            )
        )
    )
    anomaly_contamination: float = float(
        os.environ.get("ANOMALY_CONTAMINATION", "0.02")
    )

    # LLM / AI Configuration
    llm_provider: str = os.environ.get("LLM_PROVIDER", "ollama").lower()
    llm_model: str = os.environ.get("LLM_MODEL", "qwen2.5:3b")
    llm_temperature: float = float(
        os.environ.get("LLM_TEMPERATURE", "0.2")
    )
    llm_max_tokens: int = int(os.environ.get("LLM_MAX_TOKENS", "1000"))

    def __post_init__(self):
        """Validate settings after initialization."""
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        if not 0.0 < self.anomaly_contamination < 0.5:
            object.__setattr__(self, "anomaly_contamination", 0.02)

        if not 0.0 <= self.llm_temperature <= 2.0:
            object.__setattr__(self, "llm_temperature", 0.2)


settings = Settings()
