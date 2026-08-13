import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "expenses.db"


@dataclass(frozen=True)
class Settings:
    app_name: str = "Expense Tracker"
    currency: str = "PKR"
    database_path: Path = DATABASE_PATH
    log_level: str = "INFO"

    # LLM configuration
    llm_provider: str = "ollama"
    llm_model: str = os.environ.get(
        "LLM_MODEL", "qwen3"
    )
    llm_temperature: float = float(
        os.environ.get("LLM_TEMPERATURE", "0.2")
    )
    llm_max_tokens: int = int(
        os.environ.get("LLM_MAX_TOKENS", "1000")
    )

    # ML configuration
    anomaly_contamination: float = float(
        os.environ.get("ANOMALY_CONTAMINATION", "0.02")
    )


settings = Settings()
