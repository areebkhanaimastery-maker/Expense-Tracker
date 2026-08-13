"""
Machine Learning Pydantic Schemas.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AnomalyItem(BaseModel):
    expense_id: int
    amount: float
    category: str
    description: str
    date: str
    anomaly_score: float
    is_anomaly: bool
    severity: str  # High, Medium, Low


class AnomalyResponse(BaseModel):
    total_analyzed: int
    total_anomalies: int
    anomalies: List[AnomalyItem]


class PredictionItem(BaseModel):
    horizon: str  # next_day, next_7_days, next_30_days, next_month
    predicted_amount: float
    confidence: Optional[float] = None


class PredictionResponse(BaseModel):
    next_month_prediction: float
    predictions: List[PredictionItem]
    model_name: str
    disclaimer: str


class ModelTrainResponse(BaseModel):
    success: bool
    message: str
    trained_at: str
