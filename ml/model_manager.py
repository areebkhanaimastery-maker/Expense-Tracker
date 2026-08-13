"""
Model Manager — save, load, validate, and inspect trained ML models.

Uses joblib for serialization. Stores model artifacts alongside
metadata in the ml/models/ directory.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib

from app.config import settings
from app.exceptions.ml import MLModelError


logger = logging.getLogger(__name__)

MODELS_DIR = settings.models_dir


def _ensure_dir() -> None:
    """Create the models directory if it does not exist."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)


def save_model(
    model: Any,
    model_name: str,
    metrics: dict[str, float],
    feature_columns: list[str],
    train_period: tuple[str, str] | list[str],
    test_period: tuple[str, str] | list[str],
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

    try:
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
        logger.info("Saved model %s to %s", model_name, model_path)
        return model_path
    except Exception as e:
        raise MLModelError(f"Failed to save model: {e}") from e


def load_model() -> Any | None:
    """
    Load a previously saved model.

    Returns the model object or None if no model exists.
    """
    model_path = MODELS_DIR / "spending_model.joblib"

    if not model_path.exists():
        return None

    try:
        return joblib.load(model_path)
    except Exception as e:
        logger.error("Failed to load model from %s: %s", model_path, e)
        raise MLModelError(f"Model artifact is corrupt or unreadable: {e}") from e


def model_exists() -> bool:
    """Check whether a saved model file exists."""
    return (MODELS_DIR / "spending_model.joblib").exists()


def delete_model() -> bool:
    """Delete the saved model and metadata files."""
    model_path = MODELS_DIR / "spending_model.joblib"
    meta_path = MODELS_DIR / "spending_model_meta.json"

    deleted = False
    if model_path.exists():
        model_path.unlink()
        deleted = True
    if meta_path.exists():
        meta_path.unlink()

    return deleted


def get_model_info() -> dict[str, Any] | None:
    """
    Return metadata about the saved model.

    Returns None if no model metadata exists.
    """
    meta_path = MODELS_DIR / "spending_model_meta.json"

    if not meta_path.exists():
        return None

    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error("Error reading model metadata: %s", e)
        return None


def validate_model(expected_features: list[str] | None = None) -> tuple[bool, str]:
    """
    Validate that the saved model exists and matches expected features.
    """
    if not model_exists():
        return False, "No model artifact found."

    info = get_model_info()
    if not info:
        return False, "Model metadata missing or corrupt."

    if expected_features:
        saved_features = info.get("feature_columns", [])
        missing = set(expected_features) - set(saved_features)
        if missing:
            return False, f"Incompatible features. Missing: {missing}"

    return True, "Model is valid and compatible."
