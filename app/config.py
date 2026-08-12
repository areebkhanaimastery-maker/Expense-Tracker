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


settings = Settings()
