"""
Model Manager — save, load, and inspect trained ML models.

Uses joblib for serialization. Stores model artifacts alongside
metadata (training date, metrics, features, model type) in the
ml/models/ directory.
"""

import json
from datetime import datetime
from pathlib import Path

import joblib


MODELS_DIR = Path(__file__).resolve().parent / "models"


def _ensure_dir() -> None:
    """Create the models directory if it does not exist."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)


def save_model(
    model,
    model_name: str,
    metrics: dict,
    feature_columns: list[str],
    train_period: tuple[str, str],
    test_period: tuple[str, str],
    train_size: int,
    test_size: int,
) -> Path:
    """
    Save a trained model and its metadata.

    Returns the path to the saved model file.
    """
    _ensure_dir()

    model_path = MODELS_DIR / "spending_model.joblib"
    meta_path = MODELS_DIR / "spending_model_meta.json"

    joblib.dump(model, model_path)

    metadata = {
        "model_name": model_name,
        "trained_at": datetime.now().isoformat(),
        "metrics": metrics,
        "feature_columns": feature_columns,
        "train_period": list(train_period),
        "test_period": list(test_period),
        "train_size": train_size,
        "test_size": test_size,
        "version": "1.0",
    }

    meta_path.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    return model_path


def load_model():
    """
    Load a previously saved model.

    Returns the model object or None if no model exists.
    """
    model_path = MODELS_DIR / "spending_model.joblib"

    if not model_path.exists():
        return None

    return joblib.load(model_path)


def model_exists() -> bool:
    """Check whether a saved model file exists."""
    return (MODELS_DIR / "spending_model.joblib").exists()


def get_model_info() -> dict | None:
    """
    Return metadata about the saved model.

    Returns None if no model metadata exists.
    """
    meta_path = MODELS_DIR / "spending_model_meta.json"

    if not meta_path.exists():
        return None

    return json.loads(
        meta_path.read_text(encoding="utf-8")
    )
