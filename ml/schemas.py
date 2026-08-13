"""
ML Schemas and Dataclasses.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ModelMetadata:
    """Metadata describing a saved ML model."""

    model_name: str
    trained_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    metrics: dict[str, float] = field(default_factory=dict)
    feature_columns: list[str] = field(default_factory=list)
    train_period: list[str] = field(default_factory=list)
    test_period: list[str] = field(default_factory=list)
    train_size: int = 0
    test_size: int = 0
    version: str = "1.0"
